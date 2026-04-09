# ruff: noqa: TC002,E501
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_elections(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    response = await client.get("/api/v1/elections")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(seeded_db["election"])
    assert data[0]["name"] == "2026 Local General Election"


@pytest.mark.asyncio
async def test_get_election_detail_and_races(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    detail_response = await client.get(f"/api/v1/elections/{seeded_db['election']}")
    races_response = await client.get(f"/api/v1/elections/{seeded_db['election']}/races")

    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == str(seeded_db["election"])

    assert races_response.status_code == 200
    races = races_response.json()
    assert len(races) == 1
    assert races[0]["id"] == str(seeded_db["race"])
