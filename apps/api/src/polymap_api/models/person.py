# ruff: noqa: I001,TC003,E501,F401
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from polymap_ontology.enums import Gender

if TYPE_CHECKING:
    from .bill_sponsorship import BillSponsorship
    from .candidacy import Candidacy
    from .committee_assignment import CommitteeAssignment


class Person(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "person"
    __table_args__ = (Index("ix_person_name_ko", "name_ko"),)

    name_ko: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(nullable=True)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender_enum"), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_ids: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    candidacies: Mapped[list[Candidacy]] = relationship(back_populates="person")
    committee_assignments: Mapped[list[CommitteeAssignment]] = relationship(back_populates="person", passive_deletes=True)
    bill_sponsorships: Mapped[list[BillSponsorship]] = relationship(back_populates="person", passive_deletes=True)
