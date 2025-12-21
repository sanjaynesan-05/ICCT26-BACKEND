"""
Production Configuration Loader
================================
Strict validation of environment variables with Pydantic BaseSettings.
All required production configurations are validated at startup.
Render-compatible: Loads from environment variables (no sys.path hacks)
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict
from typing import Optional, List
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Production-grade configuration with strict validation.
    All environment variables are required unless marked as Optional.
    Compatible with Render deployment.
    """
    
    # ============= DATABASE CONFIGURATION =============
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost/icct26",
        description="Async SQLAlchemy database URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Maximum overflow connections")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, description="Pool recycle time in seconds")
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries (for debugging)")
    
    # ============= CLOUDINARY CONFIGURATION =============
    CLOUDINARY_CLOUD_NAME: str = Field(default="demo", description="Cloudinary cloud name")
    CLOUDINARY_API_KEY: str = Field(default="", description="Cloudinary API key")
    CLOUDINARY_API_SECRET: str = Field(default="", description="Cloudinary API secret")
    
    # ============= JWT CONFIGURATION =============
    JWT_SECRET_KEY: str = Field(default="change-me-in-production", description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    
    # ============= EMAIL/SMTP CONFIGURATION =============
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP server address")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USER: str = Field(default="", description="SMTP username")
    SMTP_PASS: str = Field(default="", description="SMTP password")
    SMTP_FROM_EMAIL: str = Field(default="noreply@icct26.com", description="From email address")
    SMTP_FROM_NAME: str = Field(default="ICCT26 Cricket Tournament", description="From name for emails")
    
    @property
    def SMTP_ENABLED(self) -> bool:
        """Check if SMTP is properly configured"""
        return bool(self.SMTP_USER and self.SMTP_PASS and self.SMTP_HOST)
    
    # Legacy field mapping for backward compatibility
    @property
    def SMTP_SERVER(self) -> str:
        return self.SMTP_HOST
    
    @property
    def SMTP_USERNAME(self) -> str:
        return self.SMTP_USER
    
    @property
    def SMTP_PASSWORD(self) -> str:
        return self.SMTP_PASS
    
    # ============= API CONFIGURATION =============
    API_URL: str = Field(default="http://localhost:8000", description="Base API URL")
    API_HOST: str = Field(default="0.0.0.0", description="API host to bind to")
    API_PORT: int = Field(default=8000, description="API port")
    API_WORKERS: int = Field(default=4, description="Number of Uvicorn workers")
    
    # ============= CORS CONFIGURATION =============
    CORS_ORIGINS: List[str] = Field(default=["*"], description="Allowed CORS origins")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials in CORS")
    
    # ============= SECURITY CONFIGURATION =============
    SECRET_KEY: str = Field(default="change-me-in-production", description="Secret key for JWT/session signing")
    MAX_REQUEST_SIZE: int = Field(default=100 * 1024 * 1024, description="Maximum request body size in bytes (100MB for file uploads)")
    REQUEST_TIMEOUT: int = Field(default=180, description="Request timeout in seconds (180s for file uploads)")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Max requests per minute per IP")
    
    # ============= LOGGING CONFIGURATION =============
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: str = Field(default="logs/app.log", description="Log file path")
    LOG_TO_FILE: bool = Field(default=True, description="Enable file logging")
    
    # ============= FEATURE FLAGS =============
    ENABLE_COMPRESSION: bool = Field(default=True, description="Enable gzip/deflate compression")
    ENABLE_RATE_LIMITING: bool = Field(default=True, description="Enable rate limiting")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # ============= ENVIRONMENT =============
    ENVIRONMENT: str = Field(default="production", description="Environment (development, staging, production)")
    
    # ============= APP METADATA =============
    APP_TITLE: str = Field(default="ICCT26 Cricket Tournament Registration API", description="Application title")
    APP_DESCRIPTION: str = Field(default="Team registration system with email notifications and admin panel", description="Application description")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    
    # ============= TOURNAMENT METADATA =============
    TOURNAMENT_NAME: str = Field(default="ICCT26 Cricket Tournament", description="Tournament name")
    TOURNAMENT_DATES: str = Field(default="January 24-26, 2026", description="Tournament dates")
    TOURNAMENT_VENUE: str = Field(default="CSI St. Peter's Church Cricket Ground", description="Tournament venue")
    TOURNAMENT_LOCATION: str = Field(default="Coimbatore, Tamil Nadu", description="Tournament location")
    TOURNAMENT_FORMAT: str = Field(default="Red Tennis Ball Cricket", description="Tournament format")
    
    # ============= TEAM REGISTRATION CONSTRAINTS =============
    MIN_PLAYERS: int = Field(default=11, description="Minimum players required per team")
    MAX_PLAYERS: int = Field(default=15, description="Maximum players allowed per team")
    MIN_PLAYER_AGE: int = Field(default=15, description="Minimum player age")
    MAX_PLAYER_AGE: int = Field(default=60, description="Maximum player age")
    
    # ============= VALID PLAYER ROLES =============
    VALID_PLAYER_ROLES: List[str] = Field(
        default=["Batsman", "Bowler", "All-Rounder", "Wicket Keeper"],
        description="Valid player roles"
    )
    
    # ============= FIELD VALIDATION CONSTRAINTS =============
    CHURCH_NAME_MAX_LENGTH: int = Field(default=200, description="Max length for church name")
    TEAM_NAME_MAX_LENGTH: int = Field(default=100, description="Max length for team name")
    PLAYER_NAME_MAX_LENGTH: int = Field(default=100, description="Max length for player name")
    PHONE_MIN_LENGTH: int = Field(default=10, description="Minimum phone number length")
    PHONE_MAX_LENGTH: int = Field(default=20, description="Maximum phone number length")
    WHATSAPP_MIN_LENGTH: int = Field(default=10, description="Minimum WhatsApp number length")
    WHATSAPP_MAX_LENGTH: int = Field(default=20, description="Maximum WhatsApp number length")
    
    model_config = ConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins or JSON array"""
        if isinstance(v, str):
            # Try JSON parse first
            if v.startswith("["):
                import json
                try:
                    return json.loads(v)
                except:
                    pass
            # Fall back to comma-separated
            return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance - instantiated once at module load
settings = Settings()
