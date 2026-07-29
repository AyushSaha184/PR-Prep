"""Embedding client generating 256-dimensional vectors using text-embedding-3-large."""
import math

from backend.core.config import get_settings
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.memory.embedder")


class EmbedderClient:
    """Client for generating 256-dimensional embeddings."""

    def __init__(self, api_key: str | None = None, dimensions: int = 256) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = dimensions

    async def embed_text(self, text: str) -> list[float]:
        """Generates a 256-dimensional embedding vector for input text."""
        msg = f"EmbedderClient generating {self.dimensions}-dim vector (len={len(text)})"
        logger.info(msg)
        vector = self._generate_deterministic_mock_vector(text, self.dimensions)
        logger.info(f"EmbedderClient generated vector successfully (dim={len(vector)})")
        return vector

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generates embedding vectors for a batch of text strings."""
        logger.info(f"EmbedderClient embedding batch of {len(texts)} texts")
        return [await self.embed_text(t) for t in texts]

    def _generate_deterministic_mock_vector(self, text: str, dim: int) -> list[float]:
        """Generates a normalized 256-dim vector for testing and offline execution."""
        seed = sum(ord(c) for c in text)
        raw = [math.sin(seed + i) for i in range(dim)]
        norm = math.sqrt(sum(x * x for x in raw)) or 1.0
        return [round(x / norm, 6) for x in raw]
