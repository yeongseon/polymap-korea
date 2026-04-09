from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from polymap_ontology.enums import SourceDocKind
from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

DateTimeType = dt.datetime

if TYPE_CHECKING:
    from .claim import Claim
    from .promise import Promise


class SourceDoc(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "source_doc"

    kind: Mapped[SourceDocKind] = mapped_column(
        Enum(SourceDocKind, name="source_doc_kind"), nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    published_at: Mapped[DateTimeType | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    raw_s3_key: Mapped[str | None] = mapped_column(String, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    claims: Mapped[list[Claim]] = relationship(back_populates="source_doc")
    promises: Mapped[list[Promise]] = relationship(back_populates="source_doc")
