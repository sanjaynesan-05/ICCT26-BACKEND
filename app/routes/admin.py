"""
Admin routes - Admin panel endpoints for team and player management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from database import get_db
from app.services import DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/teams")
def get_all_teams(db: Session = Depends(get_db)):
    """
    Get all registered teams with player count.
    
    Returns a list of all teams with essential information:
    - Team ID, Name, Church Name
    - Captain and Vice-Captain details
    - Player count
    - Registration date
    - Payment receipt status
    """
    try:
        teams = DatabaseService.get_all_teams(db)
        return {"success": True, "teams": teams}

    except Exception as e:
        logger.error(f"Error fetching teams: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams/{team_id}")
def get_team_details(team_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific team and its player roster.

    Parameters:
    - team_id: The unique team identifier (string, e.g., 'ICCT26-0001')

    Returns:
    - Team information (ID, Name, Church, Captain, Vice-Captain, etc.)
    - Complete player roster with all details
    """
    try:
        team_data = DatabaseService.get_team_details(db, team_id)

        if not team_data:
            raise HTTPException(status_code=404, detail="Team not found")

        return team_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching team details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/players/{player_id}")
def get_player_details(player_id: int, db: Session = Depends(get_db)):
    """
    Fetch details of a specific player with team context.

    Parameters:
    - player_id: The unique player identifier (integer ID)

    Returns:
    - Player information (ID, Name, Age, Phone, Role, etc.)
    - Team information (Team ID, Name, Church)
    """
    try:
        player_data = DatabaseService.get_player_details(db, player_id)

        if not player_data:
            raise HTTPException(status_code=404, detail="Player not found")

        return player_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
