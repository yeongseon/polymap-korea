# ruff: noqa: B008,TC002,TC003,E501,I001
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from polymap_api.deps import Pagination, get_db, get_pagination
from polymap_api.models import Person
from polymap_api.schemas import BillSponsorshipSummary, CommitteeAssignmentSummary, PersonRead, PersonSummary
from polymap_ontology.enums import CandidacyStatus

router = APIRouter(prefix="/persons", tags=["persons"])


class PersonCandidacySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    person_id: UUID
    race_id: UUID
    status: CandidacyStatus
    candidate_number: int | None


class PersonDetail(PersonRead):
    candidacies: list[PersonCandidacySummary]
    committee_assignments: list[CommitteeAssignmentSummary]
    bill_sponsorships: list[BillSponsorshipSummary]


@router.get("", response_model=list[PersonSummary])
async def list_persons(
    name: str | None = Query(default=None, min_length=1),
    pagination: Pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
) -> list[Person]:
    statement = select(Person).where(Person.deleted_at.is_(None))
    if name:
        like_term = f"%{name}%"
        statement = statement.where(
            or_(Person.name_ko.ilike(like_term), Person.name_en.ilike(like_term))
        )
    statement = statement.order_by(Person.name_ko.asc()).offset(pagination.offset).limit(pagination.per_page)
    result = await db.scalars(statement)
    return list(result)


@router.get("/{person_id}", response_model=PersonDetail)
async def get_person(person_id: UUID, db: AsyncSession = Depends(get_db)) -> Person:
    statement = (
        select(Person)
        .options(
            selectinload(Person.candidacies),
            selectinload(Person.committee_assignments),
            selectinload(Person.bill_sponsorships),
        )
        .where(Person.id == person_id, Person.deleted_at.is_(None))
    )
    person = await db.scalar(statement)
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return person
