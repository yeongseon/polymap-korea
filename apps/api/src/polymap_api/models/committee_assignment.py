from __future__ import annotations

import datetime as dt
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, TimestampMixin, UUIDPrimaryKeyMixin

DateType = dt.date
UUIDType = uuid.UUID

if TYPE_CHECKING:
    from .person import Person


class CommitteeAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "committee_assignment"

    person_id: Mapped[UUIDType] = mapped_column(ForeignKey("person.id"), nullable=False)
    committee_name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    start_date: Mapped[DateType | None] = mapped_column(nullable=True)
    end_date: Mapped[DateType | None] = mapped_column(nullable=True)

    person: Mapped[Person] = relationship(back_populates="committee_assignments")
