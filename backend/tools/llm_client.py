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
        parsed_output: Any = None
        refusal: str | None = None

        if self.provider == "openai" and self.openai_key:
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=self.openai_key)
                response = await client.beta.chat.completions.parse(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format=response_schema,
                    timeout=timeout_seconds,
                )
                choice = response.choices[0]
                parsed_output = choice.message.parsed
                refusal = getattr(choice.message, "refusal", None)
                if response.usage:
                    tokens_in = response.usage.prompt_tokens
                    tokens_out = response.usage.completion_tokens
                else:
                    tokens_out = 150
            except Exception as e:
                logger.warning(f"OpenAI API call failed ({e}); using offline structure fallback.")
                tokens_out = 150
        elif self.provider == "google_ai_studio" and self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model_inst = genai.GenerativeModel(
                    model_name=target_model,
                    system_instruction=system_prompt,
                )
                response = await model_inst.generate_content_async(
                    user_prompt,
                    generation_config={"response_mime_type": "application/json"},
                )
                if hasattr(response_schema, "model_validate_json"):
                    parsed_output = response_schema.model_validate_json(response.text)
                else:
                    parsed_output = response.text
                tokens_out = len(response.text) // 4
            except Exception as e:
                logger.warning(
                    f"Google AI Studio API call failed ({e}); using offline structure fallback."
                )
                tokens_out = 150
        else:
            logger.info(
                f"No API key provided for provider '{self.provider}'; running in mock mode."
            )
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
            parsed_output=parsed_output,
            model=target_model,
            provider=self.provider,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            refusal=refusal,
        )
