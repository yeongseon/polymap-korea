# ruff: noqa: I001,TC003,E501,F401
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from polymap_ontology.enums import SourceDocKind

if TYPE_CHECKING:
    from .bill_sponsorship import BillSponsorship
    from .claim import Claim
    from .committee_assignment import CommitteeAssignment
    from .promise import Promise


class SourceDoc(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "source_doc"

    kind: Mapped[SourceDocKind] = mapped_column(Enum(SourceDocKind, name="source_doc_kind_enum"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'VISIBLE'"))
    is_poll_result: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    public_expiry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    raw_s3_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    promises: Mapped[list[Promise]] = relationship(back_populates="source_doc", passive_deletes=True)
    claims: Mapped[list[Claim]] = relationship(back_populates="source_doc", passive_deletes=True)
    committee_assignments: Mapped[list[CommitteeAssignment]] = relationship(back_populates="source_doc", passive_deletes=True)
    bill_sponsorships: Mapped[list[BillSponsorship]] = relationship(back_populates="source_doc", passive_deletes=True)
