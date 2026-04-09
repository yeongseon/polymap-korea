from __future__ import annotations

import datetime as dt
import uuid

from polymap_ontology.enums import IssueRelationType
from pydantic import BaseModel, ConfigDict

DateTimeType = dt.datetime
IssueRelationTypeValue = IssueRelationType
UUIDType = uuid.UUID


class IssueBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    parent_id: UUIDType | None = None


class IssueCreate(IssueBase):
    pass


class IssueRead(IssueBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType


class IssueRelationBase(BaseModel):
    source_issue_id: UUIDType
    target_issue_id: UUIDType
    relation_type: IssueRelationTypeValue


class IssueRelationCreate(IssueRelationBase):
    pass


class IssueRelationRead(IssueRelationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
