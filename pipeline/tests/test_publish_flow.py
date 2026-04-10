from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import httpx
import pytest

from flows.publish import publish_snapshot
from publish.snapshot import index_snapshot_via_api, resolve_api_url


SNAPSHOT_PAYLOAD = {
    "version": "0.1.0",
    "schema_version": "2026-04-09",
    "generated_at": "2026-04-10T00:00:00+00:00",
    "entity_catalog": [
        {"table": "elections", "description": "선거 목록", "priority": "high"},
    ],
    "entity_count": 1,
    "publish_targets": ["api_index", "static_snapshot"],
}


def test_publish_snapshot_manifest_contains_entity_catalog(tmp_path: Path) -> None:
    result = publish_snapshot(output_dir=tmp_path, api_url=None)

    snapshot_path = Path(result["path"])
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))

    assert payload["version"] == "0.1.0"
    assert payload["publish_targets"]
    generated_at = payload["generated_at"]
    assert isinstance(generated_at, str)
    assert datetime.fromisoformat(generated_at)

    entity_catalog = payload["entity_catalog"]
    assert isinstance(entity_catalog, list)
    assert entity_catalog
    assert payload["entity_count"] == len(entity_catalog)
    assert all(
        isinstance(entity, dict)
        and {"table", "description", "priority"}.issubset(entity)
        for entity in entity_catalog
    )


def test_publish_snapshot_writes_snapshot_when_api_not_configured(tmp_path: Path) -> None:
    result = publish_snapshot(output_dir=tmp_path, api_url=None)

    snapshot_path = Path(result["path"])
    assert result["status"] == "published"
    assert result["snapshot_target"] == "json"
    assert result["api_status"] == "skipped"
    assert snapshot_path.exists()
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert payload["version"] == "0.1.0"
    assert payload["entity_count"] == len(payload["entity_catalog"])


def test_publish_snapshot_indexes_via_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_index_snapshot_via_api(
        data: dict[str, object],
        api_url: str,
        endpoint: str,
        timeout_seconds: float,
        admin_api_key: str | None,
    ) -> str:
        calls.append(
            {
                "data": data,
                "api_url": api_url,
                "endpoint": endpoint,
                "timeout_seconds": timeout_seconds,
                "admin_api_key": admin_api_key,
            }
        )
        return f"{api_url.rstrip('/')}{endpoint}"

    monkeypatch.setattr("flows.publish.index_snapshot_via_api", fake_index_snapshot_via_api)

    result = publish_snapshot(
        output_dir=tmp_path,
        api_url="http://api.internal",
        api_endpoint="/api/v1/admin/publish/snapshot",
        timeout_seconds=12.0,
    )

    assert result["api_status"] == "indexed"
    assert result["api_target"] == "http://api.internal/api/v1/admin/publish/snapshot"
    assert len(calls) == 1
    assert calls[0]["endpoint"] == "/api/v1/admin/publish/snapshot"
    assert calls[0]["timeout_seconds"] == 12.0
    assert calls[0]["admin_api_key"] == ""


def test_publish_snapshot_handles_api_failures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_index_snapshot_via_api(
        data: dict[str, object],
        api_url: str,
        endpoint: str,
        timeout_seconds: float,
        admin_api_key: str | None,
    ) -> str:
        del data, api_url, endpoint, timeout_seconds, admin_api_key
        raise httpx.HTTPStatusError(
            "server error",
            request=httpx.Request("POST", "http://api.internal/api/v1/admin/publish/snapshot"),
            response=httpx.Response(503),
        )

    monkeypatch.setattr("flows.publish.index_snapshot_via_api", fake_index_snapshot_via_api)

    result = publish_snapshot(output_dir=tmp_path, api_url="http://api.internal")

    assert result["api_status"] == "failed"
    assert result["api_target"] == "http://api.internal"
    assert "server error" in result["api_error"]


def test_index_snapshot_via_api_posts_snapshot_payload() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content.decode("utf-8"))
        captured["authorization"] = request.headers.get("Authorization")
        return httpx.Response(202, json={"status": "accepted"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        target = index_snapshot_via_api(
            SNAPSHOT_PAYLOAD,
            api_url="http://api.internal",
            admin_api_key="test-admin-key",
            client=client,
        )
    finally:
        client.close()

    assert target == "http://api.internal/api/v1/admin/publish/snapshot"
    assert captured["url"] == target
    assert captured["body"] == SNAPSHOT_PAYLOAD
    assert captured["authorization"] == "Bearer test-admin-key"


def test_index_snapshot_via_api_omits_auth_header_when_admin_key_empty() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["authorization"] = request.headers.get("Authorization")
        return httpx.Response(202, json={"status": "accepted"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        index_snapshot_via_api(SNAPSHOT_PAYLOAD, api_url="http://api.internal", admin_api_key="", client=client)
    finally:
        client.close()

    assert captured["authorization"] is None


def test_resolve_api_url_prefers_explicit_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLYMAP_API_URL", "http://env.example")

    assert resolve_api_url("http://explicit.example") == "http://explicit.example"
