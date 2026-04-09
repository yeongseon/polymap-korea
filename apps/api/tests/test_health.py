from __future__ import annotations

from fastapi.testclient import TestClient

from polymap_api.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["election_date"] == "2026-06-03"
