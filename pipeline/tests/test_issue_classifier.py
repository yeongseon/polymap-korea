from __future__ import annotations

import json
from pathlib import Path

from normalization.issues import classify_promise

TAXONOMY_JSON = Path(__file__).resolve().parents[1] / "taxonomy" / "taxonomy.json"


def _load_classifiable_slugs() -> set[str]:
    with open(TAXONOMY_JSON, encoding="utf-8") as f:
        taxonomy = json.load(f)
    slugs: set[str] = set()
    for parent in taxonomy:
        children = parent.get("children", [])
        if children:
            for child in children:
                slugs.add(child["slug"])
        else:
            slugs.add(parent["slug"])
    return slugs


def _load_all_taxonomy_slugs() -> set[str]:
    with open(TAXONOMY_JSON, encoding="utf-8") as f:
        taxonomy = json.load(f)
    slugs: set[str] = set()
    for parent in taxonomy:
        slugs.add(parent["slug"])
        for child in parent.get("children", []):
            slugs.add(child["slug"])
    return slugs


def test_classify_promise_returns_ranked_issue_matches() -> None:
    matches = classify_promise(
        "지하철 노선 확대와 버스 환승 개선",
        "대중교통 중심으로 지하철과 버스 노선을 확대하고 도로 혼잡을 줄이겠습니다.",
    )

    assert matches == ["transport-public", "transport-road"]


def test_classify_promise_limits_results_to_top_three() -> None:
    matches = classify_promise(
        "청년 일자리와 주거, 보육, 재활용, 행정 혁신",
        "일자리와 임대주택을 늘리고 어린이집 지원, 재활용 강화, 예산 혁신을 추진합니다.",
    )

    assert matches == ["economy-housing", "welfare-childcare", "administration"]


def test_classify_promise_returns_empty_list_without_keyword_hits() -> None:
    assert classify_promise("디지털 전환", "혁신적인 미래 전략") == []


def test_issue_keywords_match_classifiable_slugs() -> None:
    from normalization.issues.rules import ISSUE_KEYWORDS

    classifiable = _load_classifiable_slugs()
    keyword_slugs = set(ISSUE_KEYWORDS.keys())

    assert classifiable == keyword_slugs, (
        f"taxonomy.json classifiable slugs vs ISSUE_KEYWORDS mismatch — "
        f"missing: {sorted(classifiable - keyword_slugs)}, "
        f"extra: {sorted(keyword_slugs - classifiable)}"
    )


def test_all_taxonomy_slugs_exported() -> None:
    from normalization.issues.rules import ALL_TAXONOMY_SLUGS

    expected = _load_all_taxonomy_slugs()
    assert expected == set(ALL_TAXONOMY_SLUGS), (
        f"ALL_TAXONOMY_SLUGS mismatch — "
        f"missing: {sorted(expected - ALL_TAXONOMY_SLUGS)}, "
        f"extra: {sorted(ALL_TAXONOMY_SLUGS - expected)}"
    )


def test_classifiable_slugs_are_subset_of_all_slugs() -> None:
    all_slugs = _load_all_taxonomy_slugs()
    classifiable = _load_classifiable_slugs()
    assert classifiable.issubset(all_slugs)

    parent_only = all_slugs - classifiable
    for parent_slug in parent_only:
        with open(TAXONOMY_JSON, encoding="utf-8") as f:
            taxonomy = json.load(f)
        for entry in taxonomy:
            if entry["slug"] == parent_slug:
                assert len(entry.get("children", [])) > 0, (
                    f"{parent_slug} excluded from classifiable but has no children"
                )


def test_ttl_is_generated_from_taxonomy_json() -> None:
    from taxonomy.gen_ttl import generate_ttl

    ttl_path = Path(__file__).resolve().parents[1] / "taxonomy" / "issues.ttl"
    current_ttl = ttl_path.read_text(encoding="utf-8")
    expected_ttl = generate_ttl()

    assert current_ttl == expected_ttl, (
        "issues.ttl is out of sync with taxonomy.json — "
        "run `python pipeline/taxonomy/gen_ttl.py` to regenerate"
    )
