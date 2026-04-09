from __future__ import annotations

from typing import Any


def resolve_entity_key(source_system: str, entity_type: str, source_id: str) -> str:
    return f"{source_system}:{entity_type}:{source_id}"


def merge_entity_payloads(*payloads: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for payload in payloads:
        merged.update(payload)
    return merged
