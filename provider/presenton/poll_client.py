from __future__ import annotations
import anyio
from ..core.transport.http_client import HttpClient
from ..core.transport.retry_middleware import with_retry
from ..core.backoff.policy import RetryPolicy

async def poll_until_done(client: HttpClient, job_id: str, *, interval_ms:int=800, timeout_ms:int=90000):
    elapsed = 0
    async def _status():
        return await client.get_json(f"/v1/jobs/{job_id}")

    while elapsed < timeout_ms:
        res = await with_retry(_status, RetryPolicy(max_attempts=2, base_ms=200, max_ms=1200))
        if res.get("status") in ("succeeded","failed","canceled"):
            return res
        await anyio.sleep(interval_ms/1000)
        elapsed += interval_ms
    raise TimeoutError("presenton job timeout")
