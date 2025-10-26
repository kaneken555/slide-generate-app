# examples/presenton_local_test.py
import anyio
from provider.presenton import PresentonProvider
from provider.types import ExecCtx

async def main():
    ctx = ExecCtx(request_id="req-local", trace_id="trace-local", timeout_ms=60000)
    provider = PresentonProvider()

    result = await provider.slide_gen({
        "content": "Introduction to Machine Learning",
        "n_slides": 5,
        "language": "Japanese",
        "template": "general",
        "export_as": "pptx"
    }, ctx)

    print("=== Presenton Local Result ===")
    print(result)

if __name__ == "__main__":
    anyio.run(main)
