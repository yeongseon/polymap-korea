# ruff: noqa: B008,TC002,TC003,E501
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.deps import get_db
from polymap_api.services import ComparisonResult, ComparisonService

router = APIRouter(prefix="/compare", tags=["compare"])


class CompareRequest(BaseModel):
    candidacy_ids: list[UUID] = Field(min_length=2, max_length=4)


@router.post("", response_model=ComparisonResult)
async def compare_candidacies(
    payload: CompareRequest,
    db: AsyncSession = Depends(get_db),
) -> ComparisonResult:
    service = ComparisonService()
    try:
        return await service.compare_candidacies(payload.candidacy_ids, db)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidacy not found") from exc
