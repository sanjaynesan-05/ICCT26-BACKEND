"""
Admin routes - Admin panel endpoints for team and player management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
import logging

from database import get_db_async
from app.services import DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/teams")
async def get_all_teams(db: AsyncSession = Depends(get_db_async)):
    """
    Get all registered teams with player count.
    
    Returns a list of all teams with essential information:
    - Team ID, Name, Church Name
    - Captain and Vice-Captain details
    - Player count
    - Registration date
    - Payment receipt status
    """
    logger.info("GET /admin/teams - Fetching all teams...")
    try:
        teams = await DatabaseService.get_all_teams(db)
        logger.info(f"Successfully fetched {len(teams)} teams")
        return JSONResponse(content={"success": True, "teams": teams})

    except Exception as e:
        logger.exception(f"Error fetching teams: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/teams/{team_id}")
async def get_team_details(team_id: str, db: AsyncSession = Depends(get_db_async)):
    """
    Get detailed information about a specific team and its player roster.

    Parameters:
    - team_id: The unique team identifier (string, e.g., 'ICCT26-0001')

    Returns:
    - Team information (ID, Name, Church, Captain, Vice-Captain, etc.)
    - Complete player roster with all details
    """
    logger.info(f"GET /admin/teams/{team_id} - Fetching team details...")
    try:
        team_data = await DatabaseService.get_team_details(db, team_id)

        if not team_data:
            logger.warning(f"Team not found: {team_id}")
            raise HTTPException(status_code=404, detail="Team not found")

        logger.info(f"Successfully fetched details for team: {team_id}")
        return JSONResponse(content=team_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching team details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/players/{player_id}")
async def get_player_details(player_id: int, db: AsyncSession = Depends(get_db_async)):
    """
    Fetch details of a specific player with team context.

    Parameters:
    - player_id: The unique player identifier (integer ID)

    Returns:
    - Player information (ID, Name, Age, Phone, Role, etc.)
    - Team information (Team ID, Name, Church)
    """
    logger.info(f"GET /admin/players/{player_id} - Fetching player details...")
    try:
        player_data = await DatabaseService.get_player_details(db, player_id)

        if not player_data:
            logger.warning(f"Player not found: {player_id}")
            raise HTTPException(status_code=404, detail="Player not found")

        logger.info(f"Successfully fetched player details for ID: {player_id}")
        return JSONResponse(content=player_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching player details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
