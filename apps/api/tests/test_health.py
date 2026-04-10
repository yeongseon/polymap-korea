from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from polymap_api.deps import get_db
from polymap_api.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["election_date"] == "2026-06-03"


def test_cors_preflight_allows_local_web_origin() -> None:
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


@pytest.mark.asyncio
async def test_readiness_check_reports_database_connected(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "connected"}


@pytest.mark.asyncio
async def test_readiness_check_hides_database_errors(client: AsyncClient) -> None:
    class FailingSession:
        async def execute(self, *_args: object, **_kwargs: object) -> None:
            raise SQLAlchemyError("sensitive database details")

    async def failing_get_db() -> object:
        yield FailingSession()

    app.dependency_overrides[get_db] = failing_get_db
    try:
        response = await client.get("/api/v1/health/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"status": "error", "db": "unavailable"}
