"""Unit tests for Phase 5 LLMClient, ModelRouter, and prompt registry."""
import pytest
from pydantic import BaseModel

from backend.core.exceptions import ValidationError
from backend.prompts.registry import get_prompt_template, render_user_prompt
from backend.tools.llm_client import LLMClient
from backend.tools.model_router import select_model_for_agent


class SampleSchema(BaseModel):
    message: str


@pytest.mark.asyncio
async def test_llm_client_structured_generation() -> None:
    client = LLMClient()
    response = await client.generate_structured(
        system_prompt="You are a reviewer",
        user_prompt="Review diff",
        response_schema=SampleSchema,
        model="gpt-4o",
    )
    assert response.model == "gpt-4o"
    assert response.tokens_in > 0
    assert response.tokens_out > 0
    assert response.cost_usd > 0.0
    assert response.latency_ms >= 0


def test_model_router_selection() -> None:
    assert select_model_for_agent("security") == "gpt-4o"
    assert select_model_for_agent("tests") == "gpt-4o-mini"
    assert select_model_for_agent("docs") == "gpt-4o-mini"


def test_prompt_registry() -> None:
    security_prompt = get_prompt_template("security_v1")
    assert "UNTRUSTED DATA" in security_prompt["system"]

    rendered = render_user_prompt("quality_v1", diff="+ line 1", context="context snippet")
    assert "+ line 1" in rendered
    assert "context snippet" in rendered


def test_invalid_prompt_template_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        get_prompt_template("non_existent_prompt")
