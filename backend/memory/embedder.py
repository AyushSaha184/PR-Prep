"""Embedding client generating 256-dimensional vectors using OpenAI or Nvidia NIM."""
import math

from backend.core.config import get_settings
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.memory.embedder")


class EmbedderClient:
    """Client for generating 256-dimensional embeddings (OpenAI or Nvidia NIM)."""

    def __init__(self, api_key: str | None = None, dimensions: int = 256) -> None:
        settings = get_settings()
        self.provider = settings.EMBEDDING_PROVIDER
        self.openai_key = api_key or settings.OPENAI_API_KEY
        self.nvidia_key = settings.NVIDIA_API_KEY
        self.model = (
            settings.NVIDIA_EMBEDDING_MODEL
            if self.provider == "nvidia"
            else settings.EMBEDDING_MODEL
        )
        self.dimensions = dimensions

    async def embed_text(self, text: str) -> list[float]:
        """Generates a 256-dimensional embedding vector for input text."""
        dim = self.dimensions
        msg = f"EmbedderClient [{self.provider}] generating {dim}-dim using {self.model}"
        logger.info(msg)

        if self.provider == "openai" and self.openai_key:
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=self.openai_key)
                res = await client.embeddings.create(
                    model=self.model,
                    input=text,
                    dimensions=self.dimensions,
                )
                vector = res.data[0].embedding
                logger.info(f"EmbedderClient [openai] API vector generated (dim={len(vector)})")
                return vector
            except Exception as e:
                logger.warning(f"OpenAI embedding call failed ({e}); using mock vector.")
        elif self.provider == "nvidia" and self.nvidia_key:
            try:
                import httpx
                url = "https://ai.api.nvidia.com/v1/retrieval/nvidia/embeddings"
                headers = {
                    "Authorization": f"Bearer {self.nvidia_key}",
                    "Accept": "application/json",
                }
                payload = {"input": [text], "model": self.model, "input_type": "passage"}
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, headers=headers, json=payload, timeout=10.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        vector = data["data"][0]["embedding"][:self.dimensions]
                        logger.info(
                            f"EmbedderClient [nvidia] API vector generated (dim={len(vector)})"
                        )
                        return vector
            except Exception as e:
                logger.warning(f"Nvidia embedding call failed ({e}); using mock vector.")

        vector = self._generate_deterministic_mock_vector(text, self.dimensions)
        logger.info(
            f"EmbedderClient [{self.provider}] fallback vector generated (dim={len(vector)})"
        )
        return vector

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generates embedding vectors for a batch of text strings."""
        logger.info(f"EmbedderClient [{self.provider}] embedding batch of {len(texts)} texts")
        return [await self.embed_text(t) for t in texts]

    def _generate_deterministic_mock_vector(self, text: str, dim: int) -> list[float]:
        """Generates a normalized 256-dim vector for testing and offline execution."""
        seed = sum(ord(c) for c in text)
        raw = [math.sin(seed + i) for i in range(dim)]
        norm = math.sqrt(sum(x * x for x in raw)) or 1.0
        return [round(x / norm, 6) for x in raw]
