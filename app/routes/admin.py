"""
Admin routes - Admin panel endpoints for team and player management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
import logging

from database import get_db_async
from app.services import DatabaseService
from app.utils.file_utils import fix_file_fields, fix_player_fields

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
    - Payment receipt and pastor letter (formatted as data URIs)
    """
    logger.info("GET /admin/teams - Fetching all teams...")
    try:
        teams = await DatabaseService.get_all_teams(db)
        
        # Fix Base64 file fields for each team
        for team in teams:
            team_with_files = {
                "payment_receipt": team.get("paymentReceipt"),
                "pastor_letter": team.get("pastorLetter")
            }
            fixed = fix_file_fields(team_with_files)
            team["paymentReceipt"] = fixed.get("payment_receipt")
            team["pastorLetter"] = fixed.get("pastor_letter")
        
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
    - All file fields formatted as proper data URIs
    """
    logger.info(f"GET /admin/teams/{team_id} - Fetching team details...")
    try:
        team_data = await DatabaseService.get_team_details(db, team_id)

        if not team_data:
            logger.warning(f"Team not found: {team_id}")
            raise HTTPException(status_code=404, detail="Team not found")

        # Fix Base64 file fields (add data URI prefixes)
        if "team" in team_data:
            # Convert team dict to format expected by fix_file_fields
            team_with_files = {
                "payment_receipt": team_data["team"].get("paymentReceipt"),
                "pastor_letter": team_data["team"].get("pastorLetter"),
                "players": []
            }
            
            # Add players with file fields
            if "players" in team_data:
                for player in team_data["players"]:
                    team_with_files["players"].append({
                        **player,
                        "aadhar_file": player.get("aadharFile"),
                        "subscription_file": player.get("subscriptionFile")
                    })
            
            # Apply fixes
            fixed_data = fix_file_fields(team_with_files)
            
            # Update original response
            team_data["team"]["paymentReceipt"] = fixed_data.get("payment_receipt")
            team_data["team"]["pastorLetter"] = fixed_data.get("pastor_letter")
            
            # Update players
            for i, player in enumerate(team_data.get("players", [])):
                if i < len(fixed_data["players"]):
                    player["aadharFile"] = fixed_data["players"][i].get("aadhar_file")
                    player["subscriptionFile"] = fixed_data["players"][i].get("subscription_file")

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
    - All file fields formatted as proper data URIs
    """
    logger.info(f"GET /admin/players/{player_id} - Fetching player details...")
    try:
        player_data = await DatabaseService.get_player_details(db, player_id)

        if not player_data:
            logger.warning(f"Player not found: {player_id}")
            raise HTTPException(status_code=404, detail="Player not found")

        # Fix Base64 file fields (add data URI prefixes)
        player_dict = {
            "aadhar_file": player_data.get("aadharFile"),
            "subscription_file": player_data.get("subscriptionFile")
        }
        fixed_player = fix_player_fields(player_dict)
        
        # Update response
        player_data["aadharFile"] = fixed_player.get("aadhar_file")
        player_data["subscriptionFile"] = fixed_player.get("subscription_file")

        logger.info(f"Successfully fetched player details for ID: {player_id}")
        return JSONResponse(content=player_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching player details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
