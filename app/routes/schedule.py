"""
Cricket Match Schedule Management Routes
Handles CRUD operations for match scheduling and result tracking
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from datetime import datetime

from database import get_db
from models import Match, Team
from app.schemas_schedule import (
    MatchCreateRequest,
    MatchUpdateRequest,
    MatchStatusUpdate,
    MatchResponse,
    MatchResult,
    MatchesListResponse,
    MatchSingleResponse,
    ExportResponse,
    ApiResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/schedule", tags=["Schedule"])


# ============================================================
# Helper Functions
# ============================================================

def get_team_by_name(db: Session, team_name: str) -> Team:
    """Get team by exact name match"""
    team = db.query(Team).filter(Team.team_name == team_name.strip()).first()
    if not team:
        raise HTTPException(
            status_code=400,
            detail=f"Team '{team_name}' not found in database"
        )
    return team


def match_to_response(match: Match) -> dict:
    """Convert Match ORM object to response dict with team names"""
    result = None
    
    # Build result object only if match is completed
    if match.status == 'completed' and match.winner_id:
        result = MatchResult(
            winner=match.winner.team_name,
            margin=match.margin,
            margin_type=match.margin_type,
            won_by_batting_first=match.won_by_batting_first
        )
    
    return {
        "id": match.id,
        "round": match.round,
        "round_number": match.round_number,
        "match_number": match.match_number,
        "team1": match.team1.team_name,
        "team2": match.team2.team_name,
        "status": match.status,
        "result": result.dict() if result else None,
        "created_at": match.created_at,
        "updated_at": match.updated_at
    }


# ============================================================
# Endpoints
# ============================================================

@router.get("/matches", response_model=MatchesListResponse)
async def get_all_matches(db: Session = Depends(get_db)):
    """
    Fetch all matches for public schedule display.
    Returns matches sorted by round_number and match_number.
    """
    try:
        logger.info("Fetching all matches")
        
        matches = db.query(Match).order_by(
            Match.round_number.asc(),
            Match.match_number.asc()
        ).all()
        
        matches_data = [match_to_response(m) for m in matches]
        
        logger.info(f"✅ Successfully fetched {len(matches)} matches")
        
        return {
            "success": True,
            "data": matches_data
        }
    
    except Exception as e:
        logger.error(f"❌ Error fetching matches: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching matches")


@router.post("/matches", response_model=MatchSingleResponse, status_code=201)
async def create_match(request: MatchCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new match.
    
    Validates:
    - Both teams exist in database
    - No duplicate match (round_number + match_number)
    """
    try:
        logger.info(f"Creating match: {request.team1} vs {request.team2} (Round {request.round_number})")
        
        # Validate teams exist
        team1 = get_team_by_name(db, request.team1)
        team2 = get_team_by_name(db, request.team2)
        
        # Prevent same team playing against itself
        if team1.id == team2.id:
            raise HTTPException(
                status_code=400,
                detail="A team cannot play against itself"
            )
        
        # Check for duplicate match
        existing_match = db.query(Match).filter(
            and_(
                Match.round_number == request.round_number,
                Match.match_number == request.match_number
            )
        ).first()
        
        if existing_match:
            raise HTTPException(
                status_code=400,
                detail=f"Match already exists for Round {request.round_number}, Match {request.match_number}"
            )
        
        # Create new match
        new_match = Match(
            round=request.round,
            round_number=request.round_number,
            match_number=request.match_number,
            team1_id=team1.id,
            team2_id=team2.id,
            status="scheduled"
        )
        
        db.add(new_match)
        db.commit()
        db.refresh(new_match)
        
        logger.info(f"✅ Match created successfully (ID: {new_match.id})")
        
        return {
            "success": True,
            "message": "Match created successfully",
            "data": match_to_response(new_match)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating match: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating match")


@router.put("/matches/{match_id}", response_model=MatchSingleResponse)
async def update_match(match_id: int, request: MatchUpdateRequest, db: Session = Depends(get_db)):
    """
    Update match details (teams, round, match number).
    
    Cannot update if match is already completed.
    """
    try:
        logger.info(f"Updating match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Prevent updating completed matches
        if match.status == 'completed':
            raise HTTPException(
                status_code=409,
                detail="Cannot update a match that is completed"
            )
        
        # Validate new teams exist
        team1 = get_team_by_name(db, request.team1)
        team2 = get_team_by_name(db, request.team2)
        
        if team1.id == team2.id:
            raise HTTPException(
                status_code=400,
                detail="A team cannot play against itself"
            )
        
        # Check for duplicate match number in round (excluding current match)
        duplicate_match = db.query(Match).filter(
            and_(
                Match.round_number == request.round_number,
                Match.match_number == request.match_number,
                Match.id != match_id
            )
        ).first()
        
        if duplicate_match:
            raise HTTPException(
                status_code=400,
                detail=f"Match number {request.match_number} already exists in Round {request.round_number}"
            )
        
        # Update match
        match.round = request.round
        match.round_number = request.round_number
        match.match_number = request.match_number
        match.team1_id = team1.id
        match.team2_id = team2.id
        match.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Match {match_id} updated successfully")
        
        return {
            "success": True,
            "message": "Match updated successfully",
            "data": match_to_response(match)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating match: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating match")


@router.delete("/matches/{match_id}", response_model=ApiResponse)
async def delete_match(match_id: int, db: Session = Depends(get_db)):
    """
    Delete a match.
    
    Can only delete if status is 'scheduled'.
    Cannot delete live or completed matches.
    """
    try:
        logger.info(f"Deleting match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Prevent deleting live or completed matches
        if match.status in ['live', 'completed']:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete a match that is live or completed"
            )
        
        db.delete(match)
        db.commit()
        
        logger.info(f"✅ Match {match_id} deleted successfully")
        
        return {
            "success": True,
            "message": "Match deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error deleting match: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting match")


@router.put("/matches/{match_id}/status", response_model=MatchSingleResponse)
async def update_match_status(match_id: int, request: MatchStatusUpdate, db: Session = Depends(get_db)):
    """
    Update match status (scheduled → live → completed).
    
    Valid transitions:
    - scheduled → live
    - live → completed
    - scheduled → completed
    
    Cannot downgrade status (cannot go from live back to scheduled).
    """
    try:
        logger.info(f"Updating match {match_id} status to {request.status}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Validate status transition
        valid_transitions = {
            'scheduled': ['live', 'completed'],
            'live': ['completed'],
            'completed': []  # No transitions from completed
        }
        
        if request.status not in valid_transitions.get(match.status, []):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition from '{match.status}' to '{request.status}'"
            )
        
        match.status = request.status
        match.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Match {match_id} status updated to {request.status}")
        
        return {
            "success": True,
            "message": f"Match status updated to {request.status}",
            "data": match_to_response(match)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating match status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating match status")


@router.post("/matches/{match_id}/result", response_model=MatchSingleResponse)
async def set_match_result(match_id: int, request: MatchResult, db: Session = Depends(get_db)):
    """
    Set the final result for a completed match.
    
    CRITICAL ENDPOINT - Validates all cricket-specific constraints:
    - Winner must be one of the two teams
    - Margin must be positive
    - Margin ranges: runs (1-999), wickets (1-10)
    
    Auto-sets match status to 'completed' when result is saved.
    """
    try:
        logger.info(f"Setting result for match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Validate winner is one of the teams
        valid_winners = [match.team1.team_name, match.team2.team_name]
        if request.winner not in valid_winners:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid winner. Winner must be one of the teams: {', '.join(valid_winners)}"
            )
        
        # Get winner ID
        winner_team = db.query(Team).filter(Team.team_name == request.winner).first()
        if not winner_team:
            raise HTTPException(status_code=400, detail="Winner team not found")
        
        # Validate margin value
        if request.margin <= 0:
            raise HTTPException(status_code=400, detail="Margin must be greater than 0")
        
        # Validate margin based on type
        if request.margin_type == 'runs':
            if request.margin > 999:
                raise HTTPException(status_code=400, detail="Runs margin cannot exceed 999")
        elif request.margin_type == 'wickets':
            if request.margin > 10:
                raise HTTPException(status_code=400, detail="Wickets margin cannot exceed 10")
        
        # Update match with result
        match.winner_id = winner_team.id
        match.margin = request.margin
        match.margin_type = request.margin_type
        match.won_by_batting_first = request.won_by_batting_first
        match.status = 'completed'  # Auto-set to completed
        match.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Match {match_id} result saved successfully")
        
        return {
            "success": True,
            "message": "Match result saved successfully",
            "data": match_to_response(match)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error setting match result: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving match result")


@router.post("/export", response_model=ExportResponse)
async def export_schedule(db: Session = Depends(get_db)):
    """
    Export entire schedule as JSON.
    
    Returns all matches in order (by round_number, match_number).
    """
    try:
        logger.info("Exporting schedule")
        
        matches = db.query(Match).order_by(
            Match.round_number.asc(),
            Match.match_number.asc()
        ).all()
        
        matches_data = [match_to_response(m) for m in matches]
        
        logger.info(f"✅ Schedule exported ({len(matches)} matches)")
        
        return {
            "success": True,
            "data": matches_data
        }
    
    except Exception as e:
        logger.error(f"❌ Error exporting schedule: {str(e)}")
        raise HTTPException(status_code=500, detail="Error exporting schedule")
