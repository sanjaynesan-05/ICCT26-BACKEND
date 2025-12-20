"""
UPI Payment Flow Routes
Handles fixed-amount UPI payment generation and payment screenshot uploads
Implements two-stage registration with admin approval
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from datetime import datetime
import logging
import qrcode
from io import BytesIO
import base64
from typing import Optional

from database import get_db_async
from models import Team
from app.utils.validation import ValidationError
from app.utils.cloudinary_reliable import upload_with_retry, CloudinaryUploadError
from app.utils.error_responses import create_validation_error, create_error_response, ErrorCode

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payment", tags=["Payment"])

# ============================================================
# CONSTANTS
# ============================================================

FIXED_PAYMENT_AMOUNT = 1  # ₹1500 fixed amount
UPI_ID = "sanjaynesan007@okaxis"  # Example UPI ID - update with actual
MERCHANT_NAME = "ICCT 26"


# ============================================================
# UPI Link Generation
# ============================================================

@router.get("/upi/{team_id}")
async def get_upi_payment_link(
    team_id: str,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Generate fixed UPI payment link for registration fee.
    
    Rules:
    - Amount is LOCKED at ₹1500
    - Transaction note is team_id (prevents mixing payments)
    - QR code generated from fixed backend data
    - Frontend cannot modify amount or note
    
    Returns:
    - UPI deep link
    - QR code as base64
    - Payment instructions
    """
    logger.info(f"Generating UPI link for team: {team_id}")
    
    # Validate team exists
    team = await db.get(Team, team_id)
    if not team:
        logger.warning(f"Team not found: {team_id}")
        return JSONResponse(
            status_code=404,
            content={"detail": "Team not found"}
        )
    
    # Validate team is in PENDING_PAYMENT or PAYMENT_SUBMITTED status
    if team.status not in ["PENDING_PAYMENT", "PAYMENT_SUBMITTED"]:
        logger.warning(f"Team {team_id} in incorrect status: {team.status}")
        return JSONResponse(
            status_code=400,
            content={
                "detail": f"Cannot generate payment link for team with status: {team.status}"
            }
        )
    
    # Generate UPI deep link with LOCKED amount
    upi_link = (
        f"upi://pay"
        f"?pa={UPI_ID}"
        f"&pn={MERCHANT_NAME.replace(' ', '%20')}"
        f"&am={FIXED_PAYMENT_AMOUNT}"
        f"&cu=INR"
        f"&tn={team_id}"
    )
    
    logger.info(f"Generated UPI link: {upi_link[:50]}...")
    
    # Generate QR code from UPI link
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_link)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for frontend
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        qr_base64 = base64.b64encode(img_bytes.getvalue()).decode()
        
        logger.info(f"Generated QR code for team: {team_id}")
    except Exception as e:
        logger.error(f"QR generation failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "QR code generation failed"}
        )
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "team_id": team_id,
            "amount": FIXED_PAYMENT_AMOUNT,
            "currency": "INR",
            "upi_link": upi_link,
            "qr_code": f"data:image/png;base64,{qr_base64}",
            "merchant_name": MERCHANT_NAME,
            "upi_id": UPI_ID,
            "message": "Scan QR and pay the fixed registration amount. Do not modify amount or transaction note.",
            "instructions": [
                f"1. Scan the QR code or copy the UPI link",
                f"2. Open any UPI app (Google Pay, PhonePe, BHIM, etc.)",
                f"3. Paste the link and complete payment",
                f"4. Amount MUST be ₹{FIXED_PAYMENT_AMOUNT}",
                f"5. Upload the payment screenshot below"
            ]
        }
    )


# ============================================================
# Payment Screenshot Upload
# ============================================================

@router.post("/upload")
async def upload_payment_screenshot(
    request,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Upload payment screenshot as proof of payment.
    
    Flow:
    1. Validate team_id in request
    2. Validate team exists and status is PENDING_PAYMENT
    3. Upload screenshot to Cloudinary
    4. Update team.status = PAYMENT_SUBMITTED
    5. Return success
    
    Returns:
    - Success message
    - Status update
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    try:
        # Parse multipart form
        form = await request.form()
        team_id = form.get("team_id")
        screenshot_file = form.get("screenshot")
        
        logger.info(f"[{request_id}] Payment upload for team: {team_id}")
        
        # Validate team_id
        if not team_id:
            logger.warning(f"[{request_id}] Missing team_id in payment upload")
            return JSONResponse(
                status_code=400,
                content={"detail": "team_id is required"}
            )
        
        # Validate screenshot file
        if not screenshot_file:
            logger.warning(f"[{request_id}] Missing screenshot file")
            return JSONResponse(
                status_code=400,
                content={"detail": "Payment screenshot is required"}
            )
        
        # Validate file type and size
        try:
            from app.utils.file_validation import validate_file_type, validate_file_size
            await validate_file_type(screenshot_file, ["image/jpeg", "image/png"])
            await validate_file_size(screenshot_file, max_size=5*1024*1024)  # 5MB
        except ValidationError as e:
            logger.warning(f"[{request_id}] File validation failed: {e.message}")
            return JSONResponse(
                status_code=400,
                content={"detail": e.message}
            )
        
        # Get team from database
        from sqlalchemy import text
        result = await db.execute(
            text("SELECT * FROM teams WHERE team_id = :team_id"),
            {"team_id": team_id}
        )
        team_row = result.fetchone()
        
        if not team_row:
            logger.warning(f"[{request_id}] Team not found: {team_id}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Team not found"}
            )
        
        # Get full team object
        team = await db.get(Team, team_row.id)
        
        # Validate team status
        if team.status not in ["PENDING_PAYMENT", "PAYMENT_SUBMITTED"]:
            logger.warning(
                f"[{request_id}] Cannot upload payment for team in status: {team.status}"
            )
            return JSONResponse(
                status_code=400,
                content={
                    "detail": f"Cannot upload payment screenshot for team with status: {team.status}"
                }
            )
        
        # Upload screenshot to Cloudinary
        try:
            screenshot_url = await upload_with_retry(
                screenshot_file,
                folder=f"ICCT26/payment_screenshots/{team_id}"
            )
            logger.info(f"[{request_id}] Screenshot uploaded: {screenshot_url[:50]}...")
        except CloudinaryUploadError as e:
            logger.error(f"[{request_id}] Upload failed: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Failed to upload payment screenshot"}
            )
        
        # Update team status to PAYMENT_SUBMITTED
        team.payment_screenshot = screenshot_url
        team.status = "PAYMENT_SUBMITTED"
        team.payment_date = datetime.utcnow()
        
        await db.commit()
        
        logger.info(
            f"[{request_id}] Payment submitted for team {team_id}. "
            f"Status updated to PAYMENT_SUBMITTED"
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "team_id": team_id,
                "message": "Payment screenshot received. Awaiting admin verification."
            }
        )
    
    except Exception as e:
        logger.exception(f"[{request_id}] Payment upload error: {e}")
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": "An error occurred during payment upload"}
        )


# ============================================================
# Get Payment Status
# ============================================================

@router.get("/status/{team_id}")
async def get_payment_status(
    team_id: str,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Get payment and registration status for a team.
    
    Returns:
    - Current status
    - Payment details
    - Next steps
    """
    logger.info(f"Getting payment status for team: {team_id}")
    
    team = await db.get(Team, team_id)
    if not team:
        return JSONResponse(
            status_code=404,
            content={"detail": "Team not found"}
        )
    
    # Determine status messages
    status_map = {
        "PENDING_PAYMENT": {
            "display": "Awaiting Payment",
            "description": "Please complete the payment to proceed.",
            "action": "pay"
        },
        "PAYMENT_SUBMITTED": {
            "display": "Payment Received",
            "description": "Your payment is being verified by the admin.",
            "action": "wait"
        },
        "PENDING_APPROVAL": {
            "display": "Under Review",
            "description": "Your registration is under verification.",
            "action": "wait"
        },
        "APPROVED": {
            "display": "✓ Confirmed",
            "description": "Your registration has been confirmed!",
            "action": "complete"
        },
        "REJECTED": {
            "display": "Rejected",
            "description": "Your registration was rejected. Please contact admin.",
            "action": "contact"
        }
    }
    
    status_info = status_map.get(team.status, {
        "display": team.status,
        "description": "Unknown status",
        "action": "unknown"
    })
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "team_id": team_id,
            "team_name": team.team_name,
            "status": team.status,
            "status_display": status_info["display"],
            "status_description": status_info["description"],
            "next_action": status_info["action"],
            "payment_date": team.payment_date.isoformat() if team.payment_date else None,
            "registration_date": team.registration_date.isoformat() if team.registration_date else None
        }
    )
