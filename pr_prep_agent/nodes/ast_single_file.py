"""Parse one file and compare old/new symbols."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from git import Repo

from pr_prep_agent.logger import get_logger
from pr_prep_agent.tools.ast_tools import SUPPORTED_LANGUAGES, extract_symbols

log = get_logger()


def ast_single_file(input_state: dict[str, Any]) -> dict[str, Any]:
    node = "ast_single_file"
    file_path = str(input_state.get("file_path", ""))
    log.info("node_start", node=node, file=file_path)
    try:
        result = parse_single_file(input_state)
        log.info("node_complete", node=node, file=file_path, status=result.get("status"))
        return {"ast_single_results": [result]}
    except Exception as exc:
        log.warning("ast_failure", file=file_path, reason=str(exc))
        return {"ast_single_results": [{"file": file_path, "status": "failed", "reason": str(exc)}]}


def parse_single_file(input_state: dict[str, Any]) -> dict[str, Any]:
    file_path = str(input_state["file_path"])
    language = input_state.get("language")
    repo_path = Path(str(input_state["repo_path"]))
    status = str(input_state.get("status", "M"))
    if language not in SUPPORTED_LANGUAGES:
        return {"file": file_path, "status": "failed", "reason": "unsupported_language"}

    absolute = repo_path / file_path
    max_size = int(input_state.get("ast_max_file_size_kb", 500))
    if absolute.exists() and absolute.stat().st_size > max_size * 1024:
        log.warning("file_size_skip", file=file_path)
        return {"file": file_path, "status": "failed", "reason": "file_too_large"}

    new_content = (
        "" if status == "D" or not absolute.exists() else absolute.read_text(encoding="utf-8")
    )
    repo = Repo(str(repo_path), search_parent_directories=True)
    try:
        old_content = repo.git.show(f"HEAD:{file_path}")
    except Exception:
        old_content = ""

    old_symbols = extract_symbols(old_content, str(language)) if old_content else []
    new_symbols = extract_symbols(new_content, str(language)) if new_content else []
    removed = sorted(set(old_symbols) - set(new_symbols))
    change_type = "deleted" if status == "D" else "added" if not old_content else "modified"
    detail = f"{len(old_symbols)} old symbols, {len(new_symbols)} new symbols"
    return {
        "file": file_path,
        "status": "ok",
        "old_symbols": old_symbols,
        "new_symbols": new_symbols,
        "breaking_changes": removed,
        "change_type": change_type,
        "detail": detail,
        "reason": None,
    }
