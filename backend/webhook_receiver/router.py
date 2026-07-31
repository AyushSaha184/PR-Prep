"""FastAPI router for incoming GitHub webhook endpoint."""
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request, status

from backend.core.config import get_settings
from backend.core.exceptions import SecurityError, ValidationError
from backend.observability.logging import setup_logger
from backend.webhook_receiver.parser import parse_github_pull_request_event
from backend.webhook_receiver.validator import verify_github_signature

logger = setup_logger("pr_prep.webhook_receiver.router")
router = APIRouter(tags=["Webhooks"])

# In-memory idempotency store fallback for Phase 3
_SEEN_DELIVERIES: set[str] = set()


@router.post("/webhook/github", status_code=status.HTTP_200_OK)
async def handle_github_webhook(
    request: Request,
    x_github_delivery: str | None = Header(None, alias="X-GitHub-Delivery"),
    x_github_event: str | None = Header(None, alias="X-GitHub-Event"),
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256"),
) -> dict[str, Any]:
    """Ingress endpoint for GitHub webhooks.

    1. Validates HMAC-SHA256 signature.
    2. Checks X-GitHub-Delivery idempotency key.
    3. Parses pull_request event metadata.
    4. Enqueues job and returns HTTP 200 immediately.
    """
    settings = get_settings()
    body_bytes = await request.body()

    # 1. Signature Verification
    try:
        verify_github_signature(body_bytes, x_hub_signature_256, settings.GITHUB_WEBHOOK_SECRET)
    except SecurityError as e:
        logger.warning(f"Webhook security error: {e.message}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message) from e

    delivery_id = x_github_delivery or "unknown_delivery"
    event_type = x_github_event or "unknown_event"

    # 2. Idempotency Check
    if delivery_id in _SEEN_DELIVERIES:
        logger.info(f"Idempotency hit: delivery_id='{delivery_id}' processed. Acknowledging 200.")
        return {
            "status": "acknowledged",
            "message": "Duplicate delivery ignored",
            "delivery_id": delivery_id,
        }
    _SEEN_DELIVERIES.add(delivery_id)

    # 3. Payload Parsing
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse JSON body for delivery_id='{delivery_id}': {e}")
        bad_req = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=bad_req, detail="Invalid JSON body") from e

    try:
        parsed_event = parse_github_pull_request_event(event_type, delivery_id, payload)
    except ValidationError as e:
        logger.error(f"Payload validation error for delivery_id='{delivery_id}': {e.message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e

    if not parsed_event:
        return {
            "status": "ignored",
            "message": f"Event type '{event_type}' or action ignored",
            "delivery_id": delivery_id,
        }

    # 4. Enqueue Job & Fast Acknowledgment
    logger.info(
        f"Enqueuing review_job for {parsed_event.repository}#PR-{parsed_event.pr_number} "
        f"(delivery_id={delivery_id})"
    )

    job_data = {
        "delivery_id": delivery_id,
        "repository": parsed_event.repository,
        "pr_number": parsed_event.pr_number,
        "commit_sha": parsed_event.commit_sha,
        "action": parsed_event.action,
        "sender": parsed_event.sender,
    }

    # Attempt Redis ARQ queue dispatch with background task fallback
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        redis_url = settings.REDIS_URL
        # Parse host and port from REDIS_URL or default
        redis = await create_pool(RedisSettings.from_dsn(redis_url))
        await redis.enqueue_job("process_review_job", job_data)
        logger.info(f"Successfully enqueued review_job to Redis for delivery_id={delivery_id}")
    except Exception as e:
        logger.warning(
            f"Redis enqueue failed ({e}); dispatching review_job via background task fallback."
        )
        import asyncio

        from backend.job_queue.arq_worker import process_review_job

        asyncio.create_task(process_review_job({}, job_data))

    return {
        "status": "queued",
        "delivery_id": delivery_id,
        "repository": parsed_event.repository,
        "pr_number": parsed_event.pr_number,
        "commit_sha": parsed_event.commit_sha,
    }
