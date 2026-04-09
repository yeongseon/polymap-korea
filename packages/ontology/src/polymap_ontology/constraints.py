from __future__ import annotations

import re
from datetime import date

from .value_objects import DateRange

ELECTION_DATE_2026 = date(2026, 6, 3)
_HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


def ensure_election_date_2026(value: date) -> date:
    if value != ELECTION_DATE_2026:
        msg = f"expected election date {ELECTION_DATE_2026.isoformat()}"
        raise ValueError(msg)
    return value


def ensure_hex_color(value: str) -> str:
    if not _HEX_COLOR_PATTERN.fullmatch(value):
        msg = "expected a #RRGGBB color value"
        raise ValueError(msg)
    return value


def ensure_date_range(start_date: date, end_date: date | None) -> DateRange:
    return DateRange(start_date=start_date, end_date=end_date)
