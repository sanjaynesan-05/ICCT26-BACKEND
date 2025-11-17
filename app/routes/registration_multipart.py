"""
Team Registration Endpoint with Multipart File Upload
====================================================
Accepts files via multipart/form-data and uploads to Cloudinary.
NO base64 - direct file uploads only.
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import json
import uuid
from datetime import datetime
import logging

from database import get_db
from models import Team, Player
from app.schemas_multipart import (
    TeamRegistrationMultipart,
    TeamRegistrationResponse,
    TeamRegistrationResponseData,
    ErrorResponse,
    PlayerCreateMultipart
)
from app.utils.cloudinary_upload import (
    upload_team_files,
    upload_player_files
)
from app.utils.file_validation import (
    validate_team_files,
    validate_player_files,
    validate_required_fields,
    sanitize_cloudinary_url
)

router = APIRouter()
logger = logging.getLogger(__name__)

def generate_team_id() -> str:
    """Generate unique team ID: TEAM-YYYYMMDD-XXXXXXXX"""
    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
    return f"TEAM-{date_str}-{unique_id}"

def generate_player_id(team_id: str, index: int) -> str:
    """Generate player ID: TEAM-YYYYMMDD-XXXXXXXX-P01"""
    return f"{team_id}-P{index:02d}"


@router.post(
    "/register/team",
    response_model=TeamRegistrationResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Register a new team with file uploads",
    description="Upload team and player files directly via multipart/form-data. Files are stored in Cloudinary."
)
async def register_team_multipart(
    # Team basic info as JSON string
    team_data: str = Form(..., description="Team registration data as JSON string"),
    
    # Team-level file uploads
    pastor_letter: Optional[UploadFile] = File(None, description="Pastor recommendation letter (PDF)"),
    payment_receipt: Optional[UploadFile] = File(None, description="Payment receipt (image or PDF)"),
    group_photo: Optional[UploadFile] = File(None, description="Team group photo (image)"),
    
    # Player files as lists (one per player)
    player_aadhar_files: List[UploadFile] = File(..., description="Aadhar files for all players (PDF)"),
    player_subscription_files: List[UploadFile] = File(..., description="Subscription files for all players (PDF)"),
    
    # Database session
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new team with multipart file uploads.
    
    **Request format:**
    - `team_data`: JSON string containing team info, captain, vice-captain, and players
    - `pastor_letter`: File upload (PDF)
    - `payment_receipt`: File upload (image/PDF)
    - `group_photo`: File upload (image)
    - `player_aadhar_files[]`: Array of file uploads (PDF, one per player)
    - `player_subscription_files[]`: Array of file uploads (PDF, one per player)
    
    **Response:**
    ```json
    {
      "success": true,
      "message": "Team registered successfully",
      "team_id": "TEAM-20251117-ABC12345",
      "player_count": 12,
      "captain_name": "John Doe",
      "team_name": "Warriors"
    }
    ```
    """
    try:
        logger.info("=" * 70)
        logger.info("📝 NEW TEAM REGISTRATION REQUEST")
        logger.info("=" * 70)
        
        # STEP 1: Parse and validate team data JSON
        logger.info("STEP 1: Parsing team data...")
        try:
            team_dict = json.loads(team_data)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in team_data: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON format in team_data: {str(e)}"
            )
        
        # Validate required fields in team data
        logger.info("STEP 1.1: Validating required fields...")
        validate_required_fields(
            team_dict,
            ['team_name', 'church_name', 'captain', 'vice_captain', 'players']
        )
        
        # Parse into Pydantic model for validation
        try:
            team_info = TeamRegistrationMultipart(**team_dict)
        except Exception as e:
            logger.error(f"❌ Team data validation failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid team data format: {str(e)}"
            )
        
        logger.info(f"✅ Team data parsed: {team_info.team_name} ({len(team_info.players)} players)")
        
        # STEP 2: Validate all file uploads
        logger.info("STEP 2: Validating file uploads...")
        
        player_count = len(team_info.players)
        
        # Validate team files (type, size, format)
        try:
            validate_team_files(
                pastor_letter=pastor_letter,
                payment_receipt=payment_receipt,
                group_photo=group_photo
            )
            logger.info("✅ Team files validated")
        except HTTPException as e:
            logger.error(f"❌ Team file validation failed: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected team file validation error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Team file validation failed: {str(e)}"
            )
        
        # Validate player files (count, type, size, format)
        try:
            validate_player_files(
                aadhar_files=player_aadhar_files,
                subscription_files=player_subscription_files,
                expected_count=player_count
            )
            logger.info(f"✅ Player files validated for {player_count} players")
        except HTTPException as e:
            logger.error(f"❌ Player file validation failed: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected player file validation error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Player file validation failed: {str(e)}"
            )
        
        # STEP 3: Generate team ID
        team_id = generate_team_id()
        logger.info(f"STEP 3: Generated team ID: {team_id}")
        
        # STEP 4: Upload team files to Cloudinary
        logger.info(f"STEP 4: Uploading team files to Cloudinary...")
        try:
            team_file_urls = await upload_team_files(
                team_id=team_id,
                pastor_letter=pastor_letter,
                payment_receipt=payment_receipt,
                group_photo=group_photo
            )
            logger.info(f"✅ Team files uploaded successfully")
            logger.info(f"   - Pastor Letter: {team_file_urls.get('pastor_letter_url', 'N/A')[:50]}...")
            logger.info(f"   - Payment Receipt: {team_file_urls.get('payment_receipt_url', 'N/A')[:50]}...")
            logger.info(f"   - Group Photo: {team_file_urls.get('group_photo_url', 'N/A')[:50]}...")
        
        except HTTPException as e:
            logger.error(f"❌ Cloudinary upload failed for team files: {e.detail}")
            # Convert Cloudinary errors to user-friendly messages
            if hasattr(e, 'status_code') and e.status_code == 400:
                raise HTTPException(
                    status_code=400,
                    detail="File upload validation failed. One or more files may be corrupted or in an unsupported format."
                )
            raise HTTPException(
                status_code=500,
                detail="An error occurred while uploading team files to cloud storage. Please try again."
            )
        
        except Exception as e:
            logger.error(f"❌ Unexpected error uploading team files: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred during file upload. Please try again later."
            )
        
        # STEP 5: Create team record in database
        logger.info(f"STEP 5: Creating team record in database...")
        try:
            new_team = Team(
                team_id=team_id,
                team_name=team_info.team_name,
                church_name=team_info.church_name,
                captain_name=team_info.captain.name,
                captain_phone=team_info.captain.phone,
                captain_whatsapp=team_info.captain.whatsapp,
                captain_email=team_info.captain.email,
                vice_captain_name=team_info.vice_captain.name,
                vice_captain_phone=team_info.vice_captain.phone,
                vice_captain_whatsapp=team_info.vice_captain.whatsapp,
                vice_captain_email=team_info.vice_captain.email,
                pastor_letter=sanitize_cloudinary_url(team_file_urls.get('pastor_letter_url')),
                payment_receipt=sanitize_cloudinary_url(team_file_urls.get('payment_receipt_url')),
                group_photo=sanitize_cloudinary_url(team_file_urls.get('group_photo_url')),
                registered_at=datetime.now()
            )
            
            db.add(new_team)
            await db.flush()  # Get team ID before adding players
            logger.info(f"✅ Team {team_id} created in database")
        
        except Exception as e:
            logger.error(f"❌ Database error creating team: {str(e)}", exc_info=True)
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to save team information to database. Please try again."
            )
        
        # STEP 6: Process and upload player files
        logger.info(f"STEP 6: Processing {player_count} players...")
        players_created = []
        
        try:
            for idx, player_info in enumerate(team_info.players, start=1):
                player_id = generate_player_id(team_id, idx)
                
                logger.info(f"   Processing player {idx}/{player_count}: {player_info.name}")
                
                # Upload player files to Cloudinary
                try:
                    player_file_urls = await upload_player_files(
                        team_id=team_id,
                        player_id=player_id,
                        aadhar_file=player_aadhar_files[idx - 1],
                        subscription_file=player_subscription_files[idx - 1]
                    )
                    logger.info(f"   ✅ Player {idx} files uploaded")
                
                except HTTPException as e:
                    logger.error(f"❌ Cloudinary upload failed for player {idx}: {e.detail}")
                    await db.rollback()
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to upload files for player {idx} ({player_info.name}). Please check file format and try again."
                    )
                
                except Exception as e:
                    logger.error(f"❌ Unexpected error uploading files for player {idx}: {str(e)}")
                    await db.rollback()
                    raise HTTPException(
                        status_code=500,
                        detail=f"An error occurred while uploading files for player {idx}. Please try again."
                    )
                
                # Create player record in database
                try:
                    new_player = Player(
                        player_id=player_id,
                        team_id=team_id,
                        name=player_info.name,
                        role=player_info.role,
                        dob=datetime.strptime(player_info.dob, '%Y-%m-%d').date(),
                        aadhar_file=sanitize_cloudinary_url(player_file_urls.get('aadhar_url')),
                        subscription_file=sanitize_cloudinary_url(player_file_urls.get('subscription_url'))
                    )
                    
                    db.add(new_player)
                    players_created.append(new_player)
                    logger.info(f"   ✅ Player {player_id} created in database")
                
                except Exception as e:
                    logger.error(f"❌ Database error creating player {idx}: {str(e)}")
                    await db.rollback()
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to save player {idx} information to database."
                    )
            
            logger.info(f"✅ All {player_count} players processed successfully")
        
        except HTTPException:
            # Re-raise HTTP exceptions (already logged above)
            raise
        
        except Exception as e:
            logger.error(f"❌ Unexpected error processing players: {str(e)}", exc_info=True)
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while processing player information."
            )
        
        # STEP 7: Commit all changes to database
        logger.info("STEP 7: Committing all changes to database...")
        try:
            await db.commit()
            logger.info(f"✅ Transaction committed successfully")
        
        except Exception as e:
            logger.error(f"❌ Database commit failed: {str(e)}", exc_info=True)
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to finalize registration. Please contact support if this persists."
            )
        
        # STEP 8: Build response with clean data
        logger.info("STEP 8: Building response...")
        
        # Build response data with only Cloudinary URLs (no other metadata)
        response_data = TeamRegistrationResponseData(
            team_name=team_info.team_name,
            church_name=team_info.church_name,
            pastor_letter=sanitize_cloudinary_url(team_file_urls.get('pastor_letter_url', '')),
            payment_receipt=sanitize_cloudinary_url(team_file_urls.get('payment_receipt_url', '')),
            group_photo=sanitize_cloudinary_url(team_file_urls.get('group_photo_url', ''))
        )
        
        logger.info("=" * 70)
        logger.info(f"✅ REGISTRATION COMPLETE: {team_id}")
        logger.info(f"   Team: {team_info.team_name}")
        logger.info(f"   Church: {team_info.church_name}")
        logger.info(f"   Captain: {team_info.captain.name}")
        logger.info(f"   Players: {player_count}")
        logger.info("=" * 70)
        
        # Return success response with clean JSON
        return TeamRegistrationResponse(
            success=True,
            message="Team Registered Successfully",
            team_id=team_id,
            player_count=player_count,
            captain_name=team_info.captain.name,
            team_name=team_info.team_name,
            data=response_data
        )
    
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions (already have proper status codes and messages)
        logger.error(f"❌ HTTP Exception: {http_ex.status_code} - {http_ex.detail}")
        raise
    
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"❌ REGISTRATION FAILED - Unexpected error: {str(e)}", exc_info=True)
        
        # Rollback database transaction
        try:
            await db.rollback()
            logger.info("Database transaction rolled back")
        except Exception as rb_error:
            logger.error(f"Failed to rollback transaction: {str(rb_error)}")
        
        # Return user-friendly error
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during registration. Please try again later or contact support if the problem persists."
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "team-registration"}
