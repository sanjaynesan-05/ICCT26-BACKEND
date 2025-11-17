"""
Registration routes with Cloudinary integration
Handles team and player registration with cloud file storage
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, DataError
from datetime import datetime
import time
import logging

from app.schemas_team import TeamRegistrationRequest
from app.utils import retry_db_operation
from app.utils.cloudinary_upload import upload_file_to_cloudinary
# Temporarily inlined to test
# from app.utils.team_id_generator import generate_sequential_team_id, generate_player_id
from app.services import EmailService
from models import Team, Player
from database import get_db_async
from sqlalchemy import func

logger = logging.getLogger(__name__)
router = APIRouter()


# TEMPORARY INLINE FUNCTIONS FOR TESTING
async def generate_sequential_team_id(db: AsyncSession) -> str:
    """Generate sequential team ID: ICCT-001, ICCT-002, etc."""
    result = await db.execute(select(func.count(Team.id)))
    team_count = result.scalar() or 0
    next_number = team_count + 1
    return f"ICCT-{next_number:03d}"

def generate_player_id(team_id: str, player_index: int) -> str:
    """Generate player ID: ICCT-XXX-P01, ICCT-XXX-P02, etc."""
    return f"{team_id}-P{player_index:02d}"


@router.post("/register/team", status_code=201)
@retry_db_operation(retries=3, delay=2)
async def register_team(
    registration: TeamRegistrationRequest,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Register a team for the ICCT26 Cricket Tournament with Cloudinary file storage.
    
    Creates team record and bulk inserts all players.
    Uploads all files (pastor letter, payment receipt, group photo, aadhar, subscription) to Cloudinary.
    Stores Cloudinary URLs in database instead of Base64.
    
    Request body (JSON):
    ```json
    {
      "churchName": "Church Name",
      "teamName": "Team Name",
      "pastorLetter": "data:image/jpeg;base64,...",
      "paymentReceipt": "data:image/png;base64,...",
      "groupPhoto": "data:image/jpeg;base64,...",
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
          "role": "Batsman",
          "aadharFile": "data:application/pdf;base64,...",
          "subscriptionFile": "data:application/pdf;base64,..."
        },
        ...
      ]
    }
    ```
    
    Response (201 Created):
    ```json
    {
      "success": true,
      "message": "Team and players registered successfully",
      "team_id": "ICCT26-20251117120000",
      "team_name": "Team Name",
      "church_name": "Church Name",
      "captain_name": "Captain Name",
      "vice_captain_name": "Vice Captain Name",
      "player_count": 11,
      "registration_date": "2025-11-17T12:00:00.123456",
      "files": {
        "pastor_letter_url": "https://res.cloudinary.com/.../pastor_letter.jpg",
        "payment_receipt_url": "https://res.cloudinary.com/.../payment_receipt.png",
        "group_photo_url": "https://res.cloudinary.com/.../group_photo.jpg"
      }
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

        # Generate sequential team ID (ICCT-001, ICCT-002, etc.)
        team_id = await generate_sequential_team_id(db)
        
        logger.info(f"{'='*70}")
        logger.info(f"📝 NEW TEAM REGISTRATION (Cloudinary Mode)")
        logger.info(f"{'='*70}")
        logger.info(f"Team ID:        {team_id}")
        logger.info(f"Team Name:      {registration.teamName}")
        logger.info(f"Church:         {registration.churchName}")
        logger.info(f"Captain:        {registration.captain.name} ({registration.captain.phone})")
        logger.info(f"Vice-Captain:   {registration.viceCaptain.name} ({registration.viceCaptain.phone})")
        logger.info(f"Players:        {len(registration.players)}")
        logger.info(f"{'='*70}")

        # ============================================================
        # STEP 1: Upload Team Files to Cloudinary
        # ============================================================
        logger.info("☁️ Uploading team files to Cloudinary...")
        
        pastor_letter_url = None
        payment_receipt_url = None
        group_photo_url = None
        
        try:
            # Upload pastor letter
            if registration.pastorLetter:
                logger.info("  📄 Uploading pastor letter...")
                public_id = f"{team_id}_pastorLetter_{int(time.time())}"
                pastor_letter_url = await upload_file_to_cloudinary(
                    registration.pastorLetter,
                    folder="icct26/teams/pastorLetters",
                    public_id=public_id
                )
                logger.info(f"  ✅ Pastor letter uploaded: {pastor_letter_url}")
            
            # Upload payment receipt
            if registration.paymentReceipt:
                logger.info("  💳 Uploading payment receipt...")
                public_id = f"{team_id}_payment_{int(time.time())}"
                payment_receipt_url = await upload_file_to_cloudinary(
                    registration.paymentReceipt,
                    folder="icct26/teams/payments",
                    public_id=public_id
                )
                logger.info(f"  ✅ Payment receipt uploaded: {payment_receipt_url}")
            
            # Upload group photo
            if registration.groupPhoto:
                logger.info("  📸 Uploading group photo...")
                public_id = f"{team_id}_groupPhoto_{int(time.time())}"
                group_photo_url = await upload_file_to_cloudinary(
                    registration.groupPhoto,
                    folder="icct26/teams/groupPhotos",
                    public_id=public_id
                )
                logger.info(f"  ✅ Group photo uploaded: {group_photo_url}")
        
        except Exception as e:
            logger.error(f"❌ Failed to upload team files: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "message": f"File upload failed: {str(e)}",
                    "error": "cloudinary_upload_error"
                }
            )

        # ============================================================
        # STEP 2: Create Team Record with Cloudinary URLs
        # ============================================================
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
            payment_receipt=payment_receipt_url,  # Cloudinary URL
            pastor_letter=pastor_letter_url,      # Cloudinary URL
            group_photo=group_photo_url,          # Cloudinary URL
            registration_date=datetime.now()
        )
        
        db.add(team)
        logger.info(f"✅ Team object created with Cloudinary URLs")

        # ============================================================
        # STEP 3: Upload Player Files and Create Player Records
        # ============================================================
        logger.info(f"☁️ Uploading player files to Cloudinary...")
        
        players_list = []
        for idx, player_data in enumerate(registration.players, 1):
            player_id = generate_player_id(team_id, idx)
            
            aadhar_url = None
            subscription_url = None
            
            try:
                # Upload Aadhar file
                if player_data.aadharFile:
                    logger.info(f"  📄 Player {idx}: Uploading Aadhar...")
                    public_id = f"{player_id}_aadhar_{int(time.time())}"
                    aadhar_url = await upload_file_to_cloudinary(
                        player_data.aadharFile,
                        folder="icct26/teams/aadhar",
                        public_id=public_id
                    )
                    logger.info(f"  ✅ Aadhar uploaded: {aadhar_url}")
                
                # Upload subscription file
                if player_data.subscriptionFile:
                    logger.info(f"  📄 Player {idx}: Uploading subscription...")
                    public_id = f"{player_id}_subscription_{int(time.time())}"
                    subscription_url = await upload_file_to_cloudinary(
                        player_data.subscriptionFile,
                        folder="icct26/teams/subscriptions",
                        public_id=public_id
                    )
                    logger.info(f"  ✅ Subscription uploaded: {subscription_url}")
            
            except Exception as e:
                logger.error(f"❌ Failed to upload files for player {idx}: {str(e)}")
                # Continue with other players, but log the error
                logger.warning(f"⚠️ Player {idx} files not uploaded, continuing...")
            
            # Create player record with Cloudinary URLs
            player = Player(
                player_id=player_id,
                team_id=team_id,
                name=player_data.name,
                role=player_data.role,
                aadhar_file=aadhar_url,         # Cloudinary URL
                subscription_file=subscription_url  # Cloudinary URL
            )
            
            players_list.append(player)
            logger.info(f"  ✅ Player {idx}/{len(registration.players)}: {player_id} - {player_data.name} ({player_data.role})")
        
        db.add_all(players_list)
        logger.info(f"✅ {len(players_list)} player records queued for database insert")

        # ============================================================
        # STEP 4: Commit to Database
        # ============================================================
        from app.db_utils import safe_commit
        await safe_commit(db, max_retries=3)
        logger.info(f"✅ All records committed to database successfully")

        # Refresh to get auto-generated IDs
        await db.refresh(team)
        logger.info(f"✅ Team record refreshed (DB ID: {team.id})")

        # ============================================================
        # STEP 5: Send Confirmation Email to Captain
        # ============================================================
        email_sent = False
        try:
            logger.info(f"📧 Sending confirmation email to captain: {registration.captain.email}")
            
            # Convert player data for email template
            from app.schemas import PlayerDetails
            player_details = [
                PlayerDetails(
                    name=player.name,
                    age=25,  # Default age since not in schema
                    phone="",  # Not available in current schema
                    role=player.role
                )
                for player in players_list
            ]
            
            # Create email content
            html_content = EmailService.create_confirmation_email(
                team_name=registration.teamName,
                captain_name=registration.captain.name,
                church_name=registration.churchName,
                team_id=team_id,
                players=player_details
            )
            
            # Send email
            email_result = EmailService.send_email(
                to_email=registration.captain.email,
                subject=f"🏏 Team Registration Confirmed - {registration.teamName}",
                html_content=html_content
            )
            
            email_sent = email_result.get('success', False)
            
            if email_sent:
                logger.info(f"✅ Confirmation email sent to {registration.captain.email}")
            else:
                logger.warning(f"⚠️ Email failed to send: {email_result.get('message', 'Unknown error')}")
                logger.warning(f"⚠️ Registration successful, but email not sent")
        
        except Exception as e:
            logger.error(f"❌ Email sending error: {str(e)}")
            logger.warning(f"⚠️ Registration successful, but email failed")
            # Don't fail the registration if email fails

        # Log success
        logger.info(f"{'='*70}")
        logger.info(f"✅ REGISTRATION SUCCESSFUL (Cloudinary Mode)")
        logger.info(f"Team ID: {team_id}, Players: {len(players_list)}")
        logger.info(f"Pastor Letter: {pastor_letter_url is not None}")
        logger.info(f"Payment Receipt: {payment_receipt_url is not None}")
        logger.info(f"Group Photo: {group_photo_url is not None}")
        logger.info(f"Email Sent: {'✅ YES' if email_sent else '❌ NO'}")
        logger.info(f"{'='*70}")

        # Return success response with Cloudinary URLs
        return {
            "success": True,
            "message": "Team and players registered successfully with cloud storage!",
            "team_id": team_id,
            "team_name": registration.teamName,
            "church_name": registration.churchName,
            "captain_name": registration.captain.name,
            "vice_captain_name": registration.viceCaptain.name,
            "player_count": len(registration.players),
            "registration_date": datetime.now().isoformat(),
            "email_sent": email_sent,
            "files": {
                "pastor_letter_url": pastor_letter_url,
                "payment_receipt_url": payment_receipt_url,
                "group_photo_url": group_photo_url
            }
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except IntegrityError as e:
        # Database integrity constraint violation
        logger.error(f"❌ Integrity error: {str(e.orig)}")
        await db.rollback()
        error_msg = str(e.orig).lower()
        if "not null" in error_msg:
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
                "message": "Registration failed due to server error",
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
        "description": "Register a team and players for ICCT26 with Cloudinary storage",
        "storage": "Cloudinary Cloud Storage"
    }
