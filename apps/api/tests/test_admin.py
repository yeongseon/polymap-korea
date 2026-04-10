from __future__ import annotations

import pytest
from httpx import AsyncClient

from polymap_api.config import settings


SNAPSHOT_PAYLOAD = {
    "version": "0.1.0",
    "schema_version": "2026-04-09",
    "generated_at": "2026-04-10T00:00:00+00:00",
    "entity_catalog": [
        {"table": "elections", "description": "선거 목록", "priority": "high"},
    ],
    "entity_count": 1,
    "publish_targets": ["api_index", "static_snapshot"],
}


@pytest.mark.asyncio
async def test_publish_snapshot_accepts_admin_requests(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/admin/publish/snapshot",
        headers={"Authorization": f"Bearer {settings.admin_api_key}"},
        json=SNAPSHOT_PAYLOAD,
    )

    assert response.status_code == 202
    assert response.json() == {
        "status": "accepted",
        "message": "Snapshot v0.1.0 accepted for processing",
    }


@pytest.mark.asyncio
async def test_publish_snapshot_requires_configured_admin_key(client: AsyncClient) -> None:
    original_key = settings.admin_api_key
    settings.admin_api_key = ""
    try:
        response = await client.post(
            "/api/v1/admin/publish/snapshot",
            headers={"Authorization": "Bearer some-key"},
            json=SNAPSHOT_PAYLOAD,
        )
    finally:
        settings.admin_api_key = original_key

    assert response.status_code == 503
    assert response.json()["detail"] == "Admin API key not configured"
