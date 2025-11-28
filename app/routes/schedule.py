"""
Cricket Match Schedule Management Routes
Handles CRUD operations for match scheduling and result tracking
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from datetime import datetime, timezone

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
    ApiResponse,
    TossUpdateRequest,
    MatchTimingUpdateRequest,
    InningsScoresUpdateRequest,
    MatchScoreUrlUpdateRequest,
    MatchStartRequest,
    FirstInningsScoreRequest,
    SecondInningsScoreRequest,
    MatchFinishRequest
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


def match_to_response(match: Match, db: Session = None) -> dict:
    """Convert Match ORM object to response dict with team names - first innings only"""
    try:
        # Get team names
        team1_name = "Unknown"
        team2_name = "Unknown"
        
        if db:
            team1 = db.query(Team).filter(Team.id == match.team1_id).first()
            team2 = db.query(Team).filter(Team.id == match.team2_id).first()
            team1_name = team1.team_name if team1 else "Unknown"
            team2_name = team2.team_name if team2 else "Unknown"
        
        # Build basic match response (first innings scores only)
        response = {
            "id": match.id,
            "round": match.round,
            "round_number": match.round_number,
            "match_number": match.match_number,
            "team1": team1_name,
            "team2": team2_name,
            "status": match.status,
            "toss_winner": None,
            "toss_choice": match.toss_choice,
            "scheduled_start_time": match.scheduled_start_time,
            "actual_start_time": match.actual_start_time,
            "match_end_time": match.match_end_time,
            "team1_first_innings_score": match.team1_first_innings_score,
            "team2_first_innings_score": match.team2_first_innings_score,
            "match_score_url": match.match_score_url,
            "result": None,
            "created_at": match.created_at,
            "updated_at": match.updated_at
        }
        
        # Add toss winner name if available
        if match.toss_winner_id and db:
            toss_winner = db.query(Team).filter(Team.id == match.toss_winner_id).first()
            if toss_winner:
                response["toss_winner"] = toss_winner.team_name
        
        # Add result if match is done
        if match.status == 'done' and match.winner_id and db:
            winner_team = db.query(Team).filter(Team.id == match.winner_id).first()
            if winner_team:
                result = {
                    "winner": winner_team.team_name,
                    "margin": match.margin,
                    "margin_type": match.margin_type,
                    "won_by_batting_first": match.won_by_batting_first
                }
                response["result"] = result
        
        return response
    
    except Exception as e:
        logger.error(f"Error converting match to response: {str(e)}")
        # Return minimal response on error (first innings scores only)
        return {
            "id": match.id,
            "round": match.round,
            "round_number": match.round_number,
            "match_number": match.match_number,
            "team1": "Unknown",
            "team2": "Unknown",
            "status": match.status,
            "toss_winner": None,
            "toss_choice": match.toss_choice,
            "scheduled_start_time": match.scheduled_start_time,
            "actual_start_time": match.actual_start_time,
            "match_end_time": match.match_end_time,
            "team1_first_innings_score": match.team1_first_innings_score,
            "team2_first_innings_score": match.team2_first_innings_score,
            "result": None,
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
        
        matches_data = [match_to_response(m, db) for m in matches]
        
        logger.info(f"✅ Successfully fetched {len(matches)} matches")
        
        return {
            "success": True,
            "data": matches_data
        }
    
    except Exception as e:
        logger.error(f"❌ Error fetching matches: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching matches")


@router.get("/matches/{match_id}", response_model=MatchSingleResponse)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single match by ID.
    """
    try:
        logger.info(f"Fetching match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        logger.info(f"✅ Successfully fetched match {match_id}")
        
        match_data = match_to_response(match, db)
        match_response = MatchResponse.model_validate(match_data)
        
        return MatchSingleResponse(
            success=True,
            message="Match fetched successfully",
            data=match_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching match: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching match")


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
        
        logger.info(f"✅ Match created successfully: {new_match.id}")
        
        return {
            "success": True,
            "message": "Match created successfully",
            "data": match_to_response(new_match, db)
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
        
        # Prevent updating done matches
        if match.status == 'done':
            raise HTTPException(
                status_code=409,
                detail="Cannot update a match that is done"
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
        match.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Match {match_id} updated successfully")
        
        return {
            "success": True,
            "message": "Match updated successfully",
            "data": match_to_response(match, db)
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
        
        # Prevent deleting live or done matches
        if match.status in ['live', 'done']:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete a match that is live or done"
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
            'scheduled': ['live', 'done'],
            'live': ['done'],
            'done': []  # No transitions from done
        }
        
        if request.status not in valid_transitions.get(match.status, []):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition from '{match.status}' to '{request.status}'"
            )
        
        match.status = request.status
        match.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Match {match_id} status updated to {match.status}")
        
        return {
            "success": True,
            "message": f"Match status updated to {match.status}",
            "data": match_to_response(match, db)
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
        match.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Match {match_id} result saved successfully")
        
        return {
            "success": True,
            "message": "Match result saved successfully",
            "data": match_to_response(match, db)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error setting match result: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving match result")


@router.put("/matches/{match_id}/toss", response_model=MatchSingleResponse)
async def update_toss(match_id: int, request: TossUpdateRequest, db: Session = Depends(get_db)):
    """
    Update toss details for a match.
    
    - toss_winner: Team name that won the toss
    - toss_choice: 'bat' or 'bowl'
    """
    try:
        logger.info(f"Updating toss for match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Get the toss winner team
        toss_winner_team = get_team_by_name(db, request.toss_winner)
        
        # Toss winner must be one of the two teams
        if toss_winner_team.id not in [match.team1_id, match.team2_id]:
            raise HTTPException(
                status_code=400,
                detail="Toss winner must be one of the teams in this match"
            )
        
        match.toss_winner_id = toss_winner_team.id
        match.toss_choice = request.toss_choice.lower()
        match.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Toss updated for match {match_id}")
        
        return {
            "success": True,
            "message": "Toss details updated successfully",
            "data": match_to_response(match, db)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating toss: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating toss details")


@router.put("/matches/{match_id}/timing", response_model=MatchSingleResponse)
async def update_match_timing(match_id: int, request: MatchTimingUpdateRequest, db: Session = Depends(get_db)):
    """
    Update match timing details.
    
    - scheduled_start_time: When match is scheduled to start
    - actual_start_time: When match actually started
    - match_end_time: When match ended
    """
    try:
        logger.info(f"Updating timing for match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        if request.scheduled_start_time:
            match.scheduled_start_time = request.scheduled_start_time
        if request.actual_start_time:
            match.actual_start_time = request.actual_start_time
        if request.match_end_time:
            match.match_end_time = request.match_end_time
        
        match.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Timing updated for match {match_id}")
        
        return {
            "success": True,
            "message": "Match timing updated successfully",
            "data": match_to_response(match, db)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating timing: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating match timing")


@router.put("/matches/{match_id}/scores", response_model=MatchSingleResponse)
async def update_innings_scores(match_id: int, request: InningsScoresUpdateRequest, db: Session = Depends(get_db)):
    """
    Update first innings scores for both teams.
    
    - team1_first_innings_score: Team 1 first innings score
    - team2_first_innings_score: Team 2 first innings score
    """
    try:
        logger.info(f"Updating scores for match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        if request.team1_first_innings_score is not None:
            match.team1_first_innings_score = request.team1_first_innings_score
        if request.team2_first_innings_score is not None:
            match.team2_first_innings_score = request.team2_first_innings_score
        
        match.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Scores updated for match {match_id}")
        
        return {
            "success": True,
            "message": "Innings scores updated successfully",
            "data": match_to_response(match, db)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating scores: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating innings scores")


@router.put("/matches/{match_id}/score-url", response_model=MatchSingleResponse)
async def update_match_score_url(match_id: int, request: MatchScoreUrlUpdateRequest, db: Session = Depends(get_db)):
    """
    Update match score URL (link to external scorecard).
    
    - match_score_url: URL to match score/scorecard (must be HTTP or HTTPS)
    """
    try:
        logger.info(f"Updating match score URL for match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        match.match_score_url = request.match_score_url
        match.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Match score URL updated for match {match_id}")
        
        return {
            "success": True,
            "message": "Match score URL updated successfully",
            "data": match_to_response(match, db)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating match score URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating match score URL")


# ============================================================
# WORKFLOW ENDPOINTS (4-Stage Match Lifecycle)
# ============================================================

@router.put("/matches/{match_id}/start", response_model=MatchSingleResponse)
async def start_match(match_id: int, request: MatchStartRequest, db: Session = Depends(get_db)):
    """
    START MATCH (Stage 2 of 4-Stage Workflow)
    
    Starts a match and moves it from 'scheduled' to 'live' status.
    Sets toss details, scorecard URL, and actual start time.
    
    This is the second step in the match workflow:
    1. Create match (POST /matches) ← Stage 1
    2. **Start match (PUT /matches/{id}/start)** ← You are here (Stage 2)
    3. Update scores (PUT /matches/{id}/first-innings-score, then /second-innings-score) ← Stage 3
    4. Finish match (PUT /matches/{id}/finish) ← Stage 4
    
    Request body:
    - toss_winner: Team name that won the toss (must match team1 or team2)
    - toss_choice: 'bat' or 'bowl'
    - match_score_url: URL to external scorecard (HTTP/HTTPS)
    - actual_start_time: When match actually started
    
    Status transitions:
    - From: "scheduled"
    - To: "live"
    
    Returns: Full match object with all fields
    """
    try:
        logger.info(f"Starting match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Validate status is "scheduled"
        if match.status != "scheduled":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot start match: Status must be 'scheduled', but is '{match.status}'. "
                        f"Match already started or completed!"
            )
        
        # Get toss winner team
        toss_winner_team = get_team_by_name(db, request.toss_winner)
        
        # Validate toss_winner matches one of the teams
        if toss_winner_team.id not in [match.team1_id, match.team2_id]:
            raise HTTPException(
                status_code=400,
                detail=f"Toss winner '{request.toss_winner}' does not match either team"
            )
        
        # Update match with start details
        match.toss_winner_id = toss_winner_team.id
        match.toss_choice = request.toss_choice
        match.match_score_url = request.match_score_url
        match.actual_start_time = request.actual_start_time
        match.status = "live"
        match.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Match {match_id} started successfully. Status: live")
        
        return {
            "success": True,
            "message": "Match started successfully. First innings has begun!",
            "data": match_to_response(match, db)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error starting match: {str(e)}")
        raise HTTPException(status_code=500, detail="Error starting match")


@router.put("/matches/{match_id}/first-innings-score", response_model=MatchSingleResponse)
async def update_first_innings_score(match_id: int, request: FirstInningsScoreRequest, db: Session = Depends(get_db)):
    """
    UPDATE FIRST INNINGS SCORE (Stage 3A of 4-Stage Workflow)
    
    Records the score of the team that batted first.
    Moves match from 'live' to 'in-progress' if still in 'live' status.
    
    This is the third step in the match workflow:
    1. Create match (POST /matches) ← Stage 1
    2. Start match (PUT /matches/{id}/start) ← Stage 2
    3. **Update scores (PUT /matches/{id}/first-innings-score, then /second-innings-score)** ← You are here (Stage 3)
    4. Finish match (PUT /matches/{id}/finish) ← Stage 4
    
    Request body:
    - batting_team: Team name that batted first (must match team1 or team2)
    - score: Runs scored (1-999)
    
    Status transitions:
    - From: "live" or "in-progress"
    - To: "in-progress" (if was "live")
    
    Returns: Full match object with updated score
    """
    try:
        logger.info(f"Updating first innings score for match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Validate status is "live"
        if match.status != "live":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update first innings: Match status must be 'live', "
                        f"but is '{match.status}'"
            )
        
        # Get batting team
        batting_team = get_team_by_name(db, request.batting_team)
        
        # Validate team is one of the match teams
        if batting_team.id not in [match.team1_id, match.team2_id]:
            raise HTTPException(
                status_code=400,
                detail=f"Team '{request.batting_team}' is not part of this match"
            )
        
        # Update correct team's score
        if batting_team.id == match.team1_id:
            match.team1_first_innings_score = request.score
        else:
            match.team2_first_innings_score = request.score
        
        # Status remains "live" (no change)
        match.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ First innings score updated for match {match_id}")
        
        return {
            "success": True,
            "message": "First innings score recorded. Match in progress!",
            "data": match_to_response(match, db)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating first innings score: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating first innings score")


@router.put("/matches/{match_id}/second-innings-score", response_model=MatchSingleResponse)
async def update_second_innings_score(match_id: int, request: SecondInningsScoreRequest, db: Session = Depends(get_db)):
    """
    UPDATE SECOND INNINGS SCORE (Stage 3B of 4-Stage Workflow)
    
    Records the score of the team that batted second.
    Match remains in 'in-progress' status.
    
    This is part of the third step in the match workflow:
    1. Create match (POST /matches) ← Stage 1
    2. Start match (PUT /matches/{id}/start) ← Stage 2
    3. **Update scores (PUT /matches/{id}/first-innings-score, then /second-innings-score)** ← You are here (Stage 3)
    4. Finish match (PUT /matches/{id}/finish) ← Stage 4
    
    Request body:
    - batting_team: Team name that batted second (must match team1 or team2)
    - score: Runs scored (1-999)
    
    Status transitions:
    - From: "in-progress"
    - To: "in-progress" (no change)
    
    Returns: Full match object with updated score
    """
    try:
        logger.info(f"Updating second innings score for match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Validate status is "live"
        if match.status != "live":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update second innings: Match status must be 'live', "
                        f"but is '{match.status}'. Start the match first!"
            )
        
        # Validate first innings score exists
        if match.team1_first_innings_score is None and match.team2_first_innings_score is None:
            raise HTTPException(
                status_code=400,
                detail="Cannot update second innings: First innings score not recorded yet"
            )
        
        # Get batting team
        batting_team = get_team_by_name(db, request.batting_team)
        
        # Validate team is one of the match teams
        if batting_team.id not in [match.team1_id, match.team2_id]:
            raise HTTPException(
                status_code=400,
                detail=f"Team '{request.batting_team}' is not part of this match"
            )
        
        # Update correct team's score
        if batting_team.id == match.team1_id:
            match.team1_first_innings_score = request.score
        else:
            match.team2_first_innings_score = request.score
        
        match.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Second innings score updated for match {match_id}")
        
        return {
            "success": True,
            "message": "Second innings score recorded. Ready to finish match!",
            "data": match_to_response(match, db)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating second innings score: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating second innings score")


@router.put("/matches/{match_id}/finish", response_model=MatchSingleResponse)
async def finish_match(match_id: int, request: MatchFinishRequest, db: Session = Depends(get_db)):
    """
    FINISH MATCH (Stage 4 of 4-Stage Workflow)
    
    Completes a match and moves it from 'in-progress' to 'completed' status.
    Records winner, margin, and match end time.
    
    This is the final step in the match workflow:
    1. Create match (POST /matches) ← Stage 1
    2. Start match (PUT /matches/{id}/start) ← Stage 2
    3. Update scores (PUT /matches/{id}/first-innings-score, then /second-innings-score) ← Stage 3
    4. **Finish match (PUT /matches/{id}/finish)** ← You are here (Stage 4)
    
    Request body:
    - winner: Team name that won (must match team1 or team2)
    - margin: Margin of victory (1-999 for runs, 1-10 for wickets)
    - margin_type: Type of margin ('runs' or 'wickets')
    - match_end_time: When match ended
    
    Status transitions:
    - From: "in-progress"
    - To: "completed"
    
    Returns: Full match object with all results
    """
    try:
        logger.info(f"Finishing match {match_id}")
        
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Validate status is "live"
        if match.status != "live":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot finish match: Status must be 'live', but is '{match.status}'. "
                        f"Match must be started and scores recorded first!"
            )
        
        # Validate both innings scores exist
        if match.team1_first_innings_score is None or match.team2_first_innings_score is None:
            raise HTTPException(
                status_code=400,
                detail="Cannot finish match: Both innings scores must be recorded first"
            )
        
        # Get winner team
        winner_team = get_team_by_name(db, request.winner)
        
        # Validate winner matches one of the teams
        if winner_team.id not in [match.team1_id, match.team2_id]:
            raise HTTPException(
                status_code=400,
                detail=f"Winner '{request.winner}' does not match either team"
            )
        
        # Update match with result details
        match.winner_id = winner_team.id
        match.margin = request.margin
        match.margin_type = request.margin_type
        match.match_end_time = request.match_end_time
        match.status = "done"
        match.updated_at = datetime.now(timezone.utc)
        # Debug logging to ensure margin_type is received and set correctly
        logger.info(f"Finish request.margin_type={request.margin_type}")
        logger.info(f"Match object margin_type before commit={match.margin_type}")
        
        # Determine if batting first team won
        first_innings_batting_team = None
        if match.toss_choice == "bat":
            first_innings_batting_team = match.toss_winner_id
        else:
            # If toss winner chose to bowl, the other team batted first
            first_innings_batting_team = match.team2_id if match.toss_winner_id == match.team1_id else match.team1_id
        
        match.won_by_batting_first = (winner_team.id == first_innings_batting_team)
        
        db.commit()
        db.refresh(match)
        
        logger.info(f"✅ Match {match_id} finished successfully. Status: done")
        
        return {
            "success": True,
            "message": "Match completed successfully!",
            "data": match_to_response(match, db)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error finishing match: {str(e)}")
        raise HTTPException(status_code=500, detail="Error finishing match")


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
        
        matches_data = [match_to_response(m, db) for m in matches]
        
        logger.info(f"✅ Schedule exported ({len(matches)} matches)")
        
        return {
            "success": True,
            "data": matches_data
        }
    
    except Exception as e:
        logger.error(f"❌ Error exporting schedule: {str(e)}")
        raise HTTPException(status_code=500, detail="Error exporting schedule")
