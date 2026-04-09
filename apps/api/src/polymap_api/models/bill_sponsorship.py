# ruff: noqa: I001,TC003,E501,F401
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from polymap_ontology.enums import BillStatus

if TYPE_CHECKING:
    from .person import Person
    from .source_doc import SourceDoc


class BillSponsorship(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "bill_sponsorship"
    __table_args__ = (
        CheckConstraint("role IN ('lead_sponsor', 'co_sponsor')", name="role"),
    )

    person_id: Mapped[UUID] = mapped_column(
        ForeignKey("person.id", ondelete="CASCADE"),
        nullable=False,
    )
    bill_name: Mapped[str] = mapped_column(String(300), nullable=False)
    bill_id_external: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="lead_sponsor")
    status: Mapped[BillStatus] = mapped_column(Enum(BillStatus, name="bill_status_enum"), nullable=False)
    proposed_date: Mapped[date | None] = mapped_column(nullable=True)
    source_doc_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("source_doc.id", ondelete="SET NULL"),
        nullable=True,
    )

    person: Mapped[Person] = relationship(back_populates="bill_sponsorships")
    source_doc: Mapped[SourceDoc | None] = relationship(back_populates="bill_sponsorships")

    def __init__(self, **kwargs: Any) -> None:
        is_primary_sponsor = kwargs.pop("is_primary_sponsor", None)
        if is_primary_sponsor is not None and "role" not in kwargs:
            kwargs["role"] = "lead_sponsor" if is_primary_sponsor else "co_sponsor"
        kwargs.setdefault("role", "lead_sponsor")
        super().__init__(**kwargs)
