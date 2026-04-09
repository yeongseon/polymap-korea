from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from common.base_adapter import RawRecord

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    field: str
    message: str
    raw_value: Any = None


@dataclass
class NormalizedResult:
    entity_type: str
    data: dict[str, Any]
    source_record: RawRecord
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


class BaseNormalizer(ABC):
    @abstractmethod
    def normalize(self, records: list[RawRecord]) -> list[NormalizedResult]:
        ...

    def _validate_required(
        self, data: dict[str, Any], required_fields: list[str],
    ) -> list[ValidationError]:
        errors: list[ValidationError] = []
        for f in required_fields:
            if not data.get(f):
                errors.append(ValidationError(field=f, message=f"Missing required field: {f}"))
        return errors

    def _safe_date(self, value: str | None) -> date | None:
        if not value:
            return None
        value = value.strip()
        for fmt in ("%Y%m%d", "%Y-%m-%d", "%Y.%m.%d"):
            try:
                return date.fromisoformat(value) if fmt == "%Y-%m-%d" else _parse_date(value, fmt)
            except (ValueError, TypeError):
                continue
        logger.warning("Could not parse date: %s", value)
        return None

    def _clean_string(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()


def _parse_date(value: str, fmt: str) -> date:
    from datetime import datetime as dt

    return dt.strptime(value, fmt).date()


class NecNormalizer(BaseNormalizer):
    """Transforms NEC API responses into Person, Candidacy, Party domain dicts."""

    def normalize(self, records: list[RawRecord]) -> list[NormalizedResult]:
        results: list[NormalizedResult] = []
        for record in records:
            if not isinstance(record.data, dict):
                continue
            endpoint = record.endpoint
            if "PofelcddInfoInqire" in endpoint:
                results.extend(self._normalize_candidate(record))
            elif "ElecPrmsInfoInqire" in endpoint:
                results.extend(self._normalize_pledge(record))
            elif "PartyPlcInfoInqire" in endpoint:
                results.extend(self._normalize_party_policy(record))
            elif "CommonCodeService" in endpoint:
                results.extend(self._normalize_election_code(record))
            elif "CndaRegInvdInqire" in endpoint:
                results.extend(self._normalize_resignation(record))
        return results

    def _normalize_candidate(self, record: RawRecord) -> list[NormalizedResult]:
        data = record.data
        assert isinstance(data, dict)
        person_data: dict[str, Any] = {
            "name": self._clean_string(data.get("name") or data.get("hanglNm")),
            "birth_date": self._safe_date(
                self._clean_string(data.get("birthday") or data.get("brthday")),
            ),
            "gender": self._clean_string(data.get("giho") or data.get("gender")),
        }
        candidacy_data: dict[str, Any] = {
            "person_name": person_data["name"],
            "election_id": self._clean_string(data.get("sgId")),
            "election_type": self._clean_string(data.get("sgTypecode")),
            "district_name": self._clean_string(data.get("sdName") or data.get("wiwName")),
            "party_name": self._clean_string(data.get("jdName")),
            "candidate_number": self._clean_string(data.get("giho")),
            "status": self._clean_string(data.get("status") or "registered"),
        }
        errors = self._validate_required(person_data, ["name"])
        results = [
            NormalizedResult(
                entity_type="person",
                data=person_data,
                source_record=record,
                errors=errors,
            ),
        ]
        candidacy_errors = self._validate_required(candidacy_data, ["person_name", "election_id"])
        results.append(
            NormalizedResult(
                entity_type="candidacy",
                data=candidacy_data,
                source_record=record,
                errors=candidacy_errors,
            ),
        )
        if candidacy_data["party_name"]:
            results.append(
                NormalizedResult(
                    entity_type="party",
                    data={
                        "name": candidacy_data["party_name"],
                        "abbreviation": "",
                    },
                    source_record=record,
                ),
            )
        return results

    def _normalize_pledge(self, record: RawRecord) -> list[NormalizedResult]:
        data = record.data
        assert isinstance(data, dict)
        pledge_data: dict[str, Any] = {
            "person_name": self._clean_string(data.get("cnddtNm") or data.get("name")),
            "election_id": self._clean_string(data.get("sgId")),
            "title": self._clean_string(data.get("prmsTitle") or data.get("title")),
            "content": self._clean_string(data.get("prmsContent") or data.get("content")),
            "category": self._clean_string(data.get("prmsOrd") or data.get("category")),
        }
        errors = self._validate_required(pledge_data, ["person_name", "title"])
        return [
            NormalizedResult(
                entity_type="promise",
                data=pledge_data,
                source_record=record,
                errors=errors,
            ),
        ]

    def _normalize_party_policy(self, record: RawRecord) -> list[NormalizedResult]:
        data = record.data
        assert isinstance(data, dict)
        policy_data: dict[str, Any] = {
            "party_name": self._clean_string(data.get("jdName")),
            "election_id": self._clean_string(data.get("sgId")),
            "title": self._clean_string(data.get("prmsCont") or data.get("title")),
            "content": self._clean_string(data.get("content") or ""),
        }
        errors = self._validate_required(policy_data, ["party_name"])
        return [
            NormalizedResult(
                entity_type="party_policy",
                data=policy_data,
                source_record=record,
                errors=errors,
            ),
        ]

    def _normalize_election_code(self, record: RawRecord) -> list[NormalizedResult]:
        data = record.data
        assert isinstance(data, dict)
        code_data: dict[str, Any] = {
            "code": self._clean_string(data.get("sgId")),
            "name": self._clean_string(data.get("sgName")),
            "type_code": self._clean_string(data.get("sgTypecode")),
        }
        return [
            NormalizedResult(
                entity_type="election_code",
                data=code_data,
                source_record=record,
            ),
        ]

    def _normalize_resignation(self, record: RawRecord) -> list[NormalizedResult]:
        data = record.data
        assert isinstance(data, dict)
        resignation_data: dict[str, Any] = {
            "person_name": self._clean_string(data.get("cnddtNm") or data.get("name")),
            "election_id": self._clean_string(data.get("sgId")),
            "reason": self._clean_string(data.get("reason") or ""),
            "date": self._safe_date(self._clean_string(data.get("date") or "")),
        }
        return [
            NormalizedResult(
                entity_type="candidacy_update",
                data=resignation_data,
                source_record=record,
            ),
        ]


class AssemblyNormalizer(BaseNormalizer):
    """Transforms Assembly API responses into BillSponsorship, CommitteeAssignment dicts."""

    def normalize(self, records: list[RawRecord]) -> list[NormalizedResult]:
        results: list[NormalizedResult] = []
        for record in records:
            if not isinstance(record.data, dict):
                continue
            endpoint = record.endpoint
            if endpoint == "ALLNAMEMBER":
                results.extend(self._normalize_member(record))
            elif endpoint == "BILL":
                results.extend(self._normalize_bill(record))
            elif endpoint == "VOTE":
                results.extend(self._normalize_vote(record))
            elif endpoint == "COMMITTEEACTIVITY":
                results.extend(self._normalize_committee(record))
        return results

    def _normalize_member(self, record: RawRecord) -> list[NormalizedResult]:
        data = record.data
        assert isinstance(data, dict)
        member_data: dict[str, Any] = {
            "name": self._clean_string(data.get("HG_NM") or data.get("MONA_NM")),
            "party_name": self._clean_string(data.get("POLY_NM")),
            "district_name": self._clean_string(data.get("ORIG_NM")),
            "committee": self._clean_string(data.get("CMITS")),
            "elected_count": self._clean_string(data.get("REELE_GBN_NM")),
        }
        errors = self._validate_required(member_data, ["name"])
        return [
            NormalizedResult(
                entity_type="person",
                data=member_data,
                source_record=record,
                errors=errors,
            ),
        ]

    def _normalize_bill(self, record: RawRecord) -> list[NormalizedResult]:
        data = record.data
        assert isinstance(data, dict)
        bill_data: dict[str, Any] = {
            "bill_id": self._clean_string(data.get("BILL_ID")),
            "bill_name": self._clean_string(data.get("BILL_NM") or data.get("BILL_NAME")),
            "proposer": self._clean_string(data.get("PROPOSER")),
            "propose_date": self._safe_date(self._clean_string(data.get("PROPOSE_DT"))),
            "status": self._clean_string(data.get("PROC_RESULT_CD") or data.get("RGS_PROC_RESULT_NM")),
            "committee": self._clean_string(data.get("COMMITTEE") or data.get("CURR_COMMITTEE")),
        }
        errors = self._validate_required(bill_data, ["bill_id", "bill_name"])
        return [
            NormalizedResult(
                entity_type="bill_sponsorship",
                data=bill_data,
                source_record=record,
                errors=errors,
            ),
        ]

    def _normalize_vote(self, record: RawRecord) -> list[NormalizedResult]:
        data = record.data
        assert isinstance(data, dict)
        vote_data: dict[str, Any] = {
            "bill_id": self._clean_string(data.get("BILL_ID")),
            "member_name": self._clean_string(data.get("HG_NM")),
            "party_name": self._clean_string(data.get("POLY_NM")),
            "vote_result": self._clean_string(data.get("RESULT_VOTE_MOD")),
        }
        return [
            NormalizedResult(
                entity_type="vote_record",
                data=vote_data,
                source_record=record,
            ),
        ]

    def _normalize_committee(self, record: RawRecord) -> list[NormalizedResult]:
        data = record.data
        assert isinstance(data, dict)
        committee_data: dict[str, Any] = {
            "member_name": self._clean_string(data.get("HG_NM")),
            "committee_name": self._clean_string(data.get("CMIT_NM") or data.get("COMMITTEE")),
            "position": self._clean_string(data.get("BLNG_CMIT_NM") or ""),
        }
        errors = self._validate_required(committee_data, ["member_name", "committee_name"])
        return [
            NormalizedResult(
                entity_type="committee_assignment",
                data=committee_data,
                source_record=record,
                errors=errors,
            ),
        ]
