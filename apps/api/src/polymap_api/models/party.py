# ruff: noqa: TC003,E501,F401
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, CheckConstraint, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from .candidacy import Candidacy


class Party(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "party"
    __table_args__ = (
        CheckConstraint(
            "color_hex IS NULL OR (length(color_hex) = 7 AND substr(color_hex, 1, 1) = '#')",
            name="color_hex_format",
        ),
    )

    name_ko: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    name_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    abbreviation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color_hex: Mapped[str | None] = mapped_column(String(7), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    founded_date: Mapped[date | None] = mapped_column(nullable=True)
    dissolved_date: Mapped[date | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    candidacies: Mapped[list[Candidacy]] = relationship(back_populates="party", passive_deletes=True)

    def __init__(self, **kwargs: Any) -> None:
        if "color" in kwargs and "color_hex" not in kwargs:
            kwargs["color_hex"] = kwargs.pop("color")
        super().__init__(**kwargs)

    @property
    def color(self) -> str | None:
        return self.color_hex
