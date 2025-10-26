from __future__ import annotations
from contextlib import asynccontextmanager
import time

@asynccontextmanager
async def span(name:str, attrs:dict|None=None):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        elapsed = int((time.perf_counter()-t0)*1000)
        # 実運用ではOTelに送る。ここではprintで代替。
        print(f"[trace] {name} {elapsed}ms {attrs or {}}")
