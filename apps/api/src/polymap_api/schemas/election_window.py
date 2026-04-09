# ruff: noqa: I001,TC002,TC003
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from polymap_ontology.enums import ElectionPhase


class ElectionWindowBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    election_id: UUID
    phase: ElectionPhase
    starts_at: datetime
    ends_at: datetime


class ElectionWindowCreate(ElectionWindowBase):
    pass


class ElectionWindowUpdate(ElectionWindowBase):
    election_id: UUID | None = None
    phase: ElectionPhase | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class ElectionWindowRead(ElectionWindowBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class ElectionWindowSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phase: ElectionPhase
    starts_at: datetime
    ends_at: datetime
