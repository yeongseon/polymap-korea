# ruff: noqa: B008,TC002,TC003,E501
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from polymap_api.deps import get_db
from polymap_api.models import Issue, Promise
from polymap_api.schemas import CandidacySummary, IssueRead, PromiseSummary

router = APIRouter(prefix="/issues", tags=["issues"])


class IssueTreeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    parent_id: UUID | None
    children: list[IssueTreeNode]


class IssuePromiseSummary(PromiseSummary):
    candidacy: CandidacySummary


class IssueDetail(IssueRead):
    related_promises: list[IssuePromiseSummary]


def _serialize_issue_tree(
    issue: Issue,
    children_by_parent: dict[UUID | None, list[Issue]],
) -> IssueTreeNode:
    return IssueTreeNode(
        id=issue.id,
        name=issue.name,
        slug=issue.slug,
        parent_id=issue.parent_id,
        children=[
            _serialize_issue_tree(child, children_by_parent)
            for child in children_by_parent.get(issue.id, [])
        ],
    )


@router.get("", response_model=list[IssueTreeNode])
async def list_issues(db: AsyncSession = Depends(get_db)) -> list[IssueTreeNode]:
    issues = list(await db.scalars(select(Issue).order_by(Issue.name.asc())))
    children_by_parent: dict[UUID | None, list[Issue]] = {}
    for issue in issues:
        children_by_parent.setdefault(issue.parent_id, []).append(issue)
    return [
        _serialize_issue_tree(issue, children_by_parent)
        for issue in children_by_parent.get(None, [])
    ]


@router.get("/{issue_id}", response_model=IssueDetail)
async def get_issue(issue_id: UUID, db: AsyncSession = Depends(get_db)) -> IssueDetail:
    statement = (
        select(Issue)
        .options(selectinload(Issue.promises).selectinload(Promise.candidacy))
        .where(Issue.id == issue_id)
    )
    issue = await db.scalar(statement)
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    return IssueDetail(
        **IssueRead.model_validate(issue).model_dump(),
        related_promises=[
            IssuePromiseSummary(
                **PromiseSummary.model_validate(promise).model_dump(),
                candidacy=CandidacySummary.model_validate(promise.candidacy),
            )
            for promise in sorted(issue.promises, key=lambda item: (item.sort_order, item.created_at))
        ],
    )
