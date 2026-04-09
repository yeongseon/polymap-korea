from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from polymap_api.schemas.bill import BillSponsorshipCreate, BillSponsorshipRead
from polymap_api.schemas.candidacy import CandidacyCreate, CandidacyRead
from polymap_api.schemas.claim import ClaimCreate, ClaimRead
from polymap_api.schemas.committee import CommitteeAssignmentCreate, CommitteeAssignmentRead
from polymap_api.schemas.district import DistrictCreate, DistrictRead
from polymap_api.schemas.election import ElectionCreate, ElectionRead
from polymap_api.schemas.issue import IssueCreate, IssueRead, IssueRelationCreate, IssueRelationRead
from polymap_api.schemas.party import PartyCreate, PartyRead
from polymap_api.schemas.person import PersonCreate, PersonRead
from polymap_api.schemas.promise import PromiseCreate, PromiseRead
from polymap_api.schemas.race import RaceCreate, RaceRead
from polymap_api.schemas.source_doc import SourceDocCreate, SourceDocRead
from polymap_ontology.enums import (
    BillStatus,
    CandidacyStatus,
    ClaimType,
    ElectionType,
    Gender,
    IssueRelationType,
    PositionType,
    SourceDocKind,
)


def test_create_schemas_accept_valid_data() -> None:
    person_id = uuid.uuid4()
    race_id = uuid.uuid4()
    issue_id = uuid.uuid4()

    assert PersonCreate(name_ko="홍길동", gender=Gender.MALE).name_ko == "홍길동"
    assert PartyCreate(name_ko="미래당", color="#00AAFF").color == "#00AAFF"
    assert ElectionCreate(
        name="2026 Local General Election",
        election_type=ElectionType.LOCAL_GENERAL,
        election_date=date(2026, 6, 3),
    ).election_type is ElectionType.LOCAL_GENERAL
    assert DistrictCreate(name="Seoul", code="11", level="시도").code == "11"
    assert RaceCreate(
        election_id=uuid.uuid4(),
        district_id=uuid.uuid4(),
        position_type=PositionType.MAYOR,
    ).seat_count == 1
    assert CandidacyCreate(person_id=person_id, race_id=race_id).status is CandidacyStatus.REGISTERED
    assert PromiseCreate(candidacy_id=uuid.uuid4(), title="Transit").title == "Transit"
    assert SourceDocCreate(kind=SourceDocKind.PDF, title="Manifesto").kind is SourceDocKind.PDF
    assert ClaimCreate(
        candidacy_id=uuid.uuid4(),
        source_doc_id=uuid.uuid4(),
        claim_type=ClaimType.OFFICIAL_FACT,
        content="Fact",
    ).claim_type is ClaimType.OFFICIAL_FACT
    assert IssueCreate(name="Housing", slug="housing").slug == "housing"
    assert IssueRelationCreate(
        source_issue_id=issue_id,
        target_issue_id=uuid.uuid4(),
        relation_type=IssueRelationType.RELATED,
    ).relation_type is IssueRelationType.RELATED
    assert CommitteeAssignmentCreate(person_id=uuid.uuid4(), committee_name="Budget").committee_name == "Budget"
    assert BillSponsorshipCreate(person_id=uuid.uuid4(), bill_name="Transit Act", status=BillStatus.PROPOSED).status is BillStatus.PROPOSED


@pytest.mark.parametrize(
    ("schema_cls", "payload"),
    [
        (PersonCreate, {"name_ko": "홍길동", "gender": "bad"}),
        (PartyCreate, {"name_ko": "미래당", "color": "blue"}),
        (ElectionCreate, {"name": "Election", "election_type": "bad", "election_date": "2026-06-03"}),
        (RaceCreate, {"election_id": str(uuid.uuid4()), "district_id": str(uuid.uuid4()), "position_type": "mayor", "seat_count": 0}),
        (ClaimCreate, {"candidacy_id": str(uuid.uuid4()), "source_doc_id": str(uuid.uuid4()), "claim_type": "bad", "content": "Fact"}),
    ],
)
def test_invalid_schema_data_rejected(schema_cls: type[object], payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        schema_cls(**payload)


def test_read_schemas_support_from_attributes() -> None:
    now = datetime.now(timezone.utc)

    @dataclass
    class PersonObj:
        id: uuid.UUID
        name_ko: str
        name_en: str | None
        birth_date: date | None
        gender: Gender | None
        bio: str | None
        photo_url: str | None
        created_at: datetime
        updated_at: datetime
        deleted_at: datetime | None

    for schema_cls in [
        PersonRead,
        PartyRead,
        ElectionRead,
        DistrictRead,
        RaceRead,
        CandidacyRead,
        PromiseRead,
        SourceDocRead,
        ClaimRead,
        IssueRead,
        IssueRelationRead,
        CommitteeAssignmentRead,
        BillSponsorshipRead,
    ]:
        assert schema_cls.model_config.get("from_attributes") is True

    person = PersonObj(
        id=uuid.uuid4(),
        name_ko="홍길동",
        name_en=None,
        birth_date=None,
        gender=Gender.MALE,
        bio=None,
        photo_url=None,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )

    assert PersonRead.model_validate(person).id == person.id
