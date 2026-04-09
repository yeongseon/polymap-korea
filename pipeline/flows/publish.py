from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prefect import flow, task

logger = logging.getLogger(__name__)

DEFAULT_SNAPSHOT_DIR = Path("snapshots")


@task
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


@task
def write_snapshot(data: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_path = output_dir / f"snapshot_{timestamp}.json"
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Snapshot written to %s", file_path)
    return file_path


@flow(name="publish-snapshot")
def publish_snapshot(
    output_dir: Path | None = None,
) -> dict[str, str]:
    if output_dir is None:
        output_dir = DEFAULT_SNAPSHOT_DIR
    data = collect_curated_data()
    snapshot_path = write_snapshot(data, output_dir)
    return {
        "status": "published",
        "path": str(snapshot_path),
        "target": "postgresql",
    }
