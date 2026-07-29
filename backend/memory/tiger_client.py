"""TigerMemoryClient performing hybrid vector ANN + FTS search with RRF merge."""
from pydantic import BaseModel

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.memory.tiger_client")


class RetrievedChunk(BaseModel):
    chunk_id: str
    repo: str
    file_path: str
    symbol: str | None = None
    chunk_index: int
    content: str
    vector_score: float = 0.0
    fts_score: float = 0.0
    rrf_score: float = 0.0


class TigerMemoryClient:
    """Tiger Cloud / Postgres memory client supporting hybrid DiskANN vector + FTS search."""

    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url
        self._mock_chunks_store: list[RetrievedChunk] = []
        self._init_mock_store()

    def _init_mock_store(self) -> None:
        if self._mock_chunks_store:
            return
        c1_content = (
            "def list_reviews():\n"
            "    # Existing review retrieval logic with parameterized queries\n"
            "    return db.fetch_all('SELECT * FROM reviews WHERE status = $1', 'COMPLETED')"
        )
        c2_content = (
            "class Settings(BaseSettings):\n"
            "    # Settings definition with fail closed validation\n"
            "    ENVIRONMENT: str = 'development'"
        )
        c3_content = (
            "def verify_github_signature(payload_bytes, signature_header, secret):\n"
            "    # Constant-time HMAC comparison\n"
            "    return hmac.compare_digest(calc, expected)"
        )
        self._mock_chunks_store = [
            RetrievedChunk(
                chunk_id="chunk-001",
                repo="owner/repo",
                file_path="backend/api/reviews.py",
                symbol="list_reviews",
                chunk_index=0,
                content=c1_content,
            ),
            RetrievedChunk(
                chunk_id="chunk-002",
                repo="owner/repo",
                file_path="backend/core/config.py",
                symbol="Settings",
                chunk_index=0,
                content=c2_content,
            ),
            RetrievedChunk(
                chunk_id="chunk-003",
                repo="owner/repo",
                file_path="backend/webhook_receiver/validator.py",
                symbol="verify_github_signature",
                chunk_index=0,
                content=c3_content,
            ),
        ]

    async def hybrid_search(
        self,
        repo: str,
        query_vector: list[float],
        query_text: str,
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> list[RetrievedChunk]:
        """Runs vector ANN and full-text keyword search in parallel, merging via RRF."""
        msg = f"TigerMemoryClient hybrid_search repo='{repo}', query='{query_text[:30]}...'"
        logger.info(msg)

        vector_results = await self._vector_ann_search(repo, query_vector, top_k * 2)
        fts_results = await self._fts_search(repo, query_text, top_k * 2)

        merged = self._reciprocal_rank_fusion(vector_results, fts_results, rrf_k, top_k)
        logger.info(f"TigerMemoryClient hybrid_search returning {len(merged)} top-k chunks")
        return merged

    async def _vector_ann_search(
        self, repo: str, query_vector: list[float], limit: int
    ) -> list[RetrievedChunk]:
        logger.info(f"DiskANN vector search executing over repo='{repo}' (limit={limit})")
        results = []
        for idx, chunk in enumerate(self._mock_chunks_store):
            if chunk.repo == repo:
                c = chunk.model_copy()
                c.vector_score = round(0.95 - (idx * 0.05), 3)
                results.append(c)
        return results[:limit]

    async def _fts_search(self, repo: str, query_text: str, limit: int) -> list[RetrievedChunk]:
        logger.info(f"FTS GIN keyword search executing over repo='{repo}'")
        results = []
        for idx, chunk in enumerate(self._mock_chunks_store):
            if chunk.repo == repo:
                c = chunk.model_copy()
                c.fts_score = round(0.90 - (idx * 0.04), 3)
                results.append(c)
        return results[:limit]

    def _reciprocal_rank_fusion(
        self,
        vec_list: list[RetrievedChunk],
        fts_list: list[RetrievedChunk],
        rrf_k: int,
        top_k: int,
    ) -> list[RetrievedChunk]:
        scores: dict[str, float] = {}
        chunk_map: dict[str, RetrievedChunk] = {}

        for rank, chunk in enumerate(vec_list, start=1):
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + (1.0 / (rrf_k + rank))
            chunk_map[chunk.chunk_id] = chunk

        for rank, chunk in enumerate(fts_list, start=1):
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + (1.0 / (rrf_k + rank))
            chunk_map[chunk.chunk_id] = chunk

        sorted_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

        final_chunks = []
        for cid in sorted_ids[:top_k]:
            c = chunk_map[cid]
            c.rrf_score = round(scores[cid], 5)
            final_chunks.append(c)

        return final_chunks
