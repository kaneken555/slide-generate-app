# examples/provider_smoke.py
import os
import anyio
from provider.types import ExecCtx
from provider.openai import OpenAIProvider
from provider.presenton import PresentonProvider

async def main():
    # APIキーは環境変数から
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required"
    # Presenton使うなら
    # assert os.getenv("PRESENTON_API_KEY"), "PRESENTON_API_KEY is required"

    ctx = ExecCtx(request_id="req1", trace_id="tr1", timeout_ms=60000)

    # 例1: 推敲（OpenAI）
    gen = await OpenAIProvider().generate(
        {"text": "本日は晴天なり。", "temperature": 0.1}, ctx
    )
    print("=== OpenAI.generate ===")
    print(gen)

    # 例2: スライド生成（Presenton）
    slide_req = {
        "purpose": "社内共有",
        "slides": [{"title": "概要", "bullets": ["要点A", "要点B"]}],
    }
    deck = await PresentonProvider().slide_gen(slide_req, ctx)
    print("=== Presenton.slide_gen ===")
    print(deck)

if __name__ == "__main__":
    anyio.run(main)
