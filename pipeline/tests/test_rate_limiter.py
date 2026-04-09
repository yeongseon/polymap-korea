import pytest

from common.rate_limiter import TokenBucketRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_acquire() -> None:
    limiter = TokenBucketRateLimiter(rate=10.0, capacity=2)
    await limiter.acquire()
    await limiter.acquire()
    assert limiter.tokens <= 1.0
