"""
Pydantic Schemas for Multipart File Upload Registration
=======================================================
Handles team registration with file uploads via multipart/form-data.
NO base64 - files are uploaded directly as UploadFile objects.
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

# ============================================================
# Captain/Vice-Captain Schema
# ============================================================

class CaptainCreateMultipart(BaseModel):
    """Captain information for multipart registration"""
    name: str = Field(..., min_length=1, max_length=150, description="Captain full name")
    phone: str = Field(..., min_length=7, max_length=20, description="Captain phone")
    whatsapp: str = Field(..., min_length=10, max_length=20, description="Captain whatsapp")
    email: EmailStr = Field(..., description="Captain email")

    @field_validator('phone', 'whatsapp')
    @classmethod
    def validate_phone_format(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith('+') or v.isdigit()):
            raise ValueError('Phone must be digits or start with +')
        return v


class ViceCaptainCreateMultipart(BaseModel):
    """Vice-captain information for multipart registration"""
    name: str = Field(..., min_length=1, max_length=150)
    phone: str = Field(..., min_length=7, max_length=20)
    whatsapp: str = Field(..., min_length=10, max_length=20)
    email: EmailStr

    @field_validator('phone', 'whatsapp')
    @classmethod
    def validate_phone_format(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith('+') or v.isdigit()):
            raise ValueError('Phone must be digits or start with +')
        return v


# ============================================================
# Player Schema (without files - files handled separately)
# ============================================================

class PlayerCreateMultipart(BaseModel):
    """Player information for multipart registration (files handled separately)"""
    name: str = Field(..., min_length=1, max_length=150, description="Player full name")
    role: Optional[str] = Field(None, max_length=50, description="Player role (optional, e.g., Batsman, Bowler)")
    dob: str = Field(..., description="Date of birth (YYYY-MM-DD)")
    
    @field_validator('dob')
    @classmethod
    def validate_dob(cls, v: str) -> str:
        try:
            # Validate date format
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('DOB must be in YYYY-MM-DD format')


# ============================================================
# Team Registration Schema (without files)
# ============================================================

class TeamRegistrationMultipart(BaseModel):
    """
    Team registration schema for multipart/form-data.
    Files are NOT included here - they're handled as separate UploadFile parameters.
    """
    church_name: str = Field(..., min_length=1, max_length=255, description="Church name")
    team_name: str = Field(..., min_length=1, max_length=100, description="Team name")
    captain: CaptainCreateMultipart = Field(..., description="Captain details")
    vice_captain: ViceCaptainCreateMultipart = Field(..., description="Vice-captain details")
    players: List[PlayerCreateMultipart] = Field(..., min_items=11, max_items=15, description="11-15 players")

    @field_validator('players')
    @classmethod
    def validate_player_count(cls, v: List[PlayerCreateMultipart]) -> List[PlayerCreateMultipart]:
        if not (11 <= len(v) <= 15):
            raise ValueError('Team must have between 11 and 15 players')
        return v


# ============================================================
# Response Schemas
# ============================================================

class TeamRegistrationResponseData(BaseModel):
    """Team data returned after successful registration with Cloudinary URLs"""
    team_name: str = Field(..., description="Team name")
    church_name: str = Field(..., description="Church name")
    pastor_letter: Optional[str] = Field(None, description="Cloudinary URL for pastor letter")
    payment_receipt: Optional[str] = Field(None, description="Cloudinary URL for payment receipt")
    group_photo: Optional[str] = Field(None, description="Cloudinary URL for group photo")


class TeamRegistrationResponse(BaseModel):
    """Response after successful team registration with URLs"""
    success: bool = Field(default=True)
    message: str = Field(..., description="Success message")
    team_id: str = Field(..., description="Generated team ID")
    player_count: int = Field(..., description="Number of players registered")
    captain_name: str = Field(..., description="Captain name")
    team_name: str = Field(..., description="Team name")
    data: TeamRegistrationResponseData = Field(..., description="Team data with Cloudinary URLs")


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
