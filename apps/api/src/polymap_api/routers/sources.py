# ruff: noqa: B008,TC002,TC003,E501
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.deps import get_db
from polymap_api.models import SourceDoc
from polymap_api.schemas import SourceDocRead

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/{source_id}", response_model=SourceDocRead)
async def get_source(source_id: UUID, db: AsyncSession = Depends(get_db)) -> SourceDoc:
    source = await db.get(SourceDoc, source_id)
    if source is None or source.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source document not found")
    return source
