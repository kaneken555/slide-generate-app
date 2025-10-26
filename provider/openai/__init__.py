from __future__ import annotations
from typing import Mapping, Any
from pydantic import BaseModel
from ..types import Provider, ExecCtx
from ..core.transport.http_client import HttpClient, TransportConfig
from ..core.transport.auth_handler import bearer_header
from ..core.transport.retry_middleware import with_retry
from ..core.backoff.policy import RetryPolicy
from ..core.trace.tracer import span
from ..core.metrics.recorder import record
from ..core.utils.logger import log

OPENAI_BASE="https://api.openai.com/v1"

class _GenReq(BaseModel):
    text: str
    system: str|None = None
    temperature: float = 0.2
    max_tokens: int|None = None
    json_mode: bool = False
    model: str = "gpt-4o-mini"  # 適宜変更

def _to_openai_payload(req:_GenReq) -> Mapping[str, Any]:
    messages = []
    if req.system:
        messages.append({"role":"system","content":req.system})
    messages.append({"role":"user","content":req.text})
    p: dict[str, Any] = {
        "model": req.model,
        "messages": messages,
        "temperature": req.temperature,
    }
    if req.max_tokens: p["max_tokens"] = req.max_tokens
    if req.json_mode:
        p["response_format"] = {"type": "json_object"}
    return p

def _normalize(resp: Mapping[str, Any]) -> Mapping[str, Any]:
    choice = resp.get("choices",[{}])[0]
    content = (choice.get("message") or {}).get("content","")
    usage = resp.get("usage",{})
    return {
        "content": content,
        "meta": {"tokens_in": usage.get("prompt_tokens"), "tokens_out": usage.get("completion_tokens")}
    }

class OpenAIProvider(Provider):
    def id(self)->str: return "openai"

    def capabilities(self)->Mapping[str,Any]:
        return {"generate": True, "slideGen": False, "regions":["global"]}

    async def generate(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        gen = _GenReq(**req)
        headers = bearer_header("OPENAI_API_KEY") | {"Content-Type":"application/json"}
        client = HttpClient(self.id(), TransportConfig(base_url=OPENAI_BASE, timeout_ms=ctx.timeout_ms, headers=headers))
        payload = _to_openai_payload(gen)

        async def _call():
            async with span("openai.chat.completions", {"model": gen.model}):
                return await client.post_json("/chat/completions", json=payload)

        resp = await with_retry(_call, RetryPolicy())
        out = _normalize(resp)
        record(self.id(), "success", 1, {"op":"generate"})
        log(self.id(), "ok", request_id=ctx.request_id)
        await client.aclose()
        return out
