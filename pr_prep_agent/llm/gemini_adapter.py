"""Gemini adapter with retry and streaming support."""

from __future__ import annotations

import json
import re
from typing import Any, cast

import google.generativeai as genai
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from tenacity import RetryCallState, retry, stop_after_attempt, wait_exponential

from pr_prep_agent.logger import get_logger

log = get_logger()


def strip_json_fences(text: str) -> str:
    stripped = text.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, flags=re.DOTALL | re.IGNORECASE)
    return fenced.group(1).strip() if fenced else stripped


class GeminiAdapter:
    """Small wrapper around google-generativeai."""

    def __init__(
        self,
        api_key: str,
        model: str,
        retry_attempts: int = 3,
        retry_wait: float = 2.0,
    ) -> None:
        self.api_key = api_key
        self.model_name = model
        self.retry_attempts = retry_attempts
        self.retry_wait = retry_wait
        genai_any = cast(Any, genai)
        genai_any.configure(api_key=api_key)
        self.model = genai_any.GenerativeModel(model)

    def _before_sleep(self, retry_state: RetryCallState) -> None:
        log.warning(
            "gemini_call",
            model=self.model_name,
            attempt=retry_state.attempt_number,
            prompt_len=len(retry_state.args[1]) if len(retry_state.args) > 1 else 0,
        )

    def complete(self, prompt: str) -> str:
        @retry(
            stop=stop_after_attempt(self.retry_attempts),
            wait=wait_exponential(multiplier=self.retry_wait, min=1, max=30),
            before_sleep=self._before_sleep,
            reraise=True,
        )
        def _call(inner_prompt: str) -> str:
            response = self.model.generate_content(inner_prompt)
            return str(getattr(response, "text", ""))

        try:
            log.warning(
                "gemini_call",
                model=self.model_name,
                attempt=1,
                prompt_len=len(prompt),
            )
            return _call(prompt)
        except Exception as exc:
            raise RuntimeError(f"LLM call failed after {self.retry_attempts} attempts.") from exc

    def complete_json(self, prompt: str) -> dict[str, Any]:
        response = self.complete(f"{prompt}\n\nRespond only with a JSON object.")
        return cast(dict[str, Any], json.loads(strip_json_fences(response)))

    def complete_streaming(self, prompt: str, console: Console) -> str:
        @retry(
            stop=stop_after_attempt(self.retry_attempts),
            wait=wait_exponential(multiplier=self.retry_wait, min=1, max=30),
            before_sleep=self._before_sleep,
            reraise=True,
        )
        def _call(inner_prompt: str) -> str:
            accumulated = ""
            stream = cast(Any, self.model).generate_content_stream(inner_prompt)
            with Live(Markdown(""), console=console, refresh_per_second=12) as live:
                for chunk in stream:
                    token = str(getattr(chunk, "text", ""))
                    accumulated += token
                    live.update(Markdown(accumulated))
            return accumulated

        try:
            log.warning(
                "gemini_call",
                model=self.model_name,
                attempt=1,
                prompt_len=len(prompt),
            )
            return _call(prompt)
        except Exception as exc:
            raise RuntimeError(f"LLM call failed after {self.retry_attempts} attempts.") from exc
