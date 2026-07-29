"""Unit tests for configuration validation and fail-closed settings."""
import pytest

from backend.core.config import Settings
from backend.core.exceptions import ConfigurationError


def test_development_config_defaults() -> None:
    settings = Settings(ENVIRONMENT="development")
    assert settings.ENVIRONMENT == "development"
    assert settings.DAILY_BUDGET_CAP_USD == 50.0


def test_production_config_fails_closed_without_secrets() -> None:
    with pytest.raises(ConfigurationError) as exc_info:
        # Should raise because production requires OPENAI_API_KEY and valid webhook secret
        settings = Settings(
            ENVIRONMENT="production",
            OPENAI_API_KEY="",
            GITHUB_WEBHOOK_SECRET="development_webhook_secret_change_me",
        )
        settings.validate_production_readiness()
    assert "Production startup blocked" in str(exc_info.value)
