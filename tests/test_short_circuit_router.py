from __future__ import annotations

from pr_prep_agent.nodes.short_circuit_router import short_circuit_router


def test_docs_only_is_trivial(fake_state):
    fake_state["staged_files"] = [{"path": "README.md", "is_test": False}]

    result = short_circuit_router(fake_state)

    assert result["route_decision"] == "trivial"


def test_version_bump_package_json_is_trivial(fake_state):
    fake_state["staged_files"] = [{"path": "package.json", "is_test": False}]
    fake_state["raw_diff"] = (
        "diff --git a/package.json b/package.json\n"
        "--- a/package.json\n+++ b/package.json\n"
        '-  "version": "0.1.0"\n+  "version": "0.2.0"'
    )

    result = short_circuit_router(fake_state)

    assert result["route_decision"] == "trivial"


def test_small_diff_uses_flash(fake_state):
    fake_state["raw_diff"] = "diff --git a/app.py b/app.py\n+print('hi')"
    fake_state["staged_files"] = [{"path": "app.py", "is_test": False}]

    result = short_circuit_router(fake_state)

    assert result["route_decision"] == "flash"


def test_large_multi_file_diff_uses_pro(fake_state):
    fake_state["raw_diff"] = "\n".join(f"+line {i}" for i in range(300))
    fake_state["staged_files"] = [
        {"path": "a.py", "is_test": False},
        {"path": "b.py", "is_test": False},
        {"path": "c.py", "is_test": False},
    ]

    result = short_circuit_router(fake_state)

    assert result["route_decision"] == "pro"


def test_revert_with_mostly_deletions_is_trivial(fake_state):
    fake_state["raw_diff"] = "\n".join([f"-line {i}" for i in range(20)] + ["+one"])
    fake_state["commit_history"] = [{"message": "Revert previous feature"}]

    result = short_circuit_router(fake_state)

    assert result["route_decision"] == "trivial"
