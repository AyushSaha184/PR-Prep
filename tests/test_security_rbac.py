"""Unit tests for Phase 11 RBAC role authorization and AuditLogger secret masking."""
import pytest

from backend.core.exceptions import SecurityError
from backend.security.audit import AuditLogger
from backend.security.rbac import UserRole, verify_role_authorization


def test_rbac_authorization_success() -> None:
    assert verify_role_authorization("reviewer", UserRole.REVIEWER) is True
    assert verify_role_authorization("admin", UserRole.REVIEWER) is True
    assert verify_role_authorization("admin", UserRole.ADMIN) is True


def test_rbac_authorization_insufficient_role_fails_closed() -> None:
    with pytest.raises(SecurityError):
        verify_role_authorization("developer", UserRole.ADMIN)


def test_rbac_authorization_missing_header_fails_closed() -> None:
    with pytest.raises(SecurityError):
        verify_role_authorization(None, UserRole.DEVELOPER)


def test_audit_logger_secret_masking() -> None:
    audit = AuditLogger()
    unmasked = {
        "user": "alice",
        "api_key": "sk-1234567890abcdef1234567890",
        "github_token": "ghp_abcdef1234567890abcdef",
        "nested": {"bearer_token": "Bearer eyJhbGciOiJIUzI1NiJ9"},
    }

    masked = audit.mask_secrets(unmasked)
    assert masked["api_key"] == "[MASKED_SECRET]"
    assert masked["github_token"] == "[MASKED_SECRET]"
    assert masked["nested"]["bearer_token"] == "[MASKED_SECRET]"
    assert masked["user"] == "alice"
