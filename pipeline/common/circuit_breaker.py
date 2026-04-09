from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


class CircuitBreakerOpenError(RuntimeError):
    pass


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3
    state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    opened_at: datetime | None = None
    half_open_request_in_flight: bool = False

    def __post_init__(self) -> None:
        if self.failure_threshold <= 0:
            msg = "failure_threshold must be positive"
            raise ValueError(msg)
        if self.recovery_timeout <= 0:
            msg = "recovery_timeout must be positive"
            raise ValueError(msg)
        if self.success_threshold <= 0:
            msg = "success_threshold must be positive"
            raise ValueError(msg)

    def allow_request(self) -> None:
        now = datetime.now(timezone.utc)
        if self.state is CircuitState.OPEN:
            if self.opened_at is None:
                self.opened_at = now
            if now - self.opened_at >= timedelta(seconds=self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                self.consecutive_successes = 0
                self.half_open_request_in_flight = False
            else:
                raise CircuitBreakerOpenError("circuit breaker is open")

        if self.state is CircuitState.HALF_OPEN:
            if self.half_open_request_in_flight:
                raise CircuitBreakerOpenError("circuit breaker is half-open")
            self.half_open_request_in_flight = True

    def record_success(self) -> None:
        if self.state is CircuitState.HALF_OPEN:
            self.consecutive_successes += 1
            self.half_open_request_in_flight = False
            if self.consecutive_successes >= self.success_threshold:
                self._close()
            return

        self.consecutive_failures = 0
        self.consecutive_successes = 0

    def record_failure(self) -> None:
        self.half_open_request_in_flight = False
        if self.state is CircuitState.HALF_OPEN:
            self._open()
            return

        self.consecutive_failures += 1
        self.consecutive_successes = 0
        if self.consecutive_failures >= self.failure_threshold:
            self._open()

    def _open(self) -> None:
        self.state = CircuitState.OPEN
        self.opened_at = datetime.now(timezone.utc)
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.half_open_request_in_flight = False

    def _close(self) -> None:
        self.state = CircuitState.CLOSED
        self.opened_at = None
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.half_open_request_in_flight = False
