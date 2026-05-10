"""Configuration loading for pr-prep."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import toml


@dataclass(frozen=True)
class Config:
    gemini_api_key: str | None = None
    flash_model: str = "gemini-1.5-flash"
    pro_model: str = "gemini-1.5-pro"
    max_diff_lines: int = 800
    chunk_size_lines: int = 200
    max_commit_history: int = 20
    max_past_prs: int = 5
    base_branch: str = "main"
    retry_attempts: int = 3
    retry_wait: float = 2.0
    flash_threshold_lines: int = 200
    flash_threshold_files: int = 2
    ast_max_file_size_kb: int = 500

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ENV_MAP = {
    "GEMINI_API_KEY": "gemini_api_key",
    "PR_PREP_MODEL": "pro_model",
    "PR_PREP_FLASH_MODEL": "flash_model",
    "PR_PREP_PRO_MODEL": "pro_model",
    "PR_PREP_MAX_DIFF_LINES": "max_diff_lines",
    "PR_PREP_CHUNK_SIZE_LINES": "chunk_size_lines",
    "PR_PREP_MAX_COMMIT_HISTORY": "max_commit_history",
    "PR_PREP_MAX_PAST_PRS": "max_past_prs",
    "PR_PREP_BASE_BRANCH": "base_branch",
    "PR_PREP_RETRY_ATTEMPTS": "retry_attempts",
    "PR_PREP_RETRY_WAIT": "retry_wait",
    "PR_PREP_FLASH_THRESHOLD_LINES": "flash_threshold_lines",
    "PR_PREP_FLASH_THRESHOLD_FILES": "flash_threshold_files",
    "PR_PREP_AST_MAX_FILE_SIZE_KB": "ast_max_file_size_kb",
}

INT_FIELDS = {
    "max_diff_lines",
    "chunk_size_lines",
    "max_commit_history",
    "max_past_prs",
    "retry_attempts",
    "flash_threshold_lines",
    "flash_threshold_files",
    "ast_max_file_size_kb",
}
FLOAT_FIELDS = {"retry_wait"}


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = toml.load(path)
    return data if isinstance(data, dict) else {}


def _coerce(field: str, value: str) -> Any:
    if field in INT_FIELDS:
        return int(value)
    if field in FLOAT_FIELDS:
        return float(value)
    return value


def load_config(repo_path: str | Path) -> Config:
    """Load defaults, user config, repo config, then environment overrides."""
    merged: dict[str, Any] = Config().to_dict()
    merged.update(_load_toml(Path.home() / ".prprep.toml"))
    merged.update(_load_toml(Path(repo_path) / ".prprep.toml"))
    for env_name, field in ENV_MAP.items():
        value = os.environ.get(env_name)
        if value:
            merged[field] = _coerce(field, value)
    return Config(**merged)
