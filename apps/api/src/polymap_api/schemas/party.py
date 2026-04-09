from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, ConfigDict, Field

DateType = dt.date
DateTimeType = dt.datetime
UUIDType = uuid.UUID


class PartyBase(BaseModel):
    name_ko: str
    name_en: str | None = None
    abbreviation: str | None = None
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    logo_url: str | None = None
    founded_date: DateType | None = None


class PartyCreate(PartyBase):
    pass


class PartyRead(PartyBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
    deleted_at: DateTimeType | None = None
