# ruff: noqa: TC002
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.middleware.content_guard import ensure_content_visible, is_content_blocked
from polymap_api.models import AuditLog, ElectionWindow, SourceDoc
from polymap_api.services.expiry import expire_source_docs
from polymap_ontology.enums import SourceDocKind

SEOUL_TZ = ZoneInfo("Asia/Seoul")


@pytest.mark.asyncio
async def test_election_window_status_and_content_guard(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_db: dict[str, object],
) -> None:
    election_id = seeded_db["election"]
    assert isinstance(election_id, uuid.UUID)
    now = datetime.now(SEOUL_TZ)
    blocked_window = ElectionWindow(
        election_id=election_id,
        content_type="poll_result",
        blackout_start=now - timedelta(hours=1),
        blackout_end=now + timedelta(hours=1),
    )
    allowed_window = ElectionWindow(
        election_id=election_id,
        content_type="candidate_docs",
        blackout_start=now + timedelta(days=1),
        blackout_end=now + timedelta(days=2),
    )
    db_session.add_all([blocked_window, allowed_window])
    await db_session.commit()

    list_response = await client.get("/api/v1/compliance/election-windows")
    blocked_response = await client.get(
        f"/api/v1/compliance/election-windows/{seeded_db['election']}/status",
        params={"content_type": "poll_result"},
    )
    allowed_response = await client.get(
        f"/api/v1/compliance/election-windows/{seeded_db['election']}/status",
        params={"content_type": "candidate_docs"},
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    assert blocked_response.status_code == 200
    blocked_payload = blocked_response.json()
    assert blocked_payload["blocked"] is True
    assert blocked_payload["active_window"]["content_type"] == "poll_result"

    assert allowed_response.status_code == 200
    assert allowed_response.json()["blocked"] is False

    assert await is_content_blocked("poll_result", election_id, db_session) is True
    assert await is_content_blocked("candidate_docs", election_id, db_session) is False


@pytest.mark.asyncio
async def test_audit_log_creation_and_append_only_guard(
    client: AsyncClient,
    db_session: AsyncSession,
    seeded_db: dict[str, object],
) -> None:
    response = await client.post(
        "/api/v1/compliance/audit-log",
        headers={"X-Admin-Role": "admin"},
        json={
            "actor": "admin-user",
            "action": "REVIEW",
            "entity_type": "source_doc",
            "entity_id": str(seeded_db["source_doc"]),
            "reason_code": "LEGAL_CHECK",
            "new_value": {"visibility": "VISIBLE"},
            "legal_basis": "ELECTION_COMPLIANCE",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["actor"] == "admin-user"
    assert payload["reason_code"] == "LEGAL_CHECK"

    audit_log = await db_session.get(AuditLog, uuid.UUID(payload["id"]))
    assert audit_log is not None

    audit_log.action = "ALTERED"
    with pytest.raises(ValueError, match="append-only"):
        await db_session.commit()
    await db_session.rollback()

    await db_session.delete(audit_log)
    with pytest.raises(ValueError, match="append-only"):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_source_doc_expiry_hides_document_and_records_audit(
    db_session: AsyncSession,
    seeded_db: dict[str, object],
) -> None:
    source_doc = await db_session.get(SourceDoc, seeded_db["source_doc"])
    assert source_doc is not None
    source_doc.visibility = "VISIBLE"
    source_doc.public_expiry_at = datetime.now(timezone.utc) - timedelta(minutes=1)

    unexpired_doc = SourceDoc(
        id=uuid.uuid4(),
        kind=SourceDocKind.NEWS_ARTICLE,
        title="Still public",
        visibility="VISIBLE",
        public_expiry_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    db_session.add(unexpired_doc)
    await db_session.commit()

    expired_count = await expire_source_docs(db_session)
    await db_session.commit()
    await db_session.refresh(source_doc)
    await db_session.refresh(unexpired_doc)

    audit_logs = list(
        await db_session.scalars(
            select(AuditLog).where(
                AuditLog.entity_type == "source_doc",
                AuditLog.reason_code == "PUBLIC_EXPIRY",
            )
        )
    )

    assert expired_count == 1
    assert source_doc.visibility == "HIDDEN"
    assert unexpired_doc.visibility == "VISIBLE"
    assert len(audit_logs) == 1
    assert audit_logs[0].entity_id == source_doc.id


@pytest.mark.asyncio
async def test_content_guard_dependency_blocks_only_active_blackout(
    db_session: AsyncSession,
    seeded_db: dict[str, object],
) -> None:
    election_id = seeded_db["election"]
    assert isinstance(election_id, uuid.UUID)
    now = datetime.now(SEOUL_TZ)
    db_session.add(
        ElectionWindow(
            election_id=election_id,
            content_type="poll_result",
            blackout_start=now - timedelta(minutes=30),
            blackout_end=now + timedelta(minutes=30),
        )
    )
    await db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await ensure_content_visible("poll_result", election_id, db_session)

    assert exc_info.value.status_code == 403
    await ensure_content_visible("candidate_docs", election_id, db_session)

