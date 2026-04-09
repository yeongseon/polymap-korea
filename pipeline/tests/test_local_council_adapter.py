from __future__ import annotations

import httpx
import pytest
import respx
from typing import Any

from common.base_adapter import RawRecord
from common.circuit_breaker import CircuitBreaker
from common.rate_limiter import TokenBucketRateLimiter
from sources.local_council.adapter import LocalCouncilAdapter


MEMBERS_RESPONSE = {
    "row": [
        {
            "member_name": "김민수",
            "party": "정의당",
            "district": "서울특별시 종로구",
        },
    ],
    "list_total_count": 1,
}

BASE_URL = LocalCouncilAdapter.base_url


@pytest.fixture
def rate_limiter() -> TokenBucketRateLimiter:
    return TokenBucketRateLimiter(rate=1000.0, capacity=1000)


@pytest.fixture
def circuit_breaker() -> CircuitBreaker:
    return CircuitBreaker()


def _make_adapter(
    client: httpx.AsyncClient,
    rate_limiter: TokenBucketRateLimiter,
    circuit_breaker: CircuitBreaker,
    **kwargs: Any,
) -> LocalCouncilAdapter:
    return LocalCouncilAdapter(
        api_key="test-key",
        client=client,
        rate_limiter=rate_limiter,
        circuit_breaker=circuit_breaker,
        **kwargs,
    )


@pytest.mark.asyncio
async def test_fetch_council_members(
    rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker,
) -> None:
    with respx.mock:
        respx.get(url__startswith=BASE_URL).respond(200, json=MEMBERS_RESPONSE)
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(client, rate_limiter, circuit_breaker)
            records = await adapter.fetch_council_members("SEOUL")

    assert len(records) == 1
    assert isinstance(records[0], RawRecord)
    assert records[0].source_system == "local_council"
    assert isinstance(records[0].data, dict)
    assert records[0].data["member_name"] == "김민수"


@pytest.mark.asyncio
async def test_retry_on_malformed_json(
    rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker,
) -> None:
    with respx.mock:
        route = respx.get(url__startswith=BASE_URL)
        route.side_effect = [
            httpx.Response(200, text="not-json"),
            httpx.Response(200, json=MEMBERS_RESPONSE),
        ]
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(
                client, rate_limiter, circuit_breaker,
                max_retries=3, base_delay=0.01,
            )
            records = await adapter.fetch_council_members("SEOUL")

    assert len(records) == 1
    assert route.call_count == 2
