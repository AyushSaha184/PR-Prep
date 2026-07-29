"""Role-protected Prompt Playground for testing specialist prompts locally."""
from pydantic import BaseModel

from backend.models.findings import Finding
from backend.observability.logging import setup_logger
from backend.prompts.registry import render_user_prompt
from backend.tools.llm_client import LLMClient

logger = setup_logger("pr_prep.tools.prompt_playground")


class PlaygroundResult(BaseModel):
    prompt_name: str
    target_model: str
    rendered_prompt: str
    findings: list[Finding]
    tokens_in: int
    tokens_out: int
    estimated_cost_usd: float
    latency_ms: int


class PromptPlayground:
    """Safe prompt experimentation engine for local testing against golden PR diffs."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    async def test_prompt(
        self,
        prompt_name: str,
        diff_text: str,
        context_text: str = "",
        model_name: str = "gpt-4o",
    ) -> PlaygroundResult:
        """Executes prompt against fixture diff without posting to GitHub or mutating live state."""
        logger.info(f"PromptPlayground testing prompt '{prompt_name}' using model='{model_name}'")

        rendered = render_user_prompt(prompt_name, diff=diff_text, context=context_text)
        res = await self.llm_client.generate_structured(
            system_prompt=f"Playground evaluation for {prompt_name}",
            user_prompt=rendered,
            response_schema=Finding,
            model=model_name,
        )

        msg = f"PromptPlayground done '{prompt_name}': tokens={res.tokens_in}, cost=${res.cost_usd}"
        logger.info(msg)

        return PlaygroundResult(
            prompt_name=prompt_name,
            target_model=model_name,
            rendered_prompt=rendered,
            findings=[],
            tokens_in=res.tokens_in,
            tokens_out=res.tokens_out,
            estimated_cost_usd=res.cost_usd,
            latency_ms=res.latency_ms,
        )
