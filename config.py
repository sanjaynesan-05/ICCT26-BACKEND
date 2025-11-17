"""
Production Configuration Loader
================================
Strict validation of environment variables with Pydantic BaseSettings.
All required production configurations are validated at startup.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
import os


class ProductionSettings(BaseSettings):
    """
    Production-grade configuration with strict validation.
    All environment variables are required unless marked as Optional.
    """
    
    # ============= DATABASE CONFIGURATION =============
    DATABASE_URL: str = Field(
        ..., 
        description="Async SQLAlchemy database URL"
    )
    DATABASE_POOL_SIZE: int = Field(
        default=20,
        description="Database connection pool size"
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=10,
        description="Maximum overflow connections"
    )
    DATABASE_POOL_RECYCLE: int = Field(
        default=3600,
        description="Pool recycle time in seconds"
    )
    
    # ============= CLOUDINARY CONFIGURATION =============
    CLOUDINARY_CLOUD_NAME: str = Field(
        ...,
        description="Cloudinary cloud name"
    )
    CLOUDINARY_API_KEY: str = Field(
        ...,
        description="Cloudinary API key"
    )
    CLOUDINARY_API_SECRET: str = Field(
        ...,
        description="Cloudinary API secret"
    )
    
    # ============= EMAIL/SMTP CONFIGURATION =============
    SMTP_SERVER: str = Field(
        ...,
        description="SMTP server address"
    )
    SMTP_PORT: int = Field(
        default=587,
        description="SMTP port"
    )
    SMTP_USERNAME: str = Field(
        ...,
        description="SMTP username"
    )
    SMTP_PASSWORD: str = Field(
        ...,
        description="SMTP password"
    )
    SMTP_FROM_EMAIL: str = Field(
        ...,
        description="From email address"
    )
    
    # ============= API CONFIGURATION =============
    API_URL: str = Field(
        ...,
        description="Base API URL for external references"
    )
    API_HOST: str = Field(
        default="0.0.0.0",
        description="API host to bind to"
    )
    API_PORT: int = Field(
        default=8000,
        description="API port"
    )
    API_WORKERS: int = Field(
        default=4,
        description="Number of Uvicorn workers"
    )
    
    # ============= CORS CONFIGURATION =============
    CORS_ORIGINS: List[str] = Field(
        default=["https://icct26.com"],
        description="Allowed CORS origins (comma-separated)"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials in CORS"
    )
    
    # ============= SECURITY CONFIGURATION =============
    SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT/session signing"
    )
    MAX_REQUEST_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum request body size in bytes"
    )
    REQUEST_TIMEOUT: int = Field(
        default=60,
        description="Request timeout in seconds"
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=30,
        description="Max requests per minute per IP"
    )
    
    # ============= LOGGING CONFIGURATION =============
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    LOG_FILE: str = Field(
        default="logs/app.log",
        description="Log file path"
    )
    LOG_TO_FILE: bool = Field(
        default=True,
        description="Enable file logging"
    )
    
    # ============= FEATURE FLAGS =============
    ENABLE_COMPRESSION: bool = Field(
        default=True,
        description="Enable gzip/deflate compression"
    )
    ENABLE_RATE_LIMITING: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    DEBUG: bool = Field(
        default=False,
        description="Debug mode (never True in production)"
    )
    
    # ============= ENVIRONMENT =============
    ENVIRONMENT: str = Field(
        default="production",
        description="Environment (development, staging, production)"
    )
    
    # ============= APP METADATA =============
    APP_TITLE: str = Field(
        default="ICCT26 Cricket Tournament Registration API",
        description="Application title"
    )
    APP_DESCRIPTION: str = Field(
        default="Team registration system with email notifications and admin panel",
        description="Application description"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("DEBUG")
    def debug_never_true_in_production(cls, v, values):
        """Ensure DEBUG is False in production"""
        if v and values.get("ENVIRONMENT") == "production":
            raise ValueError("DEBUG must be False in production environment")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Ensure environment is valid"""
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v
    
    @validator("RATE_LIMIT_REQUESTS")
    def validate_rate_limit(cls, v):
        """Rate limit must be positive"""
        if v <= 0:
            raise ValueError("RATE_LIMIT_REQUESTS must be positive")
        return v
    
    def validate_database_connection(self) -> bool:
        """Validate database URL format"""
        if not self.DATABASE_URL.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite+aiosqlite://")):
            raise ValueError("DATABASE_URL must be async compatible (postgresql+asyncpg or sqlite+aiosqlite)")
        return True
    
    def validate_smtp_config(self) -> bool:
        """Validate SMTP configuration"""
        if not self.SMTP_FROM_EMAIL or "@" not in self.SMTP_FROM_EMAIL:
            raise ValueError("SMTP_FROM_EMAIL must be a valid email address")
        return True
    
    def get_database_pool_config(self) -> dict:
        """Get database pool configuration"""
        return {
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "pool_recycle": self.DATABASE_POOL_RECYCLE,
        }


def load_settings() -> ProductionSettings:
    """
    Load and validate production settings.
    Raises ValueError if any required environment variable is missing.
    """
    try:
        settings = ProductionSettings()
        settings.validate_database_connection()
        settings.validate_smtp_config()
        return settings
    except ValueError as e:
        raise RuntimeError(f"Configuration validation failed: {str(e)}")


# Global settings instance
try:
    settings = load_settings()
except RuntimeError as e:
    print(f"FATAL: {e}")
    raise
