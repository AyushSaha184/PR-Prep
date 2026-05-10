# Contributing

## Development Setup

```bash
git clone https://github.com/your-username/pr-prep
cd pr-prep
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # then add your GEMINI_API_KEY
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

## Tests

```bash
pytest tests/ -v
```

All external calls should be mocked in unit tests. Tests should not require a real Gemini key, GitHub login, or live Git repository.

## Linting

```bash
ruff check .
ruff format .
```

## Branching

Use concise branch prefixes:

- `feat/`
- `fix/`
- `chore/`
- `docs/`

## PR Checklist

- Tests pass locally.
- Linting is clean.
- README or examples are updated when behavior changes.
- New external calls are mocked in tests.
- Config or cache behavior is documented when changed.

## Adding a Supported Language

1. Add the file extension and language key to `LANGUAGE_BY_EXTENSION` in `pr_prep_agent/tools/file_tools.py`.
2. Add the language key to `SUPPORTED_LANGUAGES` in `pr_prep_agent/tools/ast_tools.py`.
3. Add the tree-sitter package to `pyproject.toml`.
4. Add a grammar import branch in `_language_module`.
5. Add regex fallback patterns for symbol extraction.
6. Add tests for added, modified, and removed symbols.

