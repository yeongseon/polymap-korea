from __future__ import annotations

from normalization.issues import classify_promise


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
