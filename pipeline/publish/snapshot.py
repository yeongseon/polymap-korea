from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_SNAPSHOT_DIR = Path("snapshots")
DEFAULT_API_ENDPOINT = "/api/v1/admin/publish/snapshot"


def collect_curated_data() -> dict[str, Any]:
    entity_catalog = [
        {"table": "elections", "description": "선거 목록", "priority": "high"},
        {"table": "districts", "description": "선거구 행정구역", "priority": "high"},
        {"table": "persons", "description": "후보자 인물 정보", "priority": "high"},
        {"table": "parties", "description": "정당 정보", "priority": "medium"},
        {"table": "races", "description": "선거 경선 단위", "priority": "high"},
        {"table": "candidacies", "description": "후보 등록 정보", "priority": "high"},
        {"table": "promises", "description": "후보 공약", "priority": "high"},
        {"table": "claims", "description": "후보 관련 주장/팩트체크", "priority": "medium"},
        {"table": "source_docs", "description": "출처 문서", "priority": "medium"},
        {"table": "issues", "description": "정책 이슈 분류", "priority": "medium"},
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
        "schema_version": "2026-04-09",
        "entity_catalog": entity_catalog,
        "entity_count": len(entity_catalog),
        "publish_targets": ["api_index", "static_snapshot"],
    }


def write_snapshot(data: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_path = output_dir / f"snapshot_{timestamp}.json"
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Snapshot written to %s", file_path)
    return file_path


def resolve_api_url(api_url: str | None = None) -> str | None:
    configured_url = api_url or os.getenv("POLYMAP_API_URL") or os.getenv("API_URL")
    if configured_url is None:
        return None
    normalized = configured_url.strip()
    return normalized or None


def resolve_admin_api_key(admin_api_key: str | None = None) -> str:
    if admin_api_key is not None:
        return admin_api_key
    return os.getenv("POLYMAP_ADMIN_API_KEY", "")


def index_snapshot_via_api(
    data: dict[str, Any],
    api_url: str,
    endpoint: str = DEFAULT_API_ENDPOINT,
    timeout_seconds: float = 30.0,
    admin_api_key: str | None = None,
    client: httpx.Client | None = None,
) -> str:
    resolved_key = resolve_admin_api_key(admin_api_key)
    normalized_base = api_url.rstrip("/")
    normalized_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    target_url = f"{normalized_base}{normalized_endpoint}"
    owns_client = client is None
    http_client = client or httpx.Client(timeout=timeout_seconds)
    headers = {"Authorization": f"Bearer {resolved_key}"} if resolved_key else None

    try:
        response = http_client.post(target_url, json=data, headers=headers)
        response.raise_for_status()
    finally:
        if owns_client:
            http_client.close()

    logger.info("Indexed snapshot via API at %s", target_url)
    return target_url


__all__ = [
    "DEFAULT_API_ENDPOINT",
    "DEFAULT_SNAPSHOT_DIR",
    "collect_curated_data",
    "index_snapshot_via_api",
    "resolve_admin_api_key",
    "resolve_api_url",
    "write_snapshot",
]
