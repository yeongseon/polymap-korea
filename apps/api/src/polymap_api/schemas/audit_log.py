# ruff: noqa: I001,TC002,TC003
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    actor: str | None
    diff: dict[str, Any] | None
    created_at: datetime
