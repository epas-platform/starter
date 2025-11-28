"""Profile-based configuration using Pydantic Settings."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


def load_profile_config(profile: str) -> dict[str, Any]:
    """Load configuration from YAML profile file."""
    config_dir = Path("/app/config")
    if not config_dir.exists():
        config_dir = Path(__file__).parent.parent.parent / "config"

    profile_path = config_dir / f"profile.{profile}.yaml"

    if profile_path.exists():
        with open(profile_path) as f:
            return yaml.safe_load(f) or {}
    return {}


class Settings(BaseSettings):
    """Application settings with profile-based configuration.

    Settings are loaded from:
    1. Environment variables (highest priority)
    2. Profile YAML file (profile.dev.yaml, profile.prod.yaml)
    3. Default values (lowest priority)
    """

    # Profile
    profile: str = Field(default="dev", alias="PROFILE")

    # App
    app_name: str = "Cradle"
    debug: bool = False
    docs_enabled: bool = True

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://cradle:cradle@localhost:5432/cradle",
        alias="DATABASE_URL",
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # AWS / LocalStack
    aws_endpoint_url: str | None = Field(default=None, alias="AWS_ENDPOINT_URL")
    aws_region: str = Field(default="us-east-1", alias="AWS_DEFAULT_REGION")
    aws_access_key_id: str = Field(default="test", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="test", alias="AWS_SECRET_ACCESS_KEY")

    # S3 Buckets
    s3_uploads_bucket: str = "cradle-uploads"
    s3_exports_bucket: str = "cradle-exports"

    # JWT
    jwt_secret: str = Field(
        default="CHANGE-ME-IN-PRODUCTION", alias="JWT_SECRET"
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:3010", "http://localhost:3000"]

    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_requests_per_minute: int = 60

    # Features
    audit_logging_enabled: bool = True
    ai_disclosure_enabled: bool = True

    # Logging
    log_level: str = "INFO"

    def model_post_init(self, __context: Any) -> None:
        """Load profile configuration after initialization."""
        profile_config = load_profile_config(self.profile)

        # Apply profile settings if not overridden by env vars
        if profile_config:
            app_config = profile_config.get("app", {})
            if "debug" in app_config and "DEBUG" not in os.environ:
                self.debug = app_config["debug"]
            if "docs_enabled" in app_config and "DOCS_ENABLED" not in os.environ:
                self.docs_enabled = app_config["docs_enabled"]

            cors_config = profile_config.get("cors", {})
            if "origins" in cors_config and "CORS_ORIGINS" not in os.environ:
                self.cors_origins = cors_config["origins"]

            rate_config = profile_config.get("rate_limit", {})
            if "enabled" in rate_config:
                self.rate_limit_enabled = rate_config["enabled"]

            log_config = profile_config.get("logging", {})
            if "level" in log_config:
                self.log_level = log_config["level"]

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT secret must be at least 32 characters")
        return v

    @property
    def is_production(self) -> bool:
        return self.profile == "prod"

    @property
    def is_development(self) -> bool:
        return self.profile == "dev"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
