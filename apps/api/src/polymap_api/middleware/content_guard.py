# ruff: noqa: B008,TC002,TC003
from __future__ import annotations

from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.deps import get_db
from polymap_api.models import ElectionWindow

SEOUL_TZ = ZoneInfo("Asia/Seoul")


def current_seoul_time() -> datetime:
    return datetime.now(SEOUL_TZ)


def _to_seoul(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=SEOUL_TZ)
    return value.astimezone(SEOUL_TZ)


async def is_content_blocked(content_type: str, election_id: UUID, db: AsyncSession) -> bool:
    result = await db.scalars(
        select(ElectionWindow).where(
            ElectionWindow.election_id == election_id,
            ElectionWindow.content_type == content_type,
        )
    )
    now = current_seoul_time()
    return any(_to_seoul(window.blackout_start) <= now <= _to_seoul(window.blackout_end) for window in result)


async def ensure_content_visible(
    content_type: str,
    election_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    if await is_content_blocked(content_type=content_type, election_id=election_id, db=db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Content is currently blocked by election blackout window")
