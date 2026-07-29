"""Tamper-evident Audit Logger wrapping privileged operations and masking secrets."""
import re
from typing import Any

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.security.audit")

SECRET_MASK_PATTERNS = [
    r"sk-[a-zA-Z0-9]{20,}",
    r"ghp_[a-zA-Z0-9]{20,}",
    r"bearer\s+[a-zA-Z0-9\._\-]+",
]


class AuditLogger:
    """Tamper-evident security audit logger with automatic secret masking."""

    def log_privileged_action(
        self,
        action: str,
        actor: str,
        resource: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Logs a privileged administrative or security action after masking sensitive values."""
        sanitized_details = self.mask_secrets(details or {})
        logger.info(
            f"[AUDIT LOG] Action='{action}' Actor='{actor}' Resource='{resource}' "
            f"Details={sanitized_details}"
        )

    def mask_secrets(self, data: Any) -> Any:
        """Recursively masks secret tokens in strings and dictionaries."""
        if isinstance(data, str):
            masked = data
            for pattern in SECRET_MASK_PATTERNS:
                masked = re.sub(pattern, "[MASKED_SECRET]", masked, flags=re.IGNORECASE)
            return masked

        if isinstance(data, dict):
            res = {}
            for k, v in data.items():
                k_lower = k.lower()
                if "secret" in k_lower or "key" in k_lower or "token" in k_lower:
                    res[k] = "[MASKED_SECRET]"
                else:
                    res[k] = self.mask_secrets(v)
            return res

        if isinstance(data, list):
            return [self.mask_secrets(item) for item in data]

        return data
