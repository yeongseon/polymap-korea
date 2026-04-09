# ruff: noqa: I001,TC002,TC003,E501,F401
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from polymap_ontology.enums import SourceDocKind


class SourceDocBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    kind: SourceDocKind
    title: str = Field(min_length=1, max_length=300)
    url: str | None = Field(default=None, max_length=1000)
    published_at: datetime | None = None
    content_hash: str | None = Field(default=None, max_length=128)
    raw_s3_key: str | None = Field(default=None, max_length=500)


class SourceDocCreate(SourceDocBase):
    pass


class SourceDocUpdate(SourceDocBase):
    kind: SourceDocKind | None = None
    title: str | None = Field(default=None, min_length=1, max_length=300)
    deleted_at: datetime | None = None


class SourceDocRead(SourceDocBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class SourceDocSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: SourceDocKind
    title: str
    published_at: datetime | None
