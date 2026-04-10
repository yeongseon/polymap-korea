# ruff: noqa: B008,TC002,TC003
from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import get_session

_ADMIN_BEARER = HTTPBearer(auto_error=False)


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


async def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_ADMIN_BEARER),
) -> None:
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin authentication required")

    if not settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Admin API key not configured")

    if credentials.credentials != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin API key")
