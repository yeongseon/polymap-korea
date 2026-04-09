from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, TimestampMixin, UUIDPrimaryKeyMixin

UUIDType = uuid.UUID

if TYPE_CHECKING:
    from .candidacy import Candidacy
    from .source_doc import SourceDoc


class Promise(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "promise"

    candidacy_id: Mapped[UUIDType] = mapped_column(ForeignKey("candidacy.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    source_doc_id: Mapped[UUIDType | None] = mapped_column(
        ForeignKey("source_doc.id"), nullable=True
    )

    candidacy: Mapped[Candidacy] = relationship(back_populates="promises")
    source_doc: Mapped[SourceDoc | None] = relationship(back_populates="promises")
