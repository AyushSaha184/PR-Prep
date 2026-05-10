"""Shared LangGraph state definitions."""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class PRContextState(TypedDict, total=False):
    repo_path: str
    staged_files: list[dict[str, Any]]
    raw_diff: str
    diff_hash: str
    diff_was_chunked: bool
    commit_history: list[dict[str, Any]]
    linked_issues: list[str]
    is_first_commit: bool
    is_detached_head: bool
    current_branch: str
    pr_template: str | None
    codeowners: str | None
    past_pr_styles: list[str]
    config: dict[str, Any]
    dry_run: bool
    no_clipboard: bool

    route_decision: str
    trivial_reason: str | None

    ast_results: list[dict[str, Any]]
    ast_single_results: Annotated[list[dict[str, Any]], operator.add]
    ast_failed_files: list[str]
    used_fallback: bool
    is_breaking_change: bool
    breaking_change_details: list[str]

    tests_modified: bool
    test_coverage_gaps: list[str]

    reviewer_suggestions: list[str]

    pr_structure: dict[str, Any] | None
    pr_markdown: str | None
    user_action: str | None
