# ruff: noqa: B008,TC002,TC003
from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session


async def get_db(session: AsyncSession = Depends(get_session)) -> AsyncIterator[AsyncSession]:
    yield session


@dataclass(slots=True)
class Pagination:
    page: int
    per_page: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


def get_pagination(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> Pagination:
    return Pagination(page=page, per_page=per_page)
