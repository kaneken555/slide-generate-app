from __future__ import annotations
from dataclasses import dataclass

@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_ms: int = 200
    max_ms: int = 4000
    jitter_ms: int = 200
