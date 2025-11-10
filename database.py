"""
database.py
----------------------------------------
Database configuration and session management
Handles both sync and async database operations for FastAPI

✅ Compatible with Neon (ssl=require)
✅ Works locally and in Render
✅ Provides both sync and async DB access
✅ Safe logging without exposing credentials
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker
from dotenv import load_dotenv

# ============================================================
# ✅ Environment Setup
# ============================================================

# Load from .env.local first (local dev), fallback to .env
load_dotenv('.env.local')
load_dotenv()

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")

# ============================================================
# ✅ Read DATABASE_URL
# ============================================================

raw_db_url = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/neondb?sslmode=require"
)

if not raw_db_url:
    raise RuntimeError("❌ DATABASE_URL not set in environment variables!")

logger.info(f"🔗 Raw DATABASE_URL loaded: {raw_db_url[:60]}...")

# ============================================================
# ✅ Sync Database Configuration (psycopg2)
# ============================================================

DATABASE_URL = raw_db_url
if raw_db_url.startswith("postgresql+asyncpg://"):
    DATABASE_URL = raw_db_url.replace("postgresql+asyncpg://", "postgresql://")
    DATABASE_URL = DATABASE_URL.replace("?ssl=require", "?sslmode=require").replace("&ssl=require", "&sslmode=require")
elif raw_db_url.startswith("postgres://"):
    DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://")

logger.info(f"⚙️ Sync DATABASE_URL configured: {DATABASE_URL[:70]}...")

# Neon-compatible SSL args
connect_args = {}
if "neon.tech" in DATABASE_URL:
    connect_args = {"sslmode": "require", "connect_timeout": 10}

# Sync engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections (Neon pooler best practice)
    pool_size=5,
    max_overflow=2,
    echo=False,
    connect_args=connect_args
)

# Sync session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# ============================================================
# ✅ Async Database Configuration (asyncpg)
# ============================================================

DATABASE_URL_ASYNC = raw_db_url
if raw_db_url.startswith("postgresql://"):
    DATABASE_URL_ASYNC = raw_db_url.replace("postgresql://", "postgresql+asyncpg://")
    DATABASE_URL_ASYNC = DATABASE_URL_ASYNC.replace("?sslmode=require", "?ssl=require").replace("&sslmode=require", "&ssl=require")

logger.info(f"⚙️ Async DATABASE_URL configured: {DATABASE_URL_ASYNC[:70]}...")

async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=2,
    future=True,
    connect_args={
        "server_settings": {"application_name": "icct26_backend"},
        "timeout": 10,
        "command_timeout": 30
    } if "neon.tech" in DATABASE_URL_ASYNC else {}
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True
)

# ============================================================
# ✅ Base Model Class
# ============================================================

Base = declarative_base()

# ============================================================
# ✅ Session Providers
# ============================================================

def get_db():
    """
    FastAPI dependency: provides a synchronous database session.
    Example:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_async():
    """
    FastAPI dependency: provides an asynchronous database session.
    Example:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db_async)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
