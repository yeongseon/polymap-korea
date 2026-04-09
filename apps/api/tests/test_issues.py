# ruff: noqa: TC002,E501
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_issues_returns_hierarchy(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    response = await client.get("/api/v1/issues")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(seeded_db["issue_parent"])
    assert data[0]["children"][0]["id"] == str(seeded_db["issue"])


@pytest.mark.asyncio
async def test_get_issue_detail_includes_related_promises(client: AsyncClient, seeded_db: dict[str, object]) -> None:
    response = await client.get(f"/api/v1/issues/{seeded_db['issue']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(seeded_db["issue"])
    assert data["related_promises"][0]["id"] == str(seeded_db["promise"])
    assert data["related_promises"][0]["candidacy"]["id"] == str(seeded_db["candidacy"])
