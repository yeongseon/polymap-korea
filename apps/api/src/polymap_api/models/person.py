from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from polymap_ontology.enums import Gender
from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

DateType = dt.date

if TYPE_CHECKING:
    from .bill_sponsorship import BillSponsorship
    from .candidacy import Candidacy
    from .committee_assignment import CommitteeAssignment


class Person(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "person"

    name_ko: Mapped[str] = mapped_column(String, nullable=False)
    name_en: Mapped[str | None] = mapped_column(String, nullable=True)
    birth_date: Mapped[DateType | None] = mapped_column(nullable=True)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender"), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String, nullable=True)

    candidacies: Mapped[list[Candidacy]] = relationship(back_populates="person")
    committee_assignments: Mapped[list[CommitteeAssignment]] = relationship(back_populates="person")
    bill_sponsorships: Mapped[list[BillSponsorship]] = relationship(back_populates="person")
