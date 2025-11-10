"""
Registration routes - Team registration endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from app.schemas import SuccessResponse
from app.schemas_team import TeamRegistrationRequest
from app.services import EmailService, DatabaseService
from database import get_db_async

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register/team", response_model=dict)
async def register_team(
    registration: TeamRegistrationRequest,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Register a team for the ICCT26 Cricket Tournament.
    
    Accepts the following JSON payload:
    ```json
    {
      "churchName": "Church Name",
      "teamName": "Team Name",
      "pastorLetter": "data:image/jpeg;base64,...",  # Optional
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
          "role": "Batsman|Bowler|All-Rounder|Wicket Keeper",
          "aadharFile": "data:image/jpeg;base64,...",  # Optional
          "subscriptionFile": "data:image/jpeg;base64,..."  # Optional
        },
        // ... 10-14 more players (11-15 total required)
      ],
      "paymentReceipt": "data:image/jpeg;base64,..."  # Optional
    }
    ```
    
    Returns:
    ```json
    {
      "success": true,
      "message": "Team registration successful",
      "data": {
        "team_id": "ICCT26-20251109093800",
        "team_name": "Team Name",
        "church_name": "Church Name",
        "captain_name": "Captain Name",
        "vice_captain_name": "Vice Captain Name",
        "players_count": 11,
        "registered_at": "2025-11-09T09:38:00.123456",
        "email_sent": true,
        "database_saved": true
      }
    }
    ```
    """
    try:
        # Validate player count
        if len(registration.players) < 11 or len(registration.players) > 15:
            logger.warning(
                f"Invalid player count: {len(registration.players)} for team {registration.teamName}"
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

        logger.info(f"{'='*60}")
        logger.info(f"📝 New Registration: {registration.teamName}")
        logger.info(f"   Team ID: {team_id}")
        logger.info(f"   Church: {registration.churchName}")
        logger.info(f"   Captain: {registration.captain.name}")
        logger.info(f"   Vice-Captain: {registration.viceCaptain.name}")
        logger.info(f"   Players: {len(registration.players)}")
        logger.info(f"{'='*60}")

        # Save to database
        db_id = await DatabaseService.save_registration_to_db(db, registration, team_id)
        logger.info(f"✅ Saved to database with ID: {db_id}")

        # Send confirmation email to captain
        captain_email = registration.captain.email
        email_subject = f"ICCT26 Registration Confirmed - {team_id}"
        email_html = EmailService.create_confirmation_email(
            team_name=registration.teamName,
            captain_name=registration.captain.name,
            church_name=registration.churchName,
            team_id=team_id,
            players=registration.players
        )

        email_result = EmailService.send_email(captain_email, email_subject, email_html)

        logger.info(f"✅ Registration completed for team {registration.teamName}")

        return {
            "success": True,
            "message": "Team registration successful",
            "data": {
                "team_id": team_id,
                "team_name": registration.teamName,
                "church_name": registration.churchName,
                "captain_name": registration.captain.name,
                "vice_captain_name": registration.viceCaptain.name,
                "players_count": len(registration.players),
                "registered_at": datetime.now().isoformat(),
                "email_sent": email_result.get("success", False),
                "database_saved": True
            }
        }

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "message": f"Validation error: {str(e)}"
            }
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": f"Registration failed: {str(e)}"
            }
        )
