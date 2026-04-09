from __future__ import annotations

import datetime as dt
import uuid
from typing import TYPE_CHECKING

from polymap_ontology.enums import ElectionPhase
from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, TimestampMixin, UUIDPrimaryKeyMixin

DateTimeType = dt.datetime
UUIDType = uuid.UUID

if TYPE_CHECKING:
    from .election import Election


class ElectionWindow(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "election_window"
    __table_args__ = (CheckConstraint("starts_at < ends_at", name="starts_before_ends"),)

    election_id: Mapped[UUIDType] = mapped_column(ForeignKey("election.id"), nullable=False)
    phase: Mapped[ElectionPhase] = mapped_column(
        Enum(ElectionPhase, name="election_phase"), nullable=False
    )
    starts_at: Mapped[DateTimeType] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[DateTimeType] = mapped_column(DateTime(timezone=True), nullable=False)

    election: Mapped[Election] = relationship(back_populates="election_windows")
