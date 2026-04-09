# ruff: noqa: B008,TC002,TC003,E501
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.deps import get_db
from polymap_api.middleware.content_guard import ensure_content_visible
from polymap_api.models import Candidacy, Claim, Promise, Race, SourceDoc
from polymap_api.schemas import SourceDocRead

router = APIRouter(prefix="/sources", tags=["sources"])

_POLL_SOURCE_KEYWORDS = ("poll", "survey", "여론조사", "지지도")


def _is_poll_related_source(source: SourceDoc) -> bool:
    fields = (source.title, source.url, source.raw_s3_key)
    combined = " ".join(value.casefold() for value in fields if value)
    return any(keyword in combined for keyword in _POLL_SOURCE_KEYWORDS)


async def require_poll_source_visibility(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    source = await db.get(SourceDoc, source_id)
    if source is None or source.deleted_at is not None or source.visibility == "HIDDEN":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source document not found")
    if not _is_poll_related_source(source):
        return

    election_id = await db.scalar(
        select(Race.election_id)
        .join(Candidacy, Candidacy.race_id == Race.id)
        .outerjoin(Claim, Claim.candidacy_id == Candidacy.id)
        .outerjoin(Promise, Promise.candidacy_id == Candidacy.id)
        .where((Claim.source_doc_id == source_id) | (Promise.source_doc_id == source_id))
    )
    if election_id is not None:
        await ensure_content_visible(content_type="poll_result", election_id=election_id, db=db)


@router.get("/{source_id}", response_model=SourceDocRead)
async def get_source(
    source_id: UUID,
    _: None = Depends(require_poll_source_visibility),
    db: AsyncSession = Depends(get_db),
) -> SourceDoc:
    source = await db.get(SourceDoc, source_id)
    if source is None or source.deleted_at is not None or source.visibility == "HIDDEN":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source document not found")
    return source
