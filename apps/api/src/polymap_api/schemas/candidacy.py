# ruff: noqa: I001,TC002,TC003,E501,F401
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from polymap_ontology.enums import CandidacyStatus


class CandidacyBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    person_id: UUID
    race_id: UUID
    party_id: UUID | None = None
    status: CandidacyStatus = CandidacyStatus.REGISTERED
    registered_at: date | None = None
    candidate_number: int | None = Field(default=None, ge=1)


class CandidacyCreate(CandidacyBase):
    pass


class CandidacyUpdate(CandidacyBase):
    person_id: UUID | None = None
    race_id: UUID | None = None
    status: CandidacyStatus | None = None
    candidate_number: int | None = Field(default=None, ge=1)


class CandidacyRead(CandidacyBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class CandidacySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    person_id: UUID
    race_id: UUID
    status: CandidacyStatus
    candidate_number: int | None
