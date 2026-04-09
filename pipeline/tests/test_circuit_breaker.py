from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from common.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)


def test_initial_state_is_closed() -> None:
    cb = CircuitBreaker()
    assert cb.state is CircuitState.CLOSED


def test_stays_closed_on_success() -> None:
    cb = CircuitBreaker(failure_threshold=3)
    cb.allow_request()
    cb.record_success()
    assert cb.state is CircuitState.CLOSED


def test_opens_after_threshold_failures() -> None:
    cb = CircuitBreaker(failure_threshold=3)
    for _ in range(3):
        cb.allow_request()
        cb.record_failure()
    assert cb.state is CircuitState.OPEN


def test_open_rejects_requests() -> None:
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
    cb.allow_request()
    cb.record_failure()
    assert cb.state is CircuitState.OPEN
    with pytest.raises(CircuitBreakerOpenError):
        cb.allow_request()


def test_transitions_to_half_open_after_timeout() -> None:
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
    cb.allow_request()
    cb.record_failure()
    assert cb.state is CircuitState.OPEN
    cb.opened_at = datetime.now(timezone.utc) - timedelta(seconds=2)
    cb.allow_request()
    assert cb.state is CircuitState.HALF_OPEN


def test_half_open_closes_after_successes() -> None:
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1, success_threshold=2)
    cb.allow_request()
    cb.record_failure()
    cb.opened_at = datetime.now(timezone.utc) - timedelta(seconds=2)
    cb.allow_request()
    assert cb.state is CircuitState.HALF_OPEN
    cb.record_success()
    assert cb.state is CircuitState.HALF_OPEN
    cb.allow_request()
    cb.record_success()
    assert cb.state is CircuitState.CLOSED


def test_half_open_reopens_on_failure() -> None:
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
    cb.allow_request()
    cb.record_failure()
    cb.opened_at = datetime.now(timezone.utc) - timedelta(seconds=2)
    cb.allow_request()
    assert cb.state is CircuitState.HALF_OPEN
    cb.record_failure()
    assert cb.state is CircuitState.OPEN


def test_half_open_rejects_concurrent_requests() -> None:
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
    cb.allow_request()
    cb.record_failure()
    cb.opened_at = datetime.now(timezone.utc) - timedelta(seconds=2)
    cb.allow_request()
    assert cb.state is CircuitState.HALF_OPEN
    with pytest.raises(CircuitBreakerOpenError):
        cb.allow_request()


def test_success_resets_failure_counter() -> None:
    cb = CircuitBreaker(failure_threshold=3)
    cb.allow_request()
    cb.record_failure()
    cb.allow_request()
    cb.record_failure()
    assert cb.consecutive_failures == 2
    cb.allow_request()
    cb.record_success()
    assert cb.consecutive_failures == 0
    cb.allow_request()
    cb.record_failure()
    assert cb.consecutive_failures == 1
    assert cb.state is CircuitState.CLOSED


def test_invalid_configuration() -> None:
    with pytest.raises(ValueError, match="failure_threshold"):
        CircuitBreaker(failure_threshold=0)
    with pytest.raises(ValueError, match="recovery_timeout"):
        CircuitBreaker(recovery_timeout=-1)
    with pytest.raises(ValueError, match="success_threshold"):
        CircuitBreaker(success_threshold=0)
