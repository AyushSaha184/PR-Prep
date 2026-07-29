"""Unit tests for Phase 17 PromptPlayground runner."""
import pytest

from backend.tools.prompt_playground import PromptPlayground


@pytest.mark.asyncio
async def test_prompt_playground_execution() -> None:
    playground = PromptPlayground()
    res = await playground.test_prompt(
        prompt_name="security_v1",
        diff_text="+ SELECT * FROM users WHERE name = '%s'",
        model_name="gpt-4o",
    )

    assert res.prompt_name == "security_v1"
    assert res.target_model == "gpt-4o"
    assert res.tokens_in > 0
    assert res.estimated_cost_usd > 0.0
