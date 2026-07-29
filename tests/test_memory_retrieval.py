"""Unit tests for Phase 6 Memory Architecture, Embedder, Hybrid Search, and ContextRetriever."""
import pytest

from backend.data.freshness import FreshnessTracker
from backend.memory.context_retriever import ContextRetriever
from backend.memory.embedder import EmbedderClient
from backend.memory.tiger_client import TigerMemoryClient


@pytest.mark.asyncio
async def test_embedder_vector_generation() -> None:
    embedder = EmbedderClient(dimensions=256)
    vector = await embedder.embed_text("def test_function(): pass")
    assert len(vector) == 256
    assert isinstance(vector[0], float)


@pytest.mark.asyncio
async def test_tiger_hybrid_search_rrf() -> None:
    client = TigerMemoryClient()
    dummy_vector = [0.1] * 256
    results = await client.hybrid_search(
        repo="owner/repo",
        query_vector=dummy_vector,
        query_text="list_reviews",
        top_k=2,
    )
    assert len(results) <= 2
    assert len(results) > 0
    assert results[0].rrf_score > 0.0
    assert results[0].file_path != ""


@pytest.mark.asyncio
async def test_context_retriever_assembly() -> None:
    retriever = ContextRetriever()
    res = await retriever.retrieve_context_for_diff(
        "owner/repo", "+ SELECT * FROM reviews", top_k=2
    )
    assert "formatted_context" in res
    assert "citation_ids" in res
    assert len(res["citation_ids"]) > 0


def test_freshness_tracker() -> None:
    tracker = FreshnessTracker()
    assert tracker.is_file_stale("owner/repo", "file.py", "sha1") is True
    tracker.update_file_index("owner/repo", "file.py", "sha1", "commit1", 2)
    assert tracker.is_file_stale("owner/repo", "file.py", "sha1") is False
    assert tracker.is_file_stale("owner/repo", "file.py", "sha2_changed") is True
