from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ErrorCode(str, Enum):
    AuthFailed = "AuthFailed"
    RateLimited = "RateLimited"
    ProviderDown = "ProviderDown"
    Timeout = "Timeout"
    BadInput = "BadInput"
    QuotaExceeded = "QuotaExceeded"
    SafetyBlocked = "SafetyBlocked"
    Unknown = "Unknown"

@dataclass
class ProviderError(Exception):
    code: ErrorCode
    message: str
    provider: str
    original_status: Optional[int] = None
    retry_after_ms: Optional[int] = None
