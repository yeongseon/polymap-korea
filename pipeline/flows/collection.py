from __future__ import annotations

import logging
from typing import Any

from prefect import flow, task

from common.base_adapter import RawRecord
from common.circuit_breaker import CircuitBreakerOpenError
from sources.assembly.adapter import AssemblyAdapter
from sources.local_council.adapter import LocalCouncilAdapter
from sources.nec.adapter import NecAdapter

logger = logging.getLogger(__name__)


@task(retries=2, retry_delay_seconds=30)
async def fetch_nec_election_codes(adapter: NecAdapter) -> list[RawRecord]:
    return await adapter.fetch_election_codes()


@task(retries=2, retry_delay_seconds=30)
async def fetch_nec_candidates(
    adapter: NecAdapter, sg_id: str, sg_typecode: str,
) -> list[RawRecord]:
    return await adapter.fetch_candidates(sg_id, sg_typecode)


@task(retries=2, retry_delay_seconds=30)
async def fetch_nec_pledges(
    adapter: NecAdapter, sg_id: str, sg_typecode: str,
) -> list[RawRecord]:
    return await adapter.fetch_pledges(sg_id, sg_typecode)


@task(retries=2, retry_delay_seconds=30)
async def fetch_nec_party_policies(adapter: NecAdapter, sg_id: str) -> list[RawRecord]:
    return await adapter.fetch_party_policies(sg_id)


@task(retries=2, retry_delay_seconds=30)
async def fetch_nec_resignations(adapter: NecAdapter, sg_id: str) -> list[RawRecord]:
    return await adapter.fetch_candidate_resignations(sg_id)


@task(retries=2, retry_delay_seconds=30)
async def fetch_assembly_members(adapter: AssemblyAdapter) -> list[RawRecord]:
    return await adapter.fetch_members()


@task(retries=2, retry_delay_seconds=30)
async def fetch_assembly_bills(adapter: AssemblyAdapter, member_name: str) -> list[RawRecord]:
    return await adapter.fetch_bills(member_name)


@task(retries=2, retry_delay_seconds=30)
async def fetch_assembly_votes(adapter: AssemblyAdapter, bill_id: str) -> list[RawRecord]:
    return await adapter.fetch_votes(bill_id)


@task(retries=2, retry_delay_seconds=30)
async def fetch_assembly_committee_activities(
    adapter: AssemblyAdapter, member_name: str,
) -> list[RawRecord]:
    return await adapter.fetch_committee_activities(member_name)


@task(retries=2, retry_delay_seconds=30)
async def fetch_local_council_members(
    adapter: LocalCouncilAdapter, council_code: str,
) -> list[RawRecord]:
    return await adapter.fetch_council_members(council_code)


@task(retries=2, retry_delay_seconds=30)
async def fetch_local_council_bills(
    adapter: LocalCouncilAdapter, council_code: str,
) -> list[RawRecord]:
    return await adapter.fetch_council_bills(council_code)


@flow(name="collect-nec-data")
async def collect_nec_data(
    election_id: str, sg_typecode: str = "2",
) -> dict[str, list[RawRecord]]:
    adapter = NecAdapter()
    try:
        codes = await fetch_nec_election_codes(adapter)
        candidates = await fetch_nec_candidates(adapter, election_id, sg_typecode)
        pledges = await fetch_nec_pledges(adapter, election_id, sg_typecode)
        party_policies = await fetch_nec_party_policies(adapter, election_id)
        resignations = await fetch_nec_resignations(adapter, election_id)
    except CircuitBreakerOpenError:
        logger.error("NEC circuit breaker open — skipping collection")
        return {"codes": [], "candidates": [], "pledges": [], "party_policies": [],
                "resignations": []}
    finally:
        await adapter.aclose()

    return {
        "codes": codes,
        "candidates": candidates,
        "pledges": pledges,
        "party_policies": party_policies,
        "resignations": resignations,
    }


@flow(name="collect-assembly-data")
async def collect_assembly_data() -> dict[str, list[RawRecord]]:
    adapter = AssemblyAdapter()
    members: list[RawRecord] = []
    all_bills: list[RawRecord] = []
    all_votes: list[RawRecord] = []
    all_committees: list[RawRecord] = []
    try:
        members = await fetch_assembly_members(adapter)
        for member_record in members:
            if not isinstance(member_record.data, dict):
                continue
            name = str(member_record.data.get("HG_NM", "")).strip()
            if not name:
                continue
            try:
                bills = await fetch_assembly_bills(adapter, name)
                all_bills.extend(bills)
                for bill_record in bills:
                    if not isinstance(bill_record.data, dict):
                        continue
                    bill_id = str(bill_record.data.get("BILL_ID", "")).strip()
                    if not bill_id:
                        continue
                    try:
                        all_votes.extend(await fetch_assembly_votes(adapter, bill_id))
                    except CircuitBreakerOpenError:
                        logger.warning("Circuit breaker open during assembly vote fetch for %s", bill_id)
                        break
                all_committees.extend(await fetch_assembly_committee_activities(adapter, name))
            except CircuitBreakerOpenError:
                logger.warning("Circuit breaker open during assembly detail fetch for %s", name)
                break
    except CircuitBreakerOpenError:
        logger.error("Assembly circuit breaker open — skipping collection")
        return {"members": [], "bills": [], "votes": [], "committees": []}
    finally:
        await adapter.aclose()

    return {
        "members": members,
        "bills": all_bills,
        "votes": all_votes,
        "committees": all_committees,
    }


@flow(name="collect-local-council-data")
async def collect_local_council_data(
    council_codes: list[str] | None = None,
) -> dict[str, list[RawRecord]]:
    if council_codes is None:
        council_codes = []
    adapter = LocalCouncilAdapter()
    all_members: list[RawRecord] = []
    all_bills: list[RawRecord] = []
    try:
        for code in council_codes:
            try:
                members = await fetch_local_council_members(adapter, code)
                all_members.extend(members)
                bills = await fetch_local_council_bills(adapter, code)
                all_bills.extend(bills)
            except CircuitBreakerOpenError:
                logger.error("Local council circuit breaker open for %s — skipping", code)
                break
    finally:
        await adapter.aclose()

    return {"members": all_members, "bills": all_bills}


@flow(name="collect-all")
async def collect_all(
    election_id: str,
    sg_typecode: str = "2",
    council_codes: list[str] | None = None,
) -> dict[str, Any]:
    nec_result = await collect_nec_data(election_id, sg_typecode)
    assembly_result = await collect_assembly_data()
    council_result = await collect_local_council_data(council_codes)
    return {
        "nec": nec_result,
        "assembly": assembly_result,
        "local_council": council_result,
    }
