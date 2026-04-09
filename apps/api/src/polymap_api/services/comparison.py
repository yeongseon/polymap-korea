# ruff: noqa: TC003,E501
from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from polymap_api.models import Candidacy, Promise
from polymap_api.schemas import PromiseSummary


class ComparedPromise(BaseModel):
    candidacy_id: UUID
    person_name: str
    party_name: str | None
    promises: list[PromiseSummary]


class ComparisonByIssue(BaseModel):
    issue_id: UUID | None
    issue_name: str | None
    candidates: list[ComparedPromise]


class ComparisonResult(BaseModel):
    candidacy_ids: list[UUID] = Field(min_length=2, max_length=4)
    by_issue: list[ComparisonByIssue]


class ComparisonService:
    async def compare_candidacies(
        self, candidacy_ids: list[UUID], db: AsyncSession,
    ) -> ComparisonResult:
        statement = (
            select(Candidacy)
            .options(
                selectinload(Candidacy.person),
                selectinload(Candidacy.party),
                selectinload(Candidacy.claims),
                selectinload(Candidacy.promises).selectinload(Promise.issue),
            )
            .where(Candidacy.id.in_(candidacy_ids))
        )
        candidacies = list(await db.scalars(statement))
        candidacy_by_id = {candidacy.id: candidacy for candidacy in candidacies}
        missing_ids = [candidacy_id for candidacy_id in candidacy_ids if candidacy_id not in candidacy_by_id]
        if missing_ids:
            raise LookupError("Missing candidacy")

        ordered_candidacies = [candidacy_by_id[candidacy_id] for candidacy_id in candidacy_ids]
        issues: dict[UUID | None, str | None] = {}
        promises_by_issue: dict[UUID | None, dict[UUID, list[Promise]]] = {}

        for candidacy in ordered_candidacies:
            for promise in candidacy.promises:
                issues[promise.issue_id] = promise.issue.name if promise.issue is not None else None
                promises_by_issue.setdefault(promise.issue_id, {}).setdefault(candidacy.id, []).append(promise)

        def _issue_sort_key(item: tuple[UUID | None, str | None]) -> tuple[int, str]:
            issue_id, issue_name = item
            return (1 if issue_id is None else 0, issue_name or "")

        by_issue: list[ComparisonByIssue] = []
        for issue_id, issue_name in sorted(issues.items(), key=_issue_sort_key):
            candidates: list[ComparedPromise] = []
            for candidacy in ordered_candidacies:
                issue_promises = sorted(
                    promises_by_issue.get(issue_id, {}).get(candidacy.id, []),
                    key=lambda item: (item.sort_order, item.created_at),
                )
                candidates.append(
                    ComparedPromise(
                        candidacy_id=candidacy.id,
                        person_name=candidacy.person.name_ko,
                        party_name=candidacy.party.name_ko if candidacy.party is not None else None,
                        promises=[PromiseSummary.model_validate(promise) for promise in issue_promises],
                    )
                )
            by_issue.append(ComparisonByIssue(issue_id=issue_id, issue_name=issue_name, candidates=candidates))

        return ComparisonResult(candidacy_ids=candidacy_ids, by_issue=by_issue)
