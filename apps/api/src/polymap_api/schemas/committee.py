from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, ConfigDict

DateType = dt.date
DateTimeType = dt.datetime
UUIDType = uuid.UUID


class CommitteeAssignmentBase(BaseModel):
    person_id: UUIDType
    committee_name: str
    role: str | None = None
    start_date: DateType | None = None
    end_date: DateType | None = None


class CommitteeAssignmentCreate(CommitteeAssignmentBase):
    pass


class CommitteeAssignmentRead(CommitteeAssignmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
