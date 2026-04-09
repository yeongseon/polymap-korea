from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.models import AuditLog


async def record_audit(
    db: AsyncSession,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: UUID,
    reason_code: str | None = None,
    old_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
    legal_basis: str | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        old_value=old_value,
        new_value=new_value,
        legal_basis=legal_basis,
    )
    db.add(audit_log)
    await db.flush()
    return audit_log
