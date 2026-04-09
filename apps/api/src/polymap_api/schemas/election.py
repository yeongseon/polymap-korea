from __future__ import annotations

import datetime as dt
import uuid

from polymap_ontology.enums import ElectionType
from pydantic import BaseModel, ConfigDict

DateType = dt.date
DateTimeType = dt.datetime
ElectionTypeValue = ElectionType
UUIDType = uuid.UUID


class ElectionBase(BaseModel):
    name: str
    election_type: ElectionTypeValue
    election_date: DateType


class ElectionCreate(ElectionBase):
    pass


class ElectionRead(ElectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
