from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any
from xml.etree import ElementTree

import httpx

from common.base_adapter import BaseAdapter, RawRecord
from common.circuit_breaker import CircuitBreaker
from common.rate_limiter import TokenBucketRateLimiter

logger = logging.getLogger(__name__)


class NecAdapter(BaseAdapter):
    source_system = "nec"
    base_url = "http://apis.data.go.kr/9760000/"
    default_num_rows = 100

    def __init__(
        self,
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
        rate_limiter: TokenBucketRateLimiter | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> None:
        self.api_key = api_key or os.getenv("POLYMAP_NEC_API_KEY", "")
        self._client = client
        self._owns_client = client is None
        self.rate_limiter = rate_limiter or TokenBucketRateLimiter(rate=5.0, capacity=5)
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def __aenter__(self) -> NecAdapter:
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
        sg_id = str(params["sgId"])
        sg_typecode = str(params["sgTypecode"])
        return await self.fetch_candidates(sg_id, sg_typecode)

    async def fetch_election_codes(self) -> list[RawRecord]:
        return await self._fetch_paginated("CommonCodeService/getCommonSgCodeList", {})

    async def fetch_candidates(self, sgId: str, sgTypecode: str) -> list[RawRecord]:
        return await self._fetch_paginated(
            "PofelcddInfoInqireService/getPofelcddRegistSttusInfoInqire",
            {"sgId": sgId, "sgTypecode": sgTypecode},
        )

    async def fetch_pledges(self, sgId: str, sgTypecode: str) -> list[RawRecord]:
        return await self._fetch_paginated(
            "ElecPrmsInfoInqireService/getCnddtElecPrmsInfoInqire",
            {"sgId": sgId, "sgTypecode": sgTypecode},
        )

    async def fetch_party_policies(self, sgId: str) -> list[RawRecord]:
        return await self._fetch_paginated("PartyPlcInfoInqireService/getPartyPlcInfoInqire", {"sgId": sgId})

    async def fetch_candidate_resignations(self, sgId: str) -> list[RawRecord]:
        return await self._fetch_paginated(
            "CndaRegInvdInqireService/getCndaRsgtDthInvdInqire",
            {"sgId": sgId},
        )

    async def health_check(self) -> bool:
        try:
            await self.fetch_election_codes()
        except Exception:
            logger.exception("NEC health check failed")
            return False
        return True

    async def _fetch_paginated(self, endpoint: str, params: Mapping[str, Any]) -> list[RawRecord]:
        page_no = 1
        records: list[RawRecord] = []
        while True:
            request_params = {
                "serviceKey": self.api_key,
                "numOfRows": self.default_num_rows,
                "pageNo": page_no,
                **params,
            }
            status_code, parsed = await self._fetch_with_retry(endpoint, request_params)
            items = parsed["items"]
            if not items:
                break
            records.extend(self._to_raw_records(endpoint, request_params, status_code, items))
            total_count = parsed["total_count"]
            if total_count is None or page_no * self.default_num_rows >= total_count:
                break
            page_no += 1
        return records

    async def _fetch_with_retry(
        self,
        endpoint: str,
        params: Mapping[str, Any],
    ) -> tuple[int, dict[str, Any]]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            await self.rate_limiter.acquire()
            self.circuit_breaker.allow_request()
            try:
                logger.info("NEC request", extra={"endpoint": endpoint, "params": dict(params)})
                response = await self.client.get(endpoint, params=params)
                response.raise_for_status()
                logger.info(
                    "NEC response",
                    extra={"endpoint": endpoint, "status_code": response.status_code},
                )
                parsed = self._parse_xml_response(response.text)
                self.circuit_breaker.record_success()
                return response.status_code, parsed
            except (httpx.HTTPError, httpx.TimeoutException, ElementTree.ParseError, ValueError) as exc:
                self.circuit_breaker.record_failure()
                last_error = exc
                if attempt == self.max_retries:
                    break
                await asyncio.sleep(self.base_delay * (2 ** (attempt - 1)))

        assert last_error is not None
        raise last_error

    def _parse_xml_response(self, xml_text: str) -> dict[str, Any]:
        root = ElementTree.fromstring(xml_text)
        items: list[dict[str, Any]] = []
        for item in root.findall(".//item"):
            payload: dict[str, Any] = {}
            for child in item:
                payload[child.tag] = (child.text or "").strip()
            items.append(payload)
        total_count_text = root.findtext(".//totalCount")
        total_count = int(total_count_text) if total_count_text and total_count_text.isdigit() else None
        return {"items": items, "total_count": total_count}

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
                license_note="Subject to NEC source licensing.",
                election_phase="collection",
                data=item,
            )
            record.compute_hash()
            records.append(record)
        return records
