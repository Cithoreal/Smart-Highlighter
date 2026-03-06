"""Centralized configuration management using Pydantic settings."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # === Server Configuration ===
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Enable auto-reload")
    https: bool = Field(default=False, description="Enable HTTPS")

    # === Security ===
    cors_origins: list[str] = Field(
        default=["*"], description="Allowed CORS origins (TODO: restrict in Phase 3)"
    )
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    secret_key: Optional[str] = Field(
        default=None, description="Secret key for JWT (will be required in Phase 3)"
    )

    # === LLM API Keys ===
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic API key"
    )
    google_ai_api_key: Optional[str] = Field(
        default=None, description="Google AI API key"
    )
    huggingface_api_key: Optional[str] = Field(
        default=None, description="HuggingFace API key"
    )

    # === LLM Processing ===
    default_model: str = Field(default="gpt-4o-mini", description="Default LLM model")
    chunk_size: int = Field(default=3000, description="Text chunk size for processing")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")
    max_tokens: int = Field(default=4000, description="Maximum tokens per LLM request")

    # === Storage Paths ===
    data_dir: Path = Field(
        default=Path("data"), description="Base directory for user data"
    )
    log_dir: Path = Field(
        default=Path("logs"), description="Directory for application logs"
    )

    # === Scheduler Configuration ===
    enable_scheduler: bool = Field(
        default=True, description="Enable background task scheduler"
    )
    hourly_summary_time: str = Field(
        default="0", description="Minute of hour to run hourly summaries (0-59)"
    )
    daily_summary_time: str = Field(
        default="23:55", description="Time to run daily summaries (HH:MM)"
    )

    # === Feature Flags ===
    enable_web_tracking: bool = Field(
        default=True, description="Enable web tracking endpoint"
    )
    enable_judge: bool = Field(
        default=True, description="Enable LLM-as-Judge evaluation"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    @validator("data_dir", "log_dir", pre=True)
    def ensure_path(cls, v):
        """Convert string to Path object."""
        if isinstance(v, str):
            return Path(v)
        return v

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.log_dir.mkdir(exist_ok=True, parents=True)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.
    """
    settings = Settings()
    settings.ensure_directories()
    return settings


# Convenience function for accessing settings
settings = get_settings()
