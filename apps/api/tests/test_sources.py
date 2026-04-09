# ruff: noqa: TC002
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.models import ElectionWindow, SourceDoc

SEOUL_TZ = ZoneInfo("Asia/Seoul")


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


@pytest.mark.asyncio
async def test_get_hidden_source_returns_404(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_db: dict[str, object],
) -> None:
    source = await db_session.get(SourceDoc, seeded_db["source_doc"])
    assert source is not None
    source.visibility = "HIDDEN"
    await db_session.commit()

    response = await client.get(f"/api/v1/sources/{seeded_db['source_doc']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Source document not found"


@pytest.mark.asyncio
async def test_poll_related_source_is_blocked_during_blackout(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_db: dict[str, object],
) -> None:
    source = await db_session.get(SourceDoc, seeded_db["source_doc"])
    assert source is not None
    source.title = "여론조사 결과 요약"

    now = datetime.now(SEOUL_TZ)
    db_session.add(
        ElectionWindow(
            election_id=seeded_db["election"],
            content_type="poll_result",
            blackout_start=now - timedelta(minutes=30),
            blackout_end=now + timedelta(minutes=30),
        )
    )
    await db_session.commit()

    response = await client.get(f"/api/v1/sources/{seeded_db['source_doc']}")

    assert response.status_code == 403
