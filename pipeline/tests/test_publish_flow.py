from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from flows.publish import publish_snapshot
from publish.snapshot import index_snapshot_via_api, resolve_api_url


def test_publish_snapshot_writes_snapshot_when_api_not_configured(tmp_path: Path) -> None:
    result = publish_snapshot(output_dir=tmp_path, api_url=None)

    snapshot_path = Path(result["path"])
    assert result["status"] == "published"
    assert result["snapshot_target"] == "json"
    assert result["api_status"] == "skipped"
    assert snapshot_path.exists()
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert payload["version"] == "0.1.0"


def test_publish_snapshot_indexes_via_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_index_snapshot_via_api(
        data: dict[str, object],
        api_url: str,
        endpoint: str,
        timeout_seconds: float,
    ) -> str:
        calls.append(
            {
                "data": data,
                "api_url": api_url,
                "endpoint": endpoint,
                "timeout_seconds": timeout_seconds,
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


def test_publish_snapshot_handles_api_failures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_index_snapshot_via_api(
        data: dict[str, object],
        api_url: str,
        endpoint: str,
        timeout_seconds: float,
    ) -> str:
        del data, api_url, endpoint, timeout_seconds
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
        return httpx.Response(202, json={"status": "accepted"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        target = index_snapshot_via_api({"version": "0.1.0"}, api_url="http://api.internal", client=client)
    finally:
        client.close()

    assert target == "http://api.internal/api/v1/admin/publish/snapshot"
    assert captured["url"] == target
    assert captured["body"] == {"snapshot": {"version": "0.1.0"}}


def test_resolve_api_url_prefers_explicit_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLYMAP_API_URL", "http://env.example")

    assert resolve_api_url("http://explicit.example") == "http://explicit.example"
