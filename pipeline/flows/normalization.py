from __future__ import annotations

import logging
from typing import Any

from prefect import flow, task

from common.base_adapter import RawRecord
from normalization.entity_resolver import EntityCandidate, EntityResolver
from normalization.normalizer import (
    AssemblyNormalizer,
    NecNormalizer,
    NormalizedResult,
)

logger = logging.getLogger(__name__)


@task
def run_nec_normalization(records: list[RawRecord]) -> list[NormalizedResult]:
    normalizer = NecNormalizer()
    return normalizer.normalize(records)


@task
def run_assembly_normalization(records: list[RawRecord]) -> list[NormalizedResult]:
    normalizer = AssemblyNormalizer()
    return normalizer.normalize(records)


@task
def run_entity_resolution(
    results: list[NormalizedResult],
) -> list[dict[str, Any]]:
    person_results = [r for r in results if r.entity_type == "person" and r.is_valid]
    candidates = [
        EntityCandidate(
            source=r.source_record.source_system,
            entity_type="person",
            source_id=r.data.get("name", ""),
            fields=r.data,
        )
        for r in person_results
    ]
    if not candidates:
        return []
    resolver = EntityResolver()
    resolved = resolver.resolve(candidates)
    return [
        {
            "entity_key": entity.entity_key,
            "score": entity.score,
            "resolution": entity.resolution,
            "merged_fields": entity.merged_fields,
            "candidate_count": len(entity.candidates),
        }
        for entity in resolved
    ]


@flow(name="normalize-batch")
def normalize_batch(
    source: str, records: list[RawRecord],
) -> dict[str, Any]:
    if source == "nec":
        normalized = run_nec_normalization(records)
    elif source == "assembly":
        normalized = run_assembly_normalization(records)
    else:
        logger.warning("Unknown source: %s", source)
        return {"normalized": [], "resolved": [], "errors": []}

    valid = [r for r in normalized if r.is_valid]
    errors = [r for r in normalized if not r.is_valid]

    resolved = run_entity_resolution(valid)

    return {
        "normalized": [{"type": r.entity_type, "data": r.data} for r in valid],
        "resolved": resolved,
        "errors": [
            {"type": r.entity_type, "field_errors": [e.field for e in r.errors]}
            for r in errors
        ],
    }
