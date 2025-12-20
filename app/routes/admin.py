"""
Admin routes - Admin panel endpoints for team and player management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
import logging

from database import get_db_async
from app.services import DatabaseService
from app.utils.file_utils import fix_file_fields, fix_player_fields, clean_file_fields
from app.utils.file_validation import sanitize_cloudinary_url

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
    - Payment receipt, pastor letter, and group photo (as valid Cloudinary URLs or empty strings)
    
    File Fields Guarantee:
    - All file fields return VALID Cloudinary URLs or empty strings
    - No undefined, null, Base64, or malformed values
    - Admin panel images load smoothly
    """
    logger.info("GET /admin/teams - Fetching all teams...")
    try:
        teams = await DatabaseService.get_all_teams(db)
        
        # Clean file fields: ensure they are valid Cloudinary URLs or empty strings
        for team in teams:
            team = clean_file_fields(
                team,
                ["paymentReceipt", "pastorLetter", "groupPhoto"]
            )
        
        logger.info(f"✅ Successfully fetched {len(teams)} teams with clean URLs")
        return JSONResponse(content={"success": True, "data": teams})

    except Exception as e:
        logger.exception(f"❌ Error fetching teams: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/teams/{team_id}")
async def get_team_details(team_id: str, db: AsyncSession = Depends(get_db_async)):
    """
    Get detailed information about a specific team and its player roster.

    Parameters:
    - team_id: The unique team identifier (string, e.g., 'TEAM-20251117-ABC12345')

    Returns:
    - Team information (ID, Name, Church, Captain, Vice-Captain, etc.)
    - Complete player roster with all details
    - All file fields as valid Cloudinary URLs or empty strings
    
    File Fields Guarantee:
    - Team files: paymentReceipt, pastorLetter, groupPhoto → valid URLs or empty strings
    - Player files: aadharFile, subscriptionFile → valid URLs or empty strings
    - No undefined, null, Base64, or malformed values
    """
    logger.info(f"GET /admin/teams/{team_id} - Fetching team details...")
    try:
        team_data = await DatabaseService.get_team_details(db, team_id)

        if not team_data:
            logger.warning(f"❌ Team not found: {team_id}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Team not found"}
            )

        # Clean team-level file fields
        if "team" in team_data:
            team_data["team"] = clean_file_fields(
                team_data["team"],
                ["paymentReceipt", "pastorLetter", "groupPhoto"]
            )
        
        # Clean player-level file fields
        if "players" in team_data and isinstance(team_data["players"], list):
            for player in team_data["players"]:
                player = clean_file_fields(
                    player,
                    ["aadharFile", "subscriptionFile"]
                )

        logger.info(f"✅ Successfully fetched details for team: {team_id}")
        return JSONResponse(content={"success": True, "data": team_data})

    except JSONResponse:
        raise
    except Exception as e:
        logger.exception(f"❌ Error fetching team details: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )


@router.get("/players/{player_id}")
async def get_player_details(player_id: int, db: AsyncSession = Depends(get_db_async)):
    """
    Fetch details of a specific player with team context.

    Parameters:
    - player_id: The unique player identifier (integer ID)

    Returns:
    - Player information (ID, Name, Role, etc.)
    - Team information (Team ID, Name, Church)
    - All file fields as valid Cloudinary URLs or empty strings
    
    File Fields Guarantee:
    - Player files: aadharFile, subscriptionFile → valid URLs or empty strings
    - No undefined, null, Base64, or malformed values
    """
    logger.info(f"GET /admin/players/{player_id} - Fetching player details...")
    try:
        player_data = await DatabaseService.get_player_details(db, player_id)

        if not player_data:
            logger.warning(f"❌ Player not found: {player_id}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Player not found"}
            )

        # Clean player file fields
        player_data = clean_file_fields(
            player_data,
            ["aadharFile", "subscriptionFile"]
        )

        logger.info(f"✅ Successfully fetched player details for ID: {player_id}")
        return JSONResponse(content={"success": True, "data": player_data})

    except JSONResponse:
        raise
    except Exception as e:
        logger.exception(f"❌ Error fetching player details: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )


@router.post("/payment/approve/{team_id}")
async def approve_payment(team_id: str, db: AsyncSession = Depends(get_db_async)):
    """
    Admin endpoint to approve a team's payment (change status from PENDING_PAYMENT to APPROVED).
    
    Parameters:
    - team_id: The unique team identifier
    
    Returns:
    - Updated team data with status set to APPROVED
    """
    logger.info(f"POST /admin/payment/approve/{team_id} - Approving payment...")
    try:
        team_data = await DatabaseService.get_team_details(db, team_id)
        
        if not team_data:
            logger.warning(f"❌ Team not found: {team_id}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Team not found"}
            )
        
        # Update status to APPROVED
        result = await DatabaseService.update_team_status(db, team_id, "APPROVED")
        
        if result:
            logger.info(f"✅ Payment approved for team: {team_id}")
            return JSONResponse(content={"success": True, "message": "Payment approved", "data": result})
        else:
            logger.error(f"❌ Failed to approve payment for team: {team_id}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Failed to update payment status"}
            )
        
    except Exception as e:
        logger.exception(f"❌ Error approving payment: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )


@router.post("/payment/reject/{team_id}")
async def reject_payment(team_id: str, db: AsyncSession = Depends(get_db_async)):
    """
    Admin endpoint to reject a team's payment (change status from PENDING_PAYMENT to REJECTED).
    
    Parameters:
    - team_id: The unique team identifier
    
    Returns:
    - Updated team data with status set to REJECTED
    """
    logger.info(f"POST /admin/payment/reject/{team_id} - Rejecting payment...")
    try:
        team_data = await DatabaseService.get_team_details(db, team_id)
        
        if not team_data:
            logger.warning(f"❌ Team not found: {team_id}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Team not found"}
            )
        
        # Update status to REJECTED
        result = await DatabaseService.update_team_status(db, team_id, "REJECTED")
        
        if result:
            logger.info(f"✅ Payment rejected for team: {team_id}")
            return JSONResponse(content={"success": True, "message": "Payment rejected", "data": result})
        else:
            logger.error(f"❌ Failed to reject payment for team: {team_id}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Failed to update payment status"}
            )
        
    except Exception as e:
        logger.exception(f"❌ Error rejecting payment: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )
