# ruff: noqa: TC003,E501,F401
from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PartyBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name_ko: str = Field(min_length=1, max_length=200)
    name_en: str | None = Field(default=None, max_length=200)
    abbreviation: str | None = Field(default=None, max_length=50)
    color_hex: str | None = Field(default=None, max_length=7)
    logo_url: str | None = Field(default=None, max_length=500)
    founded_date: date | None = None
    dissolved_date: date | None = None
    is_active: bool = True

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict) and "color" in data and "color_hex" not in data:
            data = dict(data)
            data["color_hex"] = data.pop("color")
        return data

    @field_validator("color_hex")
    @classmethod
    def validate_color_hex(cls, value: str | None) -> str | None:
        if value is not None and (len(value) != 7 or not value.startswith("#")):
            raise ValueError("invalid color hex")
        if value is not None and any(ch not in "0123456789abcdefABCDEF" for ch in value[1:]):
            raise ValueError("invalid color hex")
        return value

    @property
    def color(self) -> str | None:
        return self.color_hex


class PartyCreate(PartyBase):
    pass


class PartyUpdate(PartyBase):
    name_ko: str | None = Field(default=None, min_length=1, max_length=200)
    is_active: bool | None = None
    deleted_at: datetime | None = None


class PartyRead(PartyBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class PartySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name_ko: str
    abbreviation: str | None
    color_hex: str | None
