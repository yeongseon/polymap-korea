# ruff: noqa: TC002
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_district_detail(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    response = await client.get(f"/api/v1/districts/{seeded_db['district']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(seeded_db["district"])
    assert data["name_ko"] == "종로구"
    assert data["parent_id"] == str(seeded_db["district_parent"])
