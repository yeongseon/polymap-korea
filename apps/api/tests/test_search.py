# ruff: noqa: TC002,E501
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_returns_unified_results(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    response = await client.get("/api/v1/search", params={"q": "홍"})

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "홍"
    assert data["persons"][0]["id"] == str(seeded_db["person"])
    assert data["issues"] == []
    assert data["parties"] == []


@pytest.mark.asyncio
async def test_search_type_filter_limits_scope(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    response = await client.get("/api/v1/search", params={"q": "미래", "type": "party"})

    assert response.status_code == 200
    data = response.json()
    assert data["persons"] == []
    assert data["issues"] == []
    assert data["parties"][0]["id"] == str(seeded_db["party"])
