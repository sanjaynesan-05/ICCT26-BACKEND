"""
Database Hardening
===================
Connection pooling, transient retry logic, and health checks.
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy import text
from config import settings
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseHealthCheck:
    """Database connection health checks"""
    
    @staticmethod
    async def check_connection(engine: AsyncEngine) -> bool:
        """
        Check if database connection is healthy.
        Returns True if connection successful.
        """
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("Database health check passed")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @staticmethod
    async def check_with_retry(engine: AsyncEngine, max_retries: int = 3) -> bool:
        """
        Check database connection with retries.
        """
        for attempt in range(1, max_retries + 1):
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    logger.info(f"Database ready (attempt {attempt})")
                    return True
            except Exception as e:
                logger.warning(
                    f"Database connection attempt {attempt}/{max_retries} failed: {e}"
                )
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error("Database health check failed after all retries")
        return False


class TransientErrorRetry:
    """Handle transient database errors with retry logic"""
    
    TRANSIENT_ERRORS = (
        "server closed the connection unexpectedly",
        "connection reset by peer",
        "connection closed",
        "connection timeout",
        "Lost connection",
    )
    
    @staticmethod
    def is_transient_error(error: Exception) -> bool:
        """Check if error is transient"""
        error_str = str(error).lower()
        return any(
            transient in error_str
            for transient in TransientErrorRetry.TRANSIENT_ERRORS
        )
    
    @staticmethod
    async def execute_with_retry(
        async_session: AsyncSession,
        operation,
        max_retries: int = 3,
        backoff_base: float = 1.0
    ):
        """
        Execute database operation with automatic retry on transient errors.
        """
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                return await operation(async_session)
            except OperationalError as e:
                last_error = e
                
                if attempt < max_retries and TransientErrorRetry.is_transient_error(e):
                    wait_time = backoff_base * (2 ** (attempt - 1))
                    logger.warning(
                        f"Transient DB error on attempt {attempt}, retrying in {wait_time}s",
                        extra={"error": str(e)}
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except SQLAlchemyError as e:
                logger.error(f"Database error: {e}")
                raise
        
        # All retries exhausted
        logger.error(f"Database operation failed after {max_retries} retries")
        raise last_error


class DatabasePooling:
    """Database connection pool configuration"""
    
    @staticmethod
    def get_pool_config(environment: str = "production"):
        """
        Get optimal pool configuration for environment.
        """
        if environment == "production":
            return {
                "poolclass": QueuePool,
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                "pool_recycle": settings.DATABASE_POOL_RECYCLE,
                "pool_pre_ping": True,  # Test connection before using
                "echo": False,
            }
        elif environment == "development":
            return {
                "poolclass": QueuePool,
                "pool_size": 5,
                "max_overflow": 5,
                "pool_recycle": 3600,
                "pool_pre_ping": True,
                "echo": False,
            }
        else:  # testing
            return {
                "poolclass": NullPool,  # No pooling for tests
            }
    
    @staticmethod
    def create_async_engine_with_pool(
        database_url: str,
        environment: str = "production"
    ) -> AsyncEngine:
        """
        Create async engine with optimal pool settings.
        """
        pool_config = DatabasePooling.get_pool_config(environment)
        
        engine = create_async_engine(
            database_url,
            **pool_config
        )
        
        logger.info(
            f"Database engine created with pool config",
            extra={"environment": environment, "config": str(pool_config)}
        )
        
        return engine


async def setup_database_healthcheck(engine: AsyncEngine):
    """
    Startup event: Check database connectivity.
    """
    logger.info("Starting database health check...")
    
    is_healthy = await DatabaseHealthCheck.check_with_retry(engine)
    
    if not is_healthy:
        raise RuntimeError(
            "Database connection failed. Cannot start application. "
            "Check DATABASE_URL and database server status."
        )
    
    logger.info("Database health check completed successfully")


async def teardown_database(engine: AsyncEngine):
    """
    Shutdown event: Cleanup database connections.
    """
    logger.info("Disposing database connections...")
    await engine.dispose()
    logger.info("Database connections disposed")
