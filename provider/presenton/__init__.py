# provider/presenton/__init__.py
from __future__ import annotations
from typing import Mapping, Any
from ..types import Provider, ExecCtx
from ..core.transport.http_client import HttpClient, TransportConfig
from ..core.trace.tracer import span
from ..core.metrics.recorder import record
from ..core.utils.logger import log

class PresentonProvider(Provider):
    def id(self) -> str:
        return "presenton-local"

    def capabilities(self) -> Mapping[str, Any]:
        return {"slideGen": True, "regions": ["local"]}

    async def slide_gen(self, req: Mapping[str, Any], ctx: ExecCtx) -> Mapping[str, Any]:
        """
        ローカルの Presenton API にアクセスしてスライド生成を行う
        """
        client = HttpClient(
            provider=self.id(),
            cfg=TransportConfig(
                base_url="http://localhost:5001",
                timeout_ms=ctx.timeout_ms,
                headers={"Content-Type": "application/json"},
            ),
        )

        payload = {
            "content": req.get("content", ""),
            "n_slides": req.get("n_slides", 5),
            "language": req.get("language", "Japanese"),
            "template": req.get("template", "general"),
            "export_as": req.get("export_as", "pptx"),
        }

        async with span("presenton.generate", {"slides": payload["n_slides"]}):
            result = await client.post_json("/api/v1/ppt/presentation/generate", json=payload)

        record(self.id(), "success", 1, {"op": "slide_gen"})
        log(self.id(), "ok", request_id=ctx.request_id)

        await client.aclose()
        return result
