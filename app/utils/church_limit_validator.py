"""
Church Team Limit Validator
Enforces maximum 2 teams per church with race condition protection.

This module provides validation logic for church team limits at registration time.
It uses database-level locking (SELECT FOR UPDATE) within a transaction to prevent
race conditions when multiple simultaneous registration requests occur.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from models import Team
from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def validate_church_limit(db: AsyncSession, church_name: str, request_id: str = "unknown") -> bool:
    """
    Validate that a church has not exceeded the 2 team limit.
    
    This function:
    1. Uses SELECT FOR UPDATE to lock the teams table rows for this church
    2. Counts existing teams for the church
    3. Returns True if registration can proceed (< 2 teams)
    4. Returns False if limit exceeded (>= 2 teams)
    
    Must be called within a transaction that will be committed after team insertion.
    
    Args:
        db: AsyncSession database connection
        church_name: The church name to check
        request_id: Optional request ID for logging
        
    Returns:
        True if church can register another team, False if limit exceeded
        
    Raises:
        HTTPException with 400 status if limit exceeded
    """
    
    try:
        logger.info(f"[{request_id}] Checking church team limit for: {church_name}")
        
        # Use SELECT FOR UPDATE to lock rows for this church
        # This prevents race conditions where two concurrent requests could both think
        # the limit hasn't been reached
        stmt = select(func.count(Team.id)).where(
            Team.church_name == church_name
        ).with_for_update()
        
        result = await db.execute(stmt)
        team_count = result.scalar() or 0
        
        logger.info(f"[{request_id}] Current team count for '{church_name}': {team_count}")
        
        # Check if limit exceeded (maximum 2 teams per church)
        if team_count >= 2:
            logger.warning(
                f"[{request_id}] Church limit exceeded: "
                f"'{church_name}' already has {team_count} team(s), maximum is 2"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Maximum 2 teams already registered for this church"
            )
        
        logger.info(f"[{request_id}] Church limit check passed: {team_count}/2 teams")
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
