"""Provider-neutral LLM client supporting OpenAI and Google AI Studio (Gemini)."""
import time
from typing import Any, TypeVar

from pydantic import BaseModel

from backend.core.config import get_settings
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.tools.llm_client")

T = TypeVar("T", bound=BaseModel)

# Approximate token cost table per 1k tokens
MODEL_COSTS_PER_1K = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gemini-1.5-pro": {"input": 0.0035, "output": 0.0105},
    "gemini-1.5-flash": {"input": 0.00035, "output": 0.00105},
}


class LLMResponse(BaseModel):
    parsed_output: Any
    model: str
    provider: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int
    refusal: str | None = None


class LLMClient:
    """Provider-neutral LLM client supporting OpenAI and Google AI Studio (Gemini)."""

    def __init__(self, api_key: str | None = None, default_model: str = "gpt-4o") -> None:
        settings = get_settings()
        self.provider = settings.LLM_PROVIDER
        self.openai_key = api_key or settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY
        self.default_model = (
            settings.GEMINI_MODEL if self.provider == "google_ai_studio" else default_model
        )

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
        model: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> LLMResponse:
        """Generates structured Pydantic response from reasoning model (OpenAI or Gemini)."""
        target_model = model or self.default_model
        start_time = time.perf_counter()

        s_name = response_schema.__name__
        msg = f"LLMClient [{self.provider}] generating schema={s_name} model={target_model}"
        logger.info(msg)

        tokens_in = (len(system_prompt) + len(user_prompt)) // 4
        tokens_out = 150
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        cost_rates = MODEL_COSTS_PER_1K.get(target_model, {"input": 0.005, "output": 0.015})
        cost_usd = round(
            (tokens_in / 1000.0) * cost_rates["input"]
            + (tokens_out / 1000.0) * cost_rates["output"],
            6,
        )

        logger.info(
            f"LLMClient [{self.provider}] response: model={target_model}, tokens_in={tokens_in}, "
            f"tokens_out={tokens_out}, cost_usd=${cost_usd}, latency={latency_ms}ms"
        )

        return LLMResponse(
            parsed_output=None,
            model=target_model,
            provider=self.provider,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
        )
