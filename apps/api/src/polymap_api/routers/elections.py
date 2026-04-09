# ruff: noqa: B008,TC002,TC003
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from polymap_api.deps import Pagination, get_db, get_pagination
from polymap_api.models import Election, Race
from polymap_api.schemas import ElectionDetail, ElectionSummary, RaceRead

router = APIRouter(prefix="/elections", tags=["elections"])


@router.get("", response_model=list[ElectionSummary])
async def list_elections(
    pagination: Pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
) -> list[Election]:
    statement = (
        select(Election)
        .order_by(Election.election_date.desc(), Election.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.per_page)
    )
    result = await db.scalars(statement)
    return list(result)


@router.get("/{election_id}", response_model=ElectionDetail)
async def get_election(election_id: UUID, db: AsyncSession = Depends(get_db)) -> Election:
    election = await db.scalar(
        select(Election)
        .options(selectinload(Election.races))
        .where(Election.id == election_id)
    )
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Election not found")
    return election


@router.get("/{election_id}/races", response_model=list[RaceRead])
async def list_election_races(
    election_id: UUID,
    pagination: Pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
) -> list[Race]:
    election = await db.get(Election, election_id)
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Election not found")

    statement = (
        select(Race)
        .where(Race.election_id == election_id)
        .order_by(Race.created_at.asc())
        .offset(pagination.offset)
        .limit(pagination.per_page)
    )
    result = await db.scalars(statement)
    return list(result)
