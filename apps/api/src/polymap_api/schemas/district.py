# ruff: noqa: TC003,E501,F401
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

_LEVEL_ALIASES = {"시도": "metropolitan", "시군구": "basic", "선거구": "constituency"}


class DistrictBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name_ko: str = Field(min_length=1, max_length=200)
    name_en: str | None = Field(default=None, max_length=200)
    level: str = Field(min_length=1, max_length=20)
    parent_id: UUID | None = None
    code: str = Field(min_length=1, max_length=50)
    geometry: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            if "name" in data and "name_ko" not in data:
                data["name_ko"] = data.pop("name")
            if data.get("level") in _LEVEL_ALIASES:
                data["level"] = _LEVEL_ALIASES[data["level"]]
        return data

    @property
    def name(self) -> str:
        return self.name_ko


class DistrictCreate(DistrictBase):
    pass


class DistrictUpdate(DistrictBase):
    name_ko: str | None = Field(default=None, min_length=1, max_length=200)
    level: str | None = Field(default=None, min_length=1, max_length=20)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    geometry: dict[str, Any] | None = None


class DistrictRead(DistrictBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class DistrictSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name_ko: str
    level: str
    code: str
