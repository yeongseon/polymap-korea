from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

import pytest

from polymap_api.db import Base
from polymap_api.models import (
    AuditLog,
    BillSponsorship,
    Candidacy,
    Claim,
    CommitteeAssignment,
    District,
    Election,
    ElectionWindow,
    Issue,
    IssueRelation,
    Party,
    Person,
    Promise,
    Race,
    SourceDoc,
)
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


@pytest.fixture
def sample_ids() -> dict[str, uuid.UUID]:
    return {
        "audit_log": uuid.uuid4(),
        "bill_sponsorship": uuid.uuid4(),
        "candidacy": uuid.uuid4(),
        "claim": uuid.uuid4(),
        "committee_assignment": uuid.uuid4(),
        "district": uuid.uuid4(),
        "district_parent": uuid.uuid4(),
        "election": uuid.uuid4(),
        "election_window": uuid.uuid4(),
        "issue": uuid.uuid4(),
        "issue_parent": uuid.uuid4(),
        "issue_relation": uuid.uuid4(),
        "party": uuid.uuid4(),
        "person": uuid.uuid4(),
        "promise": uuid.uuid4(),
        "race": uuid.uuid4(),
        "source_doc": uuid.uuid4(),
    }


@pytest.fixture
def sample_instances(sample_ids: dict[str, uuid.UUID]) -> dict[str, object]:
    election = Election(
        id=sample_ids["election"],
        name="2026 Local General Election",
        election_type=ElectionType.LOCAL_GENERAL,
        election_date=date(2026, 6, 3),
    )
    district = District(
        id=sample_ids["district"],
        name="Seoul",
        code="11",
        level="시도",
        parent_id=sample_ids["district_parent"],
    )
    race = Race(
        id=sample_ids["race"],
        election_id=sample_ids["election"],
        district_id=sample_ids["district"],
        position_type=PositionType.MAYOR,
        seat_count=1,
    )
    person = Person(
        id=sample_ids["person"],
        name_ko="홍길동",
        name_en="Hong Gil-dong",
        birth_date=date(1980, 1, 1),
        gender=Gender.MALE,
    )
    party = Party(
        id=sample_ids["party"],
        name_ko="미래당",
        abbreviation="MD",
        color="#123ABC",
    )
    candidacy = Candidacy(
        id=sample_ids["candidacy"],
        person_id=sample_ids["person"],
        race_id=sample_ids["race"],
        party_id=sample_ids["party"],
        status=CandidacyStatus.REGISTERED,
        candidate_number=1,
    )
    source_doc = SourceDoc(
        id=sample_ids["source_doc"],
        kind=SourceDocKind.NEWS_ARTICLE,
        title="Candidate Interview",
        published_at=datetime.now(timezone.utc),
    )
    promise = Promise(
        id=sample_ids["promise"],
        candidacy_id=sample_ids["candidacy"],
        title="Transit expansion",
        source_doc_id=sample_ids["source_doc"],
    )
    claim = Claim(
        id=sample_ids["claim"],
        candidacy_id=sample_ids["candidacy"],
        source_doc_id=sample_ids["source_doc"],
        claim_type=ClaimType.SOURCED_CLAIM,
        content="Will add new subway lines.",
    )
    issue = Issue(
        id=sample_ids["issue"],
        name="Housing",
        slug="housing",
        parent_id=sample_ids["issue_parent"],
    )
    issue_relation = IssueRelation(
        id=sample_ids["issue_relation"],
        source_issue_id=sample_ids["issue"],
        target_issue_id=sample_ids["issue_parent"],
        relation_type=IssueRelationType.BROADER,
    )
    committee_assignment = CommitteeAssignment(
        id=sample_ids["committee_assignment"],
        person_id=sample_ids["person"],
        committee_name="Transport Committee",
    )
    bill_sponsorship = BillSponsorship(
        id=sample_ids["bill_sponsorship"],
        person_id=sample_ids["person"],
        bill_name="Public Transit Act",
        status=BillStatus.PROPOSED,
        is_primary_sponsor=True,
    )
    election_window = ElectionWindow(
        id=sample_ids["election_window"],
        election_id=sample_ids["election"],
        phase=ElectionPhase.CAMPAIGN,
        starts_at=datetime(2026, 5, 19, tzinfo=timezone.utc),
        ends_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
    )
    audit_log = AuditLog(
        id=sample_ids["audit_log"],
        action="create",
        entity_type="candidacy",
        entity_id=sample_ids["candidacy"],
        actor="system",
        diff={"status": "registered"},
    )

    return {
        "audit_log": audit_log,
        "base": Base,
        "bill_sponsorship": bill_sponsorship,
        "candidacy": candidacy,
        "claim": claim,
        "committee_assignment": committee_assignment,
        "district": district,
        "election": election,
        "election_window": election_window,
        "issue": issue,
        "issue_relation": issue_relation,
        "party": party,
        "person": person,
        "promise": promise,
        "race": race,
        "source_doc": source_doc,
    }
