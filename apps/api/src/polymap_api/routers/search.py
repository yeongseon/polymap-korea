# ruff: noqa: B008,TC002,E501,A002
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from polymap_api.deps import Pagination, get_db, get_pagination
from polymap_api.models import Issue, Party, Person
from polymap_api.schemas import IssueSummary, PartySummary, PersonSummary

router = APIRouter(prefix="/search", tags=["search"])

_SEARCH_TYPES = {"all", "person", "persons", "issue", "issues", "party", "parties"}


class SearchResponse(BaseModel):
    query: str
    persons: list[PersonSummary]
    issues: list[IssueSummary]
    parties: list[PartySummary]


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(min_length=1),
    type: str = Query(default="all"),
    pagination: Pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    if type not in _SEARCH_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported search type")

    like_term = f"%{q}%"
    persons: list[PersonSummary] = []
    issues: list[IssueSummary] = []
    parties: list[PartySummary] = []

    if type in {"all", "person", "persons"}:
        persons = [
            PersonSummary.model_validate(person)
            for person in list(
                await db.scalars(
                    select(Person)
                    .where(
                        Person.deleted_at.is_(None),
                        or_(Person.name_ko.ilike(like_term), Person.name_en.ilike(like_term)),
                    )
                    .order_by(Person.name_ko.asc())
                    .offset(pagination.offset)
                    .limit(pagination.per_page)
                )
            )
        ]
    if type in {"all", "issue", "issues"}:
        issues = [
            IssueSummary.model_validate(issue)
            for issue in list(
                await db.scalars(
                    select(Issue)
                    .where(or_(Issue.name.ilike(like_term), Issue.slug.ilike(like_term)))
                    .order_by(Issue.name.asc())
                    .offset(pagination.offset)
                    .limit(pagination.per_page)
                )
            )
        ]
    if type in {"all", "party", "parties"}:
        parties = [
            PartySummary.model_validate(party)
            for party in list(
                await db.scalars(
                    select(Party)
                    .where(
                        Party.deleted_at.is_(None),
                        or_(Party.name_ko.ilike(like_term), Party.abbreviation.ilike(like_term)),
                    )
                    .order_by(Party.name_ko.asc())
                    .offset(pagination.offset)
                    .limit(pagination.per_page)
                )
            )
        ]

    return SearchResponse(query=q, persons=persons, issues=issues, parties=parties)
