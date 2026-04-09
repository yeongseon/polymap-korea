from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, ConfigDict

DateTimeType = dt.datetime
UUIDType = uuid.UUID


class DistrictBase(BaseModel):
    name: str
    code: str
    level: str
    parent_id: UUIDType | None = None


class DistrictCreate(DistrictBase):
    pass


class DistrictRead(DistrictBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
