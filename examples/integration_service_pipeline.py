"""
examples/integration_service_pipeline.py

サービス層を使ったフルパイプライン統合テスト

RefineService → SlideGenService の連携動作を確認する。
既存の integration_refine_to_slidegen.py のサービス層版。
"""
import os
import anyio
from provider.types import ExecCtx
from provider.openai import OpenAIProvider
from provider.presenton import PresentonProvider
from ai_service.capabilities.refine_service import RefineService
from ai_service.capabilities.slidegen_service import SlideGenService


TOPIC = "機械学習入門"
N_SLIDES = 5


async def main():
    """フルパイプライン実行"""
    # 前提: OPENAI_API_KEY が必要。Presenton はローカル起動（デフォルト localhost:5001）
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required"

    ctx = ExecCtx(request_id="req-pipeline-1", trace_id="trace-pipeline-1", timeout_ms=120000)

    print("=" * 60)
    print("サービス層統合テスト: RefineService → SlideGenService")
    print("=" * 60)

    # ========================================
    # Step 1: RefineService でアウトライン生成
    # ========================================
    print(f"\n[Step 1] RefineService: トピック '{TOPIC}' からアウトライン生成")

    openai_provider = OpenAIProvider()
    refine_service = RefineService(openai_provider)

    refine_result = await refine_service.execute({
        "topic": TOPIC,
        "n_slides": N_SLIDES,
        "language": "Japanese",
        "temperature": 0.3,
        "max_tokens": 700,
        "model": "gpt-4o-mini"
    }, ctx)

    outline = refine_result["outline"]
    print("\n--- 生成されたアウトライン ---")
    print(outline)
    print("-" * 60)
    print(f"Token使用量: {refine_result['meta']}")

    # ========================================
    # Step 2: SlideGenService でスライド生成
    # ========================================
    print(f"\n[Step 2] SlideGenService: アウトラインからスライド生成")

    presenton_provider = PresentonProvider()
    slidegen_service = SlideGenService(presenton_provider)

    slidegen_result = await slidegen_service.execute({
        "content": outline,
        "n_slides": N_SLIDES,
        "language": "Japanese",
        "template": "general",
        "export_as": "pptx"
    }, ctx)

    print("\n--- スライド生成結果 ---")
    print(f"Presentation ID: {slidegen_result.get('presentation_id')}")
    print(f"File Path: {slidegen_result.get('file_path')}")
    print(f"Download URL: {slidegen_result.get('download_url')}")
    print(f"Status: {slidegen_result.get('status')}")
    print("-" * 60)

    # ========================================
    # 完了
    # ========================================
    print("\n" + "=" * 60)
    print("パイプライン完了！")
    print("=" * 60)
    print(f"\nトピック: {TOPIC}")
    print(f"スライド数: {N_SLIDES}")
    print(f"\nアウトライン長: {len(outline)} 文字")
    print(f"生成ファイル: {slidegen_result.get('file_path', 'N/A')}")


if __name__ == "__main__":
    anyio.run(main)
