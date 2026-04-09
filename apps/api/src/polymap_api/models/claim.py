# ruff: noqa: I001,TC003,E501,F401
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Index, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from polymap_ontology.enums import ClaimType

if TYPE_CHECKING:
    from .candidacy import Candidacy
    from .source_doc import SourceDoc


class Claim(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "claim"
    __table_args__ = (
        Index(
            "ix_claim_content_tsv",
            text("to_tsvector('simple', content)"),
            postgresql_using="gin",
        ),
    )

    source_doc_id: Mapped[UUID] = mapped_column(
        ForeignKey("source_doc.id", ondelete="CASCADE"),
        nullable=False,
    )
    candidacy_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidacy.id", ondelete="CASCADE"),
        nullable=False,
    )
    claim_type: Mapped[ClaimType] = mapped_column(Enum(ClaimType, name="claim_type_enum"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    source_doc: Mapped[SourceDoc] = relationship(back_populates="claims")
    candidacy: Mapped[Candidacy] = relationship(back_populates="claims")
