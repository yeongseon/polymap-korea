from __future__ import annotations

import re
from datetime import date

from .value_objects import DateRange

ELECTION_DATE_2026 = date(2026, 6, 3)
_HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


def ensure_election_date_2026(value: date) -> date:
    """Validate the fixed v1 election date used across demo-era contracts."""

    if value != ELECTION_DATE_2026:
        msg = f"expected election date {ELECTION_DATE_2026.isoformat()}"
        raise ValueError(msg)
    return value


def ensure_hex_color(value: str) -> str:
    """Validate canonical party color values before they reach storage or DTOs."""

    if not _HEX_COLOR_PATTERN.fullmatch(value):
        msg = "expected a #RRGGBB color value"
        raise ValueError(msg)
    return value


def ensure_date_range(start_date: date, end_date: date | None) -> DateRange:
    """Create an immutable date range value object with shared bound checks."""

    return DateRange(start_date=start_date, end_date=end_date)
