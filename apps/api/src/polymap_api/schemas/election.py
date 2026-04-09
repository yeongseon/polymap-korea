# ruff: noqa: I001,TC001,TC002,TC003,E501,F401
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from polymap_ontology.enums import ElectionType

from .race import RaceRead


class ElectionBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1, max_length=200)
    election_type: ElectionType
    election_date: date


class ElectionCreate(ElectionBase):
    pass


class ElectionUpdate(ElectionBase):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    election_type: ElectionType | None = None
    election_date: date | None = None


class ElectionRead(ElectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class ElectionDetail(ElectionRead):
    races: list[RaceRead]


class ElectionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    election_date: date
