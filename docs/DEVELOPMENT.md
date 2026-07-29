# PR Prep — Developer Experience & Contribution Guide

## 1. Quickstart & Local Setup

### Environment Requirements
- Python 3.12+ (or Python 3.14)
- Node.js 18+ and npm
- Docker and Docker Compose

### One-Command Setup
1. Create virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start local storage infrastructure:
   ```bash
   docker-compose up -d postgres redis
   ```
3. Run verification suite:
   ```bash
   .venv/bin/pytest tests/ -v
   .venv/bin/ruff check backend/ tests/
   .venv/bin/mypy backend/ tests/
   ```

---

## 2. Project Architecture & Modular Monolith

- **`backend/core/`**: Abstract workflow interfaces, Settings loader, base exceptions. **ZERO dependencies on outer submodules.**
- **`backend/models/`**: Enums, Finding schemas, Review state, Webhook event models.
- **`backend/memory/`**: 256-dim EmbedderClient (`text-embedding-3-large`), TigerMemoryClient (DiskANN + FTS GIN + RRF), ContextRetriever.
- **`backend/orchestrator/`**: LangGraph StateGraph engine, node functions (`security`, `quality`, `tests`, `docs`), parallel fan-out join, checkpointing.
- **`backend/agents/`**: Specialist agents (`SecurityAgent`, `QualityAgent`, `TestAgent`, `DocsAgent`) and deterministic `FindingAggregator`.
- **`backend/tools/`**: `ToolRegistry`, `CapabilityScope` (least-privilege validator), `DockerSandbox`, `PromptPlayground`.

---

## 3. Testing & Verification Discipline

Run full verification before submitting PRs:
```bash
.venv/bin/pytest tests/ -v
.venv/bin/ruff check backend/ tests/
.venv/bin/mypy backend/ tests/
cd frontend && npm run build
```

---

## 4. Prompt Playground Workflow

Test new or modified specialist prompts safely without posting to GitHub:
```python
from backend.tools.prompt_playground import PromptPlayground

playground = PromptPlayground()
result = await playground.test_prompt(
    prompt_name="security_v1",
    diff_text="+ SELECT * FROM users WHERE name = '%s'",
    model_name="gpt-4o",
)
print(result)
```
