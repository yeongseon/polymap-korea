from __future__ import annotations

import datetime as dt
import uuid

from polymap_ontology.enums import SourceDocKind
from pydantic import BaseModel, ConfigDict

DateTimeType = dt.datetime
SourceDocKindValue = SourceDocKind
UUIDType = uuid.UUID


class SourceDocBase(BaseModel):
    kind: SourceDocKindValue
    title: str
    url: str | None = None
    published_at: DateTimeType | None = None
    raw_s3_key: str | None = None
    content_hash: str | None = None


class SourceDocCreate(SourceDocBase):
    pass


class SourceDocRead(SourceDocBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
    deleted_at: DateTimeType | None = None
