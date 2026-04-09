# ruff: noqa: I001,TC003,E501,F401
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from polymap_ontology.enums import PositionType

if TYPE_CHECKING:
    from .candidacy import Candidacy
    from .district import District
    from .election import Election


class Race(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "race"
    __table_args__ = (
        CheckConstraint("seat_count >= 1", name="seat_count_positive"),
        UniqueConstraint("election_id", "district_id", "position_type", name="race_scope"),
    )

    election_id: Mapped[UUID] = mapped_column(
        ForeignKey("election.id", ondelete="CASCADE"),
        nullable=False,
    )
    district_id: Mapped[UUID] = mapped_column(
        ForeignKey("district.id", ondelete="RESTRICT"),
        nullable=False,
    )
    position_type: Mapped[PositionType] = mapped_column(Enum(PositionType, name="position_type_enum"), nullable=False)
    seat_count: Mapped[int] = mapped_column(nullable=False, server_default="1")

    election: Mapped[Election] = relationship(back_populates="races")
    district: Mapped[District] = relationship(back_populates="races")
    candidacies: Mapped[list[Candidacy]] = relationship(back_populates="race", passive_deletes=True)
