# PR Prep Agent

`pr-prep` is an AI-powered CLI that prepares GitHub pull requests from staged changes. Run it inside a local Git repository after `git add`; it reads the staged diff, infers intent, generates a title and PR body, surfaces risk flags and reviewer suggestions, lets you review or edit the draft, and can submit the PR through the `gh` CLI.

The optimization model avoids unnecessary LLM work. Documentation-only, version-only, and clean revert diffs are formatted locally; small or test-only changes use Gemini Flash; complex or multi-module changes use Gemini Pro; repeated diffs are served from a local MD5 cache. AST parsing is fanned out per file through LangGraph's `Send` API, with raw-diff fallback for unsupported files.

## Prerequisites

Before installing `pr-prep`, ensure you have the following on your system:
- **Python 3.9+** (or compatible)
- **Git**
- **GitHub CLI (`gh`)**: Required to submit the PR to GitHub. (e.g., `brew install gh` on macOS, or `winget install gh` on Windows). Remember to authenticate by running `gh auth login`.

## Installation

Since `pr-prep` is a CLI tool, you can install it globally so it is available in any repository, or locally for development.

### Option 1: Global Install (Recommended)
To use the `pr-prep` command in any directory, install it via `pipx` (which isolates dependencies) or globally via `pip`:

```bash
# Using pipx (recommended for CLI apps)
pipx install .

# OR using pip (user level)
pip install --user .
```

### Option 2: Local / Development Install
If you are modifying the source code for `pr-prep`, use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Setup

To generate PRs, the agent requires a Gemini API key. Make sure it is exported in your terminal profile (e.g., `~/.bashrc` or `~/.zshrc` or Windows Environment Variables):

```bash
export GEMINI_API_KEY=your_key
```

You can also configure the tool globally via a `~/.prprep.toml` file, or per repository by creating a `.prprep.toml` file located in the root of your target repository.

## Usage

```bash
cd your-repo
git add .
pr-prep
```

Common options:

```bash
pr-prep --repo /path/to/repo
pr-prep --dry-run
pr-prep --no-clipboard
pr-prep --clear-cache
```

## Config Example

```toml
gemini_api_key = "your_key_here"
pro_model = "gemini-2.5-pro"
flash_model = "gemini-2.5-flash"
base_branch = "main"
max_diff_lines = 800
chunk_size_lines = 200
flash_threshold_lines = 200
flash_threshold_files = 2
ast_max_file_size_kb = 500
```

Environment variables override config files. `GEMINI_API_KEY`, `PR_PREP_MODEL`, and `PR_PREP_FLASH_MODEL` are supported.

## Routing

- `trivial`: documentation-only changes, version bumps, and clean reverts are formatted locally without an LLM call.
- `flash`: diffs under the configured line/file thresholds or test-only diffs use the Flash model.
- `pro`: larger, architectural, multi-module, or breaking changes use the Pro model.
- `cached`: if the staged diff hash already exists in `.prprep/cache.json`, the saved PR structure is reused.

## Human Review

Before submission, the generated markdown is shown in the terminal:

- `[S]ubmit`: copies the PR body to the clipboard and proceeds to `gh pr create`.
- `[E]dit`: opens the draft in `$EDITOR`, falling back to `nano`.
- `[A]bort`: exits without submitting.

## Cache

The cache lives at `.prprep/cache.json` inside the target repository and is keyed by the MD5 hash of the staged diff. The directory is added to `.gitignore` on first run. Use this to clear it:

```bash
pr-prep --clear-cache
```

## Supported AST Languages

AST parsing is supported for:

- Python (`.py`)
- JavaScript (`.js`, `.jsx`)
- TypeScript (`.ts`, `.tsx`)
- Java (`.java`)
- Go (`.go`)
- Rust (`.rs`)
- C++ (`.cpp`, `.cc`)

Unsupported or oversized files are summarized from the raw diff instead of failing the run.

