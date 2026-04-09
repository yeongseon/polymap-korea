# ruff: noqa: TC002
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.models import SourceDoc


@pytest.mark.asyncio
async def test_get_soft_deleted_source_returns_404(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_db: dict[str, object],
) -> None:
    source = await db_session.get(SourceDoc, seeded_db["source_doc"])
    assert source is not None
    source.deleted_at = datetime.now(timezone.utc)
    await db_session.commit()

    response = await client.get(f"/api/v1/sources/{seeded_db['source_doc']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Source document not found"
