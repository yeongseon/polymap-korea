# ruff: noqa: B008,TC002,TC003,E501
from __future__ import annotations

import importlib

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from polymap_api.deps import get_db
from polymap_api.models import District, Race
from polymap_api.schemas import CandidacySummary, DistrictRead, RaceRead

_GEOCODING = importlib.import_module("polymap_api.services.geocoding")

router = APIRouter(prefix="/ballots", tags=["ballots"])


class BallotResolveRequest(BaseModel):
    address_text: str = Field(min_length=1)


class BallotRaceResult(BaseModel):
    race: RaceRead
    candidacies: list[CandidacySummary]


class BallotResolveResponse(BaseModel):
    district: DistrictRead
    races: list[BallotRaceResult]


def _district_lineage(district: District, districts_by_id: dict) -> list[District]:
    lineage = [district]
    current = district
    while current.parent_id is not None:
        current = districts_by_id[current.parent_id]
        lineage.append(current)
    return lineage


@router.post("/resolve", response_model=BallotResolveResponse)
async def resolve_ballot(
    payload: BallotResolveRequest,
    db: AsyncSession = Depends(get_db),
) -> BallotResolveResponse:
    districts = list(await db.scalars(select(District)))
    normalized_address = payload.address_text.strip()
    matched_district = await _GEOCODING.build_address_resolver().resolve(normalized_address, districts)
    if matched_district is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District could not be resolved")

    districts_by_id = {district.id: district for district in districts}
    scoped_districts = _district_lineage(matched_district, districts_by_id)
    district_order = {district.id: index for index, district in enumerate(scoped_districts)}

    races = list(
        await db.scalars(
            select(Race)
            .options(selectinload(Race.candidacies))
            .where(Race.district_id.in_([district.id for district in scoped_districts]))
        )
    )
    races.sort(key=lambda race: (district_order[race.district_id], race.created_at))

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
