"""
Pydantic schemas for team registration matching frontend JSON structure.
Complete request/response validation models.
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ============================================================
# Captain/Vice-Captain Schema
# ============================================================

class CaptainInfo(BaseModel):
    """Captain information schema - matches frontend JSON"""
    
    name: str = Field(
        ...,
        description="Captain full name",
        min_length=1,
        max_length=100
    )
    
    phone: str = Field(
        ...,
        description="Captain phone number (e.g., +919876543210)",
        min_length=10,
        max_length=15
    )
    
    whatsapp: str = Field(
        ...,
        description="Captain WhatsApp number (digits only, e.g., 9876543210)",
        min_length=10,
        max_length=10
    )
    
    email: EmailStr = Field(
        ...,
        description="Captain email address"
    )
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Ensure phone is in international format"""
        if not v.startswith('+'):
            raise ValueError('Phone must start with +')
        return v


class ViceCaptainInfo(BaseModel):
    """Vice-captain information schema - matches frontend JSON"""
    
    name: str = Field(
        ...,
        description="Vice-captain full name",
        min_length=1,
        max_length=100
    )
    
    phone: str = Field(
        ...,
        description="Vice-captain phone number (e.g., +919123456789)",
        min_length=10,
        max_length=15
    )
    
    whatsapp: str = Field(
        ...,
        description="Vice-captain WhatsApp number (digits only)",
        min_length=10,
        max_length=10
    )
    
    email: EmailStr = Field(
        ...,
        description="Vice-captain email address"
    )


# ============================================================
# Player Schema
# ============================================================

class PlayerInfo(BaseModel):
    """Player information schema - matches frontend JSON"""
    
    name: str = Field(
        ...,
        description="Player full name",
        min_length=1,
        max_length=100
    )
    
    age: int = Field(
        ...,
        description="Player age",
        ge=15,
        le=65
    )
    
    phone: str = Field(
        ...,
        description="Player phone number (e.g., +919800000001)",
        min_length=10,
        max_length=15
    )
    
    role: str = Field(
        ...,
        description="Player role (Batsman, Bowler, All-rounder, Wicket-keeper)",
        min_length=1,
        max_length=50
    )
    
    aadharFile: Optional[str] = Field(
        None,
        description="Aadhar file as base64-encoded image (data:image/jpeg;base64,...)"
    )
    
    subscriptionFile: Optional[str] = Field(
        None,
        description="Subscription file as base64-encoded image"
    )
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Ensure phone is in international format"""
        if not v.startswith('+'):
            raise ValueError('Phone must start with +')
        return v


# ============================================================
# Team Registration Request Schema
# ============================================================

class TeamRegistrationRequest(BaseModel):
    """Complete team registration schema - matches frontend JSON exactly"""
    
    churchName: str = Field(
        ...,
        description="Church name",
        min_length=1,
        max_length=200
    )
    
    teamName: str = Field(
        ...,
        description="Team name",
        min_length=1,
        max_length=100
    )
    
    pastorLetter: Optional[str] = Field(
        None,
        description="Pastor letter as base64-encoded image"
    )
    
    paymentReceipt: Optional[str] = Field(
        None,
        description="Payment receipt as base64-encoded image"
    )
    
    captain: CaptainInfo = Field(
        ...,
        description="Captain information"
    )
    
    viceCaptain: ViceCaptainInfo = Field(
        ...,
        description="Vice-captain information"
    )
    
    players: List[PlayerInfo] = Field(
        ...,
        description="List of team players (minimum 1)",
        min_length=1,
        max_length=15
    )
    
    class Config:
        schema_extra = {
            "example": {
                "churchName": "CSI St. Peter's Church",
                "teamName": "Youth Fellowship Team",
                "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA...",
                "paymentReceipt": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA...",
                "captain": {
                    "name": "John Doe",
                    "phone": "+919876543210",
                    "whatsapp": "9876543210",
                    "email": "john@example.com"
                },
                "viceCaptain": {
                    "name": "Jane Smith",
                    "phone": "+919123456789",
                    "whatsapp": "9123456789",
                    "email": "jane@example.com"
                },
                "players": [
                    {
                        "name": "Player One",
                        "age": 25,
                        "phone": "+919800000001",
                        "role": "Batsman",
                        "aadharFile": "data:image/jpeg;base64,...",
                        "subscriptionFile": "data:image/jpeg;base64,..."
                    }
                ]
            }
        }


# ============================================================
# Team Registration Response Schema
# ============================================================

class PlayerResponse(BaseModel):
    """Player response model"""
    
    player_id: str
    name: str
    age: int
    phone: str
    role: str
    
    class Config:
        from_attributes = True


class TeamRegistrationResponse(BaseModel):
    """Success response after team registration"""
    
    success: bool = True
    message: str
    team_id: str
    team_name: str
    church_name: str
    captain_name: str
    vice_captain_name: str
    player_count: int
    registration_date: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Team registered successfully!",
                "team_id": "TEAM-2025-001",
                "team_name": "Youth Fellowship Team",
                "church_name": "CSI St. Peter's Church",
                "captain_name": "John Doe",
                "vice_captain_name": "Jane Smith",
                "player_count": 11,
                "registration_date": "2025-01-15T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    
    success: bool = False
    error: str
    details: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid request data",
                "details": "Players list must have at least 1 player"
            }
        }
