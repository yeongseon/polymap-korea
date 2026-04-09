from __future__ import annotations

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RawRecord:
    source_system: str
    endpoint: str
    request_params: dict[str, Any]
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    http_status: int = 200
    response_hash: str = ""
    license_note: str = ""
    election_phase: str = ""
    public_expiry_at: datetime | None = None
    data: dict[str, Any] | str = field(default_factory=dict)

    def compute_hash(self) -> str:
        if isinstance(self.data, dict):
            content = json.dumps(self.data, sort_keys=True, ensure_ascii=False).encode("utf-8")
        else:
            content = self.data.encode("utf-8")
        self.response_hash = hashlib.sha256(content).hexdigest()
        return self.response_hash


class BaseAdapter(ABC):
    source_system: str = ""
    max_retries: int = 3
    base_delay: float = 1.0

    @abstractmethod
    async def fetch(self, **params: Any) -> list[RawRecord]:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
