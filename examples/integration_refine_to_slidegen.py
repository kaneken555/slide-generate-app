# examples/integration_refine_to_slidegen.py
import os
import anyio
from provider.types import ExecCtx
from provider.openai import OpenAIProvider
from provider.presenton import PresentonProvider

TOPIC = "機械学習入門"
N_SLIDES = 5

OUTLINE_PROMPT = f"""
以下のテーマについて、日本語でスライドのアウトラインを作ってください。
- テーマ: {TOPIC}
- スライド数: {N_SLIDES}
- 1枚目はタイトルと要点、以降は箇条書き中心で簡潔に
- 出力はプレーンテキスト（Markdown可）。番号付きの見出しと箇条書きで。

例:
# タイトル
- 要点A
- 要点B
## 背景
- ...
"""

async def main():
    # 前提: OPENAI_API_KEY が必要。Presenton はローカル起動（デフォルト localhost:5001）
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required"

    ctx = ExecCtx(request_id="req-integ-1", trace_id="trace-integ-1", timeout_ms=90000)

    # 1) OpenAIでアウトライン生成（Refine/Researchの代替として簡易）
    openai = OpenAIProvider()
    gen = await openai.generate(
        {
            "system": "あなたは日本語で簡潔かつ構造化されたスライドアウトラインを作る編集者です。",
            "text": OUTLINE_PROMPT,
            "temperature": 0.3,
            "max_tokens": 700,
            "model": "gpt-4o-mini",
        },
        ctx,
    )
    outline_text = gen["content"].strip()
    print("=== OUTLINE (from OpenAI) ===")
    print(outline_text)

    # 2) Presentonでスライド化（content にアウトラインをそのまま渡す）
    presenton = PresentonProvider()
    deck = await presenton.slide_gen(
        {
            "content": outline_text,   # ローカルPresentonの要求に合わせてテキストを渡す
            "n_slides": N_SLIDES,
            "language": "Japanese",    # ASCIIのダブルクォートで
            "template": "general",
            "export_as": "pptx",
        },
        ctx,
    )
    print("\n=== PRESENTON RESULT ===")
    print(deck)  # 例: {"status":"success", "file_path":"...", "download_url":"..."}

if __name__ == "__main__":
    anyio.run(main)
