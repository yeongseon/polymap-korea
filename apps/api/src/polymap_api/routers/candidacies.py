# ruff: noqa: B008,TC002,TC003,E501,I001
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from polymap_api.deps import Pagination, get_db, get_pagination
from polymap_api.middleware.content_guard import ensure_content_visible, is_content_blocked
from polymap_api.models import Candidacy, Claim, Promise, Race
from polymap_api.schemas import (
    CandidacySummary,
    ClaimRead,
    PartySummary,
    PersonSummary,
    PromiseRead,
)
from polymap_ontology.enums import CandidacyStatus

router = APIRouter(prefix="/candidacies", tags=["candidacies"])


class CandidacyDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    person_id: UUID
    race_id: UUID
    party_id: UUID | None
    status: CandidacyStatus
    registered_at: date | None
    candidate_number: int | None
    created_at: datetime
    updated_at: datetime
    person: PersonSummary
    party: PartySummary | None
    promises: list[PromiseRead]
    claims: list[ClaimRead]


async def _get_candidacy_or_404(candidacy_id: UUID, db: AsyncSession) -> Candidacy:
    statement = (
        select(Candidacy)
        .options(
            selectinload(Candidacy.person),
            selectinload(Candidacy.party),
            selectinload(Candidacy.promises),
            selectinload(Candidacy.claims),
        )
        .where(Candidacy.id == candidacy_id)
    )
    candidacy = await db.scalar(statement)
    if candidacy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidacy not found")
    return candidacy


async def require_poll_result_visibility_for_claims(
    candidacy_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    election_id = await db.scalar(
        select(Race.election_id).join(Candidacy, Candidacy.race_id == Race.id).where(Candidacy.id == candidacy_id)
    )
    if election_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidacy not found")
    await ensure_content_visible(content_type="poll_result", election_id=election_id, db=db)


@router.get("", response_model=list[CandidacySummary])
async def list_candidacies(
    election_id: UUID | None = Query(default=None),
    district_id: UUID | None = Query(default=None),
    race_id: UUID | None = Query(default=None),
    pagination: Pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
) -> list[Candidacy]:
    statement = select(Candidacy).join(Candidacy.race)
    if election_id is not None:
        statement = statement.where(Race.election_id == election_id)
    if district_id is not None:
        statement = statement.where(Race.district_id == district_id)
    if race_id is not None:
        statement = statement.where(Candidacy.race_id == race_id)
    statement = (
        statement.order_by(Candidacy.candidate_number.asc().nulls_last(), Candidacy.created_at.asc())
        .offset(pagination.offset)
        .limit(pagination.per_page)
    )
    result = await db.scalars(statement)
    return list(result)


@router.get("/{candidacy_id}", response_model=CandidacyDetail)
async def get_candidacy(candidacy_id: UUID, db: AsyncSession = Depends(get_db)) -> Candidacy | dict[str, object]:
    candidacy = await _get_candidacy_or_404(candidacy_id, db)
    election_id = await db.scalar(select(Race.election_id).where(Race.id == candidacy.race_id))
    if election_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidacy not found")
    if await is_content_blocked("poll_result", election_id, db):
        response = CandidacyDetail.model_validate(candidacy).model_dump()
        response["claims"] = []
        return response
    return candidacy


@router.get("/{candidacy_id}/promises", response_model=list[PromiseRead])
async def list_candidacy_promises(candidacy_id: UUID, db: AsyncSession = Depends(get_db)) -> list[Promise]:
    await _get_candidacy_or_404(candidacy_id, db)
    statement = (
        select(Promise)
        .where(Promise.candidacy_id == candidacy_id)
        .order_by(Promise.sort_order.asc(), Promise.created_at.asc())
    )
    result = await db.scalars(statement)
    return list(result)


@router.get("/{candidacy_id}/claims", response_model=list[ClaimRead])
async def list_candidacy_claims(
    candidacy_id: UUID,
    _: None = Depends(require_poll_result_visibility_for_claims),
    db: AsyncSession = Depends(get_db),
) -> list[Claim]:
    await _get_candidacy_or_404(candidacy_id, db)
    statement = select(Claim).where(Claim.candidacy_id == candidacy_id).order_by(Claim.created_at.asc())
    result = await db.scalars(statement)
    return list(result)
