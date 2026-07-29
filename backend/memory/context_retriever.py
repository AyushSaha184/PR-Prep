"""Hybrid Context Retriever assembling grounded RAG context for specialist agents."""
from typing import Any

from backend.memory.embedder import EmbedderClient
from backend.memory.tiger_client import RetrievedChunk, TigerMemoryClient
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.memory.context_retriever")


class ContextRetriever:
    """Assembles hybrid RAG context for specialist agents while excluding circular evidence."""

    def __init__(
        self,
        embedder: EmbedderClient | None = None,
        memory_client: TigerMemoryClient | None = None,
    ) -> None:
        self.embedder = embedder or EmbedderClient()
        self.memory_client = memory_client or TigerMemoryClient()

    async def retrieve_context_for_diff(
        self,
        repo: str,
        diff_text: str,
        top_k: int = 3,
        max_tokens: int = 1500,
    ) -> dict[str, Any]:
        """Retrieves top-k hybrid context for diff without including circular changed hunks."""
        logger.info(f"ContextRetriever retrieving context for repo='{repo}' (top_k={top_k})")

        # Step 1: Embed diff query
        query_vector = await self.embedder.embed_text(diff_text[:500])

        # Step 2: Hybrid RAG Search (DiskANN + FTS GIN + RRF)
        chunks: list[RetrievedChunk] = await self.memory_client.hybrid_search(
            repo=repo,
            query_vector=query_vector,
            query_text=diff_text[:200],
            top_k=top_k,
        )

        # Step 3: Assemble formatted context string and citation IDs
        context_snippets = []
        citation_ids = []
        total_tokens = 0

        for chunk in chunks:
            sym = chunk.symbol or "module"
            snippet = f"--- [{chunk.file_path}:{sym}] (RRF: {chunk.rrf_score}) ---\n{chunk.content}"
            estimated_tokens = len(snippet) // 4

            if total_tokens + estimated_tokens > max_tokens:
                logger.info(f"ContextRetriever reached token cap ({max_tokens}); truncating.")
                break

            context_snippets.append(snippet)
            citation_ids.append(chunk.chunk_id)
            total_tokens += estimated_tokens

        fallback = "No relevant repository context found."
        formatted_context = "\n\n".join(context_snippets) if context_snippets else fallback

        logger.info(
            f"ContextRetriever completed: retrieved {len(citation_ids)} chunks, "
            f"total_tokens~{total_tokens}"
        )

        return {
            "formatted_context": formatted_context,
            "citation_ids": citation_ids,
            "retrieved_chunks": chunks,
            "token_count": total_tokens,
        }
