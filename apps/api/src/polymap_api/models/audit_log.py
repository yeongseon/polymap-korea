# ruff: noqa: TC003,E501,F401
# pyright: reportUnusedFunction=false
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Index, String, Uuid, event, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from polymap_api.db import Base

_ACTION_ALIASES = {
    "create": "CREATE",
    "insert": "CREATE",
    "update": "UPDATE",
    "delete": "DELETE",
}


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        Index("ix_audit_log_entity_lookup", "entity_type", "entity_id"),
        Index("ix_audit_log_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    reason_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    old_value: Mapped[dict[str, Any] | None] = mapped_column(JSONB().with_variant(JSON(), "sqlite"), nullable=True)
    new_value: Mapped[dict[str, Any] | None] = mapped_column(JSONB().with_variant(JSON(), "sqlite"), nullable=True)
    legal_basis: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __init__(self, **kwargs: Any) -> None:
        action = kwargs.get("action")
        if isinstance(action, str):
            kwargs["action"] = _ACTION_ALIASES.get(action.lower(), action.upper())

        diff = kwargs.pop("diff", None)
        if diff is not None:
            kwargs.setdefault("new_value", diff)

        actor = kwargs.get("actor")
        if actor is None:
            kwargs["actor"] = "system"

        super().__init__(**kwargs)

    @property
    def diff(self) -> dict[str, Any] | None:
        return self.new_value


@event.listens_for(AuditLog, "before_update", propagate=True)
def _prevent_audit_log_update(*_: object) -> None:
    msg = "AuditLog is append-only"
    raise ValueError(msg)


@event.listens_for(AuditLog, "before_delete", propagate=True)
def _prevent_audit_log_delete(*_: object) -> None:
    msg = "AuditLog is append-only"
    raise ValueError(msg)
