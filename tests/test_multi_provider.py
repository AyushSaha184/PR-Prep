"""Unit tests for Multi-Provider AI integration: Google AI Studio and Nvidia NIM embeddings."""
import pytest
from pydantic import BaseModel

from backend.memory.embedder import EmbedderClient
from backend.tools.llm_client import LLMClient


class SampleModel(BaseModel):
    summary: str


@pytest.mark.asyncio
async def test_llm_client_google_ai_studio_provider() -> None:
    client = LLMClient()
    client.provider = "google_ai_studio"
    client.default_model = "gemini-1.5-pro"

    res = await client.generate_structured(
        system_prompt="Review diff",
        user_prompt="Gemini prompt test",
        response_schema=SampleModel,
    )
    assert res.provider == "google_ai_studio"
    assert res.model == "gemini-1.5-pro"
    assert res.tokens_in > 0
    assert res.cost_usd > 0.0


@pytest.mark.asyncio
async def test_embedder_nvidia_provider() -> None:
    embedder = EmbedderClient()
    embedder.provider = "nvidia"
    embedder.model = "nv-embed-v1"

    vector = await embedder.embed_text("def nvidia_test(): pass")
    assert embedder.provider == "nvidia"
    assert embedder.model == "nv-embed-v1"
    assert len(vector) == 256
