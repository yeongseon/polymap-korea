from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, ConfigDict

DateTimeType = dt.datetime
UUIDType = uuid.UUID


class PromiseBase(BaseModel):
    candidacy_id: UUIDType
    title: str
    description: str | None = None
    category: str | None = None
    source_doc_id: UUIDType | None = None


class PromiseCreate(PromiseBase):
    pass


class PromiseRead(PromiseBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
