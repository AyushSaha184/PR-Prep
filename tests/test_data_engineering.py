"""Unit tests for Phase 14 Repository Ingestion, Chunking, and Data Quality."""
import pytest

from backend.data.data_quality import DataQualityRunner
from backend.data.ingestion import RepositoryIngestionPipeline


@pytest.mark.asyncio
async def test_repository_ingestion_pipeline() -> None:
    pipeline = RepositoryIngestionPipeline()
    file_map = {
        "backend/main.py": "def main():\n    # App entry point\n    return True",
        "backend/config.py": "class Settings:\n    ENV = 'dev'",
    }

    res = await pipeline.ingest_repository_files("owner/repo", "sha123", file_map)
    assert res.files_processed == 2
    assert res.chunks_created >= 2
    assert res.tokens_indexed > 0


def test_data_quality_runner() -> None:
    runner = DataQualityRunner()
    report = runner.run_quality_check("owner/repo")
    assert report.passed_quality_check is True
    assert report.orphan_events_count == 0
