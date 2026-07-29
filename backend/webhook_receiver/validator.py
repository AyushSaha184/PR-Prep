"""HMAC-SHA256 signature validator for incoming GitHub webhooks."""
import hashlib
import hmac

from backend.core.exceptions import SecurityError
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.webhook_receiver.validator")


def verify_github_signature(
    payload_bytes: bytes, signature_header: str | None, secret: str
) -> bool:
    """Verifies X-Hub-Signature-256 header against raw payload and webhook secret."""
    if not signature_header:
        logger.warning("Webhook rejection: X-Hub-Signature-256 header is missing.")
        raise SecurityError("Missing X-Hub-Signature-256 header")

    if not signature_header.startswith("sha256="):
        logger.warning(f"Webhook rejection: Invalid signature format '{signature_header}'.")
        raise SecurityError("Invalid X-Hub-Signature-256 format")

    expected_signature = signature_header[7:]
    mac = hmac.new(secret.encode("utf-8"), msg=payload_bytes, digestmod=hashlib.sha256)
    calculated_signature = mac.hexdigest()

    if not hmac.compare_digest(calculated_signature, expected_signature):
        logger.warning("Webhook rejection: HMAC-SHA256 signature mismatch!")
        raise SecurityError("Invalid X-Hub-Signature-256 signature")

    logger.info("GitHub HMAC-SHA256 signature verified successfully.")
    return True
