# ruff: noqa: TC003,E501,F401
from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, JSON, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from .candidacy import Candidacy
    from .issue import Issue
    from .source_doc import SourceDoc


_PROMISE_BODY_SEARCH_INDEX = Index(
    "ix_promise_body_tsv",
    text("to_tsvector('simple', body)"),
    postgresql_using="gin",
).ddl_if(dialect="postgresql")


class Promise(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "promise"
    __table_args__ = (_PROMISE_BODY_SEARCH_INDEX,)

    candidacy_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidacy.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    issue_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("issue.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_doc_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("source_doc.id", ondelete="SET NULL"),
        nullable=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata", JSON().with_variant(JSONB(astext_type=Text()), "postgresql"), nullable=True,
    )

    candidacy: Mapped[Candidacy] = relationship(back_populates="promises")
    issue: Mapped[Issue | None] = relationship(back_populates="promises")
    source_doc: Mapped[SourceDoc | None] = relationship(back_populates="promises")

    def __init__(self, **kwargs: Any) -> None:
        if "description" in kwargs and "body" not in kwargs:
            kwargs["body"] = kwargs.pop("description")
        if "body" not in kwargs and "title" in kwargs:
            kwargs["body"] = kwargs["title"]
        if "metadata" in kwargs and "metadata_" not in kwargs:
            kwargs["metadata_"] = kwargs.pop("metadata")
        super().__init__(**kwargs)
