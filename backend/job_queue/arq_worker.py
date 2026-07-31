"""ARQ Worker consuming review_job tasks from Redis."""
from typing import Any

from backend.observability.logging import setup_logger
from backend.orchestrator.langgraph_engine import LangGraphEngine

logger = setup_logger("pr_prep.job_queue.arq_worker")


async def process_review_job(ctx: dict[str, Any], job_data: dict[str, Any]) -> dict[str, Any]:
    """Task handler for review_job execution using LangGraphEngine."""
    workflow_id = job_data.get("delivery_id", "wf_default")
    repo = job_data.get("repository", "owner/repo")
    pr = job_data.get("pr_number", 0)

    logger.info(f"ARQ Worker starting job for {repo}#PR-{pr} (wf={workflow_id})")

    # LangGraph workflow orchestration execution
    engine = LangGraphEngine()
    result = await engine.run(workflow_id, job_data)

    status_str = result.get("status")
    logger.info(f"ARQ Worker finished job for {repo}#PR-{pr} status={status_str}")
    return result


class WorkerSettings:
    functions = [process_review_job]
    redis_settings = "redis://localhost:6379/0"
