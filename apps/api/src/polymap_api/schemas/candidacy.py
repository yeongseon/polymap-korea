from __future__ import annotations

import datetime as dt
import uuid

from polymap_ontology.enums import CandidacyStatus
from pydantic import BaseModel, ConfigDict

DateType = dt.date
DateTimeType = dt.datetime
UUIDType = uuid.UUID


class CandidacyBase(BaseModel):
    person_id: UUIDType
    race_id: UUIDType
    party_id: UUIDType | None = None
    status: CandidacyStatus = CandidacyStatus.REGISTERED
    candidate_number: int | None = None
    registered_at: DateType | None = None


class CandidacyCreate(CandidacyBase):
    pass


class CandidacyRead(CandidacyBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
