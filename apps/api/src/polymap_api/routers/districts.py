# ruff: noqa: B008,TC002,TC003
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.deps import Pagination, get_db, get_pagination
from polymap_api.models import District
from polymap_api.schemas import DistrictRead, DistrictSummary

router = APIRouter(prefix="/districts", tags=["districts"])


@router.get("/{district_id}", response_model=DistrictRead)
async def get_district(district_id: UUID, db: AsyncSession = Depends(get_db)) -> District:
    district = await db.get(District, district_id)
    if district is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District not found")
    return district


@router.get("/{district_id}/children", response_model=list[DistrictSummary])
async def list_child_districts(
    district_id: UUID,
    pagination: Pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
) -> list[District]:
    district = await db.get(District, district_id)
    if district is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District not found")

    statement = (
        select(District)
        .where(District.parent_id == district_id)
        .order_by(District.name_ko.asc())
        .offset(pagination.offset)
        .limit(pagination.per_page)
    )
    result = await db.scalars(statement)
    return list(result)
