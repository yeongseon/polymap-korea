# ruff: noqa: TC003,E501,F401
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from .person import Person
    from .source_doc import SourceDoc


class CommitteeAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "committee_assignment"

    person_id: Mapped[UUID] = mapped_column(
        ForeignKey("person.id", ondelete="CASCADE"),
        nullable=False,
    )
    committee_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_date: Mapped[date | None] = mapped_column(nullable=True)
    end_date: Mapped[date | None] = mapped_column(nullable=True)
    source_doc_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("source_doc.id", ondelete="SET NULL"),
        nullable=True,
    )

    person: Mapped[Person] = relationship(back_populates="committee_assignments")
    source_doc: Mapped[SourceDoc | None] = relationship(back_populates="committee_assignments")
