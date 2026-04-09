from __future__ import annotations

from datetime import datetime, timezone

from common.base_adapter import RawRecord
from normalization.normalizer import (
    AssemblyNormalizer,
    LocalCouncilNormalizer,
    NecNormalizer,
)


def _make_record(source: str, endpoint: str, data: dict) -> RawRecord:
    record = RawRecord(
        source_system=source,
        endpoint=endpoint,
        request_params={},
        fetched_at=datetime.now(timezone.utc),
        http_status=200,
        data=data,
    )
    record.compute_hash()
    return record


class TestNecNormalizer:
    def test_normalize_candidate(self) -> None:
        normalizer = NecNormalizer()
        record = _make_record(
            "nec",
            "PofelcddInfoInqireService/getPofelcddRegistSttusInfoInqire",
            {
                "hanglNm": "홍길동",
                "birthday": "19800115",
                "sgId": "20260603",
                "sgTypecode": "2",
                "sdName": "서울특별시",
                "wiwName": "종로구",
                "jdName": "민주당",
                "giho": "1",
            },
        )
        results = normalizer.normalize([record])
        person_results = [r for r in results if r.entity_type == "person"]
        candidacy_results = [r for r in results if r.entity_type == "candidacy"]
        party_results = [r for r in results if r.entity_type == "party"]

        assert len(person_results) == 1
        assert person_results[0].is_valid
        assert person_results[0].data["name"] == "홍길동"
        assert person_results[0].data["district"] == "서울특별시 종로구"
        assert person_results[0].data["official_id"] == ""
        assert person_results[0].data["gender"] == ""

        assert len(candidacy_results) == 1
        assert candidacy_results[0].data["election_id"] == "20260603"
        assert candidacy_results[0].data["district_name"] == "서울특별시 종로구"

        assert len(party_results) == 1
        assert party_results[0].data["name"] == "민주당"

    def test_normalize_pledge(self) -> None:
        normalizer = NecNormalizer()
        record = _make_record(
            "nec",
            "ElecPrmsInfoInqireService/getCnddtElecPrmsInfoInqire",
            {
                "cnddtNm": "홍길동",
                "sgId": "20260603",
                "prmsTitle": "교통 인프라 확충",
                "prmsContent": "지하철 연장 추진",
                "prmsOrd": "1",
            },
        )
        results = normalizer.normalize([record])
        assert len(results) == 1
        assert results[0].entity_type == "promise"
        assert results[0].is_valid
        assert results[0].data["title"] == "교통 인프라 확충"

    def test_normalize_missing_required_field(self) -> None:
        normalizer = NecNormalizer()
        record = _make_record(
            "nec",
            "PofelcddInfoInqireService/getPofelcddRegistSttusInfoInqire",
            {"sgId": "20260603", "sgTypecode": "2"},
        )
        results = normalizer.normalize([record])
        assert len(results) == 1
        assert results[0].entity_type == "person"
        assert not results[0].is_valid
        assert any(e.field == "hanglNm OR name" for e in results[0].errors)

    def test_normalize_election_code(self) -> None:
        normalizer = NecNormalizer()
        record = _make_record(
            "nec",
            "CommonCodeService/getCommonSgCodeList",
            {"sgId": "20260603", "sgName": "제9회 지방선거", "sgTypecode": "2"},
        )
        results = normalizer.normalize([record])
        assert len(results) == 1
        assert results[0].entity_type == "election_code"
        assert results[0].data["code"] == "20260603"

    def test_normalize_party_policy(self) -> None:
        normalizer = NecNormalizer()
        record = _make_record(
            "nec",
            "PartyPlcInfoInqireService/getPartyPlcInfoInqire",
            {"jdName": "민주당", "sgId": "20260603", "prmsCont": "경제 활성화"},
        )
        results = normalizer.normalize([record])
        assert len(results) == 1
        assert results[0].entity_type == "party_policy"
        assert results[0].data["party_name"] == "민주당"

    def test_skips_non_dict_data(self) -> None:
        normalizer = NecNormalizer()
        record = RawRecord(
            source_system="nec",
            endpoint="PofelcddInfoInqireService/getPofelcddRegistSttusInfoInqire",
            request_params={},
            data="invalid string data",
        )
        results = normalizer.normalize([record])
        assert results == []


class TestAssemblyNormalizer:
    def test_normalize_member(self) -> None:
        normalizer = AssemblyNormalizer()
        record = _make_record(
            "assembly",
            "ALLNAMEMBER",
            {
                "HG_NM": "이재명",
                "POLY_NM": "더불어민주당",
                "ORIG_NM": "인천 계양구을",
                "CMITS": "법제사법위원회",
                "REELE_GBN_NM": "초선",
            },
        )
        results = normalizer.normalize([record])
        assert len(results) == 1
        assert results[0].entity_type == "person"
        assert results[0].is_valid
        assert results[0].data["name"] == "이재명"
        assert results[0].data["party_name"] == "더불어민주당"
        assert results[0].data["district"] == "인천 계양구을"

    def test_normalize_member_raw_schema_failure(self) -> None:
        normalizer = AssemblyNormalizer()
        record = _make_record("assembly", "ALLNAMEMBER", {"POLY_NM": "더불어민주당"})
        results = normalizer.normalize([record])

        assert len(results) == 1
        assert results[0].entity_type == "person"
        assert not results[0].is_valid
        assert any(e.field == "HG_NM OR MONA_NM" for e in results[0].errors)

    def test_normalize_bill(self) -> None:
        normalizer = AssemblyNormalizer()
        record = _make_record(
            "assembly",
            "BILL",
            {
                "BILL_ID": "PRC_A2B3C4D5",
                "BILL_NM": "지방자치법 개정안",
                "PROPOSER": "이재명",
                "PROPOSE_DT": "2026-01-15",
                "PROC_RESULT_CD": "계류",
                "CURR_COMMITTEE": "행정안전위원회",
            },
        )
        results = normalizer.normalize([record])
        assert len(results) == 1
        assert results[0].entity_type == "bill_sponsorship"
        assert results[0].is_valid
        assert results[0].data["bill_id"] == "PRC_A2B3C4D5"

    def test_normalize_vote(self) -> None:
        normalizer = AssemblyNormalizer()
        record = _make_record(
            "assembly",
            "VOTE",
            {
                "BILL_ID": "PRC_A2B3C4D5",
                "HG_NM": "이재명",
                "POLY_NM": "더불어민주당",
                "RESULT_VOTE_MOD": "찬성",
            },
        )
        results = normalizer.normalize([record])
        assert len(results) == 1
        assert results[0].entity_type == "vote_record"
        assert results[0].data["vote_result"] == "찬성"

    def test_normalize_committee(self) -> None:
        normalizer = AssemblyNormalizer()
        record = _make_record(
            "assembly",
            "COMMITTEEACTIVITY",
            {
                "HG_NM": "이재명",
                "CMIT_NM": "법제사법위원회",
                "BLNG_CMIT_NM": "위원",
            },
        )
        results = normalizer.normalize([record])
        assert len(results) == 1
        assert results[0].entity_type == "committee_assignment"
        assert results[0].is_valid
        assert results[0].data["committee_name"] == "법제사법위원회"

    def test_normalize_bill_missing_required(self) -> None:
        normalizer = AssemblyNormalizer()
        record = _make_record(
            "assembly",
            "BILL",
            {"PROPOSER": "이재명"},
        )
        results = normalizer.normalize([record])
        assert len(results) == 1
        assert not results[0].is_valid
        assert any(e.field == "BILL_ID" for e in results[0].errors)


class TestLocalCouncilNormalizer:
    def test_normalize_member(self) -> None:
        normalizer = LocalCouncilNormalizer()
        record = _make_record(
            "local_council",
            "openapi/localCouncil/memberInfo.do",
            {
                "member_name": "김민수",
                "party": "정의당",
                "district": "서울특별시 종로구",
                "committee": "행정재경위원회",
            },
        )
        record.request_params["councilCode"] = "SEOUL"

        results = normalizer.normalize([record])

        assert len(results) == 1
        assert results[0].entity_type == "person"
        assert results[0].is_valid
        assert results[0].data["name"] == "김민수"
        assert results[0].data["district"] == "서울특별시 종로구"
        assert results[0].data["official_id"] == "SEOUL_김민수"
