# ruff: noqa: TC003,E501,F401
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CommitteeAssignmentBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    person_id: UUID
    committee_name: str = Field(min_length=1, max_length=200)
    role: str | None = Field(default=None, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    source_doc_id: UUID | None = None


class CommitteeAssignmentCreate(CommitteeAssignmentBase):
    pass


class CommitteeAssignmentUpdate(CommitteeAssignmentBase):
    person_id: UUID | None = None
    committee_name: str | None = Field(default=None, min_length=1, max_length=200)


class CommitteeAssignmentRead(CommitteeAssignmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class CommitteeAssignmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    committee_name: str
    role: str | None
    start_date: date | None
