# ruff: noqa: I001,TC002,TC003,E501,F401
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from polymap_ontology.enums import ClaimType


class ClaimBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    candidacy_id: UUID
    source_doc_id: UUID
    claim_type: ClaimType
    is_legally_restricted: bool = False
    content: str = Field(min_length=1)
    excerpt: str | None = None


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdate(ClaimBase):
    candidacy_id: UUID | None = None
    source_doc_id: UUID | None = None
    claim_type: ClaimType | None = None
    is_legally_restricted: bool | None = None
    content: str | None = None
    excerpt: str | None = None


class ClaimRead(ClaimBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class ClaimSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidacy_id: UUID
    claim_type: ClaimType
    excerpt: str | None
