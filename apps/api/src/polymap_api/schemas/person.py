from __future__ import annotations

import datetime as dt
import uuid

from polymap_ontology.enums import Gender
from pydantic import BaseModel, ConfigDict

DateType = dt.date
DateTimeType = dt.datetime
GenderType = Gender
UUIDType = uuid.UUID


class PersonBase(BaseModel):
    name_ko: str
    name_en: str | None = None
    birth_date: DateType | None = None
    gender: GenderType | None = None
    bio: str | None = None
    photo_url: str | None = None


class PersonCreate(PersonBase):
    pass


class PersonRead(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
    deleted_at: DateTimeType | None = None
