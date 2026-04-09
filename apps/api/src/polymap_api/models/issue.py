from __future__ import annotations

import uuid

from polymap_ontology.enums import IssueRelationType
from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, TimestampMixin, UUIDPrimaryKeyMixin

UUIDType = uuid.UUID


class Issue(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "issue"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[UUIDType | None] = mapped_column(ForeignKey("issue.id"), nullable=True)

    parent: Mapped[Issue | None] = relationship(back_populates="children", remote_side="Issue.id")
    children: Mapped[list[Issue]] = relationship(back_populates="parent")
    outgoing_relations: Mapped[list[IssueRelation]] = relationship(
        back_populates="source_issue", foreign_keys="IssueRelation.source_issue_id"
    )
    incoming_relations: Mapped[list[IssueRelation]] = relationship(
        back_populates="target_issue", foreign_keys="IssueRelation.target_issue_id"
    )


class IssueRelation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "issue_relation"
    __table_args__ = (
        UniqueConstraint("source_issue_id", "target_issue_id", "relation_type"),
    )

    source_issue_id: Mapped[UUIDType] = mapped_column(ForeignKey("issue.id"), nullable=False)
    target_issue_id: Mapped[UUIDType] = mapped_column(ForeignKey("issue.id"), nullable=False)
    relation_type: Mapped[IssueRelationType] = mapped_column(
        Enum(IssueRelationType, name="issue_relation_type"), nullable=False
    )

    source_issue: Mapped[Issue] = relationship(
        back_populates="outgoing_relations", foreign_keys=[source_issue_id]
    )
    target_issue: Mapped[Issue] = relationship(
        back_populates="incoming_relations", foreign_keys=[target_issue_id]
    )
