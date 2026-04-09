from __future__ import annotations

import pytest
import httpx
import respx

from common.base_adapter import RawRecord
from common.circuit_breaker import CircuitBreaker
from common.rate_limiter import TokenBucketRateLimiter
from sources.assembly.adapter import AssemblyAdapter


MEMBERS_RESPONSE = {
    "ALLNAMEMBER": [
        {"list_total_count": 2},
        {
            "row": [
                {
                    "HG_NM": "이재명",
                    "POLY_NM": "더불어민주당",
                    "ORIG_NM": "인천 계양구을",
                    "CMITS": "법제사법위원회",
                    "REELE_GBN_NM": "초선",
                },
                {
                    "HG_NM": "한동훈",
                    "POLY_NM": "국민의힘",
                    "ORIG_NM": "비례대표",
                    "CMITS": "외교통일위원회",
                    "REELE_GBN_NM": "초선",
                },
            ],
        },
    ],
}

BILL_RESPONSE = {
    "BILL": [
        {"list_total_count": 1},
        {
            "row": [
                {
                    "BILL_ID": "PRC_A2B3C4D5",
                    "BILL_NM": "지방자치법 개정안",
                    "PROPOSER": "이재명",
                    "PROPOSE_DT": "2026-01-15",
                    "PROC_RESULT_CD": "계류",
                    "CURR_COMMITTEE": "행정안전위원회",
                },
            ],
        },
    ],
}

BASE_URL = AssemblyAdapter.base_url


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
    **kwargs: object,
) -> AssemblyAdapter:
    return AssemblyAdapter(
        api_key="test-key",
        client=client,
        rate_limiter=rate_limiter,
        circuit_breaker=circuit_breaker,
        **kwargs,
    )


@pytest.mark.asyncio
async def test_fetch_members(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        respx.get(url__startswith=BASE_URL).respond(200, json=MEMBERS_RESPONSE)
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(client, rate_limiter, circuit_breaker)
            records = await adapter.fetch_members()

    assert len(records) == 2
    assert all(isinstance(r, RawRecord) for r in records)
    assert records[0].source_system == "assembly"
    assert records[0].data["HG_NM"] == "이재명"
    assert records[1].data["HG_NM"] == "한동훈"


@pytest.mark.asyncio
async def test_fetch_bills(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        respx.get(url__startswith=BASE_URL).respond(200, json=BILL_RESPONSE)
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(client, rate_limiter, circuit_breaker)
            records = await adapter.fetch_bills("이재명")

    assert len(records) == 1
    assert records[0].data["BILL_ID"] == "PRC_A2B3C4D5"
    assert records[0].data["BILL_NM"] == "지방자치법 개정안"


@pytest.mark.asyncio
async def test_fetch_empty_members(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    empty_response = {"ALLNAMEMBER": [{"list_total_count": 0}]}
    with respx.mock:
        respx.get(url__startswith=BASE_URL).respond(200, json=empty_response)
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(client, rate_limiter, circuit_breaker)
            records = await adapter.fetch_members()

    assert records == []


@pytest.mark.asyncio
async def test_health_check_success(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        respx.get(url__startswith=BASE_URL).respond(200, json=MEMBERS_RESPONSE)
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(client, rate_limiter, circuit_breaker)
            result = await adapter.health_check()

    assert result is True


@pytest.mark.asyncio
async def test_retry_on_server_error(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        route = respx.get(url__startswith=BASE_URL)
        route.side_effect = [
            httpx.Response(503, text="Service Unavailable"),
            httpx.Response(200, json=MEMBERS_RESPONSE),
        ]
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(
                client, rate_limiter, circuit_breaker,
                max_retries=3, base_delay=0.01,
            )
            records = await adapter.fetch_members()

    assert len(records) == 2
    assert route.call_count == 2
