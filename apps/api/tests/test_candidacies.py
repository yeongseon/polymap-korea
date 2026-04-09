# ruff: noqa: TC002,E501
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_candidacies_supports_filters(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    response = await client.get(
        "/api/v1/candidacies",
        params={"election_id": str(seeded_db["election"]), "district_id": str(seeded_db["district"])},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_candidacy_detail_promises_and_claims(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    detail_response = await client.get(f"/api/v1/candidacies/{seeded_db['candidacy']}")
    promises_response = await client.get(f"/api/v1/candidacies/{seeded_db['candidacy']}/promises")
    claims_response = await client.get(f"/api/v1/candidacies/{seeded_db['candidacy']}/claims")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["person"]["id"] == str(seeded_db["person"])
    assert detail["party"]["id"] == str(seeded_db["party"])
    assert detail["promises"][0]["id"] == str(seeded_db["promise"])
    assert detail["claims"][0]["id"] == str(seeded_db["claim"])

    assert promises_response.status_code == 200
    assert promises_response.json()[0]["title"] == "Transit expansion"

    assert claims_response.status_code == 200
    assert claims_response.json()[0]["content"] == "Will add new subway lines."
