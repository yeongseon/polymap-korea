from __future__ import annotations

from datetime import datetime, timezone

import pytest

from common.base_adapter import RawRecord
from flows.collection import collect_assembly_data
from flows.normalization import normalize_and_resolve_all


def _make_record(source: str, endpoint: str, data: dict, request_params: dict | None = None) -> RawRecord:
    record = RawRecord(
        source_system=source,
        endpoint=endpoint,
        request_params=request_params or {},
        fetched_at=datetime.now(timezone.utc),
        http_status=200,
        data=data,
    )
    record.compute_hash()
    return record


def test_normalize_and_resolve_all_cross_source() -> None:
    results = normalize_and_resolve_all(
        {
            "nec": [
                _make_record(
                    "nec",
                    "PofelcddInfoInqireService/getPofelcddRegistSttusInfoInqire",
                    {
                        "hanglNm": "홍길동",
                        "birthday": "19800115",
                        "sgId": "20260603",
                        "sgTypecode": "2",
                        "sdName": "서울특별시",
                        "wiwName": "종로구",
                        "giho": "1",
                        "jdName": "무소속",
                    },
                ),
            ],
            "assembly": [
                _make_record(
                    "assembly",
                    "ALLNAMEMBER",
                    {
                        "HG_NM": "홍길동",
                        "ORIG_NM": "서울특별시 종로구",
                        "POLY_NM": "무소속",
                    },
                ),
            ],
            "local_council": [
                _make_record(
                    "local_council",
                    "openapi/localCouncil/memberInfo.do",
                    {
                        "member_name": "홍길동",
                        "district": "서울특별시 종로구",
                        "party": "무소속",
                    },
                    {"councilCode": "SEOUL"},
                ),
            ],
        },
    )

    assert len(results["normalized"]["nec"]) == 3
    assert len(results["normalized"]["assembly"]) == 1
    assert len(results["normalized"]["local_council"]) == 1
    assert len(results["resolved"]) == 1
    assert results["resolved"][0]["candidate_count"] == 3
    assert results["resolved"][0]["resolution"] == "review"
    assert results["resolved"][0]["merged_fields"]["district"] == "서울특별시 종로구"


@pytest.mark.asyncio
async def test_collect_assembly_data_fetches_details(monkeypatch: pytest.MonkeyPatch) -> None:
    members = [
        _make_record("assembly", "ALLNAMEMBER", {"HG_NM": "이재명"}),
        _make_record("assembly", "ALLNAMEMBER", {"HG_NM": "한동훈"}),
    ]
    bills_by_member = {
        "이재명": [_make_record("assembly", "BILL", {"BILL_ID": "BILL-1"})],
        "한동훈": [_make_record("assembly", "BILL", {"BILL_ID": "BILL-2"})],
    }
    votes_by_bill = {
        "BILL-1": [_make_record("assembly", "VOTE", {"BILL_ID": "BILL-1"})],
        "BILL-2": [_make_record("assembly", "VOTE", {"BILL_ID": "BILL-2"})],
    }
    committees_by_member = {
        "이재명": [_make_record("assembly", "COMMITTEEACTIVITY", {"HG_NM": "이재명"})],
        "한동훈": [_make_record("assembly", "COMMITTEEACTIVITY", {"HG_NM": "한동훈"})],
    }

    class StubAssemblyAdapter:
        async def aclose(self) -> None:
            return None

    async def fake_fetch_members(_adapter: object) -> list[RawRecord]:
        return members

    async def fake_fetch_bills(_adapter: object, member_name: str) -> list[RawRecord]:
        return bills_by_member[member_name]

    async def fake_fetch_votes(_adapter: object, bill_id: str) -> list[RawRecord]:
        return votes_by_bill[bill_id]

    async def fake_fetch_committees(_adapter: object, member_name: str) -> list[RawRecord]:
        return committees_by_member[member_name]

    monkeypatch.setattr("flows.collection.AssemblyAdapter", StubAssemblyAdapter)
    monkeypatch.setattr("flows.collection.fetch_assembly_members", fake_fetch_members)
    monkeypatch.setattr("flows.collection.fetch_assembly_bills", fake_fetch_bills)
    monkeypatch.setattr("flows.collection.fetch_assembly_votes", fake_fetch_votes)
    monkeypatch.setattr("flows.collection.fetch_assembly_committee_activities", fake_fetch_committees)

    result = await collect_assembly_data()

    assert len(result["members"]) == 2
    assert len(result["bills"]) == 2
    assert len(result["votes"]) == 2
    assert len(result["committees"]) == 2
