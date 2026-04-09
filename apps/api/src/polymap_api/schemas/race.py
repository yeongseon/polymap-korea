from __future__ import annotations

import datetime as dt
import uuid

from polymap_ontology.enums import PositionType
from pydantic import BaseModel, ConfigDict, Field

DateTimeType = dt.datetime
PositionTypeValue = PositionType
UUIDType = uuid.UUID


class RaceBase(BaseModel):
    election_id: UUIDType
    district_id: UUIDType
    position_type: PositionTypeValue
    seat_count: int = Field(default=1, ge=1)


class RaceCreate(RaceBase):
    pass


class RaceRead(RaceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
