from __future__ import annotations

import datetime as dt
import uuid
from typing import TYPE_CHECKING

from polymap_ontology.enums import BillStatus
from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, TimestampMixin, UUIDPrimaryKeyMixin

DateType = dt.date
UUIDType = uuid.UUID

if TYPE_CHECKING:
    from .person import Person


class BillSponsorship(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "bill_sponsorship"

    person_id: Mapped[UUIDType] = mapped_column(ForeignKey("person.id"), nullable=False)
    bill_name: Mapped[str] = mapped_column(String, nullable=False)
    bill_id_external: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[BillStatus | None] = mapped_column(
        Enum(BillStatus, name="bill_status"), nullable=True
    )
    proposed_date: Mapped[DateType | None] = mapped_column(nullable=True)
    is_primary_sponsor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    person: Mapped[Person] = relationship(back_populates="bill_sponsorships")
