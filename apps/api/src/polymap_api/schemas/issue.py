# ruff: noqa: I001,TC002,TC003,E501,F401
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from polymap_ontology.enums import IssueRelationType


class IssueBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200)
    description: str | None = None
    parent_id: UUID | None = None


class IssueCreate(IssueBase):
    pass


class IssueUpdate(IssueBase):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, min_length=1, max_length=200)


class IssueRead(IssueBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class IssueSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    parent_id: UUID | None


class IssueRelationBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source_issue_id: UUID
    target_issue_id: UUID
    relation_type: IssueRelationType


class IssueRelationCreate(IssueRelationBase):
    pass


class IssueRelationUpdate(IssueRelationBase):
    source_issue_id: UUID | None = None
    target_issue_id: UUID | None = None
    relation_type: IssueRelationType | None = None


class IssueRelationRead(IssueRelationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class IssueRelationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    relation_type: IssueRelationType
    target_issue_id: UUID
