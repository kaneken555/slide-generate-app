# slide-generate-app

3層アーキテクチャを採用したAI駆動のスライド生成アプリケーション

## 概要

このアプリケーションは、AI/LLMサービスを使用して、指定されたトピックからプレゼンテーションスライドを自動生成します。プロバイダーの抽象化、機能サービス、ワークフローオーケストレーションを備えた、クリーンな3層アーキテクチャを特徴としています。

## 機能

- **🔍 自動リサーチ**: LLMの知識を使用して任意のトピックに関する構造化された情報を収集
- **📝 アウトライン生成**: 適切に構造化されたスライドアウトラインを作成
- **🎨 スライド生成**: アウトラインからプレゼンテーションファイル（PPTX、PDF）を生成
- **🔄 ワークフローオーケストレーション**: リトライとエラーハンドリングを備えた自動エンドツーエンドパイプライン
- **🔌 プロバイダー抽象化**: 複数のLLMおよびスライド生成プロバイダーをサポート
- **📊 可観測性**: トレーシング、メトリクス、ロギングを組み込み
- **⚡ プロダクションレディ**: リトライロジック、エラーマッピング、タイムアウト処理を含む

## アーキテクチャ

このアプリケーションは3層アーキテクチャに従っています：

```
┌─────────────────────────────────────┐
│     オーケストレーター層              │
│  - WorkflowBase                     │
│  - SlideGenerationWorkflow          │
│  - ステップ管理とデータフロー         │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     Capability層                    │
│  - ResearchService                  │
│  - RefineService                    │
│  - SlideGenService                  │
│  - ビジネスロジックの抽象化           │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     Provider層                      │
│  - OpenAI (gpt-4o-mini)            │
│  - Ollama (ローカルLLM)             │
│  - Presenton (スライド生成)         │
│  - HTTPクライアントとエラーハンドリング│
└─────────────────────────────────────┘
```

## 必要要件

- Python 3.12+
- OpenAI APIキー（LLM機能用）
- Presentonサーバー（スライド生成用）

## インストール

1. リポジトリをクローン：
```bash
git clone https://github.com/yourusername/slide-generate-app.git
cd slide-generate-app
```

2. 仮想環境を作成して有効化：
```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

3. 依存関係をインストール：
```bash
pip install -r requirements.txt
```

4. 環境変数を設定：
```bash
# .envファイルを作成
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## クイックスタート

### 方法1: オーケストレーターを使用（推奨）

オーケストレーターは完全なパイプラインを自動的に実行します：

```python
from provider.types import ExecCtx
from provider.openai import OpenAIProvider
from provider.presenton import PresentonProvider
from ai_service.capabilities.research_service import ResearchService
from ai_service.capabilities.refine_service import RefineService
from ai_service.capabilities.slidegen_service import SlideGenService
from orchestrator.runtime.slide_generation_workflow import SlideGenerationWorkflow

# Setup
openai = OpenAIProvider()
presenton = PresentonProvider()

research_svc = ResearchService(openai)
refine_svc = RefineService(openai)
slidegen_svc = SlideGenService(presenton)

workflow = SlideGenerationWorkflow(research_svc, refine_svc, slidegen_svc)

# 実行
ctx = ExecCtx(request_id="req-1", trace_id="trace-1", timeout_ms=180000)
result = await workflow.execute({
    "topic": "機械学習の基礎",
    "n_slides": 5,
    "language": "Japanese"
}, ctx)

print(f"プレゼンテーション: {result['result']['file_path']}")
```

### 方法2: Capabilityサービスを直接使用

```python
from provider.openai import OpenAIProvider
from ai_service.capabilities.refine_service import RefineService

provider = OpenAIProvider()
service = RefineService(provider)

ctx = ExecCtx(request_id="req-1", trace_id="trace-1")
result = await service.execute({
    "topic": "Pythonの基礎",
    "n_slides": 5
}, ctx)

print(result["outline"])
```

### 方法3: Providerを直接使用

```python
from provider.openai import OpenAIProvider

provider = OpenAIProvider()
ctx = ExecCtx(request_id="req-1", trace_id="trace-1")

result = await provider.generate({
    "text": "量子コンピューティングについて説明してください",
    "temperature": 0.3
}, ctx)

print(result["content"])
```

## 実行例

`examples/` ディレクトリには様々なテストスクリプトが含まれています：

### オーケストレーター層
- `orchestrator_smoke.py` - 完全なワークフローオーケストレーションのテスト
- `full_pipeline.py` - 詳細な出力を含む完全なパイプライン

### Capability層
- `service_smoke.py` - 個別のCapabilityサービスのテスト
- `research_smoke.py` - 異なる深度レベルのリサーチサービス
- `integration_service_pipeline.py` - サービスレベルのパイプライン統合

### Provider層
- `openai_smoke.py` - OpenAI Providerのテスト
- `ollama_smoke.py` - Ollama（ローカルLLM）のテスト
- `presenton_local_test.py` - Presentonスライド生成のテスト
- `provider_smoke.py` - 基本的なProvider機能

### 実行方法

```bash
# オーケストレーターテスト（完全なパイプライン）
python -m examples.orchestrator_smoke

# 個別サービステスト
python -m examples.service_smoke

# リサーチに焦点を当てたテスト
python -m examples.research_smoke

# Providerテスト
python -m examples.openai_smoke
```

## 設定

### 環境変数

- `OPENAI_API_KEY` - OpenAI APIキー（必須）
- `OLLAMA_BASE` - Ollama ベースURL（デフォルト: http://localhost:11434）
- `OLLAMA_MODEL` - Ollama モデル名（デフォルト: llama3:8b）
- `PRESENTON_API_KEY` - Presenton APIキー（必要に応じて）

### Presentonセットアップ

スライド生成機能には実行中のPresentonサーバーが必要です：

```bash
# デフォルトエンドポイント: http://localhost:5001
# セットアップ手順についてはPresentonドキュメントを参照してください
```

## プロジェクト構造

```
slide-generate-app/
├── provider/                    # Provider層
│   ├── types.py                # 基本型とインターフェース
│   ├── openai/                 # OpenAI Provider
│   ├── ollama/                 # Ollama Provider
│   ├── presenton/              # Presenton Provider
│   └── core/                   # コアユーティリティ
│       ├── transport/          # HTTPクライアント
│       ├── error_map/          # エラー分類
│       ├── backoff/            # リトライロジック
│       ├── trace/              # トレーシング
│       └── metrics/            # メトリクス
├── ai_service/                  # Capability層
│   └── capabilities/
│       ├── capability_base.py  # ベースクラス
│       ├── research_service.py # リサーチ機能
│       ├── refine_service.py   # アウトライン生成機能
│       └── slidegen_service.py # スライド生成機能
├── orchestrator/                # オーケストレーター層
│   └── runtime/
│       ├── workflow_base.py              # ワークフローベースクラス
│       └── slide_generation_workflow.py  # スライド生成ワークフロー
└── examples/                    # サンプルスクリプト
```

## API仕様

### ResearchService

LLMの知識を使用してトピックに関する構造化された情報を収集します。

**入力：**
```python
{
    "topic": str,              # リサーチトピック
    "language": str,           # 出力言語（デフォルト: "Japanese"）
    "depth": str,              # "basic"、"medium"、または "detailed"
    "focus_areas": List[str],  # オプションのフォーカスエリア
    "temperature": float,      # 生成温度（デフォルト: 0.3）
    "max_tokens": int          # 最大トークン数（デフォルト: 1000）
}
```

**出力：**
```python
{
    "topic": str,
    "summary": str,
    "key_points": List[str],
    "details": str,
    "meta": dict
}
```

### RefineService

トピックから構造化されたスライドアウトラインを作成します。

**入力：**
```python
{
    "topic": str,                    # スライドトピック
    "n_slides": int,                 # スライド数（1-50）
    "language": str,                 # 出力言語
    "temperature": float,            # 生成温度
    "max_tokens": int,               # 最大トークン数
    "custom_instructions": str       # オプションのカスタム指示
}
```

**出力：**
```python
{
    "outline": str,
    "meta": dict
}
```

### SlideGenService

アウトラインテキストからプレゼンテーションファイルを生成します。

**入力：**
```python
{
    "content": str,       # アウトラインテキスト
    "n_slides": int,      # スライド数（1-100）
    "language": str,      # 言語
    "template": str,      # テンプレート名（デフォルト: "general"）
    "export_as": str      # エクスポート形式（デフォルト: "pptx"）
}
```

**出力：**
```python
{
    "presentation_id": str,
    "file_path": str,
    "download_url": str,
    "status": str
}
```

### SlideGenerationWorkflow

完全なオーケストレーションワークフロー: Research → Refine → SlideGen

**入力：**
```python
{
    "topic": str,
    "n_slides": int,
    "language": str,           # デフォルト: "Japanese"
    "research_depth": str,     # デフォルト: "medium"
    "focus_areas": List[str],  # オプション
    "template": str,           # デフォルト: "general"
    "export_as": str           # デフォルト: "pptx"
}
```

**出力：**
```python
{
    "success": bool,
    "steps": [...],           # ステップ実行の詳細
    "workflow": {...},        # ワークフローメタデータ
    "result": {
        "topic": str,
        "presentation_id": str,
        "file_path": str,
        "download_url": str
    }
}
```

## 詳細機能

### 1. Provider層

- **抽象化**: 異なるLLMおよびスライドプロバイダーの統一インターフェース
- **エラーマッピング**: プロバイダー間で標準化されたエラーコード
- **リトライロジック**: 設定可能なリトライポリシーによる指数バックオフ
- **HTTPトランスポート**: タイムアウトと認証処理を備えた非同期HTTPクライアント
- **可観測性**: トレーシング、メトリクス、構造化ロギングを組み込み

### 2. Capability層

- **ビジネスロジック**: 一般的なタスクの高レベル抽象化
- **入力検証**: Pydanticベースのリクエスト/レスポンス検証
- **プロンプト管理**: 一元化されたプロンプトテンプレート
- **プロバイダー非依存**: コードを変更せずにプロバイダーを切り替え可能

### 3. オーケストレーター層

- **ワークフロー定義**: 宣言的なステップベースのワークフロー
- **データフロー**: ステップ間の自動データ受け渡し
- **エラーハンドリング**: ステップレベルのエラーハンドリングと回復
- **進捗追跡**: ステップごとの詳細な実行メトリクス
- **リトライサポート**: ステップごとに設定可能なリトライロジック

## 開発

### テスト実行

```bash
# すべてのサンプルテストを実行
python -m examples.orchestrator_smoke
python -m examples.service_smoke
python -m examples.research_smoke
```

### 新しいProviderの追加

1. `Provider`を継承した新しいプロバイダークラスを作成
2. `generate()`および/または`slide_gen()`メソッドを実装
3. プロバイダー固有のエラーマッピングを追加
4. スモークテストでテスト

### 新しいCapabilityの追加

1. `CapabilityBase`を継承した新しいサービスクラスを作成
2. `execute()`および`_do_execute()`メソッドを実装
3. Pydanticでリクエスト/レスポンスモデルを定義
4. 必要に応じてワークフローに追加

## トラブルシューティング

### OpenAI APIエラー

- **401 Unauthorized**: `.env`ファイルの`OPENAI_API_KEY`を確認してください
- **429 Rate Limited**: リトライロジックが自動的に処理します
- **Timeout**: `ExecCtx`の`timeout_ms`を増やしてください

### Presenton接続エラー

- Presentonサーバーが`http://localhost:5001`で実行されていることを確認してください
- サーバーログでエラーを確認してください
- ワークフローは失敗時に自動的に1回リトライします

### Ollamaエラー

- Ollamaが実行されていることを確認してください：`ollama serve`
- モデルがダウンロードされていることを確認してください：`ollama pull llama3:8b`
- `OLLAMA_BASE`環境変数を確認してください

## ライセンス

[ここにライセンスを記載]

## 貢献

貢献を歓迎します！お気軽にプルリクエストを送信してください。

## 謝辞

- OpenAI - GPTモデルの提供
- Ollama - ローカルLLMサポート
- Presenton - スライド生成機能
