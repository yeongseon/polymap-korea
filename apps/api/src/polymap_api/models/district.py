from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, TimestampMixin, UUIDPrimaryKeyMixin

UUIDType = uuid.UUID

if TYPE_CHECKING:
    from .race import Race


class District(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "district"

    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    level: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[UUIDType | None] = mapped_column(ForeignKey("district.id"), nullable=True)

    parent: Mapped[District | None] = relationship(
        back_populates="children", remote_side="District.id"
    )
    children: Mapped[list[District]] = relationship(back_populates="parent")
    races: Mapped[list[Race]] = relationship(back_populates="district")
