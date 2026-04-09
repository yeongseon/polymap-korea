from __future__ import annotations

from normalization.entity_resolver import (
    EntityCandidate,
    EntityResolver,
    ResolvedEntity,
    ReviewQueue,
    merge_entity_payloads,
    resolve_entity_key,
)


def test_resolve_entity_key() -> None:
    key = resolve_entity_key("nec", "person", "12345")
    assert key == "nec:person:12345"


def test_merge_entity_payloads() -> None:
    result = merge_entity_payloads(
        {"name": "홍길동", "age": 30},
        {"party": "민주당", "age": 31},
    )
    assert result == {"name": "홍길동", "age": 31, "party": "민주당"}


def test_official_id_match_auto_merge() -> None:
    resolver = EntityResolver()
    candidates = [
        EntityCandidate(
            source="nec",
            entity_type="person",
            source_id="NEC001",
            fields={"name": "홍길동", "official_id": "PERSON-001", "district": "종로구"},
        ),
        EntityCandidate(
            source="assembly",
            entity_type="person",
            source_id="ASM001",
            fields={"name": "홍길동", "official_id": "PERSON-001", "party": "민주당"},
        ),
    ]
    result = resolver.resolve(candidates)
    assert len(result) == 1
    assert result[0].resolution == "auto_merge"
    assert result[0].score == 1.0
    assert result[0].merged_fields["district"] == "종로구"
    assert result[0].merged_fields["party"] == "민주당"


def test_name_birth_district_strong_match() -> None:
    resolver = EntityResolver()
    candidates = [
        EntityCandidate(
            source="nec",
            entity_type="person",
            source_id="NEC001",
            fields={"name": "김영희", "birth_date": "1975-03-15", "district": "강남구"},
        ),
        EntityCandidate(
            source="assembly",
            entity_type="person",
            source_id="ASM001",
            fields={"name": "김영희", "birth_date": "1975-03-15", "district": "강남구"},
        ),
    ]
    result = resolver.resolve(candidates)
    assert len(result) == 1
    assert result[0].resolution == "auto_merge"
    assert result[0].score == 0.9


def test_name_district_weak_match_goes_to_review() -> None:
    resolver = EntityResolver()
    candidates = [
        EntityCandidate(
            source="nec",
            entity_type="person",
            source_id="NEC001",
            fields={"name": "박철수", "district": "마포구"},
        ),
        EntityCandidate(
            source="assembly",
            entity_type="person",
            source_id="ASM001",
            fields={"name": "박철수", "district": "마포구"},
        ),
    ]
    result = resolver.resolve(candidates)
    assert len(result) == 1
    assert result[0].resolution == "review"
    assert result[0].score == 0.7
    assert len(resolver.review_queue.items) == 1


def test_name_only_separate() -> None:
    resolver = EntityResolver()
    candidates = [
        EntityCandidate(
            source="nec",
            entity_type="person",
            source_id="NEC001",
            fields={"name": "이민수"},
        ),
        EntityCandidate(
            source="assembly",
            entity_type="person",
            source_id="ASM001",
            fields={"name": "이민수"},
        ),
    ]
    result = resolver.resolve(candidates)
    assert len(result) == 2
    assert all(r.resolution == "separate" for r in result)


def test_no_match_separate() -> None:
    resolver = EntityResolver()
    candidates = [
        EntityCandidate(
            source="nec",
            entity_type="person",
            source_id="NEC001",
            fields={"name": "홍길동"},
        ),
        EntityCandidate(
            source="assembly",
            entity_type="person",
            source_id="ASM001",
            fields={"name": "김영희"},
        ),
    ]
    result = resolver.resolve(candidates)
    assert len(result) == 2


def test_review_queue() -> None:
    queue = ReviewQueue()
    entity = ResolvedEntity(
        entity_key="test:person:1",
        candidates=[],
        score=0.6,
        resolution="review",
        merged_fields={},
    )
    queue.add(entity)
    assert len(queue.items) == 1
    assert queue.items[0].entity_key == "test:person:1"


def test_single_candidate_stays_separate() -> None:
    resolver = EntityResolver()
    candidates = [
        EntityCandidate(
            source="nec",
            entity_type="person",
            source_id="NEC001",
            fields={"name": "홍길동"},
        ),
    ]
    result = resolver.resolve(candidates)
    assert len(result) == 1
    assert result[0].resolution == "separate"


def test_case_insensitive_matching() -> None:
    resolver = EntityResolver()
    candidates = [
        EntityCandidate(
            source="nec",
            entity_type="person",
            source_id="NEC001",
            fields={"name": "Hong GilDong", "official_id": "P001"},
        ),
        EntityCandidate(
            source="assembly",
            entity_type="person",
            source_id="ASM001",
            fields={"name": "hong gildong", "official_id": "p001"},
        ),
    ]
    result = resolver.resolve(candidates)
    assert len(result) == 1
    assert result[0].resolution == "auto_merge"
