"""File classification helpers."""

from __future__ import annotations

from pathlib import Path

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".exe",
    ".dll",
    ".so",
    ".pyc",
    ".class",
    ".jar",
    ".db",
    ".sqlite",
    ".lock",
    ".mp4",
    ".mp3",
    ".wav",
}

LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".cpp": "cpp",
    ".cc": "cpp",
}

TEST_PATTERNS = ("test_", "_test.", "/tests/", "/test/", "spec/", ".spec.", ".test.")


def normalize_repo_path(path: str | Path) -> str:
    return str(Path(path).resolve())


def detect_language(path: str | Path) -> str | None:
    return LANGUAGE_BY_EXTENSION.get(Path(path).suffix.lower())


def is_binary_file(path: str | Path) -> bool:
    file_path = Path(path)
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        with file_path.open("rb") as handle:
            return b"\x00" in handle.read(1024)
    except FileNotFoundError:
        return False
    except OSError:
        return False


def is_test_file(path: str | Path) -> bool:
    normalized = str(path).replace("\\", "/").lower()
    return any(pattern in normalized for pattern in TEST_PATTERNS)


def find_corresponding_tests(repo_path: str | Path, source_path: str) -> list[str]:
    base = Path(source_path).stem.lower()
    matches: list[str] = []
    root = Path(repo_path)
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(root).as_posix()
        if is_test_file(rel) and base in file_path.name.lower():
            matches.append(rel)
    return matches
