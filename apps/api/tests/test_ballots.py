# ruff: noqa: TC002,E501
from __future__ import annotations

import pytest
from httpx import AsyncClient


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
