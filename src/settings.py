from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal
from functools import lru_cache

class Settings(BaseSettings):
    """Base settings that apply to all environments"""
    
    # Environment configuration
    environment: Literal["development", "staging", "production"] = "development"
    
    # App basics
    app_name: str = "Healthezy"
    app_version: str = "0.1.0"
    
    # Database
    database_url: str = Field(default="", description="Database DSN")
    database_pool_size: int = 10
    
    # Security
    secret_key: str = Field(default="", description="Secret key for JWT", min_length=32)
    secret_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API settings
    api_prefix: str = "/api/v1"
    
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def is_debug(self) -> bool:
        """Auto-enable debug in development"""
        return self.environment == "development"
    
    @property
    def log_level(self) -> str:
        """Auto-adjust log level by environment"""
        if self.environment == "development":
            return "DEBUG"
        elif self.environment == "staging":
            return "INFO"
        return "WARNING"
    
    @property
    def allowed_origins(self) -> list[str]:
        # TODO: change this
        """Auto-configure CORS by environment"""
        if self.environment == "development":
            return ["*"]
        elif self.environment == "staging":
            return ["https://staging.example.com"]
        return ["https://example.com"]


class DevelopmentSettings(Settings):
    """Development-specific overrides"""
    database_url: str = Field(
        default="postgresql+psycopg2://root:secret@localhost:5433/healthezy_dev?sslmode=disable"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class ProductionSettings(Settings):
    """Production-specific settings with stricter validation"""
    
    # In production, enforce stronger requirements
    secret_key: str = Field(
        default="", min_length=64)
    database_pool_size: int = Field(default=20, ge=10, le=100)
    database_url: str = Field(
        default="",
    )
    
    model_config = SettingsConfigDict(
        env_file=".env.prod",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Factory function that returns the appropriate settings instance.
    
    The @lru_cache decorator ensures we only create one instance,
    which is important for performance.
    
    Usage:
        from config import get_settings
        settings = get_settings()
    """
    from os import getenv
    
    environment = getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "development":
        return DevelopmentSettings()
    else:  # staging or other
        return Settings()
