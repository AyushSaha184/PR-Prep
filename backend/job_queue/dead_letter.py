"""Dead-Letter Queue (DLQ) managing failed and exhausted background review jobs."""
from typing import Any

from pydantic import BaseModel, Field

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.job_queue.dead_letter")


class DeadLetterJob(BaseModel):
    job_id: str
    workflow_id: str
    repository: str
    pr_number: int
    error_message: str
    retry_count: int = 0
    replayed: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


_DEAD_LETTER_STORE: dict[str, DeadLetterJob] = {}


class DeadLetterQueue:
    """Manager for recording, inspecting, and replaying dead-lettered jobs."""

    def push_to_dlq(
        self,
        job_id: str,
        workflow_id: str,
        repository: str,
        pr_number: int,
        error_message: str,
        retry_count: int = 3,
        metadata: dict[str, Any] | None = None,
    ) -> DeadLetterJob:
        """Pushes an exhausted job into the dead-letter queue."""
        job = DeadLetterJob(
            job_id=job_id,
            workflow_id=workflow_id,
            repository=repository,
            pr_number=pr_number,
            error_message=error_message,
            retry_count=retry_count,
            metadata=metadata or {},
        )
        _DEAD_LETTER_STORE[job_id] = job
        msg = f"DLQ pushed job '{job_id}' (wf={workflow_id}) for {repository}#PR-{pr_number}"
        logger.error(f"{msg}: {error_message}")
        return job

    @staticmethod
    def list_dlq_jobs() -> list[DeadLetterJob]:
        """Lists all dead-lettered jobs."""
        return list(_DEAD_LETTER_STORE.values())

    def replay_job(self, job_id: str) -> dict[str, Any]:
        """Replays a dead-lettered job."""
        if job_id not in _DEAD_LETTER_STORE:
            raise KeyError(f"DLQ Job '{job_id}' not found")

        job = _DEAD_LETTER_STORE[job_id]
        job.replayed = True
        logger.info(f"DLQ replaying job '{job_id}' (wf={job.workflow_id})")

        return {
            "status": "replayed",
            "job_id": job_id,
            "workflow_id": job.workflow_id,
            "repository": job.repository,
            "pr_number": job.pr_number,
        }
