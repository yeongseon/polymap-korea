from __future__ import annotations

import pytest
from httpx import AsyncClient

from polymap_api.config import settings


@pytest.mark.asyncio
async def test_publish_snapshot_accepts_admin_requests(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/admin/publish/snapshot",
        headers={"Authorization": f"Bearer {settings.admin_api_key}"},
        json={"snapshot": {"version": "0.1.0"}},
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
            json={"snapshot": {"version": "0.1.0"}},
        )
    finally:
        settings.admin_api_key = original_key

    assert response.status_code == 503
    assert response.json()["detail"] == "Admin API key not configured"
