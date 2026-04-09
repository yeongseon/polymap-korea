# ruff: noqa: I001,TC002,TC003,E501,F401
from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from polymap_ontology.enums import Gender


class PersonBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name_ko: str = Field(min_length=1, max_length=200)
    name_en: str | None = Field(default=None, max_length=200)
    birth_date: date | None = None
    gender: Gender | None = None
    photo_url: str | None = Field(default=None, max_length=500)
    bio: str | None = None
    external_ids: dict[str, Any] = Field(default_factory=dict)


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name_ko: str | None = Field(default=None, min_length=1, max_length=200)
    name_en: str | None = Field(default=None, max_length=200)
    birth_date: date | None = None
    gender: Gender | None = None
    photo_url: str | None = Field(default=None, max_length=500)
    bio: str | None = None
    external_ids: dict[str, Any] | None = None
    deleted_at: datetime | None = None


class PersonRead(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class PersonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name_ko: str
    name_en: str | None
    photo_url: str | None
