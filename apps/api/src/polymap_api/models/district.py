# ruff: noqa: TC003,E501,F401
from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import JSON, CheckConstraint, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from .race import Race

_LEVEL_ALIASES = {
    "시도": "metropolitan",
    "시군구": "basic",
    "선거구": "constituency",
}


class District(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "district"
    __table_args__ = (
        CheckConstraint(
            "level IN ('metropolitan', 'basic', 'constituency')",
            name="level",
        ),
    )

    name_ko: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("district.id", ondelete="SET NULL"),
        nullable=True,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    geometry: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        server_default=text("'{}'"),
    )

    parent: Mapped[District | None] = relationship(remote_side="District.id", back_populates="children")
    children: Mapped[list[District]] = relationship(back_populates="parent", passive_deletes=True)
    races: Mapped[list[Race]] = relationship(back_populates="district")

    def __init__(self, **kwargs: Any) -> None:
        if "name" in kwargs and "name_ko" not in kwargs:
            kwargs["name_ko"] = kwargs.pop("name")
        if kwargs.get("level") in _LEVEL_ALIASES:
            kwargs["level"] = _LEVEL_ALIASES[kwargs["level"]]
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return self.name_ko
