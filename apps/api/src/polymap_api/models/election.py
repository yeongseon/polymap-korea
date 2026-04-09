from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from polymap_ontology.enums import ElectionType
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, TimestampMixin, UUIDPrimaryKeyMixin

DateType = dt.date

if TYPE_CHECKING:
    from .election_window import ElectionWindow
    from .race import Race


class Election(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "election"

    name: Mapped[str] = mapped_column(String, nullable=False)
    election_type: Mapped[ElectionType] = mapped_column(
        Enum(ElectionType, name="election_type"), nullable=False
    )
    election_date: Mapped[DateType] = mapped_column(nullable=False)

    races: Mapped[list[Race]] = relationship(back_populates="election")
    election_windows: Mapped[list[ElectionWindow]] = relationship(back_populates="election")
