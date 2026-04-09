from __future__ import annotations

import datetime as dt
import uuid

from polymap_ontology.enums import BillStatus
from pydantic import BaseModel, ConfigDict

BillStatusType = BillStatus
DateType = dt.date
DateTimeType = dt.datetime
UUIDType = uuid.UUID


class BillSponsorshipBase(BaseModel):
    person_id: UUIDType
    bill_name: str
    bill_id_external: str | None = None
    status: BillStatusType | None = None
    proposed_date: DateType | None = None
    is_primary_sponsor: bool = False


class BillSponsorshipCreate(BillSponsorshipBase):
    pass


class BillSponsorshipRead(BillSponsorshipBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUIDType
    created_at: DateTimeType
    updated_at: DateTimeType
