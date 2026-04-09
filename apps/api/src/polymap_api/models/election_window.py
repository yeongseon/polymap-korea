# ruff: noqa: I001,TC003,E501,F401
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from .election import Election


class ElectionWindow(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "election_window"
    __table_args__ = (
        CheckConstraint("blackout_start < blackout_end", name="window_bounds"),
    )

    election_id: Mapped[UUID] = mapped_column(
        ForeignKey("election.id", ondelete="CASCADE"),
        nullable=False,
    )
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    blackout_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    blackout_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    election: Mapped[Election] = relationship(back_populates="windows")

    def __init__(self, **kwargs: Any) -> None:
        phase = kwargs.pop("phase", None)
        starts_at = kwargs.pop("starts_at", None)
        ends_at = kwargs.pop("ends_at", None)

        if "content_type" not in kwargs and phase is not None:
            kwargs["content_type"] = str(phase)
        if "blackout_start" not in kwargs and starts_at is not None:
            kwargs["blackout_start"] = starts_at
        if "blackout_end" not in kwargs and ends_at is not None:
            kwargs["blackout_end"] = ends_at

        super().__init__(**kwargs)
