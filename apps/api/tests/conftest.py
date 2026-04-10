# ruff: noqa: I001,TC003,E501
from __future__ import annotations

import uuid
from collections.abc import AsyncIterator, Iterator
from datetime import date, datetime, timezone

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from polymap_api.db import Base
from polymap_api.config import settings
from polymap_api.deps import get_db
from polymap_api.main import app
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


@pytest.fixture(autouse=True)
def configure_admin_api_key() -> Iterator[str]:
    original_key = settings.admin_api_key
    settings.admin_api_key = "test-admin-key"
    try:
        yield settings.admin_api_key
    finally:
        settings.admin_api_key = original_key


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
        is_legally_restricted=False,
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


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[httpx.AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seeded_db(
    db_session: AsyncSession,
    sample_ids: dict[str, uuid.UUID],
) -> dict[str, uuid.UUID]:
    district_parent = District(
        id=sample_ids["district_parent"],
        name_ko="서울특별시",
        code="11",
        level="metropolitan",
        parent_id=None,
    )
    district = District(
        id=sample_ids["district"],
        name_ko="종로구",
        code="11110",
        level="basic",
        parent_id=sample_ids["district_parent"],
    )
    election = Election(
        id=sample_ids["election"],
        name="2026 Local General Election",
        election_type=ElectionType.LOCAL_GENERAL,
        election_date=date(2026, 6, 3),
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
    second_person_id = uuid.uuid4()
    second_person = Person(
        id=second_person_id,
        name_ko="김후보",
        name_en="Kim Candidate",
        birth_date=date(1985, 5, 5),
        gender=Gender.FEMALE,
    )
    party = Party(
        id=sample_ids["party"],
        name_ko="미래당",
        abbreviation="MD",
        color="#123ABC",
    )
    second_party_id = uuid.uuid4()
    second_party = Party(
        id=second_party_id,
        name_ko="정의당",
        abbreviation="JD",
        color="#FFCC00",
    )
    candidacy = Candidacy(
        id=sample_ids["candidacy"],
        person_id=sample_ids["person"],
        race_id=sample_ids["race"],
        party_id=sample_ids["party"],
        status=CandidacyStatus.REGISTERED,
        candidate_number=1,
    )
    second_candidacy_id = uuid.uuid4()
    second_candidacy = Candidacy(
        id=second_candidacy_id,
        person_id=second_person_id,
        race_id=sample_ids["race"],
        party_id=second_party_id,
        status=CandidacyStatus.REGISTERED,
        candidate_number=2,
    )
    source_doc = SourceDoc(
        id=sample_ids["source_doc"],
        kind=SourceDocKind.NEWS_ARTICLE,
        title="Candidate Interview",
        published_at=datetime.now(timezone.utc),
    )
    issue_parent = Issue(
        id=sample_ids["issue_parent"],
        name="Housing",
        slug="housing",
        parent_id=None,
    )
    issue = Issue(
        id=sample_ids["issue"],
        name="Transit",
        slug="transit",
        parent_id=sample_ids["issue_parent"],
    )
    promise = Promise(
        id=sample_ids["promise"],
        candidacy_id=sample_ids["candidacy"],
        title="Transit expansion",
        body="Expand subway service in central Seoul",
        issue_id=sample_ids["issue"],
        source_doc_id=sample_ids["source_doc"],
        sort_order=1,
    )
    claim = Claim(
        id=sample_ids["claim"],
        candidacy_id=sample_ids["candidacy"],
        source_doc_id=sample_ids["source_doc"],
        claim_type=ClaimType.SOURCED_CLAIM,
        is_legally_restricted=False,
        content="Will add new subway lines.",
    )
    restricted_claim = Claim(
        id=uuid.uuid4(),
        candidacy_id=sample_ids["candidacy"],
        source_doc_id=sample_ids["source_doc"],
        claim_type=ClaimType.DISPUTED,
        is_legally_restricted=True,
        content="Polling lead widened to 10 points.",
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

    db_session.add_all(
        [
            district_parent,
            district,
            election,
            race,
            person,
            second_person,
            party,
            second_party,
            candidacy,
            second_candidacy,
            source_doc,
            issue_parent,
            issue,
            promise,
            claim,
            restricted_claim,
            committee_assignment,
            bill_sponsorship,
        ]
    )
    await db_session.commit()

    return {
        **sample_ids,
        "candidacy_two": second_candidacy_id,
        "party_two": second_party_id,
        "person_two": second_person_id,
    }
