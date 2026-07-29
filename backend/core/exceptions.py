"""Shared domain exceptions for PR Prep.

Core depends on nothing; module-specific exceptions inherit from PRPrepError.
"""

class PRPrepError(Exception):
    """Base exception for all PR Prep domain errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class ConfigurationError(PRPrepError):
    """Raised when application configuration or environment settings are invalid."""
    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFIGURATION_ERROR")


class ValidationError(PRPrepError):
    """Raised when domain object validation fails."""
    def __init__(self, message: str) -> None:
        super().__init__(message, code="VALIDATION_ERROR")


class WorkflowExecutionError(PRPrepError):
    """Raised when orchestrator or workflow graph execution fails."""
    def __init__(self, message: str) -> None:
        super().__init__(message, code="WORKFLOW_EXECUTION_ERROR")


class SecurityError(PRPrepError):
    """Raised on authentication, authorization, or HMAC validation failure."""
    def __init__(self, message: str) -> None:
        super().__init__(message, code="SECURITY_ERROR")


class BudgetExceededError(PRPrepError):
    """Raised by BudgetGuard when cost cap is reached."""
    def __init__(self, message: str) -> None:
        super().__init__(message, code="BUDGET_EXCEEDED")
