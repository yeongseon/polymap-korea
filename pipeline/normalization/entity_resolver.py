from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def resolve_entity_key(source_system: str, entity_type: str, source_id: str) -> str:
    return f"{source_system}:{entity_type}:{source_id}"


def merge_entity_payloads(*payloads: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for payload in payloads:
        merged.update(payload)
    return merged


@dataclass(frozen=True)
class EntityCandidate:
    source: str
    entity_type: str
    source_id: str
    fields: dict[str, Any]
    score: float = 0.0


@dataclass(frozen=True)
class ResolvedEntity:
    entity_key: str
    candidates: list[EntityCandidate]
    score: float
    resolution: str
    merged_fields: dict[str, Any]


@dataclass
class ReviewQueue:
    items: list[ResolvedEntity] = field(default_factory=list)

    def add(self, entity: ResolvedEntity) -> None:
        self.items.append(entity)


class EntityResolver:
    def __init__(self, auto_merge_threshold: float = 0.8, review_threshold: float = 0.5) -> None:
        self.auto_merge_threshold = auto_merge_threshold
        self.review_threshold = review_threshold
        self.review_queue = ReviewQueue()

    def resolve(self, candidates: list[EntityCandidate]) -> list[ResolvedEntity]:
        groups: list[list[EntityCandidate]] = []
        for candidate in candidates:
            placed = False
            for group in groups:
                score = max(self._match_score(candidate, existing) for existing in group)
                if score >= self.review_threshold:
                    group.append(self._scored_candidate(candidate, score))
                    placed = True
                    break
            if not placed:
                groups.append([candidate])

        resolved_entities: list[ResolvedEntity] = []
        for group in groups:
            resolution_score = self._group_score(group)
            resolution = self._resolution_for_score(resolution_score, len(group))
            merged_fields = merge_entity_payloads(*(candidate.fields for candidate in group))
            resolved = ResolvedEntity(
                entity_key=self._entity_key(group),
                candidates=group,
                score=resolution_score,
                resolution=resolution,
                merged_fields=merged_fields,
            )
            if resolution == "review":
                self.review_queue.add(resolved)
            resolved_entities.append(resolved)
        return resolved_entities

    def _scored_candidate(self, candidate: EntityCandidate, score: float) -> EntityCandidate:
        if score <= candidate.score:
            return candidate
        return EntityCandidate(
            source=candidate.source,
            entity_type=candidate.entity_type,
            source_id=candidate.source_id,
            fields=candidate.fields,
            score=score,
        )

    def _group_score(self, group: list[EntityCandidate]) -> float:
        if len(group) == 1:
            return group[0].score

        pair_scores: list[float] = []
        for index, candidate in enumerate(group):
            for peer in group[index + 1 :]:
                pair_scores.append(self._match_score(candidate, peer))
        return max(pair_scores, default=0.0)

    def _resolution_for_score(self, score: float, size: int) -> str:
        if size == 1 and score < self.review_threshold:
            return "separate"
        if score >= self.auto_merge_threshold:
            return "auto_merge"
        if score >= self.review_threshold:
            return "review"
        return "separate"

    def _entity_key(self, group: list[EntityCandidate]) -> str:
        lead = group[0]
        official_id = str(lead.fields.get("official_id") or lead.source_id)
        return resolve_entity_key(lead.source, lead.entity_type, official_id)

    def _match_score(self, left: EntityCandidate, right: EntityCandidate) -> float:
        left_fields = left.fields
        right_fields = right.fields

        left_official = self._normalized(left_fields.get("official_id"))
        right_official = self._normalized(right_fields.get("official_id"))
        if left_official and right_official and left_official == right_official:
            return 1.0

        left_name = self._normalized(left_fields.get("name"))
        right_name = self._normalized(right_fields.get("name"))
        names_match = bool(left_name) and left_name == right_name
        if not names_match:
            return 0.0

        left_district = self._normalized(left_fields.get("district"))
        right_district = self._normalized(right_fields.get("district"))
        district_match = bool(left_district) and left_district == right_district

        left_birth = self._normalized(left_fields.get("birth_date"))
        right_birth = self._normalized(right_fields.get("birth_date"))
        birth_match = bool(left_birth) and left_birth == right_birth

        if names_match and birth_match and district_match:
            return 0.9
        if names_match and district_match:
            return 0.7
        if names_match:
            return 0.3
        return 0.0

    def _normalized(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip().lower()
