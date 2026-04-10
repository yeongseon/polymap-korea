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
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
        "tables": [
            "persons",
            "parties",
            "elections",
            "districts",
            "races",
            "candidacies",
            "promises",
        ],
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


def index_snapshot_via_api(
    data: dict[str, Any],
    api_url: str,
    endpoint: str = DEFAULT_API_ENDPOINT,
    timeout_seconds: float = 30.0,
    client: httpx.Client | None = None,
) -> str:
    normalized_base = api_url.rstrip("/")
    normalized_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    target_url = f"{normalized_base}{normalized_endpoint}"
    owns_client = client is None
    http_client = client or httpx.Client(timeout=timeout_seconds)

    try:
        response = http_client.post(target_url, json={"snapshot": data})
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
    "resolve_api_url",
    "write_snapshot",
]
