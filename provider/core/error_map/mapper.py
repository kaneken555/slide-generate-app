from __future__ import annotations
from .taxonomy import ErrorCode, ProviderError
from typing import Optional

def to_common(provider:str, status:int|None, text:str|None, kind:str|None=None) -> ProviderError:
    t = (text or "").lower()
    if status in (401,403):  return ProviderError(ErrorCode.AuthFailed, "auth failed", provider, status)
    if status == 429:        return ProviderError(ErrorCode.RateLimited, "rate limited", provider, status)
    if status and 500 <= status < 600: return ProviderError(ErrorCode.ProviderDown, "server error", provider, status)
    if "timeout" in t:       return ProviderError(ErrorCode.Timeout, "timeout", provider, status)
    if status == 400:        return ProviderError(ErrorCode.BadInput, "bad input", provider, status)
    if "quota" in t:         return ProviderError(ErrorCode.QuotaExceeded, "quota exceeded", provider, status)
    if "safety" in t or kind == "safety": return ProviderError(ErrorCode.SafetyBlocked, "safety blocked", provider, status)
    return ProviderError(ErrorCode.Unknown, "unknown error", provider, status)
