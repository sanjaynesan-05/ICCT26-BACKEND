"""
Configuration module for ICCT26 Cricket Tournament API
Centralized configuration for environment variables, database, and SMTP settings
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env.local (priority) or .env
load_dotenv('.env.local')  # Load .env.local first
load_dotenv()  # Then load .env as fallback

# ============================================================
# Application Configuration
# ============================================================

class Settings:
    """Application settings from environment variables"""
    
    # API Configuration
    APP_TITLE: str = "ICCT26 Cricket Tournament Registration API"
    APP_DESCRIPTION: str = "Team registration system with email notifications and admin panel"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        'postgresql://icctadmin:FhfKgVwHX7P7hmObQJFQvN0YBZxYUly7@dpg-d45imk49c44c73c4j4v0-a/icct26_db'
    )
    
    # Convert async database URL to sync format if needed
    if DATABASE_URL.startswith('postgresql+asyncpg://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    elif DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
    
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"
    
    # SMTP Configuration
    SMTP_SERVER: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME: str = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM_EMAIL: str = os.getenv('SMTP_FROM_EMAIL', SMTP_USERNAME)
    SMTP_FROM_NAME: str = os.getenv('SMTP_FROM_NAME', 'ICCT26 Cricket Tournament')
    
    SMTP_ENABLED: bool = bool(SMTP_USERNAME and SMTP_PASSWORD)
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://icct26.netlify.app",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ]
    
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Tournament Configuration
    TOURNAMENT_NAME: str = "ICCT26 Cricket Tournament 2026"
    TOURNAMENT_DATES: str = "January 24-26, 2026"
    TOURNAMENT_VENUE: str = "CSI St. Peter's Church Cricket Ground"
    TOURNAMENT_LOCATION: str = "Coimbatore, Tamil Nadu"
    TOURNAMENT_FORMAT: str = "Red Tennis Ball Cricket"
    
    # Team Registration Configuration
    MIN_PLAYERS: int = 11
    MAX_PLAYERS: int = 15
    MIN_PLAYER_AGE: int = 15
    MAX_PLAYER_AGE: int = 60
    
    # Valid Player Roles
    VALID_PLAYER_ROLES: List[str] = [
        "Batsman",
        "Bowler",
        "All-Rounder",
        "Wicket Keeper"
    ]
    
    # Field Validation Constraints
    CHURCH_NAME_MAX_LENGTH: int = 200
    TEAM_NAME_MAX_LENGTH: int = 100
    PLAYER_NAME_MAX_LENGTH: int = 100
    PHONE_MIN_LENGTH: int = 10
    PHONE_MAX_LENGTH: int = 20
    WHATSAPP_MIN_LENGTH: int = 10
    WHATSAPP_MAX_LENGTH: int = 20
    
    # Email Configuration
    EMAIL_VERIFICATION_ENABLED: bool = False
    EMAIL_FROM_ADDRESS: str = SMTP_FROM_EMAIL
    EMAIL_FROM_NAME: str = SMTP_FROM_NAME
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = 5  # 5MB limit for uploaded files
    MAX_BASE64_SIZE_CHARS: int = MAX_FILE_SIZE_MB * 1024 * 1024 * 4 // 3  # ~6.7M characters
    
    # File Type Validation (MIME types)
    ALLOWED_IMAGE_TYPES: List[str] = [
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'
    ]
    ALLOWED_DOCUMENT_TYPES: List[str] = [
        'application/pdf'
    ]
    
    class Config:
        """Pydantic config"""
        case_sensitive = True


# Create settings instance
settings = Settings()


# ============================================================
# Database URLs for Async and Sync Operations
# ============================================================

def get_async_database_url() -> str:
    """Get async database URL for AsyncPG"""
    url = settings.DATABASE_URL
    if url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgresql+asyncpg://')
    return url


def get_sync_database_url() -> str:
    """Get sync database URL for psycopg2"""
    url = settings.DATABASE_URL
    if url.startswith('postgresql+asyncpg://'):
        url = url.replace('postgresql+asyncpg://', 'postgresql://')
    return url


# ============================================================
# Neon-Optimized Async Engine Factory
# ============================================================

def get_async_engine():
    """
    Create Neon-optimized async SQLAlchemy engine with:
    ✅ Increased connection timeout (Neon cold-start can take 10s+)
    ✅ Pool pre-ping (detects dead connections automatically)
    ✅ Retry logic for transient failures
    ✅ Optimized pool sizing for serverless Neon
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    
    return create_async_engine(
        get_async_database_url(),
        echo=settings.DATABASE_ECHO,
        future=True,
        pool_pre_ping=True,        # Detect dead Neon connections automatically
        pool_size=5,               # Keep small pool alive (Neon friendly)
        max_overflow=10,           # Allow overflow for burst connections
        connect_args={
            "timeout": 30,         # ⏱ Increase connection timeout (Neon wake-up can take 10s+)
            "command_timeout": 60, # ⏳ Allow long insertions (Base64 files)
            "ssl": "require",      # Enforce SSL for Neon
        }
    )


# ============================================================
# Logging Configuration
# ============================================================

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "detailed": {
            "formatter": "detailed",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        }
    },
}
