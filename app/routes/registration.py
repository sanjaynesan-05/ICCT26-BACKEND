"""
Registration routes - Team registration endpoints
Handles team and player registration with async database operations
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, DataError
from datetime import datetime
import logging

from app.schemas_team import TeamRegistrationRequest
from models import Team, Player
from database import get_db_async

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register/team", status_code=201)
async def register_team(
    registration: TeamRegistrationRequest,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Register a team for the ICCT26 Cricket Tournament.
    
    Creates team record and bulk inserts all players linked to that team.
    Handles Base64 files (payment receipt, pastor letter, aadhar, subscription) safely.
    
    Request body (JSON):
    ```json
    {
      "churchName": "Church Name",
      "teamName": "Team Name",
      "pastorLetter": "data:image/jpeg;base64,...",
      "captain": {
        "name": "Captain Name",
        "phone": "+919876543210",
        "whatsapp": "919876543210",
        "email": "captain@example.com"
      },
      "viceCaptain": {
        "name": "Vice Captain Name",
        "phone": "+919876543211",
        "whatsapp": "919876543211",
        "email": "vicecaptain@example.com"
      },
      "players": [
        {
          "name": "Player Name",
          "age": 25,
          "phone": "+919800000001",
          "role": "Batsman",
          "aadharFile": "data:image/jpeg;base64,...",
          "subscriptionFile": "data:image/jpeg;base64,..."
        },
        ...
      ],
      "paymentReceipt": "data:image/jpeg;base64,..."
    }
    ```
    
    Response (201 Created):
    ```json
    {
      "success": true,
      "message": "Team and players registered successfully",
      "team_id": "ICCT26-20251112120000",
      "team_name": "Team Name",
      "church_name": "Church Name",
      "captain_name": "Captain Name",
      "vice_captain_name": "Vice Captain Name",
      "player_count": 11,
      "registration_date": "2025-11-12T12:00:00.123456"
    }
    ```
    """
    try:
        # Validate player count (11-15 required)
        if len(registration.players) < 11 or len(registration.players) > 15:
            logger.warning(
                f"❌ Invalid player count: {len(registration.players)} for team {registration.teamName}"
            )
            raise HTTPException(
                status_code=422,
                detail={
                    "success": False,
                    "message": f"Invalid player count. Expected 11-15 players, got {len(registration.players)}"
                }
            )

        # Generate team ID
        team_id = f"ICCT26-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"{'='*70}")
        logger.info(f"📝 NEW TEAM REGISTRATION")
        logger.info(f"{'='*70}")
        logger.info(f"Team ID:        {team_id}")
        logger.info(f"Team Name:      {registration.teamName}")
        logger.info(f"Church:         {registration.churchName}")
        logger.info(f"Captain:        {registration.captain.name} ({registration.captain.phone})")
        logger.info(f"Vice-Captain:   {registration.viceCaptain.name} ({registration.viceCaptain.phone})")
        logger.info(f"Players:        {len(registration.players)}")
        logger.info(f"{'='*70}")

        # Create Team record
        team = Team(
            team_id=team_id,
            team_name=registration.teamName,
            church_name=registration.churchName,
            captain_name=registration.captain.name,
            captain_phone=registration.captain.phone,
            captain_email=registration.captain.email,
            captain_whatsapp=registration.captain.whatsapp,
            vice_captain_name=registration.viceCaptain.name,
            vice_captain_phone=registration.viceCaptain.phone,
            vice_captain_email=registration.viceCaptain.email,
            vice_captain_whatsapp=registration.viceCaptain.whatsapp,
            payment_receipt=registration.paymentReceipt,
            pastor_letter=registration.pastorLetter,
            registration_date=datetime.now()
        )
        
        db.add(team)
        logger.info(f"✅ Team object created: {team_id}")

        # Create Player records (bulk insert)
        players_list = []
        for idx, player_data in enumerate(registration.players, 1):
            player_id = f"{team_id}-P{idx:02d}"
            # Use provided jersey_number or auto-assign from position
            jersey_num = player_data.jersey_number if player_data.jersey_number else str(idx)
            
            # DEBUG: Log the jersey_number source
            if player_data.jersey_number:
                logger.debug(f"  Player {idx}: Using FRONTEND jersey_number: {player_data.jersey_number}")
            else:
                logger.debug(f"  Player {idx}: AUTO-ASSIGNING jersey_number: {jersey_num}")
            
            player = Player(
                player_id=player_id,
                team_id=team_id,
                name=player_data.name,
                age=player_data.age,
                phone=player_data.phone,
                role=player_data.role,
                jersey_number=jersey_num,
                aadhar_file=player_data.aadharFile,
                subscription_file=player_data.subscriptionFile
            )
            
            # Verify player object has jersey_number before adding
            logger.debug(f"  Player object created: ID={player.player_id}, Jersey={player.jersey_number}")
            
            players_list.append(player)
            logger.info(f"  ✅ Player {idx}: {player_id} - {player_data.name} ({player_data.role}) Jersey: {jersey_num}")
        
        db.add_all(players_list)
        logger.info(f"✅ {len(players_list)} player records created and queued")
        
        # Verify all players have jersey_number before commit
        logger.info(f"🔍 Jersey verification before commit:")
        for p in players_list:
            logger.info(f"   - {p.player_id}: jersey_number = {p.jersey_number} (type: {type(p.jersey_number).__name__})")

        # Commit to database (with retry logic from db_utils)
        from app.db_utils import safe_commit
        await safe_commit(db, max_retries=3)
        logger.info(f"✅ All records committed to database successfully")

        # Refresh to get auto-generated IDs
        await db.refresh(team)
        logger.info(f"✅ Team record refreshed (DB ID: {team.id})")

        # Log success
        logger.info(f"{'='*70}")
        logger.info(f"✅ REGISTRATION SUCCESSFUL")
        logger.info(f"Team ID: {team_id}, Players: {len(players_list)}")
        logger.info(f"{'='*70}")

        # Return success response
        return {
            "success": True,
            "message": "Team and players registered successfully",
            "team_id": team_id,
            "team_name": registration.teamName,
            "church_name": registration.churchName,
            "captain_name": registration.captain.name,
            "vice_captain_name": registration.viceCaptain.name,
            "player_count": len(registration.players),
            "registration_date": datetime.now().isoformat()
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except IntegrityError as e:
        # Database integrity constraint violation (null, unique, etc.)
        logger.error(f"❌ Integrity error: {str(e.orig)}")
        await db.rollback()
        # Check what field failed
        error_msg = str(e.orig).lower()
        if "jersey_number" in error_msg:
            detail_msg = "Jersey number is required or invalid. Backend auto-assigns if omitted."
        elif "not null" in error_msg:
            detail_msg = "A required field is missing or null"
        elif "unique" in error_msg:
            detail_msg = "Duplicate entry (team_id or player_id already exists)"
        else:
            detail_msg = f"Database constraint violation: {str(e.orig)}"
        
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": detail_msg,
                "error": str(e.orig)
            }
        )
    
    except DataError as e:
        # Data too long, invalid data type, etc.
        logger.error(f"❌ Data error: {str(e.orig)}")
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": f"Invalid data format or field too long: {str(e.orig)}",
                "error": str(e.orig)
            }
        )
    
    except ValueError as e:
        # Validation errors
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "message": f"Validation error: {str(e)}"
            }
        )
    
    except Exception as e:
        # Database or other errors
        logger.error(f"❌ Registration failed: {type(e).__name__}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Registration failed due to database error",
                "error": str(e)
            }
        )


@router.get("/register/health", tags=["Registration"])
async def registration_health():
    """Health check for registration endpoint"""
    return {
        "status": "healthy",
        "endpoint": "/api/register/team",
        "method": "POST",
        "description": "Register a team and players for ICCT26"
    }
