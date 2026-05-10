from __future__ import annotations

from pr_prep_agent.nodes.trivial_formatter import trivial_formatter


def test_version_bump_title(fake_state):
    fake_state["trivial_reason"] = "Version bump only"
    fake_state["staged_files"] = [{"path": "package.json"}]
    fake_state["raw_diff"] = '-  "version": "0.1.0"\n+  "version": "0.2.0"'

    result = trivial_formatter(fake_state)

    assert result["pr_structure"]["title"] == "chore: bump version to 0.2.0"


def test_docs_only_title(fake_state):
    fake_state["trivial_reason"] = "Documentation-only change"
    fake_state["staged_files"] = [{"path": "README.md"}]

    result = trivial_formatter(fake_state)

    assert result["pr_structure"]["title"] == "docs: update README.md"


def test_revert_title_and_medium_risk(fake_state):
    fake_state["trivial_reason"] = "Clean revert"
    fake_state["commit_history"] = [{"message": "Revert add feature"}]

    result = trivial_formatter(fake_state)

    assert result["pr_structure"]["title"].startswith("revert:")
    assert result["pr_structure"]["risk_level"] == "medium"
