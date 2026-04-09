from __future__ import annotations

from datetime import date

import pytest

from polymap_ontology.constraints import (
    ELECTION_DATE_2026,
    ensure_date_range,
    ensure_election_date_2026,
    ensure_hex_color,
)


def test_ensure_election_date_accepts_2026_local_election_day() -> None:
    assert ensure_election_date_2026(ELECTION_DATE_2026) == date(2026, 6, 3)


def test_ensure_election_date_rejects_other_dates() -> None:
    with pytest.raises(ValueError, match="expected election date"):
        ensure_election_date_2026(date(2026, 6, 4))


def test_ensure_hex_color_accepts_valid_hex_triplets() -> None:
    assert ensure_hex_color("#12AbEf") == "#12AbEf"


def test_ensure_hex_color_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="#RRGGBB"):
        ensure_hex_color("123456")


def test_ensure_date_range_accepts_equal_bounds() -> None:
    date_range = ensure_date_range(date(2026, 5, 1), date(2026, 5, 1))
    assert date_range.start_date == date_range.end_date


def test_ensure_date_range_rejects_reversed_bounds() -> None:
    with pytest.raises(ValueError, match="start_date"):
        ensure_date_range(date(2026, 6, 1), date(2026, 5, 31))
