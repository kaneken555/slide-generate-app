import anyio
from provider.types import ExecCtx
from provider.local.ollama import OllamaProvider

async def main():
    ctx = ExecCtx(request_id="req-local", trace_id="trace-local", timeout_ms=60000)
    provider = OllamaProvider()

    req = {
        "text": "日本語で、1文の自己紹介をしてください。",
        "temperature": 0.2,
        # "model": "qwen2.5:7b-instruct",  # 変えたい場合はここで
        # "max_tokens": 128,
    }
    out = await provider.generate(req, ctx)
    print("=== OLLAMA RESULT ===")
    print(out["content"])
    print("meta:", out.get("meta"))

if __name__ == "__main__":
    anyio.run(main)
