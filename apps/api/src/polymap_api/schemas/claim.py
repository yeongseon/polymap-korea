from __future__ import annotations

import datetime as dt
import uuid

from polymap_ontology.enums import ClaimType
from pydantic import BaseModel, ConfigDict

ClaimTypeValue = ClaimType
DateTimeType = dt.datetime
UUIDType = uuid.UUID


class ClaimBase(BaseModel):
    candidacy_id: UUIDType
    source_doc_id: UUIDType
    claim_type: ClaimTypeValue
    content: str
    excerpt: str | None = None


class ClaimCreate(ClaimBase):
    pass


class ClaimRead(ClaimBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
