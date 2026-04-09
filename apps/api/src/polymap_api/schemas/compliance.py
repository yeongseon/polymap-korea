# ruff: noqa: I001,TC002,TC003
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ComplianceElectionWindowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    election_id: UUID
    content_type: str
    blackout_start: datetime
    blackout_end: datetime
    created_at: datetime
    updated_at: datetime


class ElectionWindowStatusRead(BaseModel):
    election_id: UUID
    content_type: str
    blocked: bool
    checked_at: datetime
    active_window: ComplianceElectionWindowRead | None = None


class AuditLogCreate(BaseModel):
    actor: str = Field(min_length=1, max_length=255)
    action: str = Field(min_length=1, max_length=100)
    entity_type: str = Field(min_length=1, max_length=100)
    entity_id: UUID
    reason_code: str | None = Field(default=None, max_length=100)
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    legal_basis: str | None = Field(default=None, max_length=255)


class ComplianceAuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor: str
    action: str
    entity_type: str
    entity_id: UUID
    reason_code: str | None
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    legal_basis: str | None
    created_at: datetime
