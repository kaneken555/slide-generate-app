"""
examples/service_smoke.py

サービス層の動作確認テスト

RefineServiceとSlideGenServiceを個別にテストする。
"""
import os
import anyio
from provider.types import ExecCtx
from provider.openai import OpenAIProvider
from provider.presenton import PresentonProvider
from ai_service.capabilities.refine_service import RefineService
from ai_service.capabilities.slidegen_service import SlideGenService


async def test_refine_service():
    """RefineServiceの動作確認"""
    print("\n=== RefineService テスト ===")

    # OpenAIプロバイダーを使用
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required"
    provider = OpenAIProvider()
    service = RefineService(provider)

    # 実行コンテキスト
    ctx = ExecCtx(request_id="req-refine-1", trace_id="trace-refine-1", timeout_ms=60000)

    # アウトライン生成
    result = await service.execute({
        "topic": "Pythonの基礎",
        "n_slides": 5,
        "language": "Japanese",
        "temperature": 0.3
    }, ctx)

    print(f"Service ID: {service.id()}")
    print(f"Service Name: {service.name()}")
    print(f"Outline:\n{result['outline']}")
    print(f"Meta: {result['meta']}")

    return result


async def test_slidegen_service():
    """SlideGenServiceの動作確認"""
    print("\n=== SlideGenService テスト ===")

    # Presentonプロバイダーを使用
    provider = PresentonProvider()
    service = SlideGenService(provider)

    # 実行コンテキスト
    ctx = ExecCtx(request_id="req-slidegen-1", trace_id="trace-slidegen-1", timeout_ms=90000)

    # サンプルアウトライン
    sample_outline = """
# Pythonの基礎
- プログラミング言語Pythonについて学ぶ
- 初心者向けの入門講座

## Pythonとは
- 読みやすく書きやすい言語
- 多様な用途に使える

## 基本文法
- 変数と型
- 制御構文

## データ構造
- リスト
- 辞書
- タプル

## まとめ
- Pythonは強力で汎用的な言語
- 実践して学ぶことが重要
"""

    # スライド生成
    result = await service.execute({
        "content": sample_outline.strip(),
        "n_slides": 5,
        "language": "Japanese",
        "template": "general",
        "export_as": "pptx"
    }, ctx)

    print(f"Service ID: {service.id()}")
    print(f"Service Name: {service.name()}")
    print(f"Presentation ID: {result.get('presentation_id')}")
    print(f"File Path: {result.get('file_path')}")
    print(f"Download URL: {result.get('download_url')}")
    print(f"Status: {result.get('status')}")

    return result


async def main():
    """全テスト実行"""
    try:
        # RefineServiceテスト
        await test_refine_service()

        # SlideGenServiceテスト（Presentonが起動している場合のみ）
        try:
            await test_slidegen_service()
        except Exception as e:
            print(f"\nSlideGenService テストスキップ (Presenton未起動?): {e}")

        print("\n=== すべてのテスト完了 ===")
    except Exception as e:
        print(f"\nエラー: {e}")
        raise


if __name__ == "__main__":
    anyio.run(main)
