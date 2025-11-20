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
                            "team_id": "UNKNOWN",
                            "team_name": "UNKNOWN",
                            "message": "This request has already been processed",
                            "player_count": 0
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
                if not role_val or role_val not in ["Batsman", "Bowler", "All-Rounder", "Wicket-Keeper"]:
                    raise ValidationError(role_key, f"Player {idx+1} role must be one of: Batsman, Bowler, All-Rounder, Wicket-Keeper")
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
        # GENERATE TEAM ID
        # -------------------------------
        logger.info(f"[{request_id}] Generating team id...")
        try:
            team_id = await generate_next_team_id(db)
            logger.info(f"[{request_id}] Generated team_id: {team_id}")
        except Exception as e:
            logger.exception(f"[{request_id}] Failed to generate team id: {e}")
            return create_error_response(ErrorCode.TEAM_ID_GENERATION_FAILED, "Team id generation failed", {"error": str(e)}, 500)

        # -------------------------------
        # UPLOAD TEAM FILES (Cloudinary)
        # -------------------------------
        logger.info(f"[{request_id}] Uploading team files to Cloudinary...")
        try:
            pastor_url = await upload_with_retry(pastor_letter, folder=f"ICCT26/pastor_letters/{team_id}")
            StructuredLogger.log_file_upload(request_id, "pastor_letter", "success", pastor_url)

            receipt_url = None
            if payment_receipt:
                try:
                    receipt_url = await upload_with_retry(payment_receipt, folder=f"ICCT26/receipts/{team_id}")
                    StructuredLogger.log_file_upload(request_id, "payment_receipt", "success", receipt_url)
                except CloudinaryUploadError as e:
                    logger.warning(f"[{request_id}] payment_receipt upload failed (optional): {e}")
                    StructuredLogger.log_file_upload(request_id, "payment_receipt", "failed")

            photo_url = None
            if group_photo:
                try:
                    photo_url = await upload_with_retry(group_photo, folder=f"ICCT26/group_photos/{team_id}")
                    StructuredLogger.log_file_upload(request_id, "group_photo", "success", photo_url)
                except CloudinaryUploadError as e:
                    logger.warning(f"[{request_id}] group_photo upload failed (optional): {e}")
                    StructuredLogger.log_file_upload(request_id, "group_photo", "failed")

            logger.info(f"[{request_id}] ✅ Team file uploads complete")
        except CloudinaryUploadError as e:
            logger.error(f"[{request_id}] Required upload failed: {e}")
            return create_upload_error("pastor_letter", getattr(e, "retry_count", None))

        # -------------------------------
        # CREATE DATABASE RECORDS (atomic)
        # -------------------------------
        logger.info(f"[{request_id}] Creating database records (team + players)...")
        try:
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

            player_count = 0
            for p in players:
                player_num = p["index"] + 1
                player_id = f"{team_id}-P{player_num:02d}"

                # upload player files (if any)
                aadhar_url = None
                subs_url = None

                if p["aadhar_file"]:
                    try:
                        aadhar_url = await upload_with_retry(
                            p["aadhar_file"],
                            folder=f"ICCT26/players/{team_id}/player_{p['index']}/aadhar"
                        )
                        StructuredLogger.log_file_upload(request_id, f"player_{p['index']}_aadhar", "success", aadhar_url)
                    except CloudinaryUploadError as e:
                        logger.warning(f"[{request_id}] Player {player_num} aadhar upload failed: {e}")
                        StructuredLogger.log_file_upload(request_id, f"player_{p['index']}_aadhar", "failed")

                if p["subscription_file"]:
                    try:
                        subs_url = await upload_with_retry(
                            p["subscription_file"],
                            folder=f"ICCT26/players/{team_id}/player_{p['index']}/subscription"
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
                db.add(player)
                player_count += 1

            # finalize transaction
            await db.commit()
            StructuredLogger.log_db_operation(request_id, "insert", "success", team_id)
            logger.info(f"[{request_id}] ✅ Database records created (team + {player_count} players)")

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"[{request_id}] IntegrityError on insert: {e}")
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
        # STORE IDEMPOTENCY RESPONSE
        # -------------------------------
        if idempotency_key:
            try:
                payload = json.dumps({
                    "success": True,
                    "team_id": team_id,
                    "team_name": validated_team_name,
                    "message": "Team registered successfully",
                    "player_count": player_count
                })
                await store_idempotency_key(db, idempotency_key, payload)
            except Exception as e:
                logger.warning(f"[{request_id}] Failed to store idempotency key: {e}")

        # -------------------------------
        # RETURN SUCCESS
        # -------------------------------
        logger.info(f"[{request_id}] Registration complete: {team_id}")
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
        logger.exception(f"[{request_id}] Unexpected error: {e}")
        StructuredLogger.log_exception(request_id, e)
        return create_internal_error("An unexpected error occurred during registration", {"exception_type": type(e).__name__})
