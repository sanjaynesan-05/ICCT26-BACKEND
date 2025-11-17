"""
Idempotency Service - ICCT26
=============================
Prevents duplicate submissions using idempotency keys.

Features:
- Database-backed key storage
- 10-minute TTL for keys
- Thread-safe operations
- Graceful duplicate rejection
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)
Base = declarative_base()


class IdempotencyKey(Base):
    """
    Store used idempotency keys with TTL.
    Prevents duplicate submissions within 10-minute window.
    """
    __tablename__ = "idempotency_keys"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    response_data = Column(String, nullable=True)  # Store original response


async def initialize_idempotency_table(db: AsyncSession) -> None:
    """Initialize idempotency_keys table on startup"""
    try:
        from database import async_engine
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Idempotency table initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize idempotency table: {e}")
        raise


async def check_idempotency_key(
    db: AsyncSession,
    key: str,
    ttl_minutes: int = 10
) -> Optional[str]:
    """
    Check if idempotency key has been used recently.
    
    Args:
        db: Database session
        key: Idempotency key from header
        ttl_minutes: TTL for keys (default 10 minutes)
    
    Returns:
        Optional[str]: Previous response data if duplicate, None if new
    """
    try:
        # Clean up expired keys first
        await cleanup_expired_keys(db)
        
        # Check if key exists and is not expired
        stmt = select(IdempotencyKey).where(
            IdempotencyKey.key == key,
            IdempotencyKey.expires_at > datetime.utcnow()
        )
        
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"⚠️ Duplicate submission detected: {key}")
            return existing.response_data
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error checking idempotency key: {e}")
        return None


async def store_idempotency_key(
    db: AsyncSession,
    key: str,
    response_data: str,
    ttl_minutes: int = 10
) -> None:
    """
    Store idempotency key after successful operation.
    
    Args:
        db: Database session
        key: Idempotency key
        response_data: JSON response to cache
        ttl_minutes: TTL for key
    """
    try:
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        
        idempotency_record = IdempotencyKey(
            key=key,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            response_data=response_data
        )
        
        db.add(idempotency_record)
        await db.commit()
        
        logger.info(f"✅ Stored idempotency key: {key}")
        
    except Exception as e:
        logger.error(f"❌ Error storing idempotency key: {e}")
        # Don't fail the request if we can't store the key


async def cleanup_expired_keys(db: AsyncSession) -> int:
    """
    Clean up expired idempotency keys.
    
    Args:
        db: Database session
    
    Returns:
        int: Number of keys deleted
    """
    try:
        from sqlalchemy import delete
        
        stmt = delete(IdempotencyKey).where(
            IdempotencyKey.expires_at < datetime.utcnow()
        )
        
        result = await db.execute(stmt)
        await db.commit()
        
        deleted_count = result.rowcount
        if deleted_count > 0:
            logger.info(f"🧹 Cleaned up {deleted_count} expired idempotency keys")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up idempotency keys: {e}")
        return 0
