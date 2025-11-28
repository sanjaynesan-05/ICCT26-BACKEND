"""
Pydantic schemas for cricket schedule and match management
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime


# ============================================================
# Toss Details Schema
# ============================================================

class TossDetails(BaseModel):
    """Toss information for a match"""
    toss_winner: str = Field(..., description="Team name that won the toss")
    toss_choice: str = Field(..., description="'bat' or 'bowl'")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "toss_winner": "Mumbai Kings",
                "toss_choice": "bat"
            }
        }
    )
    
    @validator('toss_choice')
    def validate_toss_choice(cls, v):
        if v.lower() not in ['bat', 'bowl']:
            raise ValueError("toss_choice must be 'bat' or 'bowl'")
        return v.lower()


# ============================================================
# Match Timing Schema
# ============================================================

class MatchTiming(BaseModel):
    """Match timing information"""
    scheduled_start_time: Optional[datetime] = Field(None, description="Scheduled match start time")
    actual_start_time: Optional[datetime] = Field(None, description="Actual match start time")
    match_end_time: Optional[datetime] = Field(None, description="Match end time")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "scheduled_start_time": "2025-11-27T10:00:00",
                "actual_start_time": "2025-11-27T10:15:00",
                "match_end_time": "2025-11-27T13:45:00"
            }
        }
    )


# ============================================================
# Innings Scores Schema
# ============================================================

class InningsScores(BaseModel):
    """Innings scores for both teams"""
    team1_first_innings_score: Optional[int] = Field(None, gt=0, description="Team 1 first innings score")
    team2_first_innings_score: Optional[int] = Field(None, gt=0, description="Team 2 first innings score")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "team1_first_innings_score": 165,
                "team2_first_innings_score": 152
            }
        }
    )


# ============================================================
# Match Result Schema
# ============================================================

class MatchResult(BaseModel):
    """Result information for a completed match"""
    winner: str = Field(..., description="Winning team name")
    margin: int = Field(..., gt=0, description="Margin of victory")
    margin_type: str = Field(..., description="'runs' or 'wickets'", alias="marginType")
    won_by_batting_first: bool = Field(..., description="True if batting first team won", alias="wonByBattingFirst")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "winner": "Mumbai Kings",
                "margin": 45,
                "margin_type": "runs",
                "won_by_batting_first": True
            }
        }
    )
    
    @validator('margin_type')
    def validate_margin_type(cls, v):
        if v not in ['runs', 'wickets']:
            raise ValueError("margin_type must be 'runs' or 'wickets'")
        return v
    
    @validator('margin')
    def validate_margin(cls, v, values):
        if 'margin_type' in values:
            if values['margin_type'] == 'runs' and v > 999:
                raise ValueError("Runs margin cannot exceed 999")
            elif values['margin_type'] == 'wickets' and v > 10:
                raise ValueError("Wickets margin cannot exceed 10")
        return v


# ============================================================
# Match Request Schemas
# ============================================================

class MatchCreateRequest(BaseModel):
    """Request body for creating a new match"""
    round: str = Field(..., min_length=1, description="Round name (e.g., 'Round 1')")
    round_number: int = Field(..., gt=0, description="Round number (numeric)")
    match_number: int = Field(..., gt=0, description="Match number within round")
    team1: str = Field(..., min_length=1, description="Team 1 name")
    team2: str = Field(..., min_length=1, description="Team 2 name")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "round": "Round 1",
                "round_number": 1,
                "match_number": 1,
                "team1": "Mumbai Kings",
                "team2": "Delhi Warriors"
            }
        }
    )
    
    @validator('team1', 'team2')
    def validate_team_names(cls, v):
        if v.strip() == "":
            raise ValueError("Team name cannot be empty")
        return v.strip()


class MatchUpdateRequest(BaseModel):
    """Request body for updating match details"""
    round: str = Field(..., min_length=1, description="Round name")
    round_number: int = Field(..., gt=0, description="Round number")
    match_number: int = Field(..., gt=0, description="Match number within round")
    team1: str = Field(..., min_length=1, description="Team 1 name")
    team2: str = Field(..., min_length=1, description="Team 2 name")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "round": "Round 1",
                "round_number": 1,
                "match_number": 1,
                "team1": "Mumbai Kings",
                "team2": "Delhi Warriors"
            }
        }
    )


class MatchStatusUpdate(BaseModel):
    """Request body for updating match status"""
    status: str = Field(..., description="Match status: 'scheduled', 'live', or 'completed'")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "live"
            }
        }
    )
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['scheduled', 'live', 'completed']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class TossUpdateRequest(BaseModel):
    """Request body for updating toss details"""
    toss_winner: str = Field(..., min_length=1, description="Team that won the toss")
    toss_choice: str = Field(..., description="'bat' or 'bowl'")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "toss_winner": "Mumbai Kings",
                "toss_choice": "bat"
            }
        }
    )
    
    @validator('toss_choice')
    def validate_toss_choice(cls, v):
        if v.lower() not in ['bat', 'bowl']:
            raise ValueError("toss_choice must be 'bat' or 'bowl'")
        return v.lower()


class MatchTimingUpdateRequest(BaseModel):
    """Request body for updating match timing"""
    scheduled_start_time: Optional[datetime] = Field(None, description="Scheduled match start time")
    actual_start_time: Optional[datetime] = Field(None, description="Actual match start time")
    match_end_time: Optional[datetime] = Field(None, description="Match end time")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scheduled_start_time": "2025-11-27T10:00:00",
                "actual_start_time": "2025-11-27T10:15:00",
                "match_end_time": "2025-11-27T13:45:00"
            }
        }
    )


class InningsScoresUpdateRequest(BaseModel):
    """Request body for updating innings scores"""
    team1_first_innings_score: Optional[int] = Field(None, gt=0, description="Team 1 first innings score")
    team2_first_innings_score: Optional[int] = Field(None, gt=0, description="Team 2 first innings score")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team1_first_innings_score": 165,
                "team2_first_innings_score": 152
            }
        }
    )


class MatchScoreUrlUpdateRequest(BaseModel):
    """Request body for updating match score URL"""
    match_score_url: str = Field(..., min_length=1, description="URL to match score/scorecard")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "match_score_url": "https://example.com/matches/123/scorecard"
            }
        }
    )
    
    @validator('match_score_url')
    def validate_url(cls, v):
        if not v.strip().startswith(('http://', 'https://')):
            raise ValueError("match_score_url must be a valid HTTP or HTTPS URL")
        return v.strip()


# ============================================================
# Match Response Schemas
# ============================================================

class MatchResponse(BaseModel):
    """Complete match information response"""
    id: int
    round: str
    round_number: int
    match_number: int
    team1: str
    team2: str
    status: str
    
    # Toss details
    toss_winner: Optional[str] = None
    toss_choice: Optional[str] = None
    
    # Match timing
    scheduled_start_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    match_end_time: Optional[datetime] = None
    
    # Innings scores (first innings only)
    team1_first_innings_score: Optional[int] = None
    team2_first_innings_score: Optional[int] = None
    
    # Match score URL
    match_score_url: Optional[str] = None
    
    # Result
    result: Optional[MatchResult] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "round": "Round 1",
                "round_number": 1,
                "match_number": 1,
                "team1": "Mumbai Kings",
                "team2": "Delhi Warriors",
                "status": "completed",
                "toss_winner": "Mumbai Kings",
                "toss_choice": "bat",
                "scheduled_start_time": "2025-11-27T10:00:00",
                "actual_start_time": "2025-11-27T10:15:00",
                "match_end_time": "2025-11-27T13:45:00",
                "team1_first_innings_score": 165,
                "team2_first_innings_score": 152,
                "result": {
                    "winner": "Mumbai Kings",
                    "margin": 45,
                    "margin_type": "runs",
                    "won_by_batting_first": True
                },
                "created_at": "2025-11-27T10:00:00",
                "updated_at": "2025-11-27T12:00:00"
            }
        }
    )


# ============================================================
# API Response Schemas
# ============================================================

class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None


class MatchesListResponse(BaseModel):
    """Response for fetching multiple matches"""
    success: bool
    data: List[MatchResponse]


class MatchSingleResponse(BaseModel):
    """Response for single match operations"""
    success: bool
    message: str
    data: MatchResponse


class ExportResponse(BaseModel):
    """Response for schedule export"""
    success: bool
    data: List[MatchResponse]
