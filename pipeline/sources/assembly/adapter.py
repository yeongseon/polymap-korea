from __future__ import annotations

from typing import Any

from common.base_adapter import BaseAdapter, RawRecord


class AssemblyAdapter(BaseAdapter):
    source_system = "assembly"

    async def fetch(self, **params: Any) -> list[RawRecord]:
        record = RawRecord(
            source_system=self.source_system,
            endpoint="member-profile",
            request_params=params,
            license_note="Subject to National Assembly data terms.",
            election_phase="pre-election",
            data={"items": []},
        )
        record.compute_hash()
        return [record]

    async def health_check(self) -> bool:
        return True
