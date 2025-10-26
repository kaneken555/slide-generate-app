from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Optional

@dataclass
class ExecCtx:
    request_id: str
    trace_id: str
    timeout_ms: int = 60000
    tenant: Optional[str] = None
    region: Optional[str] = None
    idempotency_key: Optional[str] = None
    budget_yen: Optional[float] = None

class Provider:
    def id(self) -> str: ...
    def capabilities(self) -> Mapping[str, Any]: ...
    async def generate(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        raise NotImplementedError
    async def slide_gen(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        raise NotImplementedError
