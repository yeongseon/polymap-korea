from __future__ import annotations

import datetime as dt
import uuid
from typing import TYPE_CHECKING

from polymap_ontology.enums import CandidacyStatus
from sqlalchemy import Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, TimestampMixin, UUIDPrimaryKeyMixin

DateType = dt.date
UUIDType = uuid.UUID

if TYPE_CHECKING:
    from .claim import Claim
    from .party import Party
    from .person import Person
    from .promise import Promise
    from .race import Race


class Candidacy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "candidacy"
    __table_args__ = (UniqueConstraint("person_id", "race_id"),)

    person_id: Mapped[UUIDType] = mapped_column(ForeignKey("person.id"), nullable=False)
    race_id: Mapped[UUIDType] = mapped_column(ForeignKey("race.id"), nullable=False)
    party_id: Mapped[UUIDType | None] = mapped_column(ForeignKey("party.id"), nullable=True)
    status: Mapped[CandidacyStatus] = mapped_column(
        Enum(CandidacyStatus, name="candidacy_status"),
        nullable=False,
        default=CandidacyStatus.REGISTERED,
    )
    candidate_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registered_at: Mapped[DateType | None] = mapped_column(nullable=True)

    person: Mapped[Person] = relationship(back_populates="candidacies")
    race: Mapped[Race] = relationship(back_populates="candidacies")
    party: Mapped[Party | None] = relationship(back_populates="candidacies")
    promises: Mapped[list[Promise]] = relationship(back_populates="candidacy")
    claims: Mapped[list[Claim]] = relationship(back_populates="candidacy")
