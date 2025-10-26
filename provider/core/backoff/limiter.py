import anyio
from contextlib import asynccontextmanager

class TokenBucket:
    def __init__(self, capacity:int, refill_per_sec:float):
        self._sem = anyio.Semaphore(capacity)
        self._refill = refill_per_sec
        anyio.create_task_group().start_soon(self._refill_loop)

    async def _refill_loop(self):
        while True:
            try:
                self._sem.release()
            except RuntimeError:
                pass
            await anyio.sleep(1/self._refill)

    @asynccontextmanager
    async def acquire(self):
        async with self._sem:
            yield
