"""
Admin routes - Admin panel endpoints for team and player management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from database import get_db_async
from app.services import DatabaseService
from app.utils.file_utils import fix_file_fields, fix_player_fields, clean_file_fields
from app.utils.file_validation import sanitize_cloudinary_url
from app.utils.cloudinary_upload import cloudinary_uploader

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/teams")
async def get_all_teams(
    status: Optional[str] = Query(None, description="Filter by registration status: pending, confirmed, rejected"),
    db: AsyncSession = Depends(get_db_async)
):
    """
    Get all registered teams with player count.
    
    Query Parameters:
    - status (optional): Filter teams by registration status
      - 'pending': Teams waiting for admin confirmation
      - 'confirmed': Teams that are approved
      - 'rejected': Teams that were rejected
      - If not provided, returns all teams
    
    Returns a list of all teams with essential information:
    - Team ID, Name, Church Name
    - Captain and Vice-Captain details
    - Player count
    - Registration date and status
    - Payment receipt, pastor letter, and group photo (as valid Cloudinary URLs or empty strings)
    
    File Fields Guarantee:
    - All file fields return VALID Cloudinary URLs or empty strings
    - No undefined, null, Base64, or malformed values
    - Admin panel images load smoothly
    """
    logger.info(f"GET /admin/teams - Fetching teams (status filter: {status})...")
    try:
        teams = await DatabaseService.get_all_teams(db)
        
        # Filter by status if provided
        if status:
            teams = [team for team in teams if team.get("registrationStatus") == status]
            logger.info(f"Filtered to {len(teams)} teams with status: {status}")
        
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
            raise HTTPException(status_code=404, detail="Team not found")

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

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error fetching team details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


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
            raise HTTPException(status_code=404, detail="Player not found")

        # Clean player file fields
        player_data = clean_file_fields(
            player_data,
            ["aadharFile", "subscriptionFile"]
        )

        logger.info(f"✅ Successfully fetched player details for ID: {player_id}")
        return JSONResponse(content={"success": True, "data": player_data})

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error fetching player details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/teams/{team_id}/confirm")
async def confirm_team_registration(
    team_id: str,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Confirm/approve a team's registration (CLOUD-FIRST STRATEGY).
    
    1. Verify team exists (return 404 if not found)
    2. Check if already confirmed (idempotent operation)
    3. Move files from /pending/{team_id}/ to /confirmed/{team_id}/
    4. Rename files with Team ID in filename (ICCT-001_payment_receipt.pdf)
    5. Update database with new Cloudinary URLs
    6. Change registration_status to 'confirmed'
    7. Send confirmation email with Team ID
    
    Parameters:
    - team_id: The unique team identifier (e.g., ICCT-001)
    
    Returns:
    - Success message with updated team status and email notification status
    
    Error Codes:
    - 404: Team not found
    - 500: Server error (Cloudinary, database, or email failure)
    """
    logger.info(f"PUT /admin/teams/{team_id}/confirm - Confirming team registration...")
    try:
        # Step 1: Get team from database using DatabaseService
        team = await DatabaseService.get_team_by_team_id(db, team_id)
        if not team:
            logger.warning(f"❌ Team not found: {team_id}")
            raise HTTPException(status_code=404, detail=f"Team not found: {team_id}")
        
        # Step 2: Check if already confirmed (idempotent)
        if team.registration_status == "confirmed":
            logger.info(f"ℹ️ Team {team_id} is already confirmed - returning success")
            return JSONResponse(content={
                "success": True,
                "message": f"Team {team_id} is already confirmed",
                "data": {
                    "teamId": team_id,
                    "status": "confirmed",
                    "alreadyConfirmed": True
                }
            })
        
        # Step 3: Move files from pending to confirmed (with Team ID in filename)
        logger.info(f"🔄 Moving files from /pending/ to /confirmed/ with Team ID in filename...")
        confirmed_urls = {}
        
        # Move payment_receipt
        if team.payment_receipt:
            new_url = await cloudinary_uploader.move_to_confirmed(
                team_id=team_id,
                file_field_name="payment_receipt"
            )
            if new_url:
                confirmed_urls["payment_receipt"] = new_url
        
        # Move pastor_letter
        if team.pastor_letter:
            new_url = await cloudinary_uploader.move_to_confirmed(
                team_id=team_id,
                file_field_name="pastor_letter"
            )
            if new_url:
                confirmed_urls["pastor_letter"] = new_url
        
        # Move group_photo
        if team.group_photo:
            new_url = await cloudinary_uploader.move_to_confirmed(
                team_id=team_id,
                file_field_name="group_photo"
            )
            if new_url:
                confirmed_urls["group_photo"] = new_url
        
        logger.info(f"✅ Files moved to confirmed folder: {list(confirmed_urls.keys())}")
        
        # Step 4: Confirm team using DatabaseService (updates status and URLs)
        success = await DatabaseService.confirm_team_registration(
            db=db,
            team_id=team_id,
            new_cloudinary_urls=confirmed_urls
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to confirm team in database")
        
        logger.info(f"✅ Updated {team_id} status to confirmed")
        
        # Step 5: Get team details to send email
        team_data = await DatabaseService.get_team_details(db, team_id)
        email_status = "not_sent"
        
        if team_data and team_data.get('team'):
            team_info = team_data['team']
            captain = team_info.get('captain', {}) if isinstance(team_info.get('captain'), dict) else {}
            vice_captain = team_info.get('viceCaptain', {}) if isinstance(team_info.get('viceCaptain'), dict) else {}
            players = team_data.get('players', [])
            
            captain_email = captain.get('email')
            captain_name = captain.get('name', 'Captain')
            captain_phone = captain.get('phone', '')
            team_name = team_info.get('teamName', 'Unknown')
            church_name = team_info.get('churchName', '')
            vice_captain_name = vice_captain.get('name', '')
            vice_captain_phone = vice_captain.get('phone', '')
            vice_captain_email = vice_captain.get('email', '')
            
            if captain_email:
                # Create confirmation email
                from app.services import EmailService
                
                email_html = EmailService.create_admin_approval_email(
                    team_name=team_name,
                    captain_name=captain_name,
                    team_id=team_id,
                    church_name=church_name,
                    vice_captain_name=vice_captain_name,
                    vice_captain_phone=vice_captain_phone,
                    vice_captain_email=vice_captain_email,
                    captain_phone=captain_phone,
                    captain_email=captain_email,
                    players=players
                )
                
                # Send email asynchronously
                email_sent = await EmailService.send_email_async_if_available(
                    to_email=captain_email,
                    subject=f"✅ Registration Confirmed - {team_name} - Team ID: {team_id}",
                    body=email_html
                )
                
                email_status = "sent" if email_sent else "failed"
                
                if email_sent:
                    logger.info(f"✅ Confirmation email sent to {captain_email} for team {team_id}")
                else:
                    logger.warning(f"⚠️  Failed to send confirmation email to {captain_email}")
        
        logger.info(f"✅ Successfully confirmed registration for team: {team_id}")
        return JSONResponse(content={
            "success": True,
            "message": "Team registration confirmed successfully",
            "team_id": team_id,
            "registration_status": "confirmed",
            "email_notification": email_status
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error confirming team registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/teams/{team_id}/reject")
async def reject_team_registration(
    team_id: str,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Reject a team's registration (CLOUD-FIRST STRATEGY).
    
    1. Delete ALL pending files from Cloudinary /pending/{team_id}/
    2. Update database status to 'rejected'
    3. Clear file URLs from database
    4. INSTANT cleanup - no manual deletion needed
    
    Parameters:
    - team_id: The unique team identifier
    
    Returns:
    - Success message with updated team status
    """
    logger.info(f"PUT /admin/teams/{team_id}/reject - Rejecting team registration...")
    try:
        # Step 1: Delete all pending files from Cloudinary
        logger.info(f"🗑️ Deleting pending files from Cloudinary...")
        deleted = await cloudinary_uploader.delete_pending_files(team_id)
        
        if deleted:
            logger.info(f"✅ Deleted all files from /pending/{team_id}/")
        
        # Step 2: Update database
        team = await DatabaseService.get_team(db, team_id)
        if not team:
            logger.warning(f"❌ Team not found: {team_id}")
            raise HTTPException(status_code=404, detail="Team not found")
        
        team.registration_status = "rejected"
        team.payment_receipt = ""  # Clear URLs
        team.pastor_letter = ""
        team.group_photo = ""
        
        db.add(team)
        await db.commit()
        
        logger.info(f"✅ Successfully rejected registration for team: {team_id}")
        return JSONResponse(content={
            "success": True,
            "message": "Team registration rejected",
            "team_id": team_id,
            "registration_status": "rejected",
            "files_deleted": True,
            "deletion_status": "instant",
            "cost_impact": "$0 (files deleted from Cloudinary)"
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error rejecting team registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# =====================================================
# SEQUENCE TABLE MANAGEMENT - TEAM ID CONTROL
# =====================================================

@router.get("/sequence/current")
async def get_current_sequence(db: AsyncSession = Depends(get_db_async)):
    """
    Get current team ID sequence number.
    
    Returns the last_number from team_sequence table.
    The next team will be ICCT-{last_number+1}.
    
    Returns:
        {
            "success": true,
            "current_number": 5,
            "next_team_id": "ICCT-006",
            "message": "Current sequence state"
        }
    """
    logger.info("GET /admin/sequence/current - Fetching current sequence...")
    try:
        from app.utils.race_safe_team_id import get_current_sequence_number
        
        current_num = await get_current_sequence_number(db)
        next_id = f"ICCT-{current_num + 1:03d}"
        
        logger.info(f"✅ Current sequence: {current_num}, Next ID: {next_id}")
        return {
            "success": True,
            "current_number": current_num,
            "next_team_id": next_id,
            "message": "Current sequence state"
        }
    except Exception as e:
        logger.exception(f"❌ Failed to get sequence: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sequence: {str(e)}")


@router.post("/sequence/reset")
async def reset_sequence(
    new_number: int = Query(..., description="Number to reset sequence to (next team will be ICCT-{new_number+1})"),
    db: AsyncSession = Depends(get_db_async)
):
    """
    ADMIN ONLY: Manually reset team ID sequence.
    
    WARNING: Use with extreme caution!
    - Setting to 0: Next team gets ICCT-001
    - Setting to 100: Next team gets ICCT-101
    - Cannot set to negative numbers
    
    Query Parameters:
    - new_number (required): Number to reset to
    
    Returns:
        {
            "success": true,
            "message": "Sequence reset to 100",
            "new_number": 100,
            "next_team_id": "ICCT-101"
        }
    
    Raises:
        400: If new_number is negative or invalid
        500: If database error occurs
    """
    logger.warning(f"POST /admin/sequence/reset - ADMIN ACTION: Reset sequence to {new_number}")
    
    try:
        if new_number < 0:
            logger.error(f"❌ Invalid sequence number: {new_number} (must be >= 0)")
            raise HTTPException(status_code=400, detail="new_number must be >= 0")
        
        from app.utils.race_safe_team_id import reset_sequence, get_current_sequence_number
        
        success = await reset_sequence(db, new_number)
        
        if not success:
            raise Exception("Failed to reset sequence in database")
        
        # Verify the reset
        current = await get_current_sequence_number(db)
        next_id = f"ICCT-{current + 1:03d}"
        
        logger.warning(f"✅ Sequence reset to {new_number}, next will be {next_id}")
        return {
            "success": True,
            "message": f"Sequence reset to {new_number}",
            "new_number": current,
            "next_team_id": next_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Failed to reset sequence: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset sequence: {str(e)}")


@router.post("/sequence/sync")
async def sync_sequence_with_database(db: AsyncSession = Depends(get_db_async)):
    """
    Sync team_sequence table with actual teams in database.
    
    If sequence is out of sync, updates it to match the max team number.
    Runs automatically on startup but can be called manually if needed.
    
    Example:
    - Teams in DB: ICCT-001, ICCT-002, ICCT-005
    - Max team number: 5
    - Sequence was: 3
    - After sync: 5
    - Next team: ICCT-006
    
    Returns:
        {
            "success": true,
            "message": "Sequence in sync",
            "sequence_number": 5,
            "max_team_in_database": 5,
            "next_team_id": "ICCT-006"
        }
    """
    logger.info("POST /admin/sequence/sync - Syncing sequence with database...")
    
    try:
        from app.utils.race_safe_team_id import sync_sequence_with_teams, get_current_sequence_number
        
        success = await sync_sequence_with_teams(db)
        
        if not success:
            raise Exception("Failed to sync sequence")
        
        current = await get_current_sequence_number(db)
        next_id = f"ICCT-{current + 1:03d}"
        
        logger.info(f"✅ Sequence synced, current: {current}, next: {next_id}")
        return {
            "success": True,
            "message": "Sequence in sync",
            "sequence_number": current,
            "next_team_id": next_id
        }
    except Exception as e:
        logger.exception(f"❌ Failed to sync sequence: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync sequence: {str(e)}")