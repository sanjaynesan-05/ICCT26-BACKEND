# registration_production.py
# Production-grade registration endpoint for ICCT26
# Drop into your FastAPI project (adjust imports to your layout if necessary)

from fastapi import APIRouter, Request, Header, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, Any, Dict, List
import json
import logging

# Database / models
from database import get_db_async
from models import Team, Player

# Utilities (assumes these exist in your project)
from app.utils.race_safe_team_id import generate_next_team_id
from config.settings import settings
from app.utils.validation import (
    validate_name,
    validate_team_name,
    validate_phone,
    validate_email,
    validate_file,
    ValidationError
)
from app.utils.idempotency import check_idempotency_key, store_idempotency_key
from app.utils.cloudinary_reliable import upload_with_retry, CloudinaryUploadError
from app.utils.cloudinary_upload import cloudinary_uploader
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

from starlette.datastructures import UploadFile  # type: ignore

router = APIRouter()
logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION: Retry settings with defensive fallback
# ============================================================
MAX_RETRIES = getattr(settings, 'MAX_RETRIES', 3)
logger.info(f"🔧 MAX_RETRIES configured: {MAX_RETRIES} (default: 3)")


# ============================================================
# CLEANUP FUNCTION: Cloudinary orphaned file removal
# ============================================================
async def cleanup_cloudinary_uploads(uploaded_urls: Dict[str, Optional[str]], team_id: str, request_id: str) -> bool:
    """
    Delete uploaded files from Cloudinary if database save fails.
    Prevents orphaned files when registration fails after Cloudinary uploads.
    
    Args:
        uploaded_urls: Dict with keys like 'pastor_letter', 'payment_receipt', 'group_photo'
        team_id: Team ID for logging
        request_id: Request ID for tracing
    
    Returns:
        bool: True if cleanup successful or no files to delete, False if cleanup failed
    """
    try:
        deletion_count = 0
        failed_deletions = []
        
        logger.warning(f"[{request_id}] 🧹 CLEANUP: Starting Cloudinary cleanup for team {team_id}")
        
        for file_type, url in uploaded_urls.items():
            if not url:
                continue  # Skip empty/None URLs
            
            try:
                # Extract public_id from Cloudinary URL
                # URL format: https://res.cloudinary.com/.../upload/v.../ICCT-XXX_fieldname
                if 'cloudinary.com' in url:
                    # Extract public_id from URL - last part before file extension
                    parts = url.split('/')[-1].split('.')
                    public_id = parts[0] if parts else None
                    
                    if public_id:
                        logger.info(f"[{request_id}] 🗑️ Attempting to delete from Cloudinary: {public_id}")
                        # Use cloudinary_uploader to delete
                        from app.utils.cloudinary_upload import cloudinary_uploader
                        
                        # Try to delete from both pending and confirmed folders
                        deleted = False
                        for folder in [f"pending/{team_id}", f"confirmed/{team_id}"]:
                            try:
                                cloudinary_uploader.delete_file(f"{folder}/{public_id}")
                                logger.info(f"[{request_id}] ✅ CLEANUP: Deleted {folder}/{public_id}")
                                deletion_count += 1
                                deleted = True
                                break
                            except Exception as e:
                                logger.debug(f"[{request_id}] File not in {folder}: {e}")
                                continue
                        
                        if not deleted:
                            failed_deletions.append(f"{file_type}: {public_id}")
                
            except Exception as e:
                logger.warning(f"[{request_id}] ⚠️ CLEANUP: Failed to delete {file_type}: {e}")
                failed_deletions.append(file_type)
                continue
        
        if deletion_count > 0:
            logger.warning(f"[{request_id}] ✅ CLEANUP: Deleted {deletion_count} orphaned file(s)")
        
        if failed_deletions:
            logger.error(f"[{request_id}] ⚠️ CLEANUP: Some files could not be deleted: {failed_deletions}")
        
        return True
        
    except Exception as e:
        logger.error(f"[{request_id}] ❌ CLEANUP: Cleanup failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


@router.post("/register/team")
async def register_team_production_hardened(
    request: Request,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db_async)
):
    """
    Production registration endpoint (dynamic form + files).

    Accepts flattened multipart fields from the frontend:
      - team_name, church_name, captain_name, ...
      - pastor_letter (file), payment_receipt (file), group_photo (file)
      - player_0_name, player_0_role, player_0_aadhar_file, player_0_subscription_file, ...
    Idempotency: Idempotency-Key header supported.
    Email sending removed (non-blocking / disabled).
    """

    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = request.client.host if request.client else "unknown"

    try:
        # -------------------------------
        # IDEMPOTENCY CHECK
        # -------------------------------
        if idempotency_key:
            logger.info(f"[{request_id}] Checking idempotency key: {idempotency_key}")
            existing = await check_idempotency_key(db, idempotency_key)
            if existing:
                logger.warning(f"[{request_id}] Duplicate submission detected (idempotency)")
                try:
                    payload = json.loads(existing)
                    return JSONResponse(status_code=409, content=payload)
                except Exception:
                    return JSONResponse(
                        status_code=409,
                        content={
                            "success": True,
                            "team_name": "UNKNOWN",
                            "message": "This request has already been processed. Please wait for admin confirmation.",
                            "player_count": 0,
                            "registration_status": "pending"
                        }
                    )

        StructuredLogger.log_registration_started(request_id, "unknown-team", client_ip)

        # -------------------------------
        # READ FORM ONCE
        # -------------------------------
        # IMPORTANT: Call request.form() exactly once — it consumes the body.
        form = await request.form()

        # Debug: show incoming form keys for quick troubleshooting
        form_keys = list(form.keys())
        logger.info(f"[{request_id}] Received {len(form_keys)} form keys: {form_keys}")

        # -------------------------------
        # EXTRACT TEAM & CONTACT FIELDS
        # -------------------------------
        def get_text(key: str) -> Optional[str]:
            v = form.get(key)
            if v is None:
                return None
            if isinstance(v, str):
                return v.strip()
            # If it's an UploadFile for some reason, return filename string
            if hasattr(v, "filename"):
                return getattr(v, "filename", None)
            return str(v).strip()

        def get_file(key: str) -> Optional[UploadFile]:
            v = form.get(key)
            if v is None:
                return None
            # starlette UploadFile will have attribute 'filename'
            if hasattr(v, "filename"):
                return v  # type: ignore
            return None

        # Required team/captain fields (validate below)
        team_name = get_text("team_name")
        church_name = get_text("church_name")

        captain_name = get_text("captain_name")
        captain_phone = get_text("captain_phone")
        captain_email = get_text("captain_email")
        captain_whatsapp = get_text("captain_whatsapp")

        vice_name = get_text("vice_name")
        vice_phone = get_text("vice_phone")
        vice_email = get_text("vice_email")
        vice_whatsapp = get_text("vice_whatsapp")

        # Files
        pastor_letter = get_file("pastor_letter")
        payment_receipt = get_file("payment_receipt")
        group_photo = get_file("group_photo")

        # -------------------------------
        # VALIDATE FIELDS
        # -------------------------------
        logger.info(f"[{request_id}] Validating team and contact fields...")
        try:
            if not team_name:
                raise ValidationError("team_name", "Team name is required")
            validated_team_name = validate_team_name(team_name)

            if not church_name:
                raise ValidationError("church_name", "Church name is required")
            validated_church_name = validate_name(church_name, "Church name")

            validated_captain_name = validate_name(captain_name or "", "Captain name")
            validated_captain_phone = validate_phone(captain_phone or "", "Captain phone")
            validated_captain_email = validate_email(captain_email or "", "Captain email")
            validated_captain_whatsapp = validate_phone(captain_whatsapp or "", "Captain WhatsApp")

            validated_vice_name = validate_name(vice_name or "", "Vice-captain name")
            validated_vice_phone = validate_phone(vice_phone or "", "Vice-captain phone")
            validated_vice_email = validate_email(vice_email or "", "Vice-captain email")
            validated_vice_whatsapp = validate_phone(vice_whatsapp or "", "Vice-captain WhatsApp")

            # Validate required pastor_letter file if present
            if not pastor_letter:
                raise ValidationError("pastor_letter", "Pastor letter (file) is required")
            # Use your validate_file utility to check size/mime
            await validate_file(pastor_letter, "Pastor letter")

            if payment_receipt:
                await validate_file(payment_receipt, "Payment receipt")
            if group_photo:
                await validate_file(group_photo, "Group photo")

            logger.info(f"[{request_id}] ✅ Field validation passed")
        except ValidationError as e:
            StructuredLogger.log_validation_error(request_id, e.field, e.message)
            return create_validation_error(e.field, e.message)

        # -------------------------------
        # EXTRACT PLAYERS (dynamic)
        # -------------------------------
        logger.info(f"[{request_id}] Extracting players from form (dynamic fields)...")
        players: List[Dict[str, Any]] = []
        idx = 0
        # We'll accept contiguous indices starting at 0 until a name field is missing.
        while True:
            name_key = f"player_{idx}_name"
            role_key = f"player_{idx}_role"
            aadhar_key = f"player_{idx}_aadhar_file"
            subs_key = f"player_{idx}_subscription_file"

            name_val = get_text(name_key)
            if not name_val:
                break

            role_val = get_text(role_key) or ""
            aadhar_file = get_file(aadhar_key)
            subs_file = get_file(subs_key)

            logger.info(
                f"[{request_id}] player_{idx}: name='{name_val}', role='{role_val}', "
                f"aadhar={'PRESENT' if aadhar_file else 'MISSING'}, subscription={'PRESENT' if subs_file else 'MISSING'}"
            )

            # Basic validation per player
            try:
                if len(name_val) < 2:
                    raise ValidationError(name_key, f"Player {idx+1} name too short")
                # Role is optional - only validate if provided
                if role_val and role_val not in ["Batsman", "Bowler", "All-Rounder", "Wicket-Keeper", ""]:
                    raise ValidationError(role_key, f"Player {idx+1} role must be one of: Batsman, Bowler, All-Rounder, Wicket-Keeper (or leave empty)")
                # Validate files if present
                if aadhar_file:
                    await validate_file(aadhar_file, f"player_{idx}_aadhar_file")
                if subs_file:
                    await validate_file(subs_file, f"player_{idx}_subscription_file")
            except ValidationError as e:
                StructuredLogger.log_validation_error(request_id, e.field, e.message)
                return create_validation_error(e.field, e.message)

            players.append({
                "index": idx,
                "name": name_val,
                "role": role_val,
                "aadhar_file": aadhar_file,
                "subscription_file": subs_file
            })
            idx += 1

        logger.info(f"[{request_id}] ✅ Players detected: {len(players)}")

        # -------------------------------
        # CREATE DATABASE RECORDS WITH RETRY LOGIC
        # -------------------------------
        logger.info(f"[{request_id}] Creating database records (team + players) with retry-safe logic...")
        
        # Retry loop for team insertion to handle duplicate team_id
        team_inserted = False
        team_id = None  # Initialize team_id
        pastor_url = None
        receipt_url = None
        photo_url = None
        
        for db_attempt in range(MAX_RETRIES):
            try:
                # Generate new team_id for each attempt (including first)
                team_id = await generate_next_team_id(db)
                logger.info(f"[{request_id}] Attempt {db_attempt + 1}/{MAX_RETRIES}: Generated team_id: {team_id}")
                
                # -------------------------------
                # UPLOAD TEAM FILES TO CLOUDINARY (PENDING FOLDER)
                # -------------------------------
                logger.info(f"[{request_id}] Uploading team files to Cloudinary /pending/{team_id}/...")
                try:
                    # Upload pastor letter to pending
                    pastor_letter.file.seek(0)  # Reset file pointer for retries
                    pastor_content = await pastor_letter.read()
                    pastor_url = await cloudinary_uploader.upload_pending_file(
                        file_content=pastor_content,
                        team_id=team_id,
                        file_field_name="pastor_letter",
                        original_filename=pastor_letter.filename
                    )
                    if pastor_url:
                        StructuredLogger.log_file_upload(request_id, "pastor_letter", "success", pastor_url)
                    else:
                        raise CloudinaryUploadError("Pastor letter upload failed")

                    # Upload payment receipt to pending (optional)
                    if payment_receipt:
                        try:
                            payment_receipt.file.seek(0)  # Reset file pointer
                            receipt_content = await payment_receipt.read()
                            receipt_url = await cloudinary_uploader.upload_pending_file(
                                file_content=receipt_content,
                                team_id=team_id,
                                file_field_name="payment_receipt",
                                original_filename=payment_receipt.filename
                            )
                            if receipt_url:
                                StructuredLogger.log_file_upload(request_id, "payment_receipt", "success", receipt_url)
                        except Exception as e:
                            logger.warning(f"[{request_id}] payment_receipt upload failed (optional): {e}")
                            StructuredLogger.log_file_upload(request_id, "payment_receipt", "failed")
                            receipt_url = None

                    # Upload group photo to pending (optional)
                    if group_photo:
                        try:
                            group_photo.file.seek(0)  # Reset file pointer
                            photo_content = await group_photo.read()
                            photo_url = await cloudinary_uploader.upload_pending_file(
                                file_content=photo_content,
                                team_id=team_id,
                                file_field_name="group_photo",
                                original_filename=group_photo.filename
                            )
                            if photo_url:
                                StructuredLogger.log_file_upload(request_id, "group_photo", "success", photo_url)
                        except Exception as e:
                            logger.warning(f"[{request_id}] group_photo upload failed (optional): {e}")
                            StructuredLogger.log_file_upload(request_id, "group_photo", "failed")
                            photo_url = None

                    logger.info(f"[{request_id}] ✅ Team file uploads complete (stored in pending folder)")
                except CloudinaryUploadError as e:
                    logger.error(f"[{request_id}] Required upload failed: {e}")
                    await db.rollback()
                    if db_attempt == MAX_RETRIES - 1:
                        return create_upload_error("pastor_letter", getattr(e, "retry_count", None))
                    continue
                
                # -------------------------------
                # INSERT TEAM INTO DATABASE
                # -------------------------------
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
                await db.flush()  # persist team into session (no commit yet)
                
                # Success - break out of retry loop
                team_inserted = True
                logger.info(f"[{request_id}] ✅ Team row inserted successfully with team_id: {team_id}")
                break
                
            except IntegrityError as integrity_err:
                await db.rollback()
                logger.warning(f"[{request_id}] ⚠️ IntegrityError on team insert (attempt {db_attempt + 1}): {integrity_err}")
                
                # Check if it's a duplicate team_id error
                if "teams_team_id_key" in str(integrity_err) or "duplicate key" in str(integrity_err).lower():
                    if db_attempt == MAX_RETRIES - 1:
                        logger.error(f"[{request_id}] ❌ Failed to insert team after {MAX_RETRIES} retries - duplicate team_id")
                        
                        # CLEANUP: Delete orphaned Cloudinary files
                        uploaded_files = {
                            "pastor_letter": pastor_url,
                            "payment_receipt": receipt_url,
                            "group_photo": photo_url
                        }
                        await cleanup_cloudinary_uploads(uploaded_files, team_id, request_id)
                        
                        return create_error_response(
                            ErrorCode.DATABASE_ERROR,
                            "Unable to generate unique team ID after retries",
                            {"team_id": team_id, "error": "duplicate_team_id"},
                            500
                        )
                    # Retry with new team_id
                    continue
                else:
                    # Different integrity error - might be duplicate captain/team name
                    logger.error(f"[{request_id}] ❌ Database integrity error: {integrity_err}")
                    
                    # CLEANUP: Delete orphaned Cloudinary files
                    uploaded_files = {
                        "pastor_letter": pastor_url,
                        "payment_receipt": receipt_url,
                        "group_photo": photo_url
                    }
                    await cleanup_cloudinary_uploads(uploaded_files, team_id, request_id)
                    
                    # Check for idempotency
                    if idempotency_key:
                        existing = await check_idempotency_key(db, idempotency_key)
                        if existing:
                            try:
                                payload = json.loads(existing)
                                return JSONResponse(status_code=409, content=payload)
                            except Exception:
                                pass
                    return create_error_response(
                        ErrorCode.DATABASE_ERROR,
                        "Database integrity constraint violation",
                        {"error": str(integrity_err)},
                        500
                    )
        
        if not team_inserted:
            logger.error(f"[{request_id}] ❌ Failed to insert team after all retries")
            
            # CLEANUP: Delete orphaned Cloudinary files
            uploaded_files = {
                "pastor_letter": pastor_url,
                "payment_receipt": receipt_url,
                "group_photo": photo_url
            }
            await cleanup_cloudinary_uploads(uploaded_files, team_id, request_id)
            
            return create_error_response(
                ErrorCode.DATABASE_ERROR,
                "Failed to insert team after retries",
                {},
                500
            )
        
        # After successful team insert, proceed with players
        try:

            player_count = 0
            for p in players:
                player_num = p["index"] + 1
                player_id = f"{team_id}-P{player_num:02d}"

                # 🔍 DEBUG: Log file status before upload
                logger.info(f"[{request_id}] 📤 Player {player_num} ({player_id}):")
                logger.info(f"[{request_id}]   - aadhar_file present: {bool(p['aadhar_file'])}")
                logger.info(f"[{request_id}]   - subscription_file present: {bool(p['subscription_file'])}")

                # upload player files (if any)
                aadhar_url = None
                subs_url = None

                if p["aadhar_file"]:
                    try:
                        aadhar_url = await upload_with_retry(
                            p["aadhar_file"],
                            folder=f"players/{team_id}/{player_id}"
                        )
                        StructuredLogger.log_file_upload(request_id, f"player_{p['index']}_aadhar", "success", aadhar_url)
                    except CloudinaryUploadError as e:
                        logger.warning(f"[{request_id}] Player {player_num} aadhar upload failed: {e}")
                        StructuredLogger.log_file_upload(request_id, f"player_{p['index']}_aadhar", "failed")

                if p["subscription_file"]:
                    try:
                        subs_url = await upload_with_retry(
                            p["subscription_file"],
                            folder=f"players/{team_id}/{player_id}"
                        )
                        StructuredLogger.log_file_upload(request_id, f"player_{p['index']}_subscription", "success", subs_url)
                    except CloudinaryUploadError as e:
                        logger.warning(f"[{request_id}] Player {player_num} subscription upload failed: {e}")
                        StructuredLogger.log_file_upload(request_id, f"player_{p['index']}_subscription", "failed")

                player = Player(
                    player_id=player_id,
                    team_id=team_id,
                    name=p["name"],
                    role=p["role"],
                    aadhar_file=aadhar_url,
                    subscription_file=subs_url,
                    created_at=datetime.utcnow()
                )
                
                # 🔍 DEBUG: Log what's being saved to database
                logger.info(f"[{request_id}] 💾 Database record for {player_id}:")
                logger.info(f"[{request_id}]   - aadhar_file: {aadhar_url[:50] + '...' if aadhar_url else 'NULL'}")
                logger.info(f"[{request_id}]   - subscription_file: {subs_url[:50] + '...' if subs_url else 'NULL'}")
                
                db.add(player)
                player_count += 1

            # finalize transaction
            await db.commit()
            StructuredLogger.log_db_operation(request_id, "insert", "success", team_id)
            logger.info(f"[{request_id}] ✅ Database records created (team + {player_count} players)")

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"[{request_id}] IntegrityError after team insert: {e}")
            # If there's an idempotency record, return it
            if idempotency_key:
                existing = await check_idempotency_key(db, idempotency_key)
                if existing:
                    try:
                        payload = json.loads(existing)
                        return JSONResponse(status_code=409, content=payload)
                    except Exception:
                        pass

            if "uq_team_name_captain_phone" in str(e):
                return create_duplicate_error("team_name/captain_phone", validated_team_name)
            return create_database_error("insert", str(e))

        except Exception as e:
            await db.rollback()
            logger.exception(f"[{request_id}] Database error: {e}")
            StructuredLogger.log_db_operation(request_id, "insert", "failed", team_id if 'team_id' in locals() else "unknown")
            return create_database_error("insert", str(e))

        # -------------------------------
        # STORE IDEMPOTENCY RESPONSE (without team_id for pending registrations)
        # -------------------------------
        if idempotency_key:
            try:
                payload = json.dumps({
                    "success": True,
                    "team_name": validated_team_name,
                    "message": "Registration submitted successfully. Please wait for admin confirmation.",
                    "player_count": player_count,
                    "registration_status": "pending"
                })
                await store_idempotency_key(db, idempotency_key, payload)
            except Exception as e:
                logger.warning(f"[{request_id}] Failed to store idempotency key: {e}")

        # -------------------------------
        # RETURN SUCCESS (without team_id for pending registrations)
        # -------------------------------
        logger.info(f"[{request_id}] Registration complete (pending confirmation): {team_id}")
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "team_name": validated_team_name,
                "message": "Registration submitted successfully. Please wait for admin confirmation.",
                "player_count": player_count,
                "registration_status": "pending"
            }
        )

    except Exception as e:
        logger.exception(f"[{request_id}] Unexpected error: {e}")
        StructuredLogger.log_exception(request_id, e)
        return create_internal_error("An unexpected error occurred during registration", {"exception_type": type(e).__name__})
