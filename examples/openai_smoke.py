# examples/openai_smoke.py
import anyio
from provider.types import ExecCtx
from provider.openai import OpenAIProvider

async def main():
    ctx = ExecCtx(request_id="req1", trace_id="trace1", timeout_ms=60000)
    provider = OpenAIProvider()

    # 最小入力（必要に応じて model / temperature を変更）
    req = {"text": "こんにちは。1文で自己紹介してください。", "temperature": 0.2}
    out = await provider.generate(req, ctx)

    print("=== RESULT ===")
    print(out["content"])
    print("meta:", out.get("meta"))

if __name__ == "__main__":
    anyio.run(main)
