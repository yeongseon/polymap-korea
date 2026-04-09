# ruff: noqa: I001,TC002,TC003,E501,F401
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from polymap_ontology.enums import PositionType


class RaceBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    election_id: UUID
    district_id: UUID
    position_type: PositionType
    seat_count: int = Field(ge=1, default=1)


class RaceCreate(RaceBase):
    pass


class RaceUpdate(RaceBase):
    election_id: UUID | None = None
    district_id: UUID | None = None
    position_type: PositionType | None = None
    seat_count: int | None = Field(default=None, ge=1)


class RaceRead(RaceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class RaceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    district_id: UUID
    position_type: PositionType
    seat_count: int
