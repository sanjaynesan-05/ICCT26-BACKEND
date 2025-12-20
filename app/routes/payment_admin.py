"""
Admin Payment Approval Routes
Handles admin verification and approval/rejection of payments
Final authority for registration confirmation
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging
from typing import Optional

from database import get_db_async
from models import Team

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin Payment"])


# ============================================================
# Admin Approve Payment
# ============================================================

@router.post("/approve/{team_id}")
async def admin_approve_payment(
    team_id: str,
    request,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Admin approves payment and confirms registration.
    
    Authority: FINAL - No further approval needed
    
    Flow:
    1. Validate team exists
    2. Validate team status is PAYMENT_SUBMITTED
    3. Update status to APPROVED
    4. Log approval with timestamp and admin info
    5. Return success
    
    After this:
    - Registration is CONFIRMED
    - Team can participate in tournament
    - Players are registered
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    try:
        logger.info(f"[{request_id}] Admin approval requested for team: {team_id}")
        
        # Get team
        team = await db.get(Team, team_id)
        if not team:
            logger.warning(f"[{request_id}] Team not found: {team_id}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Team not found"}
            )
        
        # Validate status
        if team.status != "PAYMENT_SUBMITTED":
            logger.warning(
                f"[{request_id}] Cannot approve team in status: {team.status}. "
                f"Expected: PAYMENT_SUBMITTED"
            )
            return JSONResponse(
                status_code=400,
                content={
                    "detail": f"Cannot approve payment for team with status: {team.status}. "
                              f"Expected status: PAYMENT_SUBMITTED"
                }
            )
        
        # Update team status to APPROVED
        team.status = "APPROVED"
        team.approval_date = datetime.utcnow()
        team.approved_by = "admin"  # Could store actual admin user if auth implemented
        
        await db.commit()
        
        logger.info(
            f"[{request_id}] ✅ Team {team_id} APPROVED by admin. "
            f"Registration is now CONFIRMED."
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "team_id": team_id,
                "team_name": team.team_name,
                "status": "APPROVED",
                "message": "Registration confirmed successfully",
                "confirmation": "Team registration and payment have been verified and approved."
            }
        )
    
    except Exception as e:
        logger.exception(f"[{request_id}] Admin approval error: {e}")
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": "An error occurred during approval"}
        )


# ============================================================
# Admin Reject Payment
# ============================================================

@router.post("/reject/{team_id}")
async def admin_reject_payment(
    team_id: str,
    request,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Admin rejects payment/registration.
    
    Authority: FINAL - Registration will not be confirmed
    
    Flow:
    1. Validate team exists
    2. Update status to REJECTED
    3. Store rejection reason
    4. Log rejection
    5. Return success
    
    After this:
    - Team must re-register
    - Previous data is marked as rejected
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    try:
        # Get rejection reason from request body
        body = await request.json()
        rejection_reason = body.get("reason", "Not specified")
        
        logger.info(
            f"[{request_id}] Admin rejection requested for team: {team_id}. "
            f"Reason: {rejection_reason}"
        )
        
        # Get team
        team = await db.get(Team, team_id)
        if not team:
            logger.warning(f"[{request_id}] Team not found: {team_id}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Team not found"}
            )
        
        # Update team status to REJECTED
        team.status = "REJECTED"
        team.rejection_reason = rejection_reason
        team.rejection_date = datetime.utcnow()
        team.rejected_by = "admin"
        
        await db.commit()
        
        logger.info(
            f"[{request_id}] ❌ Team {team_id} REJECTED by admin. "
            f"Reason: {rejection_reason}"
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "team_id": team_id,
                "team_name": team.team_name,
                "status": "REJECTED",
                "message": "Registration rejected",
                "rejection_reason": rejection_reason
            }
        )
    
    except ValueError:
        logger.warning(f"[{request_id}] Invalid request body for rejection")
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid request body"}
        )
    except Exception as e:
        logger.exception(f"[{request_id}] Admin rejection error: {e}")
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": "An error occurred during rejection"}
        )


# ============================================================
# List Pending Payments
# ============================================================

@router.get("/payments/pending")
async def get_pending_payments(
    db: AsyncSession = Depends(get_db_async)
):
    """
    Get list of all teams with payments awaiting approval.
    
    Used by admin dashboard to see pending verifications.
    """
    logger.info("Fetching pending payment approvals")
    
    try:
        from sqlalchemy import text
        
        result = await db.execute(
            text("""
                SELECT 
                    team_id, team_name, church_name,
                    captain_name, captain_phone, captain_email,
                    payment_date, payment_screenshot,
                    status
                FROM teams
                WHERE status IN ('PAYMENT_SUBMITTED', 'PENDING_APPROVAL')
                ORDER BY payment_date ASC
            """)
        )
        
        pending_teams = []
        for row in result:
            pending_teams.append({
                "team_id": row[0],
                "team_name": row[1],
                "church_name": row[2],
                "captain_name": row[3],
                "captain_phone": row[4],
                "captain_email": row[5],
                "payment_date": row[6].isoformat() if row[6] else None,
                "payment_screenshot": row[7],
                "status": row[8]
            })
        
        logger.info(f"Found {len(pending_teams)} teams with pending payments")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "count": len(pending_teams),
                "teams": pending_teams
            }
        )
    
    except Exception as e:
        logger.exception(f"Error fetching pending payments: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while fetching pending payments"}
        )


# ============================================================
# Get Team Payment Details (Admin View)
# ============================================================

@router.get("/payments/{team_id}")
async def get_team_payment_details(
    team_id: str,
    db: AsyncSession = Depends(get_db_async)
):
    """
    Get full payment and registration details for a team (admin view).
    
    Includes:
    - Payment screenshot URL
    - All team details
    - Captain info
    - Player roster
    - Status history
    """
    logger.info(f"Fetching payment details for team: {team_id}")
    
    try:
        team = await db.get(Team, team_id)
        if not team:
            logger.warning(f"Team not found: {team_id}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Team not found"}
            )
        
        # Format player data
        players = []
        if team.players:
            for player in team.players:
                players.append({
                    "player_id": player.player_id,
                    "name": player.name,
                    "role": player.role
                })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "team_id": team.team_id,
                "team_name": team.team_name,
                "church_name": team.church_name,
                "status": team.status,
                "captain": {
                    "name": team.captain_name,
                    "phone": team.captain_phone,
                    "email": team.captain_email,
                    "whatsapp": team.captain_whatsapp
                },
                "vice_captain": {
                    "name": team.vice_captain_name,
                    "phone": team.vice_captain_phone,
                    "email": team.vice_captain_email,
                    "whatsapp": team.vice_captain_whatsapp
                },
                "payment_screenshot": team.payment_screenshot,
                "payment_date": team.payment_date.isoformat() if team.payment_date else None,
                "approval_date": team.approval_date.isoformat() if team.approval_date else None,
                "registration_date": team.registration_date.isoformat() if team.registration_date else None,
                "player_count": len(players),
                "players": players
            }
        )
    
    except Exception as e:
        logger.exception(f"Error fetching payment details: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while fetching payment details"}
        )
