"""
PRODUCTION REGISTRATION ENDPOINT - HARDENED & SECURED
======================================================
Complete production-grade registration with all security features:
- Race-safe sequential team IDs
- Strong input validation
- Duplicate submission protection
- File size limits & MIME validation
- Retry logic for uploads and email
- Unified error responses
- Structured logging
- Comprehensive monitoring
"""

from fastapi import APIRouter, Form, File, UploadFile, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional
import json
import logging

# Database
from database import get_db_async
from models import Team, Player

# Utilities
from app.utils.race_safe_team_id import generate_next_team_id
from app.utils.validation import (
    validate_name,
    validate_team_name,
    validate_phone,
    validate_email,
    validate_file,
    validate_player_data,
    ValidationError
)
from app.utils.idempotency import check_idempotency_key, store_idempotency_key
from app.utils.cloudinary_reliable import upload_with_retry, CloudinaryUploadError
from app.utils.email_reliable import send_email_with_retry, create_registration_email
from app.utils.error_responses import (
    ErrorCode,
    create_error_response,
    create_validation_error,
    create_duplicate_error,
    create_database_error,
    create_upload_error,
    create_internal_error
)
from app.middleware.logging_middleware import StructuredLogger

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register/team")
async def register_team_production_hardened(
    request: Request,
    # ========== TEAM INFORMATION ==========
    team_name: str = Form(..., description="Team name"),
    church_name: str = Form(..., description="Church name"),
    
    # ========== CAPTAIN INFORMATION ==========
    captain_name: str = Form(..., description="Captain full name"),
    captain_phone: str = Form(..., description="Captain phone number"),
    captain_email: str = Form(..., description="Captain email address"),
    captain_whatsapp: str = Form(..., description="Captain WhatsApp number"),
    
    # ========== VICE-CAPTAIN INFORMATION ==========
    vice_name: str = Form(..., description="Vice-captain full name"),
    vice_phone: str = Form(..., description="Vice-captain phone number"),
    vice_email: str = Form(..., description="Vice-captain email address"),
    vice_whatsapp: str = Form(..., description="Vice-captain WhatsApp number"),
    
    # ========== PLAYERS (JSON ARRAY) ==========
    players_json: Optional[str] = Form(
        None,
        description="JSON array of players: [{\"name\": \"...\", \"role\": \"...\"}]"
    ),
    
    # ========== FILE UPLOADS (REQUIRED) ==========
    pastor_letter: UploadFile = File(..., description="Pastor recommendation letter"),
    
    # ========== FILE UPLOADS (OPTIONAL) ==========
    payment_receipt: Optional[UploadFile] = File(None, description="Payment receipt"),
    group_photo: Optional[UploadFile] = File(None, description="Team group photo"),
    
    # ========== IDEMPOTENCY ==========
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    
    # ========== DATABASE SESSION ==========
    db: AsyncSession = Depends(get_db_async)
):
    """
    🏏 PRODUCTION TEAM REGISTRATION ENDPOINT (HARDENED)
    
    **Security Features:**
    - Race-safe sequential team IDs
    - Strong input validation
    - Duplicate submission protection
    - File size limits (5MB)
    - MIME type validation
    - Retry logic for uploads
    - Structured logging
    
    **Required Form Fields:**
    - Team: team_name, church_name
    - Captain: captain_name, captain_phone, captain_email, captain_whatsapp
    - Vice-Captain: vice_name, vice_phone, vice_email, vice_whatsapp
    
    **Required Files:**
    - pastor_letter (PNG/JPEG/PDF, max 5MB)
    
    **Optional:**
    - payment_receipt, group_photo
    - players_json (JSON string)
    - Idempotency-Key header
    
    **Response (201):**
    ```json
    {
      "success": true,
      "team_id": "ICCT-001",
      "message": "Team registered successfully",
      "email_sent": true
    }
    ```
    
    **Error Codes:**
    - VALIDATION_FAILED: Invalid input
    - DUPLICATE_SUBMISSION: Team already exists
    - FILE_TOO_LARGE: File exceeds 5MB
    - INVALID_MIME_TYPE: Wrong file type
    - DB_WRITE_FAILED: Database error
    - CLOUDINARY_UPLOAD_FAILED: Upload failed
    - INTERNAL_SERVER_ERROR: Unexpected error
    """
    
    # Get request ID for logging
    request_id = getattr(request.state, 'request_id', 'unknown')
    client_ip = request.client.host if request.client else 'unknown'
    
    try:
        # ====================================================================
        # STEP 1: CHECK IDEMPOTENCY KEY
        # ====================================================================
        if idempotency_key:
            logger.info(f"[{request_id}] Checking idempotency key: {idempotency_key}")
            existing_response = await check_idempotency_key(db, idempotency_key)
            
            if existing_response:
                logger.warning(f"[{request_id}] Duplicate submission detected")
                return JSONResponse(
                    status_code=409,
                    content=json.loads(existing_response) if existing_response else {
                        "success": False,
                        "error_code": ErrorCode.DUPLICATE_SUBMISSION,
                        "message": "This request has already been processed"
                    }
                )
        
        # ====================================================================
        # STEP 2: LOG REGISTRATION START
        # ====================================================================
        StructuredLogger.log_registration_started(request_id, team_name, client_ip)
        
        # ====================================================================
        # STEP 3: VALIDATE ALL INPUTS
        # ====================================================================
        logger.info(f"[{request_id}] Step 1: Validating inputs...")
        
        try:
            # Validate team
            validated_team_name = validate_team_name(team_name)
            validated_church_name = validate_name(church_name, "Church name")
            
            # Validate captain
            validated_captain_name = validate_name(captain_name, "Captain name")
            validated_captain_phone = validate_phone(captain_phone, "Captain phone")
            validated_captain_email = validate_email(captain_email, "Captain email")
            validated_captain_whatsapp = validate_phone(captain_whatsapp, "Captain WhatsApp")
            
            # Validate vice-captain
            validated_vice_name = validate_name(vice_name, "Vice-captain name")
            validated_vice_phone = validate_phone(vice_phone, "Vice-captain phone")
            validated_vice_email = validate_email(vice_email, "Vice-captain email")
            validated_vice_whatsapp = validate_phone(vice_whatsapp, "Vice-captain WhatsApp")
            
            logger.info(f"[{request_id}] ✅ Input validation passed")
            
        except ValidationError as e:
            StructuredLogger.log_validation_error(request_id, e.field, e.message)
            return create_validation_error(e.field, e.message)
        
        # ====================================================================
        # STEP 4: VALIDATE FILES
        # ====================================================================
        logger.info(f"[{request_id}] Step 2: Validating files...")
        
        try:
            # Required file
            pastor_filename, pastor_mime = await validate_file(pastor_letter, "Pastor letter")
            
            # Optional files
            receipt_filename, receipt_mime = None, None
            if payment_receipt:
                receipt_filename, receipt_mime = await validate_file(payment_receipt, "Payment receipt")
            
            photo_filename, photo_mime = None, None
            if group_photo:
                photo_filename, photo_mime = await validate_file(group_photo, "Group photo")
            
            logger.info(f"[{request_id}] ✅ File validation passed")
            
        except ValidationError as e:
            StructuredLogger.log_validation_error(request_id, e.field, e.message)
            
            if e.error_code == "FILE_TOO_LARGE":
                return create_error_response(
                    ErrorCode.FILE_TOO_LARGE,
                    e.message,
                    {"field": e.field},
                    400
                )
            elif e.error_code == "INVALID_MIME_TYPE":
                return create_error_response(
                    ErrorCode.INVALID_MIME_TYPE,
                    e.message,
                    {"field": e.field},
                    400
                )
            else:
                return create_validation_error(e.field, e.message)
        
        # ====================================================================
        # STEP 5: VALIDATE PLAYERS JSON
        # ====================================================================
        logger.info(f"[{request_id}] Step 3: Parsing players data...")
        
        validated_players = []
        if players_json:
            try:
                players_raw = json.loads(players_json)
                for idx, player in enumerate(players_raw, 1):
                    validated_player = validate_player_data(player, idx)
                    validated_players.append(validated_player)
                
                logger.info(f"[{request_id}] ✅ Parsed {len(validated_players)} players")
                
            except json.JSONDecodeError as e:
                return create_validation_error("players_json", f"Invalid JSON: {str(e)}")
            except ValidationError as e:
                StructuredLogger.log_validation_error(request_id, e.field, e.message)
                return create_validation_error(e.field, e.message)
        
        # ====================================================================
        # STEP 6: GENERATE RACE-SAFE TEAM ID
        # ====================================================================
        logger.info(f"[{request_id}] Step 4: Generating sequential team ID...")
        
        try:
            team_id = await generate_next_team_id(db)
            logger.info(f"[{request_id}] ✅ Team ID: {team_id}")
            
        except Exception as e:
            logger.error(f"[{request_id}] ❌ Team ID generation failed: {e}")
            return create_error_response(
                ErrorCode.TEAM_ID_GENERATION_FAILED,
                "Failed to generate team ID",
                {"error": str(e)},
                500
            )
        
        # ====================================================================
        # STEP 7: UPLOAD FILES TO CLOUDINARY (WITH RETRY)
        # ====================================================================
        logger.info(f"[{request_id}] Step 5: Uploading files to Cloudinary...")
        
        try:
            # Upload pastor letter (required)
            pastor_url = await upload_with_retry(
                pastor_letter,
                folder=f"ICCT26/pastor_letters/{team_id}"
            )
            StructuredLogger.log_file_upload(request_id, "pastor_letter", "success", pastor_url)
            
            # Upload payment receipt (optional)
            receipt_url = None
            if payment_receipt:
                try:
                    receipt_url = await upload_with_retry(
                        payment_receipt,
                        folder=f"ICCT26/receipts/{team_id}"
                    )
                    StructuredLogger.log_file_upload(request_id, "payment_receipt", "success", receipt_url)
                except CloudinaryUploadError as e:
                    # Log but don't fail registration
                    StructuredLogger.log_file_upload(request_id, "payment_receipt", "failed")
                    logger.warning(f"[{request_id}] Optional file upload failed: payment_receipt")
            
            # Upload group photo (optional)
            photo_url = None
            if group_photo:
                try:
                    photo_url = await upload_with_retry(
                        group_photo,
                        folder=f"ICCT26/group_photos/{team_id}"
                    )
                    StructuredLogger.log_file_upload(request_id, "group_photo", "success", photo_url)
                except CloudinaryUploadError as e:
                    # Log but don't fail registration
                    StructuredLogger.log_file_upload(request_id, "group_photo", "failed")
                    logger.warning(f"[{request_id}] Optional file upload failed: group_photo")
            
            logger.info(f"[{request_id}] ✅ File uploads complete")
            
        except CloudinaryUploadError as e:
            logger.error(f"[{request_id}] ❌ Required file upload failed: {e.message}")
            return create_upload_error("pastor_letter", e.retry_count)
        
        # ====================================================================
        # STEP 8: CREATE DATABASE RECORDS (ATOMIC TRANSACTION)
        # ====================================================================
        logger.info(f"[{request_id}] Step 6: Creating database records...")
        
        try:
            # Create team record
            team = Team(
                team_id=team_id,
                team_name=validated_team_name,
                church_name=validated_church_name,
                captain_name=validated_captain_name,
                captain_phone=validated_captain_phone,
                captain_email=validated_captain_email,
                captain_whatsapp=validated_captain_whatsapp,
                vice_captain_name=validated_vice_name,
                vice_captain_phone=validated_vice_phone,
                vice_captain_email=validated_vice_email,
                vice_captain_whatsapp=validated_vice_whatsapp,
                pastor_letter=pastor_url,
                payment_receipt=receipt_url,
                group_photo=photo_url,
                registration_date=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            db.add(team)
            await db.flush()
            
            # Create player records
            player_count = 0
            for idx, player_data in enumerate(validated_players, 1):
                player_id = f"{team_id}-P{idx:02d}"
                player = Player(
                    player_id=player_id,
                    team_id=team_id,
                    name=player_data["name"],
                    role=player_data["role"],
                    aadhar_file=None,
                    subscription_file=None,
                    created_at=datetime.utcnow()
                )
                db.add(player)
                player_count += 1
            
            # Commit transaction
            await db.commit()
            
            StructuredLogger.log_db_operation(request_id, "insert", "success", team_id)
            logger.info(f"[{request_id}] ✅ Database records created (team + {player_count} players)")
            
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"[{request_id}] ❌ Duplicate team detected: {e}")
            
            # Check if it's the unique constraint violation
            if "uq_team_name_captain_phone" in str(e):
                return create_duplicate_error("team_name/captain_phone", validated_team_name)
            
            return create_database_error("insert", str(e))
            
        except Exception as e:
            await db.rollback()
            logger.error(f"[{request_id}] ❌ Database error: {e}")
            StructuredLogger.log_db_operation(request_id, "insert", "failed", team_id)
            return create_database_error("insert", str(e))
        
        # ====================================================================
        # STEP 9: SEND EMAIL CONFIRMATION (NON-BLOCKING)
        # ====================================================================
        logger.info(f"[{request_id}] Step 7: Sending email confirmation...")
        
        email_sent = False
        try:
            email_body = create_registration_email(
                validated_team_name,
                team_id,
                validated_captain_name,
                validated_church_name,
                player_count
            )
            
            email_sent = await send_email_with_retry(
                validated_captain_email,
                f"ICCT26 Registration Confirmation — {team_id}",
                email_body
            )
            
            status = "success" if email_sent else "failed"
            StructuredLogger.log_email_sent(request_id, validated_captain_email, status)
            
        except Exception as e:
            logger.warning(f"[{request_id}] ⚠️ Email send failed (non-fatal): {e}")
            StructuredLogger.log_email_sent(request_id, validated_captain_email, "failed")
        
        # ====================================================================
        # STEP 10: STORE IDEMPOTENCY KEY
        # ====================================================================
        if idempotency_key:
            try:
                response_data = json.dumps({
                    "success": True,
                    "team_id": team_id,
                    "team_name": validated_team_name,
                    "message": "Team registered successfully",
                    "email_sent": email_sent,
                    "player_count": player_count
                })
                
                await store_idempotency_key(db, idempotency_key, response_data)
            except Exception as e:
                logger.warning(f"[{request_id}] Failed to store idempotency key: {e}")
        
        # ====================================================================
        # STEP 11: RETURN SUCCESS RESPONSE
        # ====================================================================
        logger.info(f"[{request_id}] ✅ Registration complete: {team_id}")
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "team_id": team_id,
                "team_name": validated_team_name,
                "message": "Team registered successfully",
                "email_sent": email_sent,
                "player_count": player_count
            }
        )
        
    except Exception as e:
        # Catch-all for unexpected errors
        logger.exception(f"[{request_id}] ❌ Unexpected error: {e}")
        StructuredLogger.log_exception(request_id, e)
        return create_internal_error(
            "An unexpected error occurred during registration",
            {"exception_type": type(e).__name__}
        )
