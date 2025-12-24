"""
Church Team Limit Validator
Enforces maximum 2 teams per church.

This module provides validation logic for church team limits at registration time.
Safe for Neon PostgreSQL - does NOT use row-level locks on aggregate queries.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import Team
from fastapi import HTTPException

logger = logging.getLogger(__name__)

MAX_TEAMS_PER_CHURCH = 2


async def validate_church_limit(db: AsyncSession, church_name: str, request_id: str = "unknown") -> bool:
    """
    Validate that a church has not exceeded the 2 team limit.
    
    This function:
    1. Counts existing teams for the church (inside transaction)
    2. Returns True if registration can proceed (< 2 teams)
    3. Raises HTTPException 400 if limit exceeded (>= 2 teams)
    
    Safe for PostgreSQL - does NOT use FOR UPDATE on aggregate functions.
    
    Args:
        db: AsyncSession database connection
        church_name: The church name to check
        request_id: Optional request ID for logging
        
    Returns:
        True if church can register another team
        
    Raises:
        HTTPException with 400 status if limit exceeded
    """
    
    try:
        logger.info(f"[{request_id}] Checking church team limit for: {church_name}")
        
        # Count existing teams for this church
        # NO FOR UPDATE - PostgreSQL doesn't allow it on aggregate functions
        stmt = select(func.count(Team.id)).where(
            Team.church_name == church_name
        )
        
        result = await db.execute(stmt)
        team_count = result.scalar() or 0
        
        logger.info(f"[{request_id}] Current team count for '{church_name}': {team_count}")
        
        # Check if limit exceeded (maximum 2 teams per church)
        if team_count >= MAX_TEAMS_PER_CHURCH:
            logger.warning(
                f"[{request_id}] Church limit exceeded: "
                f"'{church_name}' already has {team_count} team(s), maximum is {MAX_TEAMS_PER_CHURCH}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {MAX_TEAMS_PER_CHURCH} teams already registered for this church"
            )
        
        logger.info(f"[{request_id}] Church limit check passed: {team_count}/{MAX_TEAMS_PER_CHURCH} teams")
        return True
        
    except HTTPException:
        # Re-raise HTTP exceptions (limit exceeded)
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error validating church limit: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error validating church registration limit"
        )


async def get_church_availability(db: AsyncSession) -> list:
    """
    Get availability status for all churches.
    
    Returns a list of churches with their team count and lock status.
    This is read-only and does not affect registration logic.
    
    Args:
        db: AsyncSession database connection
        
    Returns:
        List of dicts with: church_name, team_count, locked (bool)
    """
    
    try:
        # Query to get church_name and count of teams per church
        stmt = select(
            Team.church_name,
            func.count(Team.id).label('team_count')
        ).group_by(Team.church_name)
        
        result = await db.execute(stmt)
        rows = result.fetchall()
        
        # Format response
        churches = []
        for row in rows:
            church_name, team_count = row
            churches.append({
                "church_name": church_name,
                "team_count": team_count,
                "locked": team_count >= 2  # Locked if at or over 2 teams
            })
        
        # Sort by church name for consistency
        churches.sort(key=lambda x: x["church_name"])
        
        return churches
        
    except Exception as e:
        logger.error(f"Error fetching church availability: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching church availability"
        )
