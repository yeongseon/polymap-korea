# ruff: noqa: B008,TC002,TC003
from __future__ import annotations

from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.deps import get_db
from polymap_api.middleware.content_guard import is_content_blocked
from polymap_api.models import ElectionWindow
from polymap_api.schemas.compliance import (
    AuditLogCreate,
    ComplianceAuditLogRead,
    ComplianceElectionWindowRead,
    ElectionWindowStatusRead,
)
from polymap_api.services.audit import record_audit

router = APIRouter(prefix="/compliance", tags=["compliance"])
SEOUL_TZ = ZoneInfo("Asia/Seoul")


def _to_seoul(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=SEOUL_TZ)
    return value.astimezone(SEOUL_TZ)


async def require_admin_placeholder(
    x_admin_role: str = Header(default="", alias="X-Admin-Role"),
) -> None:
    if x_admin_role.lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


@router.get("/election-windows", response_model=list[ComplianceElectionWindowRead])
async def list_election_windows(db: AsyncSession = Depends(get_db)) -> list[ElectionWindow]:
    result = await db.scalars(
        select(ElectionWindow).order_by(
            ElectionWindow.blackout_start.asc(),
            ElectionWindow.created_at.asc(),
        )
    )
    return list(result)


@router.get("/election-windows/{election_id}/status", response_model=ElectionWindowStatusRead)
async def get_election_window_status(
    election_id: UUID,
    content_type: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
) -> ElectionWindowStatusRead:
    result = await db.scalars(
        select(ElectionWindow).where(
            ElectionWindow.election_id == election_id,
            ElectionWindow.content_type == content_type,
        )
    )
    windows = list(result)
    blocked = await is_content_blocked(content_type=content_type, election_id=election_id, db=db)
    checked_at = datetime.now(SEOUL_TZ)
    active_window = next(
        (
            window
            for window in windows
            if _to_seoul(window.blackout_start) <= checked_at <= _to_seoul(window.blackout_end)
        ),
        None,
    )
    return ElectionWindowStatusRead(
        election_id=election_id,
        content_type=content_type,
        blocked=blocked,
        checked_at=checked_at,
        active_window=(ComplianceElectionWindowRead.model_validate(active_window) if active_window is not None else None),
    )


@router.post("/audit-log", response_model=ComplianceAuditLogRead, status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    payload: AuditLogCreate,
    _: None = Depends(require_admin_placeholder),
    db: AsyncSession = Depends(get_db),
) -> ComplianceAuditLogRead:
    audit_log = await record_audit(db=db, **payload.model_dump())
    await db.commit()
    await db.refresh(audit_log)
    return ComplianceAuditLogRead.model_validate(audit_log)
