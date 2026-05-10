from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest


@pytest.fixture
def fake_state(tmp_path):
    return {
        "repo_path": str(tmp_path),
        "staged_files": [
            {
                "path": "src/app.py",
                "status": "M",
                "language": "python",
                "is_binary": False,
                "is_test": False,
            }
        ],
        "raw_diff": "",
        "diff_hash": "",
        "diff_was_chunked": False,
        "commit_history": [],
        "linked_issues": [],
        "is_first_commit": False,
        "is_detached_head": False,
        "current_branch": "main",
        "pr_template": None,
        "codeowners": None,
        "past_pr_styles": [],
        "config": {
            "gemini_api_key": "test-key",
            "flash_model": "gemini-1.5-flash",
            "pro_model": "gemini-1.5-pro",
            "max_diff_lines": 800,
            "chunk_size_lines": 200,
            "max_commit_history": 20,
            "max_past_prs": 5,
            "base_branch": "main",
            "retry_attempts": 1,
            "retry_wait": 0.01,
            "flash_threshold_lines": 200,
            "flash_threshold_files": 2,
            "ast_max_file_size_kb": 500,
        },
        "route_decision": "",
        "trivial_reason": None,
        "ast_results": [],
        "ast_single_results": [],
        "ast_failed_files": [],
        "used_fallback": False,
        "is_breaking_change": False,
        "breaking_change_details": [],
        "tests_modified": False,
        "test_coverage_gaps": [],
        "reviewer_suggestions": [],
        "pr_structure": None,
        "pr_markdown": None,
        "user_action": None,
    }


@pytest.fixture
def mock_repo():
    commit = SimpleNamespace(
        hexsha="abcdef1234567890",
        message="Fix app behavior\n\nCloses #123",
        author=SimpleNamespace(name="Alice"),
        committed_datetime=datetime(2026, 5, 10, tzinfo=UTC),
    )
    repo = SimpleNamespace()
    repo.working_tree_dir = "/repo"
    repo.active_branch = "feature/test"
    repo.head = SimpleNamespace(commit=SimpleNamespace(hexsha="1234567890abcdef"))
    repo.iter_commits = lambda max_count=20: [commit]
    return repo


@pytest.fixture
def mock_gemini_adapter():
    class MockGeminiAdapter:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.calls: list[str] = []

        def complete(self, prompt: str) -> str:
            self.calls.append(prompt)
            return "File summary"

        def complete_json(self, prompt: str) -> dict[str, Any]:
            self.calls.append(prompt)
            return {
                "title": "Update app behavior",
                "summary": "Updates the app behavior for tests.",
                "changes": ["Changed app behavior"],
                "breaking_change_note": None,
                "testing_notes": "Not run.",
                "reviewer_suggestions": ["Alice"],
                "risk_level": "low",
                "linked_issues": ["#123"],
            }

        def complete_streaming(self, prompt: str, console: Any) -> str:
            self.calls.append(prompt)
            return (
                '{"title":"Update app behavior","summary":"Updates the app behavior for tests.",'
                '"changes":["Changed app behavior"],"breaking_change_note":null,'
                '"testing_notes":"Not run.","reviewer_suggestions":["Alice"],'
                '"risk_level":"low","linked_issues":["#123"]}'
            )

    return MockGeminiAdapter


@pytest.fixture
def temp_repo(tmp_path):
    (tmp_path / "src").mkdir()
    return tmp_path
