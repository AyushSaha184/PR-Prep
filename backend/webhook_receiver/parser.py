"""Parser for GitHub webhook event payloads."""
from typing import Any

from backend.core.exceptions import ValidationError
from backend.models.webhook import WebhookEvent
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.webhook_receiver.parser")

SUPPORTED_ACTIONS = {"opened", "synchronize", "reopened"}


def parse_github_pull_request_event(
    event_type: str, delivery_id: str, payload: dict[str, Any]
) -> WebhookEvent | None:
    """Parses GitHub pull_request payload.

    Returns WebhookEvent if supported, or None if the action is ignored.
    """
    if event_type != "pull_request":
        logger.info(f"Ignoring event_type='{event_type}' (delivery_id={delivery_id})")
        return None

    action = payload.get("action", "")
    if action not in SUPPORTED_ACTIONS:
        logger.info(f"Ignoring action='{action}' (delivery_id={delivery_id})")
        return None

    pr_data = payload.get("pull_request")
    repo_data = payload.get("repository")

    if not pr_data or not repo_data:
        msg = f"Malformed payload missing PR or repo object (delivery_id={delivery_id})"
        logger.error(msg)
        raise ValidationError("Malformed webhook payload")

    pr_number = pr_data.get("number")
    commit_sha = pr_data.get("head", {}).get("sha")
    repo_full_name = repo_data.get("full_name")
    sender = payload.get("sender", {}).get("login", "unknown")

    if not pr_number or not commit_sha or not repo_full_name:
        logger.error(f"Incomplete PR metadata in payload (delivery_id={delivery_id})")
        raise ValidationError("Incomplete PR metadata")

    event = WebhookEvent(
        delivery_id=delivery_id,
        event_type=event_type,
        action=action,
        repository=repo_full_name,
        pr_number=int(pr_number),
        commit_sha=str(commit_sha),
        sender=str(sender),
        raw_payload=payload,
    )
    logger.info(
        f"Parsed pull_request event: {repo_full_name}#PR-{pr_number} "
        f"action='{action}' commit='{commit_sha[:7]}' (delivery_id={delivery_id})"
    )
    return event
