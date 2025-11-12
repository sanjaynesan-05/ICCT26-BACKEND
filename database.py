"""
Database configuration for ICCT26 API
Complete async + sync support with PostgreSQL and Neon

Features:
✅ Full async/await support with asyncpg
✅ Sync support for sync endpoints
✅ Neon PostgreSQL compatibility
✅ Connection pooling optimized for serverless
✅ SSL/TLS security
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# ============================================================
# Configuration
# ============================================================

# Load environment variables (.env.local first, then .env)
load_dotenv('.env.local')
load_dotenv()

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")

# ============================================================
# Read DATABASE_URL
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/icct26?sslmode=require"
)

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL environment variable not set!")

logger.info(f"🔗 Database URL loaded: {DATABASE_URL[:60]}...")


# ============================================================
# Helper: Convert URL format
# ============================================================

def get_sync_database_url() -> str:
    """
    Convert async URL to sync URL for psycopg2
    - Replace postgresql+asyncpg:// with postgresql://
    - Ensure ?ssl=require becomes ?sslmode=require
    """
    url = DATABASE_URL
    
    # Convert asyncpg to sync
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    
    # Fix SSL parameter
    url = url.replace("?ssl=require", "?sslmode=require")
    url = url.replace("&ssl=require", "&sslmode=require")
    
    return url


def get_async_database_url() -> str:
    """
    Convert sync URL to async URL for asyncpg
    - Replace postgresql:// with postgresql+asyncpg://
    - Ensure ?sslmode=require becomes ?ssl=require
    """
    url = DATABASE_URL
    
    # Convert to asyncpg if not already
    if not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    
    # Fix SSL parameter
    url = url.replace("?sslmode=require", "?ssl=require")
    url = url.replace("&sslmode=require", "&ssl=require")
    
    return url


# ============================================================
# Sync Database (psycopg2)
# ============================================================

SYNC_DATABASE_URL = get_sync_database_url()
logger.info(f"⚙️  Sync URL: {SYNC_DATABASE_URL[:60]}...")

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_size=5,       # Neon pooler limit
    max_overflow=2,    # Allow overflow beyond pool_size
    echo=False,
    future=True
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


# ============================================================
# Async Database (asyncpg)
# ============================================================

ASYNC_DATABASE_URL = get_async_database_url()
logger.info(f"⚙️  Async URL: {ASYNC_DATABASE_URL[:60]}...")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    poolclass=NullPool,  # ✅ CRITICAL: Fresh connection for each request (prevents Neon "connection closed" errors)
    pool_pre_ping=True,   # ✅ Validates connection alive before use
    future=True,
    connect_args={
        "server_settings": {"application_name": "icct26_backend"},
        "timeout": 30,     # ✅ Increased from 10s to 30s for cold-start
    }
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True
)

# ============================================================
# Base Model Class
# ============================================================

Base = declarative_base()


# ============================================================
# Dependency Providers
# ============================================================

def get_db():
    """
    FastAPI sync dependency for database session.
    
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Your code here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_async():
    """
    FastAPI async dependency for database session.
    
    Usage:
        @app.post("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db_async)):
            # Your code here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ============================================================
# Logging
# ============================================================

logger.info("✅ Database configuration loaded successfully")
logger.info(f"   Sync engine: {type(sync_engine).__name__}")
logger.info(f"   Async engine: {type(async_engine).__name__}")
