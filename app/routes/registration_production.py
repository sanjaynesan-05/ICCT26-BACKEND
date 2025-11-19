# (put this code where your existing register_team_production_hardened function lives)
from fastapi import APIRouter, Form, File, UploadFile, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List, Any
import json
import logging
import re

# Database
from database import get_db_async
from models import Team, Player

# Utilities (your existing helpers)
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
    🏏 PRODUCTION TEAM REGISTRATION ENDPOINT
    
    Accepts team info + dynamic player fields:
    - player_0_name, player_0_role, player_0_aadhar_file, player_0_subscription_file
    - player_1_name, player_1_role, player_1_aadhar_file, player_1_subscription_file
    - etc.
    
    NO EMAIL SENDING - removed as per requirements
    """
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = request.client.host if request.client else "unknown"

    try:
        # ====================================================================
        # STEP 1: IDEMPOTENCY CHECK
        # ====================================================================
        if idempotency_key:
            logger.info(f"[{request_id}] Checking idempotency key: {idempotency_key}")
            existing_response = await check_idempotency_key(db, idempotency_key)
            if existing_response:
                logger.warning(f"[{request_id}] Duplicate submission detected (idempotency)")
                try:
                    payload = json.loads(existing_response)
                    return JSONResponse(status_code=409, content=payload)
                except Exception:
                    payload = {
                        "success": True,
                        "team_id": "UNKNOWN",
                        "team_name": "UNKNOWN",
                        "message": "Team registered successfully",
                        "player_count": 0
                    }
                    return JSONResponse(status_code=409, content=payload)

        StructuredLogger.log_registration_started(request_id, team_name, client_ip)

        # ====================================================================
        # STEP 2: VALIDATE TEAM/CAPTAIN/VICE-CAPTAIN INPUTS
        # ====================================================================
        logger.info(f"[{request_id}] Step 1: Validating inputs...")
        try:
            validated_team_name = validate_team_name(team_name)
            validated_church_name = validate_name(church_name, "Church name")

            validated_captain_name = validate_name(captain_name, "Captain name")
            validated_captain_phone = validate_phone(captain_phone, "Captain phone")
            validated_captain_email = validate_email(captain_email, "Captain email")
            validated_captain_whatsapp = validate_phone(captain_whatsapp, "Captain WhatsApp")

            validated_vice_name = validate_name(vice_name, "Vice-captain name")
            validated_vice_phone = validate_phone(vice_phone, "Vice-captain phone")
            validated_vice_email = validate_email(vice_email, "Vice-captain email")
            validated_vice_whatsapp = validate_phone(vice_whatsapp, "Vice-captain WhatsApp")

            logger.info(f"[{request_id}] ✅ Input validation passed")
        except ValidationError as e:
            StructuredLogger.log_validation_error(request_id, e.field, e.message)
            return create_validation_error(e.field, e.message)

        # ====================================================================
        # STEP 3: VALIDATE TEAM FILES
        # ====================================================================
        logger.info(f"[{request_id}] Step 2: Validating team files...")
        try:
            pastor_filename, pastor_mime = await validate_file(pastor_letter, "Pastor letter")
            
            receipt_filename, receipt_mime = (None, None)
            if payment_receipt:
                receipt_filename, receipt_mime = await validate_file(payment_receipt, "Payment receipt")
            
            photo_filename, photo_mime = (None, None)
            if group_photo:
                photo_filename, photo_mime = await validate_file(group_photo, "Group photo")
            
            logger.info(f"[{request_id}] ✅ Team file validation passed")
        except ValidationError as e:
            StructuredLogger.log_validation_error(request_id, e.field, e.message)
            if e.error_code == "FILE_TOO_LARGE":
                return create_error_response(ErrorCode.FILE_TOO_LARGE, e.message, {"field": e.field}, 400)
            if e.error_code == "INVALID_MIME_TYPE":
                return create_error_response(ErrorCode.INVALID_MIME_TYPE, e.message, {"field": e.field}, 400)
            return create_validation_error(e.field, e.message)

        # ====================================================================
        # STEP 4: EXTRACT PLAYERS FROM FORM (DYNAMIC player_i_* fields)
        # ====================================================================
        logger.info(f"[{request_id}] Step 3: Extracting players from form...")
        form = await request.form()
        
        # 🔍 DEBUG: Log all form keys to help debug missing files
        form_keys = list(form.keys())
        logger.info(f"[{request_id}] 📋 Received {len(form_keys)} form keys")
        player_file_keys = [k for k in form_keys if 'player_' in k and ('aadhar' in k or 'subscription' in k)]
        if player_file_keys:
            logger.info(f"[{request_id}] 📁 Player file keys detected: {player_file_keys}")
        else:
            logger.warning(f"[{request_id}] ⚠️ NO player file keys found in form data!")
        
        # Helper to safely get form values
        def get_form_value(key: str) -> Optional[str]:
            val = form.get(key)
            if isinstance(val, str):
                return val.strip() if val else None
            return None
        
        def get_form_file(key: str) -> Optional[UploadFile]:
            val = form.get(key)
            if isinstance(val, UploadFile):
                return val
            return None
        
        # Dynamically detect all players by checking player_i_name fields
        players_data = []
        player_index = 0
        
        while True:
            name_key = f"player_{player_index}_name"
            role_key = f"player_{player_index}_role"
            aadhar_key = f"player_{player_index}_aadhar_file"
            subscription_key = f"player_{player_index}_subscription_file"
            
            player_name = get_form_value(name_key)
            
            # If no name found, we've reached the end of players
            if not player_name:
                break
            
            player_role = get_form_value(role_key)
            aadhar_file = get_form_file(aadhar_key)
            subscription_file = get_form_file(subscription_key)
            
            # 🔍 DEBUG: Log file detection
            logger.info(f"[{request_id}] Player {player_index}: name={player_name}, role={player_role}, "
                       f"aadhar={'PRESENT' if aadhar_file else 'MISSING'}, "
                       f"subscription={'PRESENT' if subscription_file else 'MISSING'}")
            
            # Validate player data
            try:
                if not player_name or len(player_name) < 2:
                    raise ValidationError(name_key, f"Player {player_index + 1} name is required (min 2 characters)")
                if not player_role or player_role not in ["Batsman", "Bowler", "All-Rounder", "Wicket-Keeper"]:
                    raise ValidationError(role_key, f"Player {player_index + 1} role must be one of: Batsman, Bowler, All-Rounder, Wicket-Keeper")
            except ValidationError as e:
                StructuredLogger.log_validation_error(request_id, e.field, e.message)
                return create_validation_error(e.field, e.message)
            
            players_data.append({
                "index": player_index,
                "name": player_name,
                "role": player_role,
                "aadhar_file": aadhar_file,
                "subscription_file": subscription_file
            })
            
            player_index += 1
        
        logger.info(f"[{request_id}] ✅ Found {len(players_data)} players in form")

        # ====================================================================
        # STEP 5: GENERATE TEAM ID
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
        # STEP 6: UPLOAD TEAM FILES TO CLOUDINARY
        # ====================================================================
        logger.info(f"[{request_id}] Step 5: Uploading team files to Cloudinary...")
        try:
            pastor_url = await upload_with_retry(
                pastor_letter,
                folder=f"ICCT26/pastor_letters/{team_id}"
            )
            StructuredLogger.log_file_upload(request_id, "pastor_letter", "success", pastor_url)

            receipt_url = None
            if payment_receipt:
                try:
                    receipt_url = await upload_with_retry(
                        payment_receipt,
                        folder=f"ICCT26/receipts/{team_id}"
                    )
                    StructuredLogger.log_file_upload(request_id, "payment_receipt", "success", receipt_url)
                except CloudinaryUploadError:
                    StructuredLogger.log_file_upload(request_id, "payment_receipt", "failed")
                    logger.warning(f"[{request_id}] Optional file upload failed: payment_receipt")

            photo_url = None
            if group_photo:
                try:
                    photo_url = await upload_with_retry(
                        group_photo,
                        folder=f"ICCT26/group_photos/{team_id}"
                    )
                    StructuredLogger.log_file_upload(request_id, "group_photo", "success", photo_url)
                except CloudinaryUploadError:
                    StructuredLogger.log_file_upload(request_id, "group_photo", "failed")
                    logger.warning(f"[{request_id}] Optional file upload failed: group_photo")

            logger.info(f"[{request_id}] ✅ Team file uploads complete")
        except CloudinaryUploadError as e:
            logger.error(f"[{request_id}] ❌ Required file upload failed: {e.message}")
            return create_upload_error("pastor_letter", e.retry_count)

        # ====================================================================
        # STEP 7: CREATE DATABASE RECORDS (ATOMIC TRANSACTION)
        # ====================================================================
        logger.info(f"[{request_id}] Step 6: Creating database records...")
        try:
            # Create Team record
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
            await db.flush()  # Persist team first for FK references

            # Create Player records with file uploads
            player_count = 0
            for player_data in players_data:
                player_num = player_data["index"] + 1
                player_id = f"{team_id}-P{player_num:02d}"
                
                # Upload player files to Cloudinary
                aadhar_url = None
                subscription_url = None
                
                if player_data["aadhar_file"]:
                    try:
                        aadhar_url = await upload_with_retry(
                            player_data["aadhar_file"],
                            folder=f"ICCT26/players/{team_id}/player_{player_data['index']}/aadhar"
                        )
                        StructuredLogger.log_file_upload(
                            request_id,
                            f"player_{player_data['index']}_aadhar",
                            "success",
                            aadhar_url
                        )
                    except CloudinaryUploadError as e:
                        logger.warning(f"[{request_id}] Player {player_num} aadhar upload failed: {e.message}")
                        StructuredLogger.log_file_upload(request_id, f"player_{player_data['index']}_aadhar", "failed")
                
                if player_data["subscription_file"]:
                    try:
                        subscription_url = await upload_with_retry(
                            player_data["subscription_file"],
                            folder=f"ICCT26/players/{team_id}/player_{player_data['index']}/subscription"
                        )
                        StructuredLogger.log_file_upload(
                            request_id,
                            f"player_{player_data['index']}_subscription",
                            "success",
                            subscription_url
                        )
                    except CloudinaryUploadError as e:
                        logger.warning(f"[{request_id}] Player {player_num} subscription upload failed: {e.message}")
                        StructuredLogger.log_file_upload(request_id, f"player_{player_data['index']}_subscription", "failed")
                
                # Create Player database record
                player = Player(
                    player_id=player_id,
                    team_id=team_id,
                    name=player_data["name"],
                    role=player_data["role"],
                    aadhar_file=aadhar_url,
                    subscription_file=subscription_url,
                    created_at=datetime.utcnow()
                )
                db.add(player)
                player_count += 1

            # Commit transaction (team + all players)
            await db.commit()
            StructuredLogger.log_db_operation(request_id, "insert", "success", team_id)
            logger.info(f"[{request_id}] ✅ Database records created (team + {player_count} players)")

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"[{request_id}] ❌ Duplicate team detected: {e}")
            
            # Check if duplicate via idempotency
            if idempotency_key:
                existing_response = await check_idempotency_key(db, idempotency_key)
                if existing_response:
                    try:
                        payload = json.loads(existing_response)
                        return JSONResponse(status_code=409, content=payload)
                    except Exception:
                        pass
            
            # Check for unique constraint violation
            if "uq_team_name_captain_phone" in str(e):
                return create_duplicate_error("team_name/captain_phone", validated_team_name)
            
            return create_database_error("insert", str(e))

        except Exception as e:
            await db.rollback()
            logger.error(f"[{request_id}] ❌ Database error: {e}")
            StructuredLogger.log_db_operation(request_id, "insert", "failed", team_id)
            return create_database_error("insert", str(e))

        # ====================================================================
        # STEP 8: STORE IDEMPOTENCY KEY
        # ====================================================================
        if idempotency_key:
            try:
                response_data = json.dumps({
                    "success": True,
                    "team_id": team_id,
                    "team_name": validated_team_name,
                    "message": "Team registered successfully",
                    "player_count": player_count
                })
                await store_idempotency_key(db, idempotency_key, response_data)
            except Exception as e:
                logger.warning(f"[{request_id}] Failed to store idempotency key: {e}")

        # ====================================================================
        # STEP 9: RETURN SUCCESS RESPONSE
        # ====================================================================
        logger.info(f"[{request_id}] ✅ Registration complete: {team_id}")
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "team_id": team_id,
                "team_name": validated_team_name,
                "message": "Team registered successfully",
                "player_count": player_count
            }
        )

    except Exception as e:
        logger.exception(f"[{request_id}] ❌ Unexpected error: {e}")
        StructuredLogger.log_exception(request_id, e)
        return create_internal_error(
            "An unexpected error occurred during registration",
            {"exception_type": type(e).__name__}
        )
