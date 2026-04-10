# ruff: noqa: TC002
from __future__ import annotations

import importlib
from datetime import date
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.models import District, Election, Race
from polymap_ontology.enums import ElectionType, PositionType

geocoding = importlib.import_module("polymap_api.services.geocoding")


@pytest.fixture
async def district_fixture(db_session: AsyncSession) -> dict[str, District]:
    election = Election(
        id=uuid4(),
        name="2026 Local General Election",
        election_type=ElectionType.LOCAL_GENERAL,
        election_date=date(2026, 6, 3),
    )
    seoul = District(id=uuid4(), name_ko="서울특별시", code="11-seoul", level="metropolitan", parent_id=None)
    jongno = District(id=uuid4(), name_ko="종로구", code="11-jongno", level="basic", parent_id=seoul.id)
    sajik = District(id=uuid4(), name_ko="사직동", code="11-jongno-sajik", level="constituency", parent_id=jongno.id)
    race = Race(
        id=uuid4(),
        election_id=election.id,
        district_id=sajik.id,
        position_type=PositionType.COUNCIL_MEMBER,
        seat_count=1,
    )

    db_session.add_all([election, seoul, jongno, sajik, race])
    await db_session.commit()
    return {"seoul": seoul, "jongno": jongno, "sajik": sajik}


@pytest.mark.asyncio
async def test_juso_resolver_matches_specific_district(district_fixture: dict[str, District]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["keyword"] == "서울 종로구 사직로 161"
        return httpx.Response(
            200,
            json={
                "results": {
                    "common": {"errorCode": "0", "errorMessage": "정상"},
                    "juso": [
                        {
                            "roadAddrPart1": "서울특별시 종로구 사직로 161",
                            "jibunAddr": "서울특별시 종로구 사직동 1-1",
                            "siNm": "서울특별시",
                            "sggNm": "종로구",
                            "emdNm": "사직동",
                        }
                    ],
                }
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        resolver = geocoding.JusoApiResolver(api_key="test-key", client=client)
        resolved = await resolver.resolve("서울 종로구 사직로 161", list(district_fixture.values()))

    assert resolved is not None
    assert resolved.id == district_fixture["sajik"].id


@pytest.mark.asyncio
async def test_chain_resolver_falls_back_when_juso_lookup_fails(district_fixture: dict[str, District]) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "unavailable"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        resolver = geocoding.ChainResolver(
            [
                geocoding.JusoApiResolver(api_key="test-key", client=client),
                geocoding.FallbackResolver(),
            ]
        )
        resolved = await resolver.resolve("서울특별시 종로구 사직동", list(district_fixture.values()))

    assert resolved is not None
    assert resolved.id == district_fixture["sajik"].id


@pytest.mark.asyncio
async def test_juso_resolver_ignores_api_errors_with_no_match(district_fixture: dict[str, District]) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": {
                    "common": {"errorCode": "E0001", "errorMessage": "invalid key"},
                    "juso": [],
                }
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        resolver = geocoding.ChainResolver(
            [
                geocoding.JusoApiResolver(api_key="bad-key", client=client),
                geocoding.FallbackResolver(),
            ]
        )
        resolved = await resolver.resolve("부산광역시 해운대구 우동", list(district_fixture.values()))

    assert resolved is None
