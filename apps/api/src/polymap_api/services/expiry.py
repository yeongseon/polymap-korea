from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.models import SourceDoc
from polymap_api.services.audit import record_audit


async def expire_source_docs(db: AsyncSession) -> int:
    now = datetime.now(timezone.utc)
    result = await db.scalars(
        select(SourceDoc).where(
            SourceDoc.public_expiry_at.is_not(None),
            SourceDoc.public_expiry_at < now,
            SourceDoc.visibility != "HIDDEN",
        )
    )
    expired_docs = list(result)

    for source_doc in expired_docs:
        old_value = {"visibility": source_doc.visibility}
        source_doc.visibility = "HIDDEN"
        await record_audit(
            db,
            actor="system",
            action="EXPIRE",
            entity_type="source_doc",
            entity_id=source_doc.id,
            reason_code="PUBLIC_EXPIRY",
            old_value=old_value,
            new_value={"visibility": source_doc.visibility},
            legal_basis="PUBLIC_EXPIRY_POLICY",
        )

    await db.flush()
    return len(expired_docs)
