from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base, UUIDPrimaryKeyMixin

DateTimeType = dt.datetime
UUIDType = uuid.UUID


class AuditLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_log"

    action: Mapped[str] = mapped_column(String, nullable=False)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), nullable=False)
    actor: Mapped[str | None] = mapped_column(String, nullable=True)
    diff: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[DateTimeType] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
