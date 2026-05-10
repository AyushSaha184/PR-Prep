from __future__ import annotations

from types import SimpleNamespace

from pr_prep_agent.nodes import ast_single_file


class FakeRepo:
    old_content = ""

    def __init__(self, *args, **kwargs) -> None:
        self.git = SimpleNamespace(show=lambda _spec: self.old_content)


def test_file_over_500kb_is_skipped(tmp_path):
    path = tmp_path / "big.py"
    path.write_text("x" * (501 * 1024), encoding="utf-8")

    result = ast_single_file.parse_single_file(
        {
            "file_path": "big.py",
            "language": "python",
            "repo_path": str(tmp_path),
            "status": "M",
            "ast_max_file_size_kb": 500,
        }
    )

    assert result == {"file": "big.py", "status": "failed", "reason": "file_too_large"}


def test_python_removed_function_reports_breaking_change(tmp_path, monkeypatch):
    path = tmp_path / "app.py"
    path.write_text("def kept():\n    pass\n", encoding="utf-8")
    FakeRepo.old_content = "def kept():\n    pass\n\ndef removed():\n    pass\n"
    monkeypatch.setattr(ast_single_file, "Repo", FakeRepo)

    result = ast_single_file.parse_single_file(
        {"file_path": "app.py", "language": "python", "repo_path": str(tmp_path), "status": "M"}
    )

    assert result["status"] == "ok"
    assert result["breaking_changes"] == ["removed"]


def test_new_file_has_no_breaking_changes(tmp_path, monkeypatch):
    path = tmp_path / "new.py"
    path.write_text("def created():\n    pass\n", encoding="utf-8")

    class NewRepo:
        def __init__(self, *args, **kwargs) -> None:
            self.git = SimpleNamespace(show=lambda _spec: (_ for _ in ()).throw(Exception("new")))

    monkeypatch.setattr(ast_single_file, "Repo", NewRepo)

    result = ast_single_file.parse_single_file(
        {"file_path": "new.py", "language": "python", "repo_path": str(tmp_path), "status": "A"}
    )

    assert result["breaking_changes"] == []


def test_deleted_file_is_handled(tmp_path, monkeypatch):
    FakeRepo.old_content = "def removed():\n    pass\n"
    monkeypatch.setattr(ast_single_file, "Repo", FakeRepo)

    result = ast_single_file.parse_single_file(
        {"file_path": "gone.py", "language": "python", "repo_path": str(tmp_path), "status": "D"}
    )

    assert result["status"] == "ok"
    assert result["change_type"] == "deleted"


def test_unsupported_language_returns_failed(tmp_path):
    result = ast_single_file.parse_single_file(
        {"file_path": "app.rb", "language": "ruby", "repo_path": str(tmp_path), "status": "M"}
    )

    assert result["status"] == "failed"
