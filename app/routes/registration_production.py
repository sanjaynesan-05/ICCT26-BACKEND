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
from app.utils.church_limit_validator import validate_church_limit
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
        # PRE-VALIDATE CAPTAIN EMAIL
        # -------------------------------
        logger.info(f"[{request_id}] Checking captain email uniqueness...")
        from sqlalchemy import select
        existing_captain = await db.execute(
            select(Team).where(Team.captain_email == validated_captain_email)
        )
        if existing_captain.scalar():
            logger.warning(f"[{request_id}] ❌ Captain email already registered: {validated_captain_email}")
            return create_error_response(
                ErrorCode.DUPLICATE_CAPTAIN_EMAIL,
                "This captain email is already used to register a team",
                {"email": validated_captain_email},
                409
            )

        # -------------------------------
        # GENERATE TEAM ID (ATOMIC, NO RETRY)
        # -------------------------------
        logger.info(f"[{request_id}] Generating team ID...")
        team_id = await generate_next_team_id(db)
        logger.info(f"[{request_id}] ✅ Generated team_id: {team_id}")
        
        # -------------------------------
        # CHECK CLOUDINARY CONFIGURATION
        # -------------------------------
        if not settings.CLOUDINARY_ENABLED:
            logger.error(f"[{request_id}] ❌ CLOUDINARY NOT CONFIGURED!")
            logger.error(f"[{request_id}] Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in .env file")
            logger.error(f"[{request_id}] See docs/CLOUDINARY_SETUP.md for instructions")
            return create_error_response(
                ErrorCode.VALIDATION_ERROR,
                "File upload service not configured. Please contact administrator.",
                {"error": "Cloudinary credentials missing"},
                503
            )
        
        # -------------------------------
        # UPLOAD TEAM FILES TO CLOUDINARY
        # -------------------------------
        logger.info(f"[{request_id}] Uploading team files to Cloudinary...")
        uploaded_urls = {}
        
        try:
            # Upload pastor letter (required)
            logger.info(f"[{request_id}] Uploading pastor_letter...")
            pastor_url = await upload_with_retry(
                pastor_letter,
                folder=f"pending/{team_id}",
                public_id=f"{team_id}_pastor_letter",
                resource_type="auto"
            )
            uploaded_urls["pastor_letter"] = pastor_url
            logger.info(f"[{request_id}] ✅ pastor_letter: {pastor_url}")
            StructuredLogger.log_file_upload(request_id, "pastor_letter", "success", pastor_url)

            # Upload payment receipt (optional)
            receipt_url = None
            if payment_receipt:
                logger.info(f"[{request_id}] Uploading payment_receipt...")
                receipt_url = await upload_with_retry(
                    payment_receipt,
                    folder=f"pending/{team_id}",
                    public_id=f"{team_id}_payment_receipt",
                    resource_type="auto"
                )
                uploaded_urls["payment_receipt"] = receipt_url
                logger.info(f"[{request_id}] ✅ payment_receipt: {receipt_url}")
                StructuredLogger.log_file_upload(request_id, "payment_receipt", "success", receipt_url)

            # Upload group photo (optional)
            photo_url = None
            if group_photo:
                logger.info(f"[{request_id}] Uploading group_photo...")
                photo_url = await upload_with_retry(
                    group_photo,
                    folder=f"pending/{team_id}",
                    public_id=f"{team_id}_group_photo",
                    resource_type="auto"
                )
                uploaded_urls["group_photo"] = photo_url
                logger.info(f"[{request_id}] ✅ group_photo: {photo_url}")
                StructuredLogger.log_file_upload(request_id, "group_photo", "success", photo_url)

            logger.info(f"[{request_id}] ✅ All team files uploaded successfully")
            
        except CloudinaryUploadError as e:
            logger.error(f"[{request_id}] ❌ Cloudinary upload failed: {e}")
            StructuredLogger.log_file_upload(request_id, "team_files", "failed", str(e))
            return create_upload_error("team files", str(e))
        except Exception as e:
            logger.error(f"[{request_id}] ❌ Unexpected upload error: {e}")
            return create_internal_error("File upload failed", {"error": str(e)})
        
        # -------------------------------
        # INSERT TEAM AND PLAYERS (SINGLE TRANSACTION)
        # -------------------------------
        logger.info(f"[{request_id}] Inserting team and players...")
        
        try:
            # CHECK CHURCH TEAM LIMIT (with row-level locking)
            # This validation runs within the transaction to prevent race conditions
            logger.info(f"[{request_id}] Validating church team limit...")
            await validate_church_limit(db, validated_church_name, request_id)
            logger.info(f"[{request_id}] Church limit validation passed")
            
            # Create team
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
            logger.info(f"[{request_id}] ✅ Team added to session")
            
            # Create players with Cloudinary uploads
            player_list = []
            for p in players:
                player_num = p["index"] + 1
                player_id = f"{team_id}-P{player_num:02d}"

                # Upload player files to Cloudinary
                aadhar_url = None
                subs_url = None

                try:
                    if p["aadhar_file"]:
                        logger.info(f"[{request_id}] Uploading player {player_num} aadhar...")
                        aadhar_url = await upload_with_retry(
                            p["aadhar_file"],
                            folder=f"pending/{team_id}/players",
                            public_id=f"{player_id}_aadhar",
                            resource_type="auto"
                        )
                        uploaded_urls[f"player_{p['index']}_aadhar"] = aadhar_url
                        logger.info(f"[{request_id}] ✅ Player {player_num} aadhar: {aadhar_url}")
                        StructuredLogger.log_file_upload(request_id, f"player_{p['index']}_aadhar", "success", aadhar_url)

                    if p["subscription_file"]:
                        logger.info(f"[{request_id}] Uploading player {player_num} subscription...")
                        subs_url = await upload_with_retry(
                            p["subscription_file"],
                            folder=f"pending/{team_id}/players",
                            public_id=f"{player_id}_subscription",
                            resource_type="auto"
                        )
                        uploaded_urls[f"player_{p['index']}_subscription"] = subs_url
                        logger.info(f"[{request_id}] ✅ Player {player_num} subscription: {subs_url}")
                        StructuredLogger.log_file_upload(request_id, f"player_{p['index']}_subscription", "success", subs_url)
                        
                except CloudinaryUploadError as e:
                    logger.error(f"[{request_id}] ❌ Player {player_num} file upload failed: {e}")
                    # Cleanup already uploaded files
                    await cleanup_cloudinary_uploads(uploaded_urls, team_id, request_id)
                    return create_upload_error(f"player {player_num} files", str(e))
                except Exception as e:
                    logger.error(f"[{request_id}] ❌ Unexpected error uploading player {player_num} files: {e}")
                    await cleanup_cloudinary_uploads(uploaded_urls, team_id, request_id)
                    return create_internal_error(f"Player {player_num} file upload failed", {"error": str(e)})

                # Create player object after successful uploads
                player = Player(
                    player_id=player_id,
                    team_id=team_id,
                    name=p["name"],
                    role=p["role"],
                    aadhar_file=aadhar_url,
                    subscription_file=subs_url,
                    created_at=datetime.utcnow()
                )
                player_list.append(player)
            
            db.add_all(player_list)
            logger.info(f"[{request_id}] ✅ {len(player_list)} players added to session")
            
            # Commit transaction
            await db.commit()
            logger.info(f"[{request_id}] ✅ Transaction committed successfully")
            StructuredLogger.log_db_operation(request_id, "insert", "success", team_id)

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"[{request_id}] ❌ IntegrityError: {e}")
            
            # Cleanup uploaded files since database insert failed
            logger.warning(f"[{request_id}] Database insert failed, cleaning up {len(uploaded_urls)} uploaded files...")
            await cleanup_cloudinary_uploads(uploaded_urls, team_id, request_id)
            
            # Handle specific integrity errors
            if "teams_team_id_key" in str(e):
                return create_error_response(
                    ErrorCode.DUPLICATE_TEAM_ID,
                    "Team ID collision. Please retry.",
                    {"team_id": team_id},
                    500
                )
            
            if "captain_email" in str(e).lower() or "uq_team_name_captain_phone" in str(e):
                return create_error_response(
                    ErrorCode.DUPLICATE_CAPTAIN_EMAIL,
                    "Captain email or team name already registered",
                    {},
                    409
                )
            
            return create_error_response(
                ErrorCode.DATABASE_ERROR,
                "Database error during registration",
                {"error": str(e)},
                500
            )
        
        except HTTPException as http_exc:
            # Church limit validation or other HTTP exceptions
            await db.rollback()
            logger.warning(f"[{request_id}] ❌ Request rejected: {http_exc.detail}")
            
            # Cleanup uploaded files
            await cleanup_cloudinary_uploads(uploaded_urls, team_id, request_id)
            
            # Return the HTTP exception as-is (preserve status code and detail)
            return JSONResponse(
                status_code=http_exc.status_code,
                content={"success": False, "detail": http_exc.detail}
            )

        except Exception as e:
            await db.rollback()
            logger.exception(f"[{request_id}] ❌ Unexpected database error: {e}")
            
            # Cleanup uploaded files on any database error
            logger.warning(f"[{request_id}] Unexpected error, cleaning up {len(uploaded_urls)} uploaded files...")
            await cleanup_cloudinary_uploads(uploaded_urls, team_id, request_id)
            
            StructuredLogger.log_exception(request_id, e)
            return create_error_response(
                ErrorCode.DATABASE_ERROR,
                "Unexpected error during registration",
                {"error": str(e)},
                500
            )

        # -------------------------------
        # STORE IDEMPOTENCY RESPONSE
        # -------------------------------
        if idempotency_key:
            try:
                payload = json.dumps({
                    "success": True,
                    "team_name": validated_team_name,
                    "message": "Registration submitted successfully. Please wait for admin confirmation.",
                    "player_count": len(players),
                    "registration_status": "pending"
                })
                await store_idempotency_key(db, idempotency_key, payload)
            except Exception as e:
                logger.warning(f"[{request_id}] Failed to store idempotency key: {e}")

        # -------------------------------
        # RETURN SUCCESS
        # -------------------------------
        logger.info(f"[{request_id}] ✅ Registration complete: {team_id}")
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "team_name": validated_team_name,
                "message": "Registration submitted successfully. Please wait for admin confirmation.",
                "player_count": len(players),
                "registration_status": "pending"
            }
        )

    except Exception as e:
        logger.exception(f"[{request_id}] ❌ Unexpected error: {e}")
        StructuredLogger.log_exception(request_id, e)
        return create_internal_error("An unexpected error occurred during registration", {"exception_type": type(e).__name__})
