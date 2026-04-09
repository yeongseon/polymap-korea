from __future__ import annotations

from fastapi import FastAPI

from .config import settings

app = FastAPI(
    title="PolyMap Korea API",
    description="2026 지방선거 유권자 정보 탐색 서비스 API",
    version="0.1.0",
)


@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "version": settings.app_version,
        "election_date": "2026-06-03",
    }
