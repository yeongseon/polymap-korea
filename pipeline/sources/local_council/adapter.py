from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

import httpx

from common.base_adapter import BaseAdapter, RawRecord
from common.circuit_breaker import CircuitBreaker
from common.rate_limiter import TokenBucketRateLimiter

logger = logging.getLogger(__name__)


class LocalCouncilAdapter(BaseAdapter):
    source_system = "local_council"
    base_url = "https://clik.nanet.go.kr/"
    page_size = 100

    def __init__(
        self,
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
        rate_limiter: TokenBucketRateLimiter | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> None:
        self.api_key = api_key or os.getenv("POLYMAP_LOCAL_COUNCIL_API_KEY", "")
        self._client = client
        self._owns_client = client is None
        self.rate_limiter = rate_limiter or TokenBucketRateLimiter(rate=0.01, capacity=1)
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def __aenter__(self) -> LocalCouncilAdapter:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self._client

    async def fetch(self, **params: Any) -> list[RawRecord]:
        council_code = str(params["councilCode"])
        return await self.fetch_council_members(council_code)

    async def fetch_council_members(self, councilCode: str) -> list[RawRecord]:
        return await self._fetch_paginated(
            "openapi/localCouncil/memberInfo.do",
            {"councilCode": councilCode, "councilType": "metropolitan"},
        )

    async def fetch_council_bills(self, councilCode: str) -> list[RawRecord]:
        return await self._fetch_paginated(
            "openapi/localCouncil/billInfo.do",
            {"councilCode": councilCode, "councilType": "metropolitan"},
        )

    async def health_check(self) -> bool:
        try:
            status_code, _, _ = await self._fetch_with_retry(
                "openapi/localCouncil/memberInfo.do",
                {"pIndex": 1, "pSize": 1, "councilType": "metropolitan"},
            )
        except Exception:
            logger.exception("Local council health check failed")
            return False
        return status_code == 200

    async def _fetch_paginated(self, endpoint: str, params: Mapping[str, Any]) -> list[RawRecord]:
        page_index = 1
        records: list[RawRecord] = []
        while True:
            request_params = {
                "key": self.api_key,
                "Type": "json",
                "pIndex": page_index,
                "pSize": self.page_size,
                **params,
            }
            status_code, items, total_count = await self._fetch_with_retry(endpoint, request_params)
            if not items:
                break
            records.extend(self._to_raw_records(endpoint, request_params, status_code, items))
            if total_count is None or page_index * self.page_size >= total_count:
                break
            page_index += 1
        return records

    async def _fetch_with_retry(
        self,
        endpoint: str,
        params: Mapping[str, Any],
    ) -> tuple[int, list[dict[str, Any]], int | None]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            await self.rate_limiter.acquire()
            self.circuit_breaker.allow_request()
            try:
                logger.info(
                    "Local council request",
                    extra={"endpoint": endpoint, "params": dict(params)},
                )
                response = await self.client.get(endpoint, params=params)
                response.raise_for_status()
                logger.info(
                    "Local council response",
                    extra={"endpoint": endpoint, "status_code": response.status_code},
                )
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError(f"Unexpected response structure for {endpoint}")
                items, total_count = self._extract_items(payload)
                self.circuit_breaker.record_success()
                return response.status_code, items, total_count
            except (httpx.HTTPError, httpx.TimeoutException, ValueError) as exc:
                self.circuit_breaker.record_failure()
                last_error = exc
                if attempt == self.max_retries:
                    break
                await asyncio.sleep(self.base_delay * (2 ** (attempt - 1)))

        assert last_error is not None
        raise last_error

    def _extract_items(self, payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int | None]:
        if isinstance(payload.get("row"), list):
            items = [item for item in payload["row"] if isinstance(item, dict)]
            count_value = payload.get("list_total_count")
            if isinstance(count_value, int):
                return items, count_value
            if isinstance(count_value, str) and count_value.isdigit():
                return items, int(count_value)
            return items, None

        for value in payload.values():
            if isinstance(value, list):
                for entry in value:
                    if isinstance(entry, dict) and isinstance(entry.get("row"), list):
                        rows = [item for item in entry["row"] if isinstance(item, dict)]
                        count_value = entry.get("list_total_count")
                        if isinstance(count_value, int):
                            return rows, count_value
                        if isinstance(count_value, str) and count_value.isdigit():
                            return rows, int(count_value)
                        return rows, None
        raise ValueError("Unexpected response structure for local council response")

    def _to_raw_records(
        self,
        endpoint: str,
        request_params: Mapping[str, Any],
        status_code: int,
        items: list[dict[str, Any]],
    ) -> list[RawRecord]:
        records: list[RawRecord] = []
        for item in items:
            record = RawRecord(
                source_system=self.source_system,
                endpoint=endpoint,
                request_params=dict(request_params),
                fetched_at=datetime.now(timezone.utc),
                http_status=status_code,
                license_note="Subject to local council publication rules.",
                election_phase="collection",
                data=item,
            )
            record.compute_hash()
            records.append(record)
        return records
