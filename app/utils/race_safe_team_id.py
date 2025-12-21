"""
Race-Safe Sequential Team ID Generator - ICCT26
================================================
Database-backed team ID generation with concurrency protection.
Uses SELECT FOR UPDATE to prevent race conditions.

Features:
- Atomic ID generation
- No duplicate IDs under concurrent requests
- Transaction-safe
- Format: ICCT-001, ICCT-002, etc.
"""

import logging
from sqlalchemy import Column, Integer, String, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)
Base = declarative_base()


class TeamSequence(Base):
    """
    Dedicated table for tracking sequential team IDs.
    Single row with last used number.
    """
    __tablename__ = "team_sequence"
    
    id = Column(Integer, primary_key=True, default=1)
    last_number = Column(Integer, nullable=False, default=0)
    prefix = Column(String(10), nullable=False, default="ICCT")


async def initialize_team_sequence(db: AsyncSession) -> None:
    """
    Initialize team_sequence table if it doesn't exist.
    Should be called on application startup.
    """
    try:
        # Create table if not exists
        from database import async_engine
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Check if sequence row exists, if not create it
        result = await db.execute(select(TeamSequence).where(TeamSequence.id == 1))
        sequence = result.scalar_one_or_none()
        
        if not sequence:
            sequence = TeamSequence(id=1, last_number=0, prefix="ICCT")
            db.add(sequence)
            await db.commit()
            logger.info("✅ Team sequence initialized with starting value 0")
        else:
            logger.info(f"✅ Team sequence already initialized at {sequence.last_number}")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize team sequence: {e}")
        raise


async def generate_next_team_id(db: AsyncSession, prefix: str = "ICCT") -> str:
    """
    Generate next sequential team ID with race condition protection.
    
    Uses raw SQL with database-level locking.
    Guarantees no duplicate IDs even under high concurrency.
    
    Args:
        db: Async database session (must not be in a transaction)
        prefix: Team ID prefix (default: "ICCT")
    
    Returns:
        str: Next team ID in format "ICCT-001", "ICCT-002", etc.
    
    Raises:
        Exception: If database operation fails
    """
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Ensure table exists with initial row
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS team_sequence (
                    id INTEGER PRIMARY KEY,
                    last_number INTEGER NOT NULL DEFAULT 0
                )
            """))
            
            # Ensure initial row exists
            await db.execute(text("""
                INSERT INTO team_sequence (id, last_number)
                VALUES (1, 0)
                ON CONFLICT (id) DO NOTHING
            """))
            
            # Lock and increment - database-level atomic operation
            result = await db.execute(text("""
                UPDATE team_sequence 
                SET last_number = last_number + 1 
                WHERE id = 1 
                RETURNING last_number
            """))
            
            row = result.fetchone()
            if not row:
                raise Exception("Failed to update sequence")
            
            next_number = row[0]
            team_id = f"{prefix}-{next_number:03d}"
            
            logger.info(f"✅ Generated team ID: {team_id}")
            return team_id
                
        except Exception as e:
            retry_count += 1
            logger.warning(f"⚠️ Team ID generation attempt {retry_count} failed: {e}")
            
            if retry_count >= max_retries:
                logger.error(f"❌ Team ID generation failed after {max_retries} retries: {e}")
                raise Exception(f"Failed to generate team ID after {max_retries} retries: {str(e)}")
            
            # Small delay before retry
            import asyncio
            await asyncio.sleep(0.1 * retry_count)
    
    raise Exception("Failed to generate team ID after all retries")


async def get_current_sequence_number(db: AsyncSession) -> int:
    """
    Get current sequence number (for testing/debugging).
    
    Args:
        db: Async database session
    
    Returns:
        int: Current last_number value
    """
    try:
        result = await db.execute(select(TeamSequence).where(TeamSequence.id == 1))
        sequence = result.scalar_one_or_none()
        return sequence.last_number if sequence else 0
    except Exception as e:
        logger.error(f"❌ Failed to get current sequence: {e}")
        return 0


async def reset_sequence(db: AsyncSession, start_number: int = 0) -> None:
    """
    Reset sequence to specific number (admin use only).
    
    Args:
        db: Async database session
        start_number: Number to reset to
    """
    try:
        async with db.begin_nested():
            stmt = select(TeamSequence).where(TeamSequence.id == 1).with_for_update()
            result = await db.execute(stmt)
            sequence = result.scalar_one_or_none()
            
            if sequence:
                sequence.last_number = start_number
                await db.flush()
                logger.warning(f"⚠️ Team sequence reset to {start_number}")
            else:
                logger.error("❌ Cannot reset: sequence not initialized")
                
    except Exception as e:
        logger.error(f"❌ Failed to reset sequence: {e}")
        raise
