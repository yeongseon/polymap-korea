from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from polymap_ontology.enums import ClaimType
from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, TimestampMixin, UUIDPrimaryKeyMixin

UUIDType = uuid.UUID

if TYPE_CHECKING:
    from .candidacy import Candidacy
    from .source_doc import SourceDoc


class Claim(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "claim"

    candidacy_id: Mapped[UUIDType] = mapped_column(ForeignKey("candidacy.id"), nullable=False)
    source_doc_id: Mapped[UUIDType] = mapped_column(ForeignKey("source_doc.id"), nullable=False)
    claim_type: Mapped[ClaimType] = mapped_column(
        Enum(ClaimType, name="claim_type"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)

    candidacy: Mapped[Candidacy] = relationship(back_populates="claims")
    source_doc: Mapped[SourceDoc] = relationship(back_populates="claims")
