# ruff: noqa: E501,I001
from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .deps import get_db
from .routers import ballots, candidacies, compare, compliance, districts, elections, issues, persons, search, sources, sse

app = FastAPI(
    title="PolyMap Korea API",
    description="2026 지방선거 유권자 정보 탐색 서비스 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "version": settings.app_version,
        "election_date": "2026-06-03",
    }


@app.get("/api/v1/health/ready", response_model=None)
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, str] | JSONResponse:
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "db": "unavailable",
                "detail": str(exc),
            },
        )

    return {
        "status": "ok",
        "db": "connected",
    }


app.include_router(elections.router, prefix="/api/v1")
app.include_router(districts.router, prefix="/api/v1")
app.include_router(persons.router, prefix="/api/v1")
app.include_router(candidacies.router, prefix="/api/v1")
app.include_router(ballots.router, prefix="/api/v1")
app.include_router(issues.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(compare.router, prefix="/api/v1")
app.include_router(sse.router, prefix="/api/v1")
app.include_router(compliance.router, prefix="/api/v1")
