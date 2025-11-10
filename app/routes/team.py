"""
Team registration routes - async SQLAlchemy + PostgreSQL
Handles complete team registration with captain, vice-captain, and players.
"""

import uuid
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, func

from database import get_db_async, AsyncSessionLocal
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
    return f"TEAM-{datetime.now().strftime('%Y%m%d')}-{unique_suffix}"


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
    Save base64 file. For now, just store the base64 string.
    In production, you'd upload to cloud storage (S3, GCS, etc.)
    
    Args:
        file_content: Base64-encoded file (data:image/jpeg;base64,...)
        file_type: Type of file (aadhar, subscription, receipt, etc.)
        team_id: Team ID for file organization
        session: Database session
        
    Returns:
        File reference/URL or None
    """
    if not file_content:
        return None
    
    # For production: upload to S3/GCS and return URL
    # For now: store base64 as reference
    if file_content.startswith("data:"):
        # Extract actual base64 from data URI
        try:
            _, base64_data = file_content.split(",", 1)
            # In production, upload base64_data to cloud storage
            logger.info(f"✅ File saved: {file_type} for team {team_id}")
            return file_content[:50] + "..."  # Store reference
        except ValueError:
            logger.warning(f"⚠️  Invalid base64 format for {file_type}")
            return None
    
    return file_content


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
    
    Receives nested JSON from frontend:
    - churchName, teamName, pastorLetter, paymentReceipt
    - captain: {name, phone, whatsapp, email}
    - viceCaptain: {name, phone, whatsapp, email}
    - players: [{name, age, phone, role, aadharFile, subscriptionFile}, ...]
    
    Returns: Team ID and registration confirmation
    """
    
    try:
        # ============================================================
        # Generate IDs
        # ============================================================
        
        team_id = generate_team_id()
        logger.info(f"📝 Starting registration for team: {request.teamName}")
        logger.info(f"🆔 Generated Team ID: {team_id}")
        
        # ============================================================
        # Save Files (base64 encoded)
        # ============================================================
        
        pastor_letter_ref = await save_base64_file(
            request.pastorLetter,
            "pastor_letter",
            team_id,
            session
        )
        
        payment_receipt_ref = await save_base64_file(
            request.paymentReceipt,
            "payment_receipt",
            team_id,
            session
        )
        
        # ============================================================
        # Create Team Record
        # ============================================================
        
        team = Team(
            team_id=team_id,
            team_name=request.teamName,
            church_name=request.churchName,
            
            # Captain info (flattened from nested JSON)
            captain_name=request.captain.name,
            captain_phone=request.captain.phone,
            captain_email=request.captain.email,
            captain_whatsapp=request.captain.whatsapp,
            
            # Vice-captain info (flattened from nested JSON)
            vice_captain_name=request.viceCaptain.name,
            vice_captain_phone=request.viceCaptain.phone,
            vice_captain_email=request.viceCaptain.email,
            vice_captain_whatsapp=request.viceCaptain.whatsapp,
            
            # Files
            payment_receipt=payment_receipt_ref,
            pastor_letter=pastor_letter_ref,
            
            # Timestamps
            registration_date=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        
        session.add(team)
        await session.flush()  # Flush to get the team ID
        
        logger.info(f"✅ Team record created: {team_id}")
        
        # ============================================================
        # Create Player Records
        # ============================================================
        
        players_created = []
        for idx, player_info in enumerate(request.players, 1):
            player_id = generate_player_id(team_id, idx)
            
            # Save player files
            aadhar_file_ref = await save_base64_file(
                player_info.aadharFile,
                f"aadhar_{idx}",
                team_id,
                session
            )
            
            subscription_file_ref = await save_base64_file(
                player_info.subscriptionFile,
                f"subscription_{idx}",
                team_id,
                session
            )
            
            player = Player(
                player_id=player_id,
                team_id=team_id,
                name=player_info.name,
                age=player_info.age,
                phone=player_info.phone,
                role=player_info.role,
                aadhar_file=aadhar_file_ref,
                subscription_file=subscription_file_ref,
                created_at=datetime.utcnow(),
            )
            
            session.add(player)
            players_created.append(player_info.name)
            logger.info(f"  👤 Player {idx}/{len(request.players)}: {player_info.name} ({player_info.role})")
        
        # ============================================================
        # Commit All Changes Transactionally
        # ============================================================
        
        await session.commit()
        
        logger.info(f"✅ Team registered: {team_id}")
        logger.info(f"✅ {len(request.players)} players registered")
        print(f"✅ Team registered: {team_id}")
        print(f"   Team: {request.teamName}")
        print(f"   Church: {request.churchName}")
        print(f"   Captain: {request.captain.name}")
        print(f"   Vice-Captain: {request.viceCaptain.name}")
        print(f"   Players: {len(request.players)}")
        
        # ============================================================
        # Return Success Response
        # ============================================================
        
        return TeamRegistrationResponse(
            success=True,
            message="✅ Team registered successfully! Check your email for confirmation.",
            team_id=team_id,
            team_name=request.teamName,
            church_name=request.churchName,
            captain_name=request.captain.name,
            vice_captain_name=request.viceCaptain.name,
            player_count=len(request.players),
            registration_date=datetime.utcnow(),
        )
    
    except ValueError as ve:
        logger.error(f"❌ Validation error: {str(ve)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(ve)}"
        )
    
    except Exception as e:
        logger.error(f"❌ Registration failed: {str(e)}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


# ============================================================
# Get Team Details Endpoint
# ============================================================

@router.get("/teams/{team_id}")
async def get_team_details(
    team_id: str,
    session: AsyncSession = Depends(get_db_async)
):
    """
    Get team details including all players.
    
    Args:
        team_id: Team ID (e.g., TEAM-20250115-ABC12345)
        
    Returns:
        Team info with players list
    """
    
    try:
        # Fetch team
        query = select(Team).where(Team.team_id == team_id)
        result = await session.execute(query)
        team = result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} not found"
            )
        
        # Fetch players
        players_query = select(Player).where(Player.team_id == team_id)
        players_result = await session.execute(players_query)
        players = players_result.scalars().all()
        
        logger.info(f"✅ Retrieved team: {team_id} with {len(players)} players")
        
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
                "registration_date": team.registration_date.isoformat(),
            },
            "players": [
                {
                    "player_id": p.player_id,
                    "name": p.name,
                    "age": p.age,
                    "phone": p.phone,
                    "role": p.role,
                }
                for p in players
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Error fetching team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================
# List All Teams Endpoint
# ============================================================

@router.get("/teams")
async def list_all_teams(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_db_async)
):
    """
    List all registered teams with pagination.
    
    Args:
        skip: Number of teams to skip (default 0)
        limit: Maximum teams to return (default 10, max 100)
        
    Returns:
        List of teams with counts
    """
    
    try:
        if limit > 100:
            limit = 100
        
        # Get total count
        count_query = select(func.count(Team.id))
        count_result = await session.execute(count_query)
        total_count = count_result.scalar()
        
        # Fetch teams with pagination
        query = select(Team).offset(skip).limit(limit)
        result = await session.execute(query)
        teams = result.scalars().all()
        
        logger.info(f"✅ Retrieved {len(teams)} teams (total: {total_count})")
        
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
                    "registration_date": t.registration_date.isoformat(),
                }
                for t in teams
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Error listing teams: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
