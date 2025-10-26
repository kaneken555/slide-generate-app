from __future__ import annotations
from typing import Mapping, Any
from pydantic import BaseModel
import os

from ..types import Provider, ExecCtx
from ..core.transport.http_client import HttpClient, TransportConfig
from ..core.transport.retry_middleware import with_retry
from ..core.backoff.policy import RetryPolicy
from ..core.trace.tracer import span
from ..core.metrics.recorder import record
from ..core.utils.logger import log

# 環境変数でベースURLやモデルを切り替え可
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")

class _GenReq(BaseModel):
    text: str
    system: str | None = None
    temperature: float = 0.2
    max_tokens: int | None = None
    model: str = OLLAMA_MODEL

def _to_ollama_payload(req: _GenReq) -> Mapping[str, Any]:
    # /api/chat を使う（messages形式）
    messages = []
    if req.system:
        messages.append({"role": "system", "content": req.system})
    messages.append({"role": "user", "content": req.text})

    payload: dict[str, Any] = {
        "model": req.model,
        "messages": messages,
        "stream": False,  # まずは非ストリームで
        "options": {"temperature": req.temperature},
    }
    # max_tokens は options.num_predict で指定（未指定ならデフォルト）
    if req.max_tokens:
        payload["options"]["num_predict"] = req.max_tokens
    return payload

def _normalize(resp: Mapping[str, Any]) -> Mapping[str, Any]:
    # /api/chat の非ストリームレスポンス例:
    # {"model":"...","created_at":"...","message":{"role":"assistant","content":"..."}, "done":true, ...}
    msg = resp.get("message", {}) or {}
    content = msg.get("content", "")
    # トークン使用量は modelsにより出ないこともあるのでベーシックに
    return {
        "content": content,
        "meta": {
            "provider": "ollama",
            "model": resp.get("model"),
        },
    }

class OllamaProvider(Provider):
    def id(self) -> str:
        return "ollama"

    def capabilities(self) -> Mapping[str, Any]:
        return {"generate": True, "slideGen": False, "regions": ["local"]}

    async def generate(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        gen = _GenReq(**req)
        client = HttpClient(
            self.id(),
            TransportConfig(
                base_url=OLLAMA_BASE,
                timeout_ms=ctx.timeout_ms,
                headers={"Content-Type": "application/json"},
            ),
        )
        payload = _to_ollama_payload(gen)

        async def _call():
            # /api/chat にPOST
            async with span("ollama.chat", {"model": gen.model}):
                return await client.post_json("/api/chat", json=payload)

        resp = await with_retry(_call, RetryPolicy())
        out = _normalize(resp)
        record(self.id(), "success", 1, {"op": "generate"})
        log(self.id(), "ok", request_id=ctx.request_id)
        await client.aclose()
        return out

    async def slide_gen(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        # ローカルLLM単体ではスライド生成APIを持たない想定
        raise NotImplementedError("OllamaProvider does not support slide_gen")
