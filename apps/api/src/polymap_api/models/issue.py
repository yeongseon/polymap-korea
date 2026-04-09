# ruff: noqa: I001,TC003,E501,F401
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from polymap_ontology.enums import IssueRelationType

if TYPE_CHECKING:
    from .promise import Promise


class Issue(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "issue"

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("issue.id", ondelete="SET NULL"),
        nullable=True,
    )

    parent: Mapped[Issue | None] = relationship(remote_side="Issue.id", back_populates="children")
    children: Mapped[list[Issue]] = relationship(back_populates="parent", passive_deletes=True)
    promises: Mapped[list[Promise]] = relationship(back_populates="issue", passive_deletes=True)
    outgoing_relations: Mapped[list[IssueRelation]] = relationship(
        foreign_keys="IssueRelation.source_issue_id",
        back_populates="source_issue",
        passive_deletes=True,
    )
    incoming_relations: Mapped[list[IssueRelation]] = relationship(
        foreign_keys="IssueRelation.target_issue_id",
        back_populates="target_issue",
        passive_deletes=True,
    )


class IssueRelation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "issue_relation"
    __table_args__ = (
        UniqueConstraint(
            "source_issue_id",
            "target_issue_id",
            "relation_type",
            name="source_target_relation",
        ),
        CheckConstraint("source_issue_id <> target_issue_id", name="distinct_issue_nodes"),
    )

    source_issue_id: Mapped[UUID] = mapped_column(
        ForeignKey("issue.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_issue_id: Mapped[UUID] = mapped_column(
        ForeignKey("issue.id", ondelete="CASCADE"),
        nullable=False,
    )
    relation_type: Mapped[IssueRelationType] = mapped_column(
        Enum(IssueRelationType, name="issue_relation_type_enum"),
        nullable=False,
    )

    source_issue: Mapped[Issue] = relationship(
        foreign_keys=[source_issue_id],
        back_populates="outgoing_relations",
    )
    target_issue: Mapped[Issue] = relationship(
        foreign_keys=[target_issue_id],
        back_populates="incoming_relations",
    )
