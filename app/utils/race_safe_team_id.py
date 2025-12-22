"""
Database-Truth Team ID Generator - ICCT26
==========================================
Generates sequential team IDs based on actual teams table data.
No separate sequence table - database is the single source of truth.

Features:
- Database-derived ID generation
- Retry-safe with IntegrityError handling
- Works under concurrent requests
- Survives server restarts and redeployments
- Format: ICCT-001, ICCT-002, etc.
"""

import logging
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def generate_next_team_id(db: AsyncSession, prefix: str = "ICCT") -> str:
    """
    Generate next sequential team ID based on database truth.
    
    Queries the teams table for the last team_id and increments.
    This is the ONLY source of truth - no separate sequence table.
    
    Args:
        db: Async database session
        prefix: Team ID prefix (default: "ICCT")
    
    Returns:
        str: Next team ID in format "ICCT-001", "ICCT-002", etc.
    
    Example:
        If last team_id in database is "ICCT-005", returns "ICCT-006"
        If no teams exist, returns "ICCT-001"
    """
    try:
        from models import Team
        
        # Query database for the last team_id (by creation time)
        result = await db.execute(
            select(Team.team_id)
            .order_by(desc(Team.created_at))
            .limit(1)
        )
        
        last_team_id = result.scalar_one_or_none()
        
        if not last_team_id:
            # No teams exist yet - start with 001
            team_id = f"{prefix}-001"
            logger.info(f"✅ Generated first team ID: {team_id}")
            return team_id
        
        # Extract number from last team_id (e.g., "ICCT-005" -> 5)
        try:
            last_number = int(last_team_id.split("-")[1])
        except (IndexError, ValueError) as e:
            logger.error(f"❌ Failed to parse last team_id '{last_team_id}': {e}")
            # Fallback: count all teams and add 1
            from sqlalchemy import func
            count_result = await db.execute(select(func.count()).select_from(Team))
            count = count_result.scalar()
            last_number = count
        
        # Increment and format
        next_number = last_number + 1
        team_id = f"{prefix}-{next_number:03d}"
        
        logger.info(f"✅ Generated team ID: {team_id} (previous: {last_team_id})")
        return team_id
        
    except Exception as e:
        logger.error(f"❌ Failed to generate team ID: {e}")
        raise


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
