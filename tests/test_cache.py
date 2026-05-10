from __future__ import annotations

from pr_prep_agent import cache


def test_save_writes_cache_structure(tmp_path):
    pr_structure = {"title": "Test PR"}

    cache.save("abc", tmp_path, pr_structure, "main")

    content = (tmp_path / ".prprep" / "cache.json").read_text(encoding="utf-8")
    assert '"abc"' in content
    assert '"branch": "main"' in content
    assert '"title": "Test PR"' in content


def test_load_returns_pr_structure_on_hash_match(tmp_path):
    pr_structure = {"title": "Test PR"}
    cache.save("abc", tmp_path, pr_structure, "main")

    result = cache.load("abc", tmp_path)

    assert result == pr_structure


def test_load_returns_none_on_hash_miss(tmp_path):
    cache.save("abc", tmp_path, {"title": "Test PR"}, "main")

    assert cache.load("missing", tmp_path) is None


def test_clear_deletes_cache_file(tmp_path):
    cache.save("abc", tmp_path, {"title": "Test PR"}, "main")

    cache.clear(tmp_path)

    assert not (tmp_path / ".prprep" / "cache.json").exists()


def test_cache_errors_are_swallowed(tmp_path, monkeypatch):
    blocker = tmp_path / "blocker"
    blocker.write_text("not a dir", encoding="utf-8")
    monkeypatch.setattr(cache, "_cache_path", lambda _repo_path: blocker / "cache.json")

    cache.save("abc", tmp_path, {"title": "Test PR"}, "main")

    assert cache.load("abc", tmp_path) is None
