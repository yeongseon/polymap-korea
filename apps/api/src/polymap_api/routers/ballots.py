# ruff: noqa: B008,TC002,E501
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from polymap_api.deps import get_db
from polymap_api.models import District, Race
from polymap_api.schemas import CandidacySummary, DistrictRead, RaceRead

router = APIRouter(prefix="/ballots", tags=["ballots"])


class BallotResolveRequest(BaseModel):
    address_text: str = Field(min_length=1)


class BallotRaceResult(BaseModel):
    race: RaceRead
    candidacies: list[CandidacySummary]


class BallotResolveResponse(BaseModel):
    district: DistrictRead
    races: list[BallotRaceResult]


@router.post("/resolve", response_model=BallotResolveResponse)
async def resolve_ballot(
    payload: BallotResolveRequest,
    db: AsyncSession = Depends(get_db),
) -> BallotResolveResponse:
    districts = list(await db.scalars(select(District)))
    normalized_address = payload.address_text.strip()
    matched_district = next(
        (
            district
            for district in sorted(
                districts,
                key=lambda item: (item.parent_id is None, -len(item.name_ko)),
            )
            if district.name_ko in normalized_address
        ),
        None,
    )
    if matched_district is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District could not be resolved")

    races = list(
        await db.scalars(
            select(Race)
            .options(selectinload(Race.candidacies))
            .where(Race.district_id == matched_district.id)
            .order_by(Race.created_at.asc())
        )
    )

    return BallotResolveResponse(
        district=DistrictRead.model_validate(matched_district),
        races=[
            BallotRaceResult(
                race=RaceRead.model_validate(race),
                candidacies=sorted(
                    [CandidacySummary.model_validate(candidacy) for candidacy in race.candidacies],
                    key=lambda item: (item.candidate_number is None, item.candidate_number or 0),
                ),
            )
            for race in races
        ],
    )
