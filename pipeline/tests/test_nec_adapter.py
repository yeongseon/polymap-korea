import httpx
import pytest
import respx
from typing import Any

from common.base_adapter import RawRecord
from common.circuit_breaker import CircuitBreaker
from common.rate_limiter import TokenBucketRateLimiter
from sources.nec.adapter import NecAdapter

NEC_XML_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <header>
        <resultCode>00</resultCode>
        <resultMsg>NORMAL SERVICE.</resultMsg>
    </header>
    <body>
        <items>
            <item>
                <sgId>20260603</sgId>
                <sgTypecode>2</sgTypecode>
                <hanglNm>홍길동</hanglNm>
                <jdName>민주당</jdName>
                <sdName>서울특별시</sdName>
                <wiwName>종로구</wiwName>
            </item>
            <item>
                <sgId>20260603</sgId>
                <sgTypecode>2</sgTypecode>
                <hanglNm>김영희</hanglNm>
                <jdName>국민의힘</jdName>
                <sdName>서울특별시</sdName>
                <wiwName>종로구</wiwName>
            </item>
        </items>
        <numOfRows>100</numOfRows>
        <pageNo>1</pageNo>
        <totalCount>2</totalCount>
    </body>
</response>"""

NEC_XML_EMPTY = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <header>
        <resultCode>00</resultCode>
    </header>
    <body>
        <items/>
        <totalCount>0</totalCount>
    </body>
</response>"""

ELECTION_CODES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <body>
        <items>
            <item>
                <sgId>20260603</sgId>
                <sgName>제9회 전국동시지방선거</sgName>
                <sgTypecode>2</sgTypecode>
            </item>
        </items>
        <totalCount>1</totalCount>
    </body>
</response>"""

BASE_URL = NecAdapter.base_url


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
) -> NecAdapter:
    return NecAdapter(
        api_key="test-key",
        client=client,
        rate_limiter=rate_limiter,
        circuit_breaker=circuit_breaker,
        **kwargs,
    )


@pytest.mark.asyncio
async def test_fetch_candidates(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        respx.get(url__startswith=BASE_URL).respond(200, text=NEC_XML_RESPONSE)
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(client, rate_limiter, circuit_breaker)
            records = await adapter.fetch_candidates("20260603", "2")

    assert len(records) == 2
    assert all(isinstance(r, RawRecord) for r in records)
    assert records[0].source_system == "nec"
    assert isinstance(records[0].data, dict)
    assert isinstance(records[1].data, dict)
    assert records[0].data["hanglNm"] == "홍길동"
    assert records[1].data["hanglNm"] == "김영희"
    assert all(r.response_hash != "" for r in records)


@pytest.mark.asyncio
async def test_fetch_election_codes(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        respx.get(url__startswith=BASE_URL).respond(200, text=ELECTION_CODES_XML)
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(client, rate_limiter, circuit_breaker)
            records = await adapter.fetch_election_codes()

    assert len(records) == 1
    assert isinstance(records[0].data, dict)
    assert records[0].data["sgId"] == "20260603"


@pytest.mark.asyncio
async def test_fetch_empty_response(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        respx.get(url__startswith=BASE_URL).respond(200, text=NEC_XML_EMPTY)
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(client, rate_limiter, circuit_breaker)
            records = await adapter.fetch_candidates("20260603", "2")

    assert records == []


@pytest.mark.asyncio
async def test_retry_on_failure(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        route = respx.get(url__startswith=BASE_URL)
        route.side_effect = [
            httpx.Response(500, text="Internal Server Error"),
            httpx.Response(200, text=ELECTION_CODES_XML),
        ]
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(
                client, rate_limiter, circuit_breaker,
                max_retries=3, base_delay=0.01,
            )
            records = await adapter.fetch_election_codes()

    assert len(records) == 1
    assert route.call_count == 2


@pytest.mark.asyncio
async def test_retry_on_malformed_xml(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        route = respx.get(url__startswith=BASE_URL)
        route.side_effect = [
            httpx.Response(200, text="<response><body>broken"),
            httpx.Response(200, text=ELECTION_CODES_XML),
        ]
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(
                client, rate_limiter, circuit_breaker,
                max_retries=3, base_delay=0.01,
            )
            records = await adapter.fetch_election_codes()

    assert len(records) == 1
    assert route.call_count == 2


@pytest.mark.asyncio
async def test_health_check_success(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        respx.get(url__startswith=BASE_URL).respond(200, text=ELECTION_CODES_XML)
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(client, rate_limiter, circuit_breaker)
            result = await adapter.health_check()

    assert result is True


@pytest.mark.asyncio
async def test_health_check_failure(rate_limiter: TokenBucketRateLimiter, circuit_breaker: CircuitBreaker) -> None:
    with respx.mock:
        respx.get(url__startswith=BASE_URL).respond(500, text="Error")
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            adapter = _make_adapter(
                client, rate_limiter, circuit_breaker,
                max_retries=1, base_delay=0.01,
            )
            result = await adapter.health_check()

    assert result is False
