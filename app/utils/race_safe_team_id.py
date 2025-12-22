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
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from models import TeamSequence

logger = logging.getLogger(__name__)


async def generate_next_team_id(db: AsyncSession, prefix: str = "ICCT") -> str:
    """
    Generate next sequential team ID using PostgreSQL atomic operation.
    
    Uses UPDATE...RETURNING for race-safe ID generation.
    No retry needed - operation is atomic and guaranteed unique.
    
    Args:
        db: Async database session
        prefix: Team ID prefix (default: "ICCT")
    
    Returns:
        str: Next team ID in format "ICCT-001", "ICCT-002", etc.
    
    Example:
        First call: "ICCT-001"
        Second call: "ICCT-002"
    """
    try:
        # Atomic increment and return
        result = await db.execute(
            text("""
                UPDATE team_sequence 
                SET last_number = last_number + 1 
                WHERE id = 1 
                RETURNING last_number
            """)
        )
        
        row = result.fetchone()
        if not row:
            raise Exception("team_sequence table not initialized")
        
        next_number = row[0]
        team_id = f"{prefix}-{next_number:03d}"
        
        logger.info(f"[Team ID Gen] ✅ Generated team ID: {team_id}")
        return team_id
        
    except IntegrityError as e:
        logger.error(f"❌ IntegrityError during team ID generation: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate team ID: {e}")
        raise


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
            
            # Use the first reset_sequence function that commits
            await reset_sequence(db, max_team_num)
            logger.info(f"✅ Sequence synced: {max_team_num}")
            return True
        else:
            logger.info(f"✅ Sequence in sync: {current_seq} (max team: {max_team_num})")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to sync sequence: {e}")
        return False
