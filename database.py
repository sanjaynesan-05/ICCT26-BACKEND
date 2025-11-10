"""
Database configuration and session management
Handles both sync and async database operations
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env.local (priority) or .env
load_dotenv('.env.local')  # Load .env.local first
load_dotenv()  # Then load .env as fallback

# ============================================================
# Synchronous Database Configuration (for psycopg2)
# ============================================================

# PostgreSQL connection URL - Use environment variable
# Read DATABASE_URL directly and convert for psycopg2
raw_db_url = os.environ.get(
    'DATABASE_URL',
    "postgresql://neondb_owner:npg_3ON2HQpSvJBT@ep-winter-salad-ad6doxno-pooler.c-2.us-east-1.aws.neon.tech/neondb?ssl=require"
)

# Convert to psycopg2 compatible format (sync)
DATABASE_URL = raw_db_url
if raw_db_url.startswith('postgresql+asyncpg://'):
    # Convert from async to sync format
    DATABASE_URL = raw_db_url.replace('postgresql+asyncpg://', 'postgresql://')
    # Replace ssl=require with sslmode=require for psycopg2
    DATABASE_URL = DATABASE_URL.replace('?ssl=require', '?sslmode=require')
    DATABASE_URL = DATABASE_URL.replace('&ssl=require', '&sslmode=require')
elif raw_db_url.startswith('postgres://'):
    DATABASE_URL = raw_db_url.replace('postgres://', 'postgresql://')

print(f"Sync DATABASE_URL configured: {DATABASE_URL[:70]}...")

# Create synchronous SQLAlchemy engine with optimized settings for Neon
connect_args = {}
if "neon.tech" in DATABASE_URL:
    connect_args = {
        "sslmode": "require",
        "connect_timeout": 10
    }

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes (Neon pooler limitation)
    pool_size=5,  # Smaller pool size for serverless
    max_overflow=2,
    echo=False,
    connect_args=connect_args
)

# Create synchronous session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================================
# Asynchronous Database Configuration (for asyncpg)
# ============================================================

# Convert to async format
DATABASE_URL_ASYNC = raw_db_url
if raw_db_url.startswith('postgresql://'):
    DATABASE_URL_ASYNC = raw_db_url.replace('postgresql://', 'postgresql+asyncpg://')
    # Replace sslmode=require with ssl=require for asyncpg
    DATABASE_URL_ASYNC = DATABASE_URL_ASYNC.replace('?sslmode=require', '?ssl=require')
    DATABASE_URL_ASYNC = DATABASE_URL_ASYNC.replace('&sslmode=require', '&ssl=require')

print(f"Async DATABASE_URL configured: {DATABASE_URL_ASYNC[:70]}...")

# Create asynchronous SQLAlchemy engine with optimized settings for Neon
async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_size=5,  # Smaller pool size for serverless
    max_overflow=2,
    future=True,
    connect_args={
        "server_settings": {"application_name": "icct26_backend"},
        "timeout": 10,
        "command_timeout": 30
    } if "neon.tech" in DATABASE_URL_ASYNC else {}
)

# Create asynchronous session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True
)

# ============================================================
# Base class for ORM models
# ============================================================

Base = declarative_base()

# ============================================================
# Dependency Providers
# ============================================================


def get_db():
    """
    Dependency for FastAPI - provides synchronous database session
    
    Usage:
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
    Dependency for FastAPI - provides asynchronous database session
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db_async)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
