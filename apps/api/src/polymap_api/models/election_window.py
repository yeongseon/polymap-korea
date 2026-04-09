# ruff: noqa: I001,TC003,E501,F401
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from polymap_ontology.enums import ElectionPhase

if TYPE_CHECKING:
    from .election import Election


class ElectionWindow(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "election_window"
    __table_args__ = (
        CheckConstraint("starts_at < ends_at", name="window_bounds"),
        UniqueConstraint("election_id", "phase", name="election_phase"),
    )

    election_id: Mapped[UUID] = mapped_column(
        ForeignKey("election.id", ondelete="CASCADE"),
        nullable=False,
    )
    phase: Mapped[ElectionPhase] = mapped_column(Enum(ElectionPhase, name="election_phase_enum"), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    election: Mapped[Election] = relationship(back_populates="windows")
