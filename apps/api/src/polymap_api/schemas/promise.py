# ruff: noqa: TC003,E501,F401
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PromiseBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    candidacy_id: UUID
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(default="", min_length=0)
    category: str | None = Field(default=None, max_length=100)
    issue_id: UUID | None = None
    source_doc_id: UUID | None = None
    sort_order: int = 0

    @model_validator(mode="before")
    @classmethod
    def normalize_body(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            if "description" in data and "body" not in data:
                data["body"] = data.pop("description")
            if not data.get("body") and data.get("title"):
                data["body"] = data["title"]
        return data


class PromiseCreate(PromiseBase):
    pass


class PromiseUpdate(PromiseBase):
    candidacy_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=300)
    body: str | None = None
    sort_order: int | None = None


class PromiseRead(PromiseBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class PromiseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidacy_id: UUID
    title: str
    sort_order: int
