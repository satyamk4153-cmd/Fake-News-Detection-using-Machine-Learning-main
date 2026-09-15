"""Configuration settings for TruthLens API."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = "TruthLens"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "truthlens-dev-insecure-secret-key-change-in-production-min32chars!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./truthlens.db"
    
    # Cache / Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE_ANONYMOUS: int = 60
    RATE_LIMIT_PER_MINUTE_AUTH: int = 120
    RATE_LIMIT_PER_MINUTE_ADMIN: int = 300
    
    # ML & Inference
    MODEL_DIR: str = "ml/artifacts"
    ACTIVE_MODEL_VERSION: str = "ensemble-v1.0"
    UNCERTAINTY_THRESHOLD_LOW: float = 0.35
    UNCERTAINTY_THRESHOLD_HIGH: float = 0.65
    MIN_ARTICLE_LENGTH: int = 50
    MAX_ARTICLE_LENGTH: int = 50000
    MIN_HEADLINE_LENGTH: int = 15
    MAX_HEADLINE_LENGTH: int = 500
    
    # SSRF & URL Extraction
    MAX_URL_REDIRECTS: int = 3
    URL_REQUEST_TIMEOUT_SECONDS: int = 8
    MAX_URL_CONTENT_BYTES: int = 5242880  # 5 MB
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
