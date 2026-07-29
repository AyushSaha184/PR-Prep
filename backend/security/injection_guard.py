"""Prompt-injection guard detecting and sanitizing malicious untrusted content."""
import re

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.security.injection_guard")

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s+prompt\s+override",
    r"you\s+are\s+now\s+a",
    r"do\s+not\s+output\s+json",
    r"print\s+environment\s+variables",
    r"cat\s+/etc/passwd",
    r"sudo\s+rm",
]


class InjectionGuard:
    """Detects and mitigates prompt-injection attacks in untrusted diffs and PR descriptions."""

    def detect_injection(self, text: str) -> bool:
        """Returns True if suspicious prompt-injection pattern is detected."""
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                msg = f"InjectionGuard flagged potential injection matching pattern: '{pattern}'"
                logger.warning(msg)
                return True
        return False

    def sanitize_untrusted_text(self, text: str) -> str:
        """Sanitizes untrusted text by neutralizing injection markers."""
        if not self.detect_injection(text):
            return text

        logger.info("InjectionGuard sanitizing untrusted text content.")
        sanitized = text
        for pattern in INJECTION_PATTERNS:
            repl = "[FLAGGED_INJECTION_REMOVED]"
            sanitized = re.sub(pattern, repl, sanitized, flags=re.IGNORECASE)
        return sanitized
