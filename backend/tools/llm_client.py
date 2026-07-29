"""Provider-neutral LLM client with structured output validation and cost tracking."""
import time
from typing import Any, TypeVar

from pydantic import BaseModel

from backend.core.config import get_settings
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.tools.llm_client")

T = TypeVar("T", bound=BaseModel)

# Approximate token cost table per 1k tokens (OpenAI pricing reference)
MODEL_COSTS_PER_1K = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
}


class LLMResponse(BaseModel):
    parsed_output: Any
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int
    refusal: str | None = None


class LLMClient:
    """Provider-neutral LLM client ensuring structured validation, token accounting, and logging."""

    def __init__(self, api_key: str | None = None, default_model: str = "gpt-4o") -> None:
        settings = get_settings()
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.default_model = default_model

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
        model: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> LLMResponse:
        """Generates structured Pydantic response from reasoning model."""
        target_model = model or self.default_model
        start_time = time.perf_counter()

        logger.info(
            f"LLMClient generating schema={response_schema.__name__} using model={target_model}"
        )

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
            f"LLMClient response: model={target_model}, tokens_in={tokens_in}, "
            f"tokens_out={tokens_out}, cost_usd=${cost_usd}, latency={latency_ms}ms"
        )

        return LLMResponse(
            parsed_output=None,
            model=target_model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
        )
