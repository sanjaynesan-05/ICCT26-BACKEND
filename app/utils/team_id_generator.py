"""
Team ID generation utility
Generates sequential team IDs: ICCT-001, ICCT-002, ICCT-003, etc.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models import Team
import logging

logger = logging.getLogger(__name__)


async def generate_sequential_team_id(db: AsyncSession) -> str:
    """
    Generate sequential team ID in format: ICCT-001, ICCT-002, etc.
    
    Queries database to find the highest existing team number and increments it.
    Thread-safe with database-level counting.
    
    Args:
        db: Async database session
        
    Returns:
        str: Sequential team ID (e.g., "ICCT-001")
    """
    try:
        # Count existing teams to determine next number
        result = await db.execute(select(func.count(Team.id)))
        team_count = result.scalar() or 0
        
        # Next team number (1-indexed)
        next_number = team_count + 1
        
        # Format as ICCT-001, ICCT-002, etc. (3-digit zero-padded)
        team_id = f"ICCT-{next_number:03d}"
        
        logger.info(f"✅ Generated team ID: {team_id} (Total teams: {team_count + 1})")
        return team_id
        
    except Exception as e:
        logger.error(f"❌ Error generating team ID: {str(e)}")
        # Fallback to timestamp-based ID if database query fails
        from datetime import datetime
        fallback_id = f"ICCT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.warning(f"⚠️ Using fallback team ID: {fallback_id}")
        return fallback_id


def generate_player_id(team_id: str, player_index: int) -> str:
    """
    Generate player ID based on team ID and player index.
    
    Args:
        team_id: Team ID (e.g., "ICCT-001")
        player_index: Player number (1-indexed, 1-15)
        
    Returns:
        str: Player ID (e.g., "ICCT-001-P01", "ICCT-001-P02")
    """
    return f"{team_id}-P{player_index:02d}"


# Alias for backward compatibility
generate_team_id = generate_sequential_team_id
