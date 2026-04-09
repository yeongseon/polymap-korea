# ruff: noqa: I001,TC002,TC003,E501,F401
from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from polymap_ontology.enums import BillStatus

_ALLOWED_ROLE = {"lead_sponsor", "co_sponsor"}


class BillSponsorshipBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    person_id: UUID
    bill_name: str = Field(min_length=1, max_length=300)
    bill_id_external: str | None = Field(default=None, max_length=100)
    role: str = Field(default="lead_sponsor", min_length=1, max_length=20)
    status: BillStatus
    proposed_date: date | None = None
    source_doc_id: UUID | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            is_primary = data.pop("is_primary_sponsor", None)
            if is_primary is not None and "role" not in data:
                data["role"] = "lead_sponsor" if is_primary else "co_sponsor"
            data.setdefault("role", "lead_sponsor")
        return data

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in _ALLOWED_ROLE:
            raise ValueError("invalid bill role")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: BillStatus) -> BillStatus:
        return value


class BillSponsorshipCreate(BillSponsorshipBase):
    pass


class BillSponsorshipUpdate(BillSponsorshipBase):
    person_id: UUID | None = None
    bill_name: str | None = Field(default=None, min_length=1, max_length=300)
    role: str | None = Field(default=None, min_length=1, max_length=20)
    status: BillStatus | None = None

    @field_validator("role")
    @classmethod
    def validate_optional_role(cls, value: str | None) -> str | None:
        if value is not None and value not in _ALLOWED_ROLE:
            raise ValueError("invalid bill role")
        return value

    @field_validator("status")
    @classmethod
    def validate_optional_status(cls, value: BillStatus | None) -> BillStatus | None:
        return value


class BillSponsorshipRead(BillSponsorshipBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class BillSponsorshipSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bill_name: str
    role: str
    status: BillStatus
