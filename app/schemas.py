"""
Pydantic schemas for request/response validation
Contains all data models for API contracts
"""

from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.config import settings


# ============================================================
# Request Schemas
# ============================================================

class PlayerDetails(BaseModel):
    """Player information schema"""
    
    name: str = Field(
        ...,
        description="Player full name",
        min_length=1,
        max_length=settings.PLAYER_NAME_MAX_LENGTH
    )
    
    age: int = Field(
        ...,
        description="Player age",
        ge=settings.MIN_PLAYER_AGE,
        le=settings.MAX_PLAYER_AGE
    )
    
    phone: str = Field(
        ...,
        description="Player phone number in E.164 format (e.g., +919876543210)",
        min_length=settings.PHONE_MIN_LENGTH,
        max_length=settings.PHONE_MAX_LENGTH
    )
    
    role: str = Field(
        ...,
        description=f"Player role - one of {settings.VALID_PLAYER_ROLES}"
    )
    
    aadharFile: Optional[str] = Field(
        None,
        description="Aadhar file (base64 encoded image)"
    )
    
    subscriptionFile: Optional[str] = Field(
        None,
        description="Church subscription file (base64 encoded image)"
    )

    @validator('role')
    def validate_role(cls, v):
        """Validate player role"""
        if v not in settings.VALID_PLAYER_ROLES:
            raise ValueError(
                f'Role must be one of {settings.VALID_PLAYER_ROLES}'
            )
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Rajesh Kumar",
            "age": 25,
            "phone": "+919876543210",
            "role": "Batsman",
            "aadharFile": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
            "subscriptionFile": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
        }
    })


class CaptainInfo(BaseModel):
    """Captain information schema"""
    
    name: str = Field(
        ...,
        description="Captain full name",
        min_length=1,
        max_length=settings.PLAYER_NAME_MAX_LENGTH
    )
    
    phone: str = Field(
        ...,
        description="Captain phone number in E.164 format",
        min_length=settings.PHONE_MIN_LENGTH,
        max_length=settings.PHONE_MAX_LENGTH
    )
    
    whatsapp: str = Field(
        ...,
        description="Captain WhatsApp number (with or without +91)",
        min_length=settings.WHATSAPP_MIN_LENGTH,
        max_length=settings.WHATSAPP_MAX_LENGTH
    )
    
    email: EmailStr = Field(
        ...,
        description="Captain email address"
    )

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "John Doe",
            "phone": "+919876543210",
            "whatsapp": "919876543210",
            "email": "john@example.com"
        }
    })


class ViceCaptainInfo(BaseModel):
    """Vice-Captain information schema"""
    
    name: str = Field(
        ...,
        description="Vice-Captain full name",
        min_length=1,
        max_length=settings.PLAYER_NAME_MAX_LENGTH
    )
    
    phone: str = Field(
        ...,
        description="Vice-Captain phone number in E.164 format",
        min_length=settings.PHONE_MIN_LENGTH,
        max_length=settings.PHONE_MAX_LENGTH
    )
    
    whatsapp: str = Field(
        ...,
        description="Vice-Captain WhatsApp number (with or without +91)",
        min_length=settings.WHATSAPP_MIN_LENGTH,
        max_length=settings.WHATSAPP_MAX_LENGTH
    )
    
    email: EmailStr = Field(
        ...,
        description="Vice-Captain email address"
    )

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Jane Smith",
            "phone": "+919123456789",
            "whatsapp": "919123456789",
            "email": "jane@example.com"
        }
    })


class TeamRegistration(BaseModel):
    """Team registration schema - matches frontend payload exactly"""
    
    churchName: str = Field(
        ...,
        description="Church or organization name",
        min_length=1,
        max_length=settings.CHURCH_NAME_MAX_LENGTH
    )
    
    teamName: str = Field(
        ...,
        description="Team name (should be unique)",
        min_length=1,
        max_length=settings.TEAM_NAME_MAX_LENGTH
    )
    
    pastorLetter: Optional[str] = Field(
        None,
        description="Pastor's letter (base64 encoded image or PDF)"
    )
    
    captain: CaptainInfo = Field(
        ...,
        description="Team captain details"
    )
    
    viceCaptain: ViceCaptainInfo = Field(
        ...,
        description="Team vice-captain details"
    )
    
    players: List[PlayerDetails] = Field(
        ...,
        description=f"Player roster ({settings.MIN_PLAYERS}-{settings.MAX_PLAYERS} players)",
        min_items=settings.MIN_PLAYERS,
        max_items=settings.MAX_PLAYERS
    )
    
    paymentReceipt: Optional[str] = Field(
        None,
        description="Payment receipt (base64 encoded image or PDF)"
    )

    @validator('players')
    def validate_player_count(cls, v):
        """Validate player count"""
        if len(v) < settings.MIN_PLAYERS or len(v) > settings.MAX_PLAYERS:
            raise ValueError(
                f'Team must have {settings.MIN_PLAYERS}-{settings.MAX_PLAYERS} players'
            )
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "churchName": "CSI St. Peter's Church",
            "teamName": "Youth Fellowship Team",
            "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
            "captain": {
                "name": "John Doe",
                "phone": "+919876543210",
                "whatsapp": "919876543210",
                "email": "john@example.com"
            },
            "viceCaptain": {
                "name": "Jane Smith",
                "phone": "+919123456789",
                "whatsapp": "919123456789",
                "email": "jane@example.com"
            },
            "players": [
                {
                    "name": "Player One",
                    "age": 25,
                    "phone": "+919800000001",
                    "role": "Batsman"
                }
            ],
            "paymentReceipt": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
        }
    })


# ============================================================
# Response Schemas
# ============================================================

class RegistrationResponse(BaseModel):
    """Team registration response"""
    
    team_id: str = Field(..., description="Unique team identifier")
    team_name: str = Field(..., description="Team name")
    church_name: str = Field(..., description="Church name")
    captain_name: str = Field(..., description="Captain name")
    vice_captain_name: str = Field(..., description="Vice-captain name")
    players_count: int = Field(..., description="Number of players")
    registered_at: str = Field(..., description="Registration timestamp")
    email_sent: bool = Field(..., description="Whether confirmation email was sent")
    database_saved: bool = Field(..., description="Whether data was saved to database")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "team_id": "ICCT26-20251109093800",
            "team_name": "Youth Fellowship Team",
            "church_name": "CSI St. Peter's Church",
            "captain_name": "John Doe",
            "vice_captain_name": "Jane Smith",
            "players_count": 11,
            "registered_at": "2025-11-09T09:38:00.123456",
            "email_sent": True,
            "database_saved": True
        }
    })


class TeamListItem(BaseModel):
    """Team item in team list response"""
    
    teamId: str = Field(..., description="Team ID")
    teamName: str = Field(..., description="Team name")
    churchName: str = Field(..., description="Church name")
    captainName: str = Field(..., description="Captain name")
    captainPhone: str = Field(..., description="Captain phone")
    captainEmail: str = Field(..., description="Captain email")
    viceCaptainName: Optional[str] = Field(None, description="Vice-captain name")
    viceCaptainPhone: Optional[str] = Field(None, description="Vice-captain phone")
    viceCaptainEmail: Optional[str] = Field(None, description="Vice-captain email")
    playerCount: int = Field(..., description="Player count")
    registrationDate: Optional[str] = Field(None, description="Registration date")
    paymentReceipt: Optional[str] = Field(None, description="Payment receipt status")


class PlayerInfo(BaseModel):
    """Player information in responses"""
    
    playerId: int = Field(..., description="Player ID")
    name: str = Field(..., description="Player name")
    age: int = Field(..., description="Player age")
    phone: str = Field(..., description="Player phone")
    role: str = Field(..., description="Player role")


class TeamDetail(BaseModel):
    """Detailed team information"""
    
    teamId: str = Field(..., description="Team ID")
    teamName: str = Field(..., description="Team name")
    churchName: str = Field(..., description="Church name")
    captain: Optional[CaptainInfo] = Field(None, description="Captain info")
    viceCaptain: Optional[ViceCaptainInfo] = Field(None, description="Vice-captain info")
    paymentReceipt: Optional[str] = Field(None, description="Payment receipt")
    registrationDate: Optional[str] = Field(None, description="Registration date")


class SuccessResponse(BaseModel):
    """Generic success response"""
    
    success: bool = Field(..., description="Success flag")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")


class ErrorResponse(BaseModel):
    """Generic error response"""
    
    success: bool = Field(False, description="Success flag")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error detail")


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="Status")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Timestamp")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database status")
