# slide-generate-app

AI-powered slide generation application with a three-layer architecture.

## Overview / 概要

This application automatically generates presentation slides from a given topic using AI/LLM services. It features a clean three-layer architecture with provider abstraction, capability services, and workflow orchestration.

## Features / 機能

- **🔍 Automatic Research**: Gathers structured information about any topic using LLM knowledge
- **📝 Outline Generation**: Creates well-structured slide outlines
- **🎨 Slide Generation**: Generates presentation files (PPTX, PDF) from outlines
- **🔄 Workflow Orchestration**: Automated end-to-end pipeline with retry and error handling
- **🔌 Provider Abstraction**: Support for multiple LLM and slide generation providers
- **📊 Observability**: Built-in tracing, metrics, and logging
- **⚡ Production-Ready**: Includes retry logic, error mapping, and timeout handling

## Architecture / アーキテクチャ

The application follows a three-layer architecture:

```
┌─────────────────────────────────────┐
│     Orchestrator Layer              │
│  - WorkflowBase                     │
│  - SlideGenerationWorkflow          │
│  - Step management & data flow      │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     Capability Layer                │
│  - ResearchService                  │
│  - RefineService                    │
│  - SlideGenService                  │
│  - Business logic abstraction       │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     Provider Layer                  │
│  - OpenAI (gpt-4o-mini)            │
│  - Ollama (local LLM)              │
│  - Presenton (slide generation)    │
│  - HTTP client & error handling    │
└─────────────────────────────────────┘
```

## Requirements / 必要要件

- Python 3.12+
- OpenAI API key (for LLM features)
- Presenton server (for slide generation)

## Installation / インストール

1. Clone the repository:
```bash
git clone https://github.com/yourusername/slide-generate-app.git
cd slide-generate-app
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Quick Start / クイックスタート

### Option 1: Using Orchestrator (Recommended) / オーケストレーター使用（推奨）

The orchestrator runs the complete pipeline automatically:

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

# Execute
ctx = ExecCtx(request_id="req-1", trace_id="trace-1", timeout_ms=180000)
result = await workflow.execute({
    "topic": "Machine Learning Fundamentals",
    "n_slides": 5,
    "language": "Japanese"
}, ctx)

print(f"Presentation: {result['result']['file_path']}")
```

### Option 2: Using Capability Services Directly / Capabilityサービス直接使用

```python
from provider.openai import OpenAIProvider
from ai_service.capabilities.refine_service import RefineService

provider = OpenAIProvider()
service = RefineService(provider)

ctx = ExecCtx(request_id="req-1", trace_id="trace-1")
result = await service.execute({
    "topic": "Python Basics",
    "n_slides": 5
}, ctx)

print(result["outline"])
```

### Option 3: Using Providers Directly / Provider直接使用

```python
from provider.openai import OpenAIProvider

provider = OpenAIProvider()
ctx = ExecCtx(request_id="req-1", trace_id="trace-1")

result = await provider.generate({
    "text": "Explain quantum computing",
    "temperature": 0.3
}, ctx)

print(result["content"])
```

## Examples / 実行例

The `examples/` directory contains various test scripts:

### Orchestrator Layer / オーケストレーター層
- `orchestrator_smoke.py` - Full workflow orchestration test
- `full_pipeline.py` - Complete pipeline with detailed output

### Capability Layer / Capability層
- `service_smoke.py` - Individual capability service tests
- `research_smoke.py` - Research service with different depth levels
- `integration_service_pipeline.py` - Service-level pipeline integration

### Provider Layer / Provider層
- `openai_smoke.py` - OpenAI provider test
- `ollama_smoke.py` - Ollama (local LLM) test
- `presenton_local_test.py` - Presenton slide generation test
- `provider_smoke.py` - Basic provider functionality

### Running Examples / 実行方法

```bash
# Orchestrator test (full pipeline)
python -m examples.orchestrator_smoke

# Individual service tests
python -m examples.service_smoke

# Research-focused test
python -m examples.research_smoke

# Provider tests
python -m examples.openai_smoke
```

## Configuration / 設定

### Environment Variables / 環境変数

- `OPENAI_API_KEY` - OpenAI API key (required)
- `OLLAMA_BASE` - Ollama base URL (default: http://localhost:11434)
- `OLLAMA_MODEL` - Ollama model name (default: llama3:8b)
- `PRESENTON_API_KEY` - Presenton API key (if needed)

### Presenton Setup / Presentonセットアップ

The slide generation feature requires a running Presenton server:

```bash
# Default endpoint: http://localhost:5001
# See Presenton documentation for setup instructions
```

## Project Structure / プロジェクト構造

```
slide-generate-app/
├── provider/                    # Provider layer
│   ├── types.py                # Base types and interfaces
│   ├── openai/                 # OpenAI provider
│   ├── ollama/                 # Ollama provider
│   ├── presenton/              # Presenton provider
│   └── core/                   # Core utilities
│       ├── transport/          # HTTP client
│       ├── error_map/          # Error taxonomy
│       ├── backoff/            # Retry logic
│       ├── trace/              # Tracing
│       └── metrics/            # Metrics
├── ai_service/                  # Capability layer
│   └── capabilities/
│       ├── capability_base.py  # Base class
│       ├── research_service.py # Research capability
│       ├── refine_service.py   # Refine capability
│       └── slidegen_service.py # Slide gen capability
├── orchestrator/                # Orchestrator layer
│   └── runtime/
│       ├── workflow_base.py              # Workflow base class
│       └── slide_generation_workflow.py  # Slide generation workflow
└── examples/                    # Example scripts
```

## API Documentation / API仕様

### ResearchService

Gathers structured information about a topic using LLM knowledge.

**Input:**
```python
{
    "topic": str,              # Research topic
    "language": str,           # Output language (default: "Japanese")
    "depth": str,              # "basic", "medium", or "detailed"
    "focus_areas": List[str],  # Optional focus areas
    "temperature": float,      # Generation temperature (default: 0.3)
    "max_tokens": int          # Max tokens (default: 1000)
}
```

**Output:**
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

Creates structured slide outlines from topics.

**Input:**
```python
{
    "topic": str,                    # Slide topic
    "n_slides": int,                 # Number of slides (1-50)
    "language": str,                 # Output language
    "temperature": float,            # Generation temperature
    "max_tokens": int,               # Max tokens
    "custom_instructions": str       # Optional custom instructions
}
```

**Output:**
```python
{
    "outline": str,
    "meta": dict
}
```

### SlideGenService

Generates presentation files from outline text.

**Input:**
```python
{
    "content": str,       # Outline text
    "n_slides": int,      # Number of slides (1-100)
    "language": str,      # Language
    "template": str,      # Template name (default: "general")
    "export_as": str      # Export format (default: "pptx")
}
```

**Output:**
```python
{
    "presentation_id": str,
    "file_path": str,
    "download_url": str,
    "status": str
}
```

### SlideGenerationWorkflow

Complete orchestrated workflow: Research → Refine → SlideGen

**Input:**
```python
{
    "topic": str,
    "n_slides": int,
    "language": str,           # default: "Japanese"
    "research_depth": str,     # default: "medium"
    "focus_areas": List[str],  # optional
    "template": str,           # default: "general"
    "export_as": str           # default: "pptx"
}
```

**Output:**
```python
{
    "success": bool,
    "steps": [...],           # Step execution details
    "workflow": {...},        # Workflow metadata
    "result": {
        "topic": str,
        "presentation_id": str,
        "file_path": str,
        "download_url": str
    }
}
```

## Features in Detail / 詳細機能

### 1. Provider Layer / Provider層

- **Abstraction**: Unified interface for different LLM and slide providers
- **Error Mapping**: Standardized error codes across providers
- **Retry Logic**: Exponential backoff with configurable retry policies
- **HTTP Transport**: Async HTTP client with timeout and auth handling
- **Observability**: Built-in tracing, metrics, and structured logging

### 2. Capability Layer / Capability層

- **Business Logic**: High-level abstractions for common tasks
- **Input Validation**: Pydantic-based request/response validation
- **Prompt Management**: Centralized prompt templates
- **Provider Agnostic**: Can switch providers without changing code

### 3. Orchestrator Layer / Orchestrator層

- **Workflow Definition**: Declarative step-based workflows
- **Data Flow**: Automatic data passing between steps
- **Error Handling**: Step-level error handling and recovery
- **Progress Tracking**: Detailed execution metrics per step
- **Retry Support**: Configurable retry logic per step

## Development / 開発

### Running Tests / テスト実行

```bash
# Run all example tests
python -m examples.orchestrator_smoke
python -m examples.service_smoke
python -m examples.research_smoke
```

### Adding a New Provider / 新しいProviderの追加

1. Create a new provider class inheriting from `Provider`
2. Implement `generate()` and/or `slide_gen()` methods
3. Add provider-specific error mapping
4. Test with smoke tests

### Adding a New Capability / 新しいCapabilityの追加

1. Create a new service class inheriting from `CapabilityBase`
2. Implement `execute()` and `_do_execute()` methods
3. Define request/response models with Pydantic
4. Add to workflow if needed

## Troubleshooting / トラブルシューティング

### OpenAI API Errors

- **401 Unauthorized**: Check `OPENAI_API_KEY` in `.env`
- **429 Rate Limited**: Retry logic will handle this automatically
- **Timeout**: Increase `timeout_ms` in `ExecCtx`

### Presenton Connection Errors

- Ensure Presenton server is running on `http://localhost:5001`
- Check server logs for errors
- Workflow will automatically retry once on failure

### Ollama Errors

- Ensure Ollama is running: `ollama serve`
- Check model is downloaded: `ollama pull llama3:8b`
- Verify `OLLAMA_BASE` environment variable

## License / ライセンス

[Your License Here]

## Contributing / 貢献

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments / 謝辞

- OpenAI for GPT models
- Ollama for local LLM support
- Presenton for slide generation capabilities
