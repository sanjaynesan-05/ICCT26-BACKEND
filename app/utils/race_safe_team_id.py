"""
Sequence-Based Team ID Generator - ICCT26
=========================================
Generates sequential team IDs using dedicated sequence table with row locking.

Features:
- Atomic ID generation with SELECT...FOR UPDATE locking
- No race conditions under concurrent requests
- Sequence table is source of truth (manually controllable)
- Automatic rollback on insert failure (no gaps)
- Works under high concurrent load
- Format: ICCT-001, ICCT-002, etc.
"""

import logging
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


async def generate_next_team_id(db: AsyncSession, prefix: str = "ICCT") -> str:
    """
    Generate next sequential team ID using sequence table with row locking.
    
    Uses SELECT...FOR UPDATE to ensure atomic operation:
    1. Lock sequence row (database enforces single reader)
    2. Read current last_number
    3. Increment atomically
    4. Update sequence table
    5. Lock released when transaction ends
    
    This prevents race conditions under ANY concurrent load.
    
    Args:
        db: Async database session
        prefix: Team ID prefix (default: "ICCT")
    
    Returns:
        str: Next team ID in format "ICCT-001", "ICCT-002", etc.
    
    Raises:
        Exception: If sequence table not initialized
    
    Example:
        Sequence: last_number = 5
        Returns: "ICCT-006"
        Sequence updated to: last_number = 6
    """
    try:
        # Step 1: LOCK the sequence row with SELECT...FOR UPDATE
        # This ensures only one transaction can access it at a time
        logger.debug(f"[Team ID Gen] Acquiring lock on team_sequence row...")
        
        result = await db.execute(
            text("""
                SELECT last_number 
                FROM team_sequence 
                WHERE id = 1
                FOR UPDATE
            """)
        )
        
        row = result.fetchone()
        if not row:
            raise Exception("team_sequence table not initialized. Run startup to initialize.")
        
        current_number = row[0]
        logger.debug(f"[Team ID Gen] Lock acquired. Current number: {current_number}")
        
        # Step 2: Increment atomically (while row is locked)
        next_number = current_number + 1
        
        # Step 3: Update sequence table (still locked, atomic operation)
        logger.debug(f"[Team ID Gen] Updating sequence: {current_number} → {next_number}")
        
        await db.execute(
            text("""
                UPDATE team_sequence 
                SET last_number = :next_num,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            """),
            {"next_num": next_number}
        )
        
        # Step 4: Generate and return formatted ID
        team_id = f"{prefix}-{next_number:03d}"
        logger.info(f"✅ Generated team ID: {team_id} (sequence: {current_number} → {next_number})")
        
        return team_id
        # Lock is automatically released when transaction ends
        # (either COMMIT or ROLLBACK)
        
    except IntegrityError as e:
        logger.error(f"❌ IntegrityError during team ID generation: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate team ID: {e}")
        raise


async def generate_next_team_id_with_retry(db: AsyncSession, max_retries: int = 5) -> str:
    """
    Generate team ID with retry logic.
    
    Retries if temporary database errors occur.
    
    Args:
        db: Async database session
        max_retries: Maximum retry attempts
    
    Returns:
        str: Next team ID
    
    Raises:
        Exception: If fails after max retries
    """
    for attempt in range(max_retries):
        try:
            return await generate_next_team_id(db)
        except Exception as e:
            await db.rollback()
            logger.warning(f"Team ID generation attempt {attempt + 1} failed: {e}")
            
            if attempt == max_retries - 1:
                logger.error(f"❌ Team ID generation failed after {max_retries} retries")
                raise
            
            # Small delay before retry
            delay = 0.1 * (attempt + 1)
            logger.info(f"Retrying in {delay}s...")
            await asyncio.sleep(delay)


async def get_current_sequence_number(db: AsyncSession) -> int:
    """
    Get current sequence number (for debugging/admin).
    
    Args:
        db: Async database session
    
    Returns:
        int: Current last_number value
    """
    try:
        result = await db.execute(
            text("SELECT last_number FROM team_sequence WHERE id = 1")
        )
        row = result.fetchone()
        return row[0] if row else 0
    except Exception as e:
        logger.error(f"❌ Failed to get sequence number: {e}")
        return 0


async def reset_sequence(db: AsyncSession, start_number: int = 0) -> bool:
    """
    Reset sequence to specific number (ADMIN USE ONLY).
    
    WARNING: Use only if you know what you're doing!
    This allows manual control over team ID numbering.
    
    Args:
        db: Async database session
        start_number: Number to reset to
    
    Returns:
        bool: True if successful
    """
    try:
        logger.warning(f"⚠️ ADMIN: Resetting team_sequence to {start_number}")
        
        await db.execute(
            text("""
                UPDATE team_sequence 
                SET last_number = :num,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            """),
            {"num": start_number}
        )
        
        await db.commit()
        logger.warning(f"✅ Sequence reset to {start_number}")
        return True
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to reset sequence: {e}")
        return False


async def sync_sequence_with_teams(db: AsyncSession) -> bool:
    """
    Sync sequence table with actual teams table.
    
    If sequence is out of sync, update it to match max team_id.
    Runs on startup to ensure consistency.
    
    Returns:
        bool: True if in sync or corrected
    """
    try:
        # Get max team number from teams table
        result = await db.execute(
            text("""
                SELECT COALESCE(MAX(CAST(SUBSTRING(team_id, 6) AS INTEGER)), 0)
                FROM teams
                WHERE team_id LIKE 'ICCT-%'
            """)
        )
        max_team_num = result.scalar() or 0
        
        # Get current sequence number
        current_seq = await get_current_sequence_number(db)
        
        if max_team_num > current_seq:
            logger.warning(f"⚠️ Sequence out of sync! Max team: ICCT-{max_team_num:03d}, Sequence: {current_seq}")
            logger.warning(f"Correcting sequence to {max_team_num}...")
            
            await reset_sequence(db, max_team_num)
            logger.info(f"✅ Sequence synced: {max_team_num}")
            return True
        else:
            logger.info(f"✅ Sequence in sync: {current_seq} (max team: {max_team_num})")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to sync sequence: {e}")
        return False


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
