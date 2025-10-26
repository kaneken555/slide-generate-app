from __future__ import annotations
import anyio, random
from .policy import RetryPolicy
from typing import Awaitable, Callable

async def retry_async(fn: Callable[[], Awaitable], *,
                      should_retry: Callable[[Exception], bool],
                      policy: RetryPolicy) -> any:
    attempt = 0
    while True:
        try:
            return await fn()
        except Exception as e:
            attempt += 1
            if attempt >= policy.max_attempts or not should_retry(e):
                raise
            delay = min(policy.base_ms * (2 ** (attempt - 1)) + random.randint(0, policy.jitter_ms),
                        policy.max_ms) / 1000
            await anyio.sleep(delay)
