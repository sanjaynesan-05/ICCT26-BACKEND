"""
Team registration routes - async SQLAlchemy + PostgreSQL
Handles complete team registration with captain, vice-captain, and players.
"""

import uuid
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db_async
from models import Team, Player
from app.schemas_team import TeamRegistrationRequest, TeamRegistrationResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Registration"],
    responses={404: {"description": "Not found"}},
)


# ============================================================
# Helper Functions
# ============================================================

def generate_team_id() -> str:
    """Generate unique team ID"""
    unique_suffix = str(uuid.uuid4())[:8].upper()
    return f"TEAM-{datetime.utcnow().strftime('%Y%m%d')}-{unique_suffix}"


def generate_player_id(team_id: str, player_index: int) -> str:
    """Generate unique player ID"""
    return f"{team_id}-P{player_index:02d}"


async def save_base64_file(
    file_content: Optional[str],
    file_type: str,
    team_id: str,
    session: AsyncSession
) -> Optional[str]:
    """
    Save base64 file. For now, just store a short reference.
    """
    if not file_content:
        return None

    if isinstance(file_content, str) and file_content.startswith("data:"):
        # store short preview so DB columns don't overflow and for debug
        try:
            _, base64_data = file_content.split(",", 1)
            logger.debug(f"Received {file_type} for {team_id}, length={len(base64_data)}")
            # In prod: upload base64_data to object storage and return URL
            return file_content[:200] + "..." if len(file_content) > 200 else file_content
        except ValueError:
            logger.warning(f"Invalid base64 for {file_type} on team {team_id}")
            return file_content[:200] + "..."
    # If it's already a filename/URL or short string
    return file_content if len(file_content) <= 1000 else file_content[:1000] + "..."


# ============================================================
# Team Registration Endpoint
# ============================================================

@router.post(
    "/register/team",
    response_model=TeamRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": TeamRegistrationResponse},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def register_team(
    request: TeamRegistrationRequest,
    session: AsyncSession = Depends(get_db_async)
) -> TeamRegistrationResponse:
    """
    Register a new cricket team with captain, vice-captain, and players.
    Accepts both camelCase and snake_case keys from clients.
    """
    try:
        # generate team id
        team_id = generate_team_id()
        logger.info(f"📝 New registration start: {request.teamName} / {team_id}")

        # save uploaded file references (shortened)
        pastor_letter_ref = await save_base64_file(request.pastorLetter, "pastor_letter", team_id, session)
        payment_receipt_ref = await save_base64_file(request.paymentReceipt, "payment_receipt", team_id, session)

        # create Team object (flatten captain and viceCaptain)
        team = Team(
            team_id=team_id,
            team_name=request.teamName,
            church_name=request.churchName,

            captain_name=request.captain.name,
            captain_phone=request.captain.phone,
            captain_email=request.captain.email,
            captain_whatsapp=request.captain.whatsapp,

            vice_captain_name=request.viceCaptain.name,
            vice_captain_phone=request.viceCaptain.phone,
            vice_captain_email=request.viceCaptain.email,
            vice_captain_whatsapp=request.viceCaptain.whatsapp,

            payment_receipt=payment_receipt_ref,
            pastor_letter=pastor_letter_ref,

            registration_date=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )

        session.add(team)
        await session.flush()  # flush to DB to ensure team exists (no commit yet)

        # create player rows
        players_created = []
        for idx, p in enumerate(request.players, start=1):
            player_id = generate_player_id(team_id, idx)
            aadhar_ref = await save_base64_file(p.aadharFile, f"aadhar_{idx}", team_id, session)
            sub_ref = await save_base64_file(p.subscriptionFile, f"subscription_{idx}", team_id, session)

            player = Player(
                player_id=player_id,
                team_id=team_id,
                name=p.name,
                age=p.age,
                phone=p.phone,
                role=p.role,
                aadhar_file=aadhar_ref,
                subscription_file=sub_ref,
                created_at=datetime.utcnow(),
            )
            session.add(player)
            players_created.append(p.name)
            logger.debug(f"  added player {player_id} -> {p.name}")

        # final commit
        await session.commit()

        logger.info(f"✅ Team registered: {team_id} ({len(players_created)} players)")
        return TeamRegistrationResponse(
            success=True,
            message="✅ Team registered successfully! Check your email for confirmation.",
            team_id=team_id,
            team_name=request.teamName,
            church_name=request.churchName,
            captain_name=request.captain.name,
            vice_captain_name=request.viceCaptain.name,
            player_count=len(players_created),
            registration_date=datetime.utcnow(),
        )

    except Exception as e:
        logger.exception("❌ Registration failed")
        try:
            await session.rollback()
        except Exception:
            logger.exception("Failed to rollback session")
        # if it's a user/client error we might want to return 400; default 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================================
# Get Team Details Endpoint
# ============================================================

@router.get("/teams/{team_id}")
async def get_team_details(
    team_id: str,
    session: AsyncSession = Depends(get_db_async)
):
    logger.info(f"GET /api/teams/{team_id}")
    try:
        q = select(Team).where(Team.team_id == team_id)
        result = await session.execute(q)
        team = result.scalar_one_or_none()
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team {team_id} not found")

        players_q = select(Player).where(Player.team_id == team_id)
        players_result = await session.execute(players_q)
        players = players_result.scalars().all()

        return {
            "success": True,
            "team": {
                "team_id": team.team_id,
                "team_name": team.team_name,
                "church_name": team.church_name,
                "captain": {
                    "name": team.captain_name,
                    "phone": team.captain_phone,
                    "email": team.captain_email,
                    "whatsapp": team.captain_whatsapp,
                },
                "viceCaptain": {
                    "name": team.vice_captain_name,
                    "phone": team.vice_captain_phone,
                    "email": team.vice_captain_email,
                    "whatsapp": team.vice_captain_whatsapp,
                },
                "registration_date": team.registration_date.isoformat() if team.registration_date else None,
            },
            "players": [
                {
                    "player_id": p.player_id,
                    "name": p.name,
                    "age": p.age,
                    "phone": p.phone,
                    "role": p.role,
                } for p in players
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching team details")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================================
# List All Teams Endpoint
# ============================================================

@router.get("/teams")
async def list_all_teams(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_db_async)
):
    logger.info(f"GET /api/teams skip={skip} limit={limit}")
    try:
        if limit > 100:
            limit = 100

        count_q = select(func.count(Team.id))
        count_result = await session.execute(count_q)
        total_count = count_result.scalar_one()

        q = select(Team).offset(skip).limit(limit)
        r = await session.execute(q)
        teams = r.scalars().all()

        return {
            "success": True,
            "total_teams": total_count,
            "returned": len(teams),
            "skip": skip,
            "limit": limit,
            "teams": [
                {
                    "team_id": t.team_id,
                    "team_name": t.team_name,
                    "church_name": t.church_name,
                    "captain_name": t.captain_name,
                    "registration_date": t.registration_date.isoformat() if t.registration_date else None,
                } for t in teams
            ]
        }

    except Exception as e:
        logger.exception("Error listing teams")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
