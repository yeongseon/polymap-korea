from __future__ import annotations

from typing import Any

from common.base_adapter import BaseAdapter, RawRecord


class LocalCouncilAdapter(BaseAdapter):
    source_system = "local_council"

    async def fetch(self, **params: Any) -> list[RawRecord]:
        record = RawRecord(
            source_system=self.source_system,
            endpoint="meeting-records",
            request_params=params,
            license_note="Subject to local council publication rules.",
            election_phase="pre-election",
            data={"items": []},
        )
        record.compute_hash()
        return [record]

    async def health_check(self) -> bool:
        return True
