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


class AssemblyAdapter(BaseAdapter):
    source_system = "assembly"
    base_url = "https://open.assembly.go.kr/portal/openapi/"
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
        self.api_key = api_key or os.getenv("POLYMAP_ASSEMBLY_API_KEY", "")
        self._client = client
        self._owns_client = client is None
        self.rate_limiter = rate_limiter or TokenBucketRateLimiter(rate=5.0, capacity=5)
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def __aenter__(self) -> AssemblyAdapter:
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
        return await self.fetch_members()

    async def fetch_members(self) -> list[RawRecord]:
        return await self._fetch_paginated("ALLNAMEMBER", {})

    async def fetch_bills(self, memberName: str) -> list[RawRecord]:
        return await self._fetch_paginated("BILL", {"PROPOSER": memberName})

    async def fetch_votes(self, billId: str) -> list[RawRecord]:
        return await self._fetch_paginated("VOTE", {"BILL_ID": billId})

    async def fetch_committee_activities(self, memberName: str) -> list[RawRecord]:
        return await self._fetch_paginated("COMMITTEEACTIVITY", {"HG_NM": memberName})

    async def health_check(self) -> bool:
        try:
            await self.fetch_members()
        except Exception:
            logger.exception("Assembly health check failed")
            return False
        return True

    async def _fetch_paginated(self, endpoint: str, params: Mapping[str, Any]) -> list[RawRecord]:
        page_index = 1
        records: list[RawRecord] = []
        while True:
            request_params = {
                "KEY": self.api_key,
                "Type": "json",
                "pIndex": page_index,
                "pSize": self.page_size,
                **params,
            }
            response = await self._request_with_retry(endpoint, request_params)
            payload = response.json()
            items, total_count = self._extract_items(payload, endpoint)
            if not items:
                break
            records.extend(self._to_raw_records(endpoint, request_params, response.status_code, items))
            if total_count is None or page_index * self.page_size >= total_count:
                break
            page_index += 1
        return records

    async def _request_with_retry(
        self,
        endpoint: str,
        params: Mapping[str, Any],
    ) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            await self.rate_limiter.acquire()
            self.circuit_breaker.allow_request()
            try:
                logger.info("Assembly request", extra={"endpoint": endpoint, "params": dict(params)})
                response = await self.client.get(endpoint, params=params)
                response.raise_for_status()
                logger.info(
                    "Assembly response",
                    extra={"endpoint": endpoint, "status_code": response.status_code},
                )
                self.circuit_breaker.record_success()
                return response
            except (httpx.HTTPError, httpx.TimeoutException, ValueError) as exc:
                self.circuit_breaker.record_failure()
                last_error = exc
                if attempt == self.max_retries:
                    break
                await asyncio.sleep(self.base_delay * (2 ** (attempt - 1)))

        assert last_error is not None
        raise last_error

    def _extract_items(self, payload: dict[str, Any], endpoint: str) -> tuple[list[dict[str, Any]], int | None]:
        dataset = payload.get(endpoint)
        if not isinstance(dataset, list):
            return [], None

        items: list[dict[str, Any]] = []
        total_count: int | None = None
        for entry in dataset:
            if not isinstance(entry, dict):
                continue
            rows = entry.get("row")
            if isinstance(rows, list):
                items.extend(item for item in rows if isinstance(item, dict))
            if total_count is None:
                count_value = entry.get("list_total_count")
                if isinstance(count_value, int):
                    total_count = count_value
                elif isinstance(count_value, str) and count_value.isdigit():
                    total_count = int(count_value)
        return items, total_count

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
                license_note="Subject to National Assembly data terms.",
                election_phase="collection",
                data=item,
            )
            record.compute_hash()
            records.append(record)
        return records
