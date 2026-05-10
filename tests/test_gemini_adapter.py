from __future__ import annotations

import pytest

from pr_prep_agent.llm import gemini_adapter
from pr_prep_agent.llm.gemini_adapter import GeminiAdapter


class Chunk:
    def __init__(self, text: str) -> None:
        self.text = text


def test_complete_json_strips_json_fences(monkeypatch):
    class Model:
        def generate_content(self, _prompt):
            return Chunk('```json\n{"title": "Hello"}\n```')

    monkeypatch.setattr(gemini_adapter.genai, "configure", lambda api_key: None)
    monkeypatch.setattr(gemini_adapter.genai, "GenerativeModel", lambda model: Model())

    adapter = GeminiAdapter("key", "model", retry_attempts=1, retry_wait=0.01)

    assert adapter.complete_json("prompt") == {"title": "Hello"}


def test_retry_succeeds_on_second_attempt(monkeypatch):
    class Model:
        def __init__(self) -> None:
            self.calls = 0

        def generate_content(self, _prompt):
            self.calls += 1
            if self.calls == 1:
                raise ValueError("temporary")
            return Chunk("ok")

    model = Model()
    monkeypatch.setattr(gemini_adapter.genai, "configure", lambda api_key: None)
    monkeypatch.setattr(gemini_adapter.genai, "GenerativeModel", lambda _model: model)

    adapter = GeminiAdapter("key", "model", retry_attempts=2, retry_wait=0.01)

    assert adapter.complete("prompt") == "ok"
    assert model.calls == 2


def test_raises_runtime_error_after_retries(monkeypatch):
    class Model:
        def generate_content(self, _prompt):
            raise ValueError("down")

    monkeypatch.setattr(gemini_adapter.genai, "configure", lambda api_key: None)
    monkeypatch.setattr(gemini_adapter.genai, "GenerativeModel", lambda _model: Model())

    adapter = GeminiAdapter("key", "model", retry_attempts=1, retry_wait=0.01)

    with pytest.raises(RuntimeError, match="LLM call failed"):
        adapter.complete("prompt")


def test_complete_streaming_accumulates_chunks(monkeypatch):
    class Model:
        def generate_content_stream(self, _prompt):
            return [Chunk("a"), Chunk("b"), Chunk("c")]

    monkeypatch.setattr(gemini_adapter.genai, "configure", lambda api_key: None)
    monkeypatch.setattr(gemini_adapter.genai, "GenerativeModel", lambda _model: Model())

    adapter = GeminiAdapter("key", "model", retry_attempts=1, retry_wait=0.01)

    assert adapter.complete_streaming("prompt", gemini_adapter.Console()) == "abc"
