from __future__ import annotations
from typing import Callable, Awaitable
from ..backoff.executor import retry_async
from ..backoff.policy import RetryPolicy
from ..error_map.taxonomy import ProviderError, ErrorCode

def should_retry(e: Exception) -> bool:
    if not isinstance(e, ProviderError):
        return False
    return e.code in (ErrorCode.RateLimited, ErrorCode.ProviderDown, ErrorCode.Timeout)

async def with_retry(fn: Callable[[], Awaitable], policy: RetryPolicy):
    return await retry_async(fn, should_retry=should_retry, policy=policy)
