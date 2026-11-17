"""
Idempotency Service - ICCT26
=============================
Prevents duplicate submissions using idempotency keys.

Registration keys never expire: a retry that arrives after a committed
registration must replay the original 201. The claim/takeover logic for
POST /api/register/team lives in app/routes/registration_production.py:
  processing (fresh)            -> 409 REQUEST_IN_PROGRESS
  failed / processing > 15 min  -> taken over atomically by one request
  completed                     -> saved response replayed
The helpers below are generic and are not used by the registration route.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, select
from sqlalchemy.ext.asyncio import AsyncSession
from database import Base

logger = logging.getLogger(__name__)


class IdempotencyKey(Base):
    """
    Durable registration request state. Records are intentionally not expired:
    a retry after a committed transaction must replay the original result.
    """
    __tablename__ = "idempotency_keys"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    endpoint = Column(String(100), nullable=False, default="/api/register/team")
    request_fingerprint = Column(String(64), nullable=True)
    state = Column(String(20), nullable=False, default="processing", index=True)
    response_data = Column(Text, nullable=True)
    team_id = Column(String(50), nullable=True)


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
    Return the stored response for a key if the key exists (any age).
    
    Args:
        db: Database session
        key: Idempotency key from header
        ttl_minutes: Ignored; kept for backward compatibility
    
    Returns:
        Optional[str]: Previous response data if duplicate, None if new
    """
    try:
        # Completed and processing records are both relevant to replay safety.
        stmt = select(IdempotencyKey).where(
            IdempotencyKey.key == key
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
    ttl_minutes: int = 10,
    request_fingerprint: Optional[str] = None,
    state: str = "completed",
    team_id: Optional[str] = None
) -> None:
    """
    Store an idempotency key with its response. The key never expires
    (expires_at is left NULL).
    
    Args:
        db: Database session
        key: Idempotency key
        response_data: JSON response to cache
        ttl_minutes: Ignored; kept for backward compatibility
    """
    try:
        expires_at = None
        
        idempotency_record = IdempotencyKey(
            key=key,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            response_data=response_data,
            request_fingerprint=request_fingerprint,
            state=state,
            team_id=team_id,
        )
        
        db.add(idempotency_record)
        await db.commit()
        
        logger.info(f"✅ Stored idempotency key: {key}")
        
    except Exception as e:
        logger.error(f"❌ Error storing idempotency key: {e}")
        # Don't fail the request if we can't store the key


async def cleanup_expired_keys(db: AsyncSession) -> int:
    """
    Delete keys whose expires_at is set and in the past.
    
    Registration keys are stored with expires_at = NULL, so this never
    deletes them; it only removes rows that were explicitly given an expiry.
    
    Args:
        db: Database session
    
    Returns:
        int: Number of keys deleted (normally 0)
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
            logger.info(f"🧹 Deleted {deleted_count} idempotency keys with a past expires_at")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up idempotency keys: {e}")
        return 0


# Alias for backward compatibility
save_idempotency_key = store_idempotency_key
