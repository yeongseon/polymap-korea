from __future__ import annotations

import asyncio
import time


class TokenBucketRateLimiter:
    def __init__(self, rate: float, capacity: int) -> None:
        if rate <= 0:
            msg = "rate must be positive"
            raise ValueError(msg)
        if capacity <= 0:
            msg = "capacity must be positive"
            raise ValueError(msg)
        self.rate = rate
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.updated_at = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.updated_at
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.updated_at = now

    async def acquire(self, tokens: float = 1.0) -> None:
        if tokens <= 0:
            msg = "tokens must be positive"
            raise ValueError(msg)

        while True:
            async with self._lock:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                wait_time = (tokens - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
