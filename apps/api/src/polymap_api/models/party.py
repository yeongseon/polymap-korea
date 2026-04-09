from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

DateType = dt.date

if TYPE_CHECKING:
    from .candidacy import Candidacy


class Party(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "party"

    name_ko: Mapped[str] = mapped_column(String, nullable=False)
    name_en: Mapped[str | None] = mapped_column(String, nullable=True)
    abbreviation: Mapped[str | None] = mapped_column(String, nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    founded_date: Mapped[DateType | None] = mapped_column(nullable=True)

    candidacies: Mapped[list[Candidacy]] = relationship(back_populates="party")
