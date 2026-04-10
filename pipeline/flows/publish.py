from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import httpx
from prefect import flow, task

from publish.snapshot import (
    DEFAULT_API_ENDPOINT,
    DEFAULT_SNAPSHOT_DIR,
    collect_curated_data as collect_curated_snapshot_data,
    index_snapshot_via_api,
    resolve_api_url,
    write_snapshot as persist_snapshot,
)

logger = logging.getLogger(__name__)


@task
def collect_curated_data() -> dict[str, Any]:
    return collect_curated_snapshot_data()


@task
def write_snapshot(data: dict[str, Any], output_dir: Path) -> Path:
    return persist_snapshot(data, output_dir)


@task
def index_snapshot(
    data: dict[str, Any],
    api_url: str | None,
    api_endpoint: str,
    timeout_seconds: float,
) -> dict[str, str]:
    resolved_api_url = resolve_api_url(api_url)
    if resolved_api_url is None:
        return {"api_status": "skipped", "api_target": "not-configured"}

    try:
        api_target = index_snapshot_via_api(
            data,
            api_url=resolved_api_url,
            endpoint=api_endpoint,
            timeout_seconds=timeout_seconds,
        )
    except httpx.HTTPError as exc:
        logger.warning("Publish API indexing failed: %s", exc)
        return {"api_status": "failed", "api_target": resolved_api_url, "api_error": str(exc)}

    return {"api_status": "indexed", "api_target": api_target}


@flow(name="publish-snapshot")
def publish_snapshot(
    output_dir: Path | None = None,
    api_url: str | None = None,
    api_endpoint: str = DEFAULT_API_ENDPOINT,
    timeout_seconds: float = 30.0,
) -> dict[str, str]:
    if output_dir is None:
        output_dir = DEFAULT_SNAPSHOT_DIR
    data = collect_curated_data()
    snapshot_path = write_snapshot(data, output_dir)
    result = {
        "status": "published",
        "path": str(snapshot_path),
        "snapshot_target": "json",
    }
    result.update(index_snapshot(data, api_url=api_url, api_endpoint=api_endpoint, timeout_seconds=timeout_seconds))
    return result
