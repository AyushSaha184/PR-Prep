"""Application configuration settings loader using Pydantic BaseSettings.

Fails closed at startup if required settings are missing in production mode.
"""
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.exceptions import ConfigurationError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database & Storage
    TIGER_DATABASE_URL: str = Field(
        default="postgresql+asyncpg://pr_prep:pr_prep_password@localhost:5432/pr_prep_dev"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # GitHub App Integration Credentials
    GITHUB_APP_ID: str = Field(default="123456")
    GITHUB_WEBHOOK_SECRET: str = Field(default="development_webhook_secret_change_me")
    GITHUB_PRIVATE_KEY_PATH: str = Field(default="")

    # AI Provider
    OPENAI_API_KEY: str = Field(default="")
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS: int = 256
    DEFAULT_REASONING_MODEL: str = "gpt-4o"

    # Budget & Governance Controls
    DAILY_BUDGET_CAP_USD: float = 50.0
    BUDGET_GUARD_ENABLED: bool = True

    # HITL Thresholds
    CONFIDENCE_THRESHOLD_AUTO_POST: float = 0.85
    MANDATORY_ESCALATION_SEVERITY: str = "CRITICAL"

    def validate_production_readiness(self) -> None:
        """Enforces fail-closed configuration check in non-development environments."""
        if self.ENVIRONMENT in ("production", "staging"):
            missing = []
            if not self.OPENAI_API_KEY:
                missing.append("OPENAI_API_KEY")
            dev_secret = "development_webhook_secret_change_me"
            if not self.GITHUB_WEBHOOK_SECRET or self.GITHUB_WEBHOOK_SECRET == dev_secret:
                missing.append("GITHUB_WEBHOOK_SECRET")
            if not self.GITHUB_APP_ID or self.GITHUB_APP_ID == "123456":
                missing.append("GITHUB_APP_ID")
            if missing:
                missing_str = ", ".join(missing)
                raise ConfigurationError(
                    f"Production startup blocked: missing required credentials: {missing_str}"
                )


_settings_instance: Settings | None = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
        _settings_instance.validate_production_readiness()
    return _settings_instance
