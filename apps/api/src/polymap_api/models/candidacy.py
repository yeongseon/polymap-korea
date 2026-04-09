# ruff: noqa: I001,TC003,E501,F401
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymap_api.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from polymap_ontology.enums import CandidacyStatus

if TYPE_CHECKING:
    from .claim import Claim
    from .party import Party
    from .person import Person
    from .promise import Promise
    from .race import Race


class Candidacy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "candidacy"
    __table_args__ = (
        CheckConstraint("candidate_number IS NULL OR candidate_number >= 1", name="candidate_number_positive"),
        UniqueConstraint("person_id", "race_id", name="person_race"),
    )

    person_id: Mapped[UUID] = mapped_column(
        ForeignKey("person.id", ondelete="RESTRICT"),
        nullable=False,
    )
    race_id: Mapped[UUID] = mapped_column(
        ForeignKey("race.id", ondelete="CASCADE"),
        nullable=False,
    )
    party_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("party.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[CandidacyStatus] = mapped_column(
        Enum(CandidacyStatus, name="candidacy_status_enum"),
        nullable=False,
        server_default=CandidacyStatus.REGISTERED.value,
    )
    registered_at: Mapped[date | None] = mapped_column(nullable=True)
    candidate_number: Mapped[int | None] = mapped_column(nullable=True)

    person: Mapped[Person] = relationship(back_populates="candidacies")
    race: Mapped[Race] = relationship(back_populates="candidacies")
    party: Mapped[Party | None] = relationship(back_populates="candidacies")
    promises: Mapped[list[Promise]] = relationship(back_populates="candidacy", passive_deletes=True)
    claims: Mapped[list[Claim]] = relationship(back_populates="candidacy", passive_deletes=True)
