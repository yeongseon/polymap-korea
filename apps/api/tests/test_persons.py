# ruff: noqa: TC002,E501
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_persons_supports_name_search(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    response = await client.get("/api/v1/persons", params={"name": "홍길"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(seeded_db["person"])


@pytest.mark.asyncio
async def test_get_person_detail_includes_related_resources(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    response = await client.get(f"/api/v1/persons/{seeded_db['person']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(seeded_db["person"])
    assert data["candidacies"][0]["id"] == str(seeded_db["candidacy"])
    assert data["committee_assignments"][0]["committee_name"] == "Transport Committee"
    assert data["bill_sponsorships"][0]["bill_name"] == "Public Transit Act"
