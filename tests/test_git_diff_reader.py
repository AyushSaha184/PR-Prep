from __future__ import annotations

from types import SimpleNamespace

import pytest

from pr_prep_agent.nodes import git_diff_reader as reader


class FakeGit:
    def __init__(self, raw_diff: str, name_status: str) -> None:
        self.raw_diff = raw_diff
        self.name_status = name_status

    def diff(self, *args: str) -> str:
        if "--name-status" in args:
            return self.name_status
        return self.raw_diff


def test_staged_diff_is_retrieved_and_stored(fake_state, mock_repo, monkeypatch):
    raw = "diff --git a/app.py b/app.py\n+print('hi')"
    mock_repo.git = FakeGit(raw, "M\tapp.py")
    monkeypatch.setattr(reader, "get_repo", lambda _path: mock_repo)
    monkeypatch.setattr(reader.cache, "load", lambda *_args: None)

    result = reader.git_diff_reader(fake_state)

    assert result["raw_diff"] == raw
    assert result["staged_files"][0]["path"] == "app.py"
    assert result["diff_hash"]


def test_detached_head_sets_sha_branch(fake_state, mock_repo, monkeypatch):
    raw = "diff --git a/app.py b/app.py\n+print('hi')"

    class DetachedRepo:
        working_tree_dir = str(fake_state["repo_path"])
        git = FakeGit(raw, "M\tapp.py")
        head = SimpleNamespace(commit=SimpleNamespace(hexsha="1234567890abcdef"))

        @property
        def active_branch(self):
            raise TypeError("detached")

        def iter_commits(self, max_count=20):
            return []

    monkeypatch.setattr(reader, "get_repo", lambda _path: DetachedRepo())
    monkeypatch.setattr(reader.cache, "load", lambda *_args: None)

    result = reader.git_diff_reader(fake_state)

    assert result["is_detached_head"] is True
    assert result["current_branch"] == "12345678"


def test_no_staged_files_raises(fake_state, mock_repo, monkeypatch):
    mock_repo.git = FakeGit("", "")
    monkeypatch.setattr(reader, "get_repo", lambda _path: mock_repo)

    with pytest.raises(RuntimeError, match="No staged changes found"):
        reader.git_diff_reader(fake_state)


def test_large_diff_is_chunked(fake_state, mock_repo, monkeypatch):
    section1 = "diff --git a/a.py b/a.py\n" + "\n".join(f"+line {i}" for i in range(900))
    section2 = "diff --git a/b.py b/b.py\n" + "\n".join(f"+line {i}" for i in range(900))
    mock_repo.git = FakeGit(f"{section1}\n{section2}", "M\ta.py\nM\tb.py")
    monkeypatch.setattr(reader, "get_repo", lambda _path: mock_repo)
    monkeypatch.setattr(reader.cache, "load", lambda *_args: None)

    result = reader.git_diff_reader(fake_state)

    assert result["diff_was_chunked"] is True
    assert "[701 lines truncated]" in result["raw_diff"]


def test_linked_issues_from_commit_messages(fake_state, mock_repo, monkeypatch):
    raw = "diff --git a/app.py b/app.py\n+print('hi')"
    mock_repo.git = FakeGit(raw, "M\tapp.py")
    monkeypatch.setattr(reader, "get_repo", lambda _path: mock_repo)
    monkeypatch.setattr(reader.cache, "load", lambda *_args: None)

    result = reader.git_diff_reader(fake_state)

    assert result["linked_issues"] == ["#123"]


def test_first_commit_sets_flag(fake_state, mock_repo, monkeypatch):
    raw = "diff --git a/app.py b/app.py\n+print('hi')"
    mock_repo.git = FakeGit(raw, "M\tapp.py")
    mock_repo.iter_commits = lambda max_count=20: []
    monkeypatch.setattr(reader, "get_repo", lambda _path: mock_repo)
    monkeypatch.setattr(reader.cache, "load", lambda *_args: None)

    result = reader.git_diff_reader(fake_state)

    assert result["is_first_commit"] is True
