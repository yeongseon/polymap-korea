# ruff: noqa: I001,E501,SIM118
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import UniqueConstraint
from sqlalchemy.sql.schema import Table

from polymap_api.db import Base
from polymap_api.models import AuditLog, Candidacy, Claim, District, ElectionWindow, Issue, IssueRelation, Party, Person, Promise, SourceDoc

SEOUL_TZ = ZoneInfo("Asia/Seoul")


def test_all_expected_tables_registered() -> None:
    assert sorted(Base.metadata.tables) == [
        "audit_log",
        "bill_sponsorship",
        "candidacy",
        "claim",
        "committee_assignment",
        "district",
        "election",
        "election_window",
        "issue",
        "issue_relation",
        "party",
        "person",
        "promise",
        "race",
        "source_doc",
    ]


def test_model_instantiation(sample_instances: dict[str, object]) -> None:
    person = sample_instances["person"]
    race = sample_instances["race"]
    claim = sample_instances["claim"]

    assert isinstance(person, Person)
    assert isinstance(race, object)
    assert claim.__class__.__name__ == "Claim"


def test_unique_constraints_declared() -> None:
    candidacy_table = Candidacy.__table__
    issue_relation_table = IssueRelation.__table__

    assert isinstance(candidacy_table, Table)
    assert isinstance(issue_relation_table, Table)

    candidacy_constraints = {
        tuple(constraint.columns.keys())
        for constraint in candidacy_table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    issue_relation_constraints = {
        tuple(constraint.columns.keys())
        for constraint in issue_relation_table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert ("person_id", "race_id") in candidacy_constraints
    assert (
        "source_issue_id",
        "target_issue_id",
        "relation_type",
    ) in issue_relation_constraints


def test_relationship_attributes_exist() -> None:
    assert hasattr(Person, "candidacies")
    assert hasattr(Person, "committee_assignments")
    assert hasattr(Person, "bill_sponsorships")
    assert hasattr(Candidacy, "claims")
    assert hasattr(Claim, "candidacy")
    assert hasattr(District, "parent")
    assert hasattr(District, "children")
    assert hasattr(Issue, "parent")
    assert hasattr(Issue, "children")


def test_audit_log_has_no_updated_at_column() -> None:
    assert "updated_at" not in AuditLog.__table__.columns.keys()


def test_claim_uses_candidacy_foreign_key() -> None:
    claim_table = Claim.__table__

    assert "candidacy_id" in claim_table.columns.keys()
    assert "subject_person_id" not in claim_table.columns.keys()
    assert {fk.column.table.name for fk in claim_table.c.candidacy_id.foreign_keys} == {"candidacy"}


def test_issue_has_unique_slug_column() -> None:
    issue_table = Issue.__table__

    assert "slug" in issue_table.columns.keys()
    assert issue_table.c.slug.unique is True


def test_soft_delete_scope_matches_oracle_approval() -> None:
    for model in (Candidacy, Promise, Claim):
        assert "deleted_at" not in model.__table__.columns.keys()

    assert "deleted_at" in Person.__table__.columns.keys()
    assert "deleted_at" in Party.__table__.columns.keys()
    assert "deleted_at" in SourceDoc.__table__.columns.keys()


def test_election_window_normalizes_blackout_datetimes_to_seoul() -> None:
    window = ElectionWindow(
        id=uuid.uuid4(),
        election_id=uuid.uuid4(),
        content_type="poll_result",
        blackout_start=datetime(2026, 6, 2, 9, 0, 0),
        blackout_end=datetime(2026, 6, 2, 3, 0, 0, tzinfo=timezone.utc),
    )

    assert window.blackout_start.tzinfo == SEOUL_TZ
    assert window.blackout_end.tzinfo == SEOUL_TZ
    assert window.blackout_end.hour == 12
