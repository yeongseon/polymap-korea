from __future__ import annotations

from polymap_ontology.enums import (
    BillStatus,
    CandidacyStatus,
    ClaimType,
    ElectionPhase,
    ElectionType,
    Gender,
    IssueRelationType,
    PositionType,
    SourceDocKind,
)


def test_gender_values_are_stable() -> None:
    assert {member.value for member in Gender} == {"male", "female", "other"}


def test_election_related_enum_values_are_stable() -> None:
    assert ElectionType.LOCAL_GENERAL.value == "local_general"
    assert ElectionPhase.ELECTION_DAY.value == "election_day"
    assert PositionType.PROPORTIONAL_COUNCIL.value == "proportional_council"
    assert CandidacyStatus.DISQUALIFIED.value == "disqualified"


def test_source_and_issue_enum_membership() -> None:
    assert SourceDocKind("news_article") is SourceDocKind.NEWS_ARTICLE
    assert IssueRelationType("related") is IssueRelationType.RELATED
    assert ClaimType("ai_summary") is ClaimType.AI_SUMMARY
    assert BillStatus("passed") is BillStatus.PASSED
