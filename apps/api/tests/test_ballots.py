# ruff: noqa: I001,TC002,E501
from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.models import Candidacy, District, Election, Party, Person, Race
from polymap_ontology.enums import CandidacyStatus, ElectionType, Gender, PositionType


@pytest.mark.asyncio
async def test_resolve_ballot_from_address(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    response = await client.post(
        "/api/v1/ballots/resolve",
        json={"address_text": "서울특별시 종로구 사직동"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["district"]["id"] == str(seeded_db["district"])
    assert len(data["races"]) == 1
    assert data["races"][0]["race"]["id"] == str(seeded_db["race"])
    assert [item["candidate_number"] for item in data["races"][0]["candidacies"]] == [1, 2]


@pytest.mark.asyncio
async def test_resolve_ballot_prefers_parent_matched_district(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    election = Election(
        id=uuid4(),
        name="2026 Ambiguous District Election",
        election_type=ElectionType.LOCAL_GENERAL,
        election_date=date(2026, 6, 3),
    )
    seoul = District(id=uuid4(), name_ko="서울특별시", code="11-seoul", level="metropolitan", parent_id=None)
    seoul_junggu = District(id=uuid4(), name_ko="중구", code="11-junggu", level="basic", parent_id=seoul.id)
    daegu = District(id=uuid4(), name_ko="대구광역시", code="27-daegu", level="metropolitan", parent_id=None)
    daegu_junggu = District(id=uuid4(), name_ko="중구", code="27-junggu", level="basic", parent_id=daegu.id)
    race = Race(
        id=uuid4(),
        election_id=election.id,
        district_id=seoul_junggu.id,
        position_type=PositionType.COUNCIL_MEMBER,
        seat_count=1,
    )

    db_session.add_all([election, seoul, seoul_junggu, daegu, daegu_junggu, race])
    await db_session.commit()

    response = await client.post(
        "/api/v1/ballots/resolve",
        json={"address_text": "서울특별시 중구 을지로"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["district"]["id"] == str(seoul_junggu.id)
    assert [item["race"]["id"] for item in data["races"]] == [str(race.id)]


@pytest.mark.asyncio
async def test_resolve_ballot_includes_parent_scoped_races(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_db: dict[str, object],
) -> None:
    parent_race = Race(
        id=uuid4(),
        election_id=seeded_db["election"],
        district_id=seeded_db["district_parent"],
        position_type=PositionType.GOVERNOR,
        seat_count=1,
    )
    parent_person = Person(
        id=uuid4(),
        name_ko="박후보",
        name_en="Park Candidate",
        birth_date=date(1975, 7, 7),
        gender=Gender.FEMALE,
    )
    parent_party = Party(
        id=uuid4(),
        name_ko="시민당",
        abbreviation="CD",
        color="#00AAFF",
    )
    parent_candidacy = Candidacy(
        id=uuid4(),
        person_id=parent_person.id,
        race_id=parent_race.id,
        party_id=parent_party.id,
        status=CandidacyStatus.REGISTERED,
        candidate_number=9,
    )

    db_session.add_all([parent_race, parent_person, parent_party, parent_candidacy])
    await db_session.commit()

    response = await client.post(
        "/api/v1/ballots/resolve",
        json={"address_text": "서울특별시 종로구 사직동"},
    )

    assert response.status_code == 200
    data = response.json()
    assert [item["race"]["id"] for item in data["races"]] == [
        str(seeded_db["race"]),
        str(parent_race.id),
    ]
    assert data["races"][1]["candidacies"][0]["candidate_number"] == 9


@pytest.mark.asyncio
async def test_resolve_ballot_unknown_address_returns_404(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/ballots/resolve",
        json={"address_text": "화성시 어딘가 없는동"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "District could not be resolved"
