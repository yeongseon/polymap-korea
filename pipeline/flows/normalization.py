from __future__ import annotations

import logging
from typing import Any

from prefect import flow, task

from common.base_adapter import RawRecord
from normalization.entity_resolver import EntityCandidate, EntityResolver
from normalization.normalizer import (
    AssemblyNormalizer,
    LocalCouncilNormalizer,
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
def run_local_council_normalization(records: list[RawRecord]) -> list[NormalizedResult]:
    normalizer = LocalCouncilNormalizer()
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
    elif source == "local_council":
        normalized = run_local_council_normalization(records)
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


@flow(name="normalize-and-resolve-all")
def normalize_and_resolve_all(source_records: dict[str, list[RawRecord]]) -> dict[str, Any]:
    normalized_by_source: dict[str, list[NormalizedResult]] = {
        "nec": run_nec_normalization(source_records.get("nec", [])),
        "assembly": run_assembly_normalization(source_records.get("assembly", [])),
        "local_council": run_local_council_normalization(source_records.get("local_council", [])),
    }
    all_normalized = [result for results in normalized_by_source.values() for result in results]
    valid = [result for result in all_normalized if result.is_valid]
    errors = [result for result in all_normalized if not result.is_valid]
    resolved = run_entity_resolution(valid)

    return {
        "normalized": {
            source: [{"type": result.entity_type, "data": result.data} for result in results if result.is_valid]
            for source, results in normalized_by_source.items()
        },
        "resolved": resolved,
        "errors": [
            {
                "source": result.source_record.source_system,
                "type": result.entity_type,
                "field_errors": [error.field for error in result.errors],
            }
            for result in errors
        ],
    }
