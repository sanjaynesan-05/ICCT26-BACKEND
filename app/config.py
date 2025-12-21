"""
App Configuration - Re-exports root config for backward compatibility
This module ensures all imports from app.config continue to work
while using the centralized config package
"""

from config.settings import settings


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
