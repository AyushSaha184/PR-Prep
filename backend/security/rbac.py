"""Server-side Role-Based Access Control (RBAC) middleware and dependencies."""
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from fastapi import Header, HTTPException, status

from backend.core.exceptions import SecurityError
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.security.rbac")


class UserRole(StrEnum):
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    ADMIN = "admin"
    SERVICE = "service"


ROLE_WEIGHTS: dict[UserRole, int] = {
    UserRole.DEVELOPER: 1,
    UserRole.REVIEWER: 2,
    UserRole.ADMIN: 3,
    UserRole.SERVICE: 3,
}


def verify_role_authorization(current_role: str | None, required_role: UserRole) -> bool:
    """Verifies that user role meets or exceeds required role hierarchy."""
    if not current_role:
        logger.warning("RBAC rejection: X-User-Role header missing.")
        raise SecurityError("Missing X-User-Role authentication header")

    try:
        user_role_enum = UserRole(current_role.lower())
    except ValueError as e:
        logger.warning(f"RBAC rejection: Unknown user role '{current_role}'.")
        raise SecurityError(f"Unknown user role '{current_role}'") from e

    current_weight = ROLE_WEIGHTS.get(user_role_enum, 0)
    required_weight = ROLE_WEIGHTS.get(required_role, 99)

    if current_weight < required_weight:
        msg = f"RBAC rejection: Role '{current_role}' lacks required permission '{required_role}'"
        logger.warning(msg)
        raise SecurityError(f"Insufficient permissions. Required: {required_role.value}")

    logger.info(f"RBAC granted for role '{current_role}' (required '{required_role.value}')")
    return True


def require_role(required_role: UserRole) -> Callable[..., Any]:
    """FastAPI dependency factory enforcing server-side RBAC authorization."""

    async def dependency(x_user_role: str | None = Header(None, alias="X-User-Role")) -> str:
        try:
            verify_role_authorization(x_user_role, required_role)
            return x_user_role or "unknown"
        except SecurityError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=e.message
            ) from e

    return dependency
