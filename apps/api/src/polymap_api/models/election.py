# ruff: noqa: I001,TC003,E501,F401
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from polymap_ontology.enums import ElectionType

if TYPE_CHECKING:
    from .election_window import ElectionWindow
    from .race import Race


class Election(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "election"
    __table_args__ = (Index("ix_election_election_date", "election_date"),)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    election_type: Mapped[ElectionType] = mapped_column(Enum(ElectionType, name="election_type_enum"), nullable=False)
    election_date: Mapped[date] = mapped_column(nullable=False)

    races: Mapped[list[Race]] = relationship(back_populates="election", passive_deletes=True)
    windows: Mapped[list[ElectionWindow]] = relationship(back_populates="election", passive_deletes=True)
