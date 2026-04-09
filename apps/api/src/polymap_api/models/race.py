from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from polymap_ontology.enums import PositionType
from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, TimestampMixin, UUIDPrimaryKeyMixin

UUIDType = uuid.UUID

if TYPE_CHECKING:
    from .candidacy import Candidacy
    from .district import District
    from .election import Election


class Race(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "race"

    election_id: Mapped[UUIDType] = mapped_column(ForeignKey("election.id"), nullable=False)
    district_id: Mapped[UUIDType] = mapped_column(ForeignKey("district.id"), nullable=False)
    position_type: Mapped[PositionType] = mapped_column(
        Enum(PositionType, name="position_type"), nullable=False
    )
    seat_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    election: Mapped[Election] = relationship(back_populates="races")
    district: Mapped[District] = relationship(back_populates="races")
    candidacies: Mapped[list[Candidacy]] = relationship(back_populates="race")
