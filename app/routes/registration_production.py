"""
POST /api/register/team: multipart team registration (2027 frontend contract).

Flow:
  1. Validate the Idempotency-Key header and every form field (422 VALIDATION_ERROR).
  2. Claim the idempotency key (new key / replay / in-progress / takeover).
  3. Reject an already-registered church BEFORE uploading anything.
  4. Upload the receipt to {CLOUDINARY_PREFIX}/pending/{idempotency_key}/payment_receipt.
     No database transaction or lock is open during the upload.
  5. One short transaction: next team number, team + players, key -> completed.
  6. No email is sent at registration; the team is emailed only after admin approval.
"""

import hashlib
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import FormData, UploadFile

from config.churches import build_church_lookup, normalize_church_name, parse_church_list
from config.settings import settings
from database import get_db_async
from models import Player, Team
from app.utils.cloudinary_reliable import CloudinaryUploadError, upload_with_retry
from app.utils.error_responses import ErrorCode, create_error_response
from app.utils.validation import (
    ValidationError,
    validate_email,
    validate_file,
    validate_name,
    validate_phone,
    validate_team_name,
)

logger = logging.getLogger(__name__)
router = APIRouter()

ENDPOINT = "/api/register/team"
CHURCH_UNIQUE_CONSTRAINT = "uq_registered_team_church"
# Other unique indexes on teams in the live database -> (form field, message).
_OTHER_UNIQUE = {
    "ix_teams_captain_email": ("captain_email", "This captain email is already used by another registered team."),
    "ix_teams_captain_phone": ("captain_phone", "This captain phone number is already used by another registered team."),
    "uq_team_name_captain_phone": ("team_name", "A team with this name and captain phone is already registered."),
}
STALE_PROCESSING_MINUTES = 15
RETRY_AFTER_SECONDS = "5"

_UUID_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
_PLAYER_FIELD_PATTERN = re.compile(r"^player_(\d+)_name$")
MIN_PLAYERS = 13
MAX_PLAYERS = 17


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

def _error(code: str, message: str, details: Optional[Dict[str, Any]] = None, status: int = 400,
           headers: Optional[Dict[str, str]] = None) -> JSONResponse:
    return create_error_response(code, message, details, status, headers)


def _validation_error(message: str, field: Optional[str], reason: Optional[str] = None) -> JSONResponse:
    details: Dict[str, Any] = {}
    if field:
        details["field"] = field
    if reason:
        details["reason"] = reason
    return _error(ErrorCode.VALIDATION_ERROR, message, details, status=422)


def _in_progress() -> JSONResponse:
    return _error(
        ErrorCode.REQUEST_IN_PROGRESS,
        "This registration is still being processed. Please wait.",
        status=409,
        headers={"Retry-After": RETRY_AFTER_SECONDS},
    )


def _church_taken(church_name: str) -> JSONResponse:
    return _error(
        ErrorCode.CHURCH_ALREADY_REGISTERED,
        f"{church_name} already has its one allowed entry.",
        {"field": "church_name"},
        status=409,
    )


# ---------------------------------------------------------------------------
# Form parsing
# ---------------------------------------------------------------------------

def _text(form: FormData, key: str) -> Optional[str]:
    value = form.get(key)
    if value is None or isinstance(value, UploadFile):
        return None
    return str(value).strip()


def _file(form: FormData, key: str) -> Optional[UploadFile]:
    value = form.get(key)
    return value if isinstance(value, UploadFile) else None


def _player_fields(form: FormData) -> Tuple[List[str], Optional[str]]:
    """Return the player field keys in index order, or an error message."""
    indexes: Dict[int, str] = {}
    for key, _ in form.multi_items():
        if not key.startswith("player_"):
            continue
        match = _PLAYER_FIELD_PATTERN.fullmatch(key)
        if not match:
            return [], f"Malformed player field name: {key}"
        index = int(match.group(1))
        if index in indexes:
            return [], f"Duplicate player index: {key}"
        indexes[index] = key
    if sorted(indexes) != list(range(len(indexes))):
        return [], "Player indexes must be sequential starting at 0"
    return [indexes[i] for i in range(len(indexes))], None


async def _sha256(upload: UploadFile) -> str:
    await upload.seek(0)
    digest = hashlib.sha256()
    while chunk := await upload.read(1024 * 1024):
        digest.update(chunk)
    await upload.seek(0)
    return digest.hexdigest()


def _fingerprint(values: Dict[str, Any], receipt_digest: str) -> str:
    payload = json.dumps({"fields": values, "receipt": receipt_digest}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_fields(form: FormData, player_keys: List[str]) -> Dict[str, Any]:
    """Validate every text field. Raises ValidationError on the first failure."""
    def optional_phone(key: str, label: str) -> Optional[str]:
        raw = _text(form, key)
        return validate_phone(raw, label) if raw else None  # '' -> NULL

    church_raw = " ".join((_text(form, "church_name") or "").split())
    if not church_raw:
        raise ValidationError(ErrorCode.CHURCH_REQUIRED, "Church name is required", "church_name")
    lookup = build_church_lookup(parse_church_list(settings.CHURCH_LIST))
    normalized = normalize_church_name(church_raw)
    if lookup and normalized not in lookup:
        raise ValidationError(ErrorCode.VALIDATION_ERROR, "Church is not in the tournament list", "church_name")

    return {
        "team_name": validate_team_name(_text(form, "team_name") or ""),
        # Store the configured spelling so admin pages and availability agree.
        "church_name": lookup.get(normalized, church_raw),
        "church_name_normalized": normalized,
        "captain_name": validate_name(_text(form, "captain_name") or "", "Captain name"),
        "captain_phone": validate_phone(_text(form, "captain_phone") or "", "Captain phone"),
        "captain_email": validate_email(_text(form, "captain_email") or "", "Captain email"),
        "captain_whatsapp": optional_phone("captain_whatsapp", "Captain whatsapp"),
        "vice_name": validate_name(_text(form, "vice_name") or "", "Vice name"),
        "vice_phone": validate_phone(_text(form, "vice_phone") or "", "Vice phone"),
        "vice_email": validate_email(_text(form, "vice_email") or "", "Vice email"),
        "vice_whatsapp": optional_phone("vice_whatsapp", "Vice whatsapp"),
        "players": [_validate_player(form, i, key) for i, key in enumerate(player_keys)],
    }


def _validate_player(form: FormData, index: int, key: str) -> str:
    try:
        return validate_name(_text(form, key) or "", f"Player {index + 1} name")
    except ValidationError as exc:
        exc.field = key  # report the real form field, e.g. player_0_name
        raise


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

async def _claim_key(db: AsyncSession, key: str, fingerprint: str) -> Tuple[Optional[int], Optional[JSONResponse]]:
    """
    Claim the idempotency key for this request.

    Returns (record_id, None) when this request owns the key and should proceed,
    or (None, response) when the caller must return `response` immediately.
    """
    inserted = await db.execute(
        text("""
            INSERT INTO idempotency_keys (key, request_fingerprint, state, endpoint, created_at)
            VALUES (:key, :fp, 'processing', :endpoint, now())
            ON CONFLICT (key) DO NOTHING
            RETURNING id
        """),
        {"key": key, "fp": fingerprint, "endpoint": ENDPOINT},
    )
    record_id = inserted.scalar_one_or_none()
    await db.commit()
    if record_id is not None:
        return record_id, None

    existing = (await db.execute(
        text("SELECT request_fingerprint, state, response_data FROM idempotency_keys WHERE key = :key"),
        {"key": key},
    )).one_or_none()
    await db.commit()
    if existing is None:
        # Deleted between INSERT and SELECT; let the client retry with the same key.
        return None, _in_progress()

    stored_fp, state, response_data = existing
    if stored_fp and stored_fp != fingerprint:
        return None, _error(
            ErrorCode.DUPLICATE_SUBMISSION,
            "This Idempotency-Key was already used for a different registration.",
            status=409,
        )
    if state == "completed" and response_data:
        return None, JSONResponse(status_code=201, content=json.loads(response_data))

    # failed, or processing for too long: take it over atomically.
    taken = await db.execute(
        text(f"""
            UPDATE idempotency_keys
               SET state = 'processing', created_at = now(), response_data = NULL,
                   request_fingerprint = :fp
             WHERE key = :key
               AND (state = 'failed'
                    OR (state = 'processing'
                        AND created_at < now() - interval '{STALE_PROCESSING_MINUTES} minutes'))
            RETURNING id
        """),
        {"key": key, "fp": fingerprint},
    )
    record_id = taken.scalar_one_or_none()
    await db.commit()
    if record_id is None:
        return None, _in_progress()
    return record_id, None


async def _mark_failed(db: AsyncSession, record_id: int, error_code: str, message: str) -> None:
    """Release the key so a retry with the same key can take it over."""
    try:
        await db.execute(
            text("""
                UPDATE idempotency_keys SET state = 'failed', response_data = :data
                 WHERE id = :id AND state = 'processing'
            """),
            {"id": record_id, "data": json.dumps({"success": False, "error_code": error_code, "message": message})},
        )
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to mark idempotency key %s as failed", record_id)


# ---------------------------------------------------------------------------
# Cloudinary (module-level so tests can patch them)
# ---------------------------------------------------------------------------

def _receipt_location(idempotency_key: str) -> Tuple[str, str]:
    return f"{settings.CLOUDINARY_PREFIX}/pending/{idempotency_key}", "payment_receipt"


async def _upload_receipt(receipt: UploadFile, idempotency_key: str) -> str:
    if not settings.CLOUDINARY_ENABLED:
        raise CloudinaryUploadError("File upload service is not configured")
    folder, public_id = _receipt_location(idempotency_key)
    return await upload_with_retry(receipt, folder=folder, public_id=public_id, resource_type="auto")


async def _delete_receipt(idempotency_key: str) -> None:
    """Best-effort removal of an uploaded receipt after a failed registration."""
    try:
        from app.utils.cloudinary_upload import cloudinary_uploader
        folder, public_id = _receipt_location(idempotency_key)
        await cloudinary_uploader.delete_file(f"{folder}/{public_id}")
    except Exception:
        logger.exception("Receipt cleanup failed for key %s", idempotency_key)


def _constraint_name(exc: IntegrityError) -> Optional[str]:
    orig = exc.orig
    for candidate in (orig, getattr(orig, "__cause__", None)):
        name = getattr(candidate, "constraint_name", None)
        if name:
            return name
        diag = getattr(candidate, "diag", None)
        if diag is not None and getattr(diag, "constraint_name", None):
            return diag.constraint_name
    return None


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/register/team")
async def register_team(
    request: Request,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db_async),
):
    # 1. Validate everything before touching the database or Cloudinary.
    if not idempotency_key or not _UUID_PATTERN.fullmatch(idempotency_key.strip()):
        return _validation_error("Idempotency-Key header must be a UUID", "Idempotency-Key")
    key = idempotency_key.strip().lower()

    form = await request.form()

    receipt = _file(form, "payment_receipt")
    if receipt is None:
        return _validation_error("Payment receipt is required", "payment_receipt", ErrorCode.PAYMENT_RECEIPT_REQUIRED)
    try:
        await validate_file(receipt, "Payment receipt")
    except ValidationError as exc:
        return _validation_error(exc.message, "payment_receipt", exc.error_code)

    player_keys, player_error = _player_fields(form)
    if player_error:
        return _validation_error(player_error, "players", ErrorCode.PLAYER_NAME_INVALID)
    if not MIN_PLAYERS <= len(player_keys) <= MAX_PLAYERS:
        return _validation_error(
            f"Team must have between {MIN_PLAYERS} and {MAX_PLAYERS} players (got {len(player_keys)})",
            "players",
            ErrorCode.PLAYER_COUNT_INVALID,
        )

    try:
        values = _validate_fields(form, player_keys)
    except ValidationError as exc:
        return _validation_error(exc.message, exc.field, exc.error_code)

    fingerprint = _fingerprint(values, await _sha256(receipt))

    # 2. Idempotency.
    try:
        record_id, early = await _claim_key(db, key, fingerprint)
    except Exception:
        await db.rollback()
        logger.exception("Could not claim idempotency key %s", key)
        return _error(ErrorCode.DATABASE_ERROR, "Registration could not be saved", status=500)
    if early is not None:
        return early

    # 3. Church check before any upload (the UNIQUE index stays as the final guard).
    try:
        taken = (await db.execute(
            text("SELECT 1 FROM teams WHERE church_name_normalized = :n LIMIT 1"),
            {"n": values["church_name_normalized"]},
        )).first()
        await db.commit()  # end the read transaction; nothing stays open during the upload
    except Exception:
        await db.rollback()
        logger.exception("Church check failed for key %s", key)
        await _mark_failed(db, record_id, ErrorCode.DATABASE_ERROR, "Registration could not be saved")
        return _error(ErrorCode.DATABASE_ERROR, "Registration could not be saved", status=500)
    if taken:
        await _mark_failed(db, record_id, ErrorCode.CHURCH_ALREADY_REGISTERED, "Church already registered")
        return _church_taken(values["church_name"])

    # 4. Upload with no transaction or lock held.
    try:
        receipt_url = await _upload_receipt(receipt, key)
    except Exception:
        logger.exception("Payment receipt upload failed for key %s", key)
        await _mark_failed(db, record_id, ErrorCode.FILE_UPLOAD_FAILED, "Payment receipt upload failed")
        return _error(ErrorCode.FILE_UPLOAD_FAILED, "Payment receipt upload failed. Please try again.", status=503)

    # 5. One short transaction.
    team_id = None
    try:
        number = (await db.execute(
            text("UPDATE team_sequence SET last_number = last_number + 1 WHERE id = 1 RETURNING last_number")
        )).scalar_one_or_none()
        if number is None:
            raise RuntimeError("team_sequence row id=1 is missing (run scripts/migrate_2027.py)")
        team_id = f"ICCT-{number:03d}"

        db.add(Team(
            team_id=team_id,
            team_name=values["team_name"],
            church_name=values["church_name"],
            church_name_normalized=values["church_name_normalized"],
            captain_name=values["captain_name"],
            captain_phone=values["captain_phone"],
            captain_email=values["captain_email"],
            captain_whatsapp=values["captain_whatsapp"],
            vice_captain_name=values["vice_name"],
            vice_captain_phone=values["vice_phone"],
            vice_captain_email=values["vice_email"],
            vice_captain_whatsapp=values["vice_whatsapp"],
            payment_receipt=receipt_url,
            registration_status="pending",
        ))
        await db.flush()
        for index, name in enumerate(values["players"], start=1):
            db.add(Player(player_id=f"{team_id}-P{index:02d}", team_id=team_id, name=name))

        response = {
            "success": True,
            "data": {"registration_status": "pending", "team_id": team_id, "team_name": values["team_name"]},
            "message": "Registration submitted successfully",
        }
        completed = await db.execute(
            text("""
                UPDATE idempotency_keys SET state = 'completed', team_id = :team_id, response_data = :data
                 WHERE id = :id AND state = 'processing'
            """),
            {"id": record_id, "team_id": team_id, "data": json.dumps(response)},
        )
        if completed.rowcount != 1:
            # Another request took this key over after it went stale. It owns the
            # key and the same upload path now, so don't touch either.
            await db.rollback()
            return _in_progress()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        await _delete_receipt(key)
        constraint = _constraint_name(exc)
        if constraint == CHURCH_UNIQUE_CONSTRAINT:
            await _mark_failed(db, record_id, ErrorCode.CHURCH_ALREADY_REGISTERED, "Church already registered")
            return _church_taken(values["church_name"])
        if constraint in _OTHER_UNIQUE:
            field, message = _OTHER_UNIQUE[constraint]
            await _mark_failed(db, record_id, ErrorCode.VALIDATION_ERROR, message)
            return _validation_error(message, field, "ALREADY_REGISTERED")
        logger.exception("Integrity error saving registration (constraint=%s)", _constraint_name(exc))
        await _mark_failed(db, record_id, ErrorCode.DATABASE_ERROR, "Registration could not be saved")
        return _error(ErrorCode.DATABASE_ERROR, "Registration could not be saved", status=500)
    except Exception:
        await db.rollback()
        await _delete_receipt(key)
        logger.exception("Unexpected registration failure (team_id=%s)", team_id)
        await _mark_failed(db, record_id, ErrorCode.DATABASE_ERROR, "Registration could not be saved")
        return _error(ErrorCode.DATABASE_ERROR, "Registration could not be saved", status=500)

    # No email here: the team is only emailed once an admin approves it
    # (PUT /admin/teams/{team_id}/confirm).
    return JSONResponse(status_code=201, content=response)
