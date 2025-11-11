"""
Pydantic schemas for team registration matching frontend JSON structure.
Accepts both camelCase (frontend) and snake_case (raw/postman) inputs via aliases.

File Validation:
- All Files (pastorLetter, paymentReceipt, aadharFile, subscriptionFile): JPEG, PNG, PDF ONLY
- Size limit: 5MB per file (configurable)
- Base64 format required with data:mime/type; prefix
- Magic byte verification for file type validation
"""

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import base64
from app.config import settings

# Allowed MIME types - JPEG, PNG, and PDF ONLY for all file uploads
ALLOWED_FILE_MIMES = ["image/jpeg", "image/png", "application/pdf"]


# ============================================================
# Captain/Vice-Captain Schema
# ============================================================

class CaptainInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=150, description="Captain full name", alias="name")
    phone: str = Field(..., min_length=7, max_length=20, description="Captain phone (with or without +)", alias="phone")
    whatsapp: str = Field(..., min_length=10, max_length=20, description="Captain whatsapp (digits only or +91...)", alias="whatsapp")
    email: EmailStr = Field(..., description="Captain email", alias="email")

    # Accepts either + prefixed or plain digits (lenient)
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith('+') or v.isdigit()):
            raise ValueError('Phone must be digits or start with +')
        return v

    @field_validator('whatsapp')
    @classmethod
    def validate_whatsapp(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() and not v.startswith('+'):
            raise ValueError('WhatsApp must be digits or start with +')
        # allow either 10-digit local or +91... style
        return v


class ViceCaptainInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=150, alias="name")
    phone: str = Field(..., min_length=7, max_length=20, alias="phone")
    whatsapp: str = Field(..., min_length=10, max_length=20, alias="whatsapp")
    email: EmailStr = Field(..., alias="email")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith('+') or v.isdigit()):
            raise ValueError('Phone must be digits or start with +')
        return v

    @field_validator('whatsapp')
    @classmethod
    def validate_whatsapp(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() and not v.startswith('+'):
            raise ValueError('WhatsApp must be digits or start with +')
        return v


# ============================================================
# Player Schema
# ============================================================

class PlayerInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=150, alias="name")
    age: int = Field(..., ge=15, le=65, alias="age")
    phone: str = Field(..., min_length=7, max_length=20, alias="phone")
    role: str = Field(..., min_length=1, max_length=50, alias="role")

    # incoming keys: aadharFile (camelCase) OR aadhar_file (snake_case)
    aadharFile: Optional[str] = Field(None, description="Aadhar base64 or filename", alias="aadhar_file")
    subscriptionFile: Optional[str] = Field(None, description="Subscription base64 or filename", alias="subscription_file")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith('+') or v.isdigit()):
            raise ValueError('Phone must be digits or start with +')
        return v


# ============================================================
# Team Registration Request Schema
# ============================================================

class TeamRegistrationRequest(BaseModel):
    """
    Accepts either:
      - camelCase keys from frontend (churchName, teamName, pastorLetter, paymentReceipt)
      - OR snake_case keys from other clients (church_name, team_name, pastor_letter, payment_receipt)
    """
    model_config = ConfigDict(populate_by_name=True)

    churchName: str = Field(..., min_length=1, max_length=200, description="Church name", alias="church_name")
    teamName: str = Field(..., min_length=1, max_length=200, description="Team name", alias="team_name")

    pastorLetter: Optional[str] = Field(None, description="Pastor letter as base64 or filename", alias="pastor_letter")
    paymentReceipt: Optional[str] = Field(None, description="Payment receipt as base64 or filename", alias="payment_receipt")

    captain: CaptainInfo = Field(..., description="Captain information", alias="captain")
    viceCaptain: ViceCaptainInfo = Field(..., description="Vice-captain information", alias="viceCaptain")

    # Accept list length 1..15 (for testing keep 1 allowed). If you want enforce 11, change min_length to 11.
    players: List[PlayerInfo] = Field(..., min_length=1, max_length=15, description="List of players", alias="players")

    # File validation for all files (pastor letter, payment receipt, aadhar, subscription)
    @field_validator('pastorLetter', 'paymentReceipt')
    @classmethod
    def validate_team_files(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate files for team (Base64 encoded with data URI format)
        
        Accepts:
        - data:image/jpeg;base64,<base64_data>
        - data:image/png;base64,<base64_data>
        - data:application/pdf;base64,<base64_data>
        
        Also accepts raw Base64 without data URI prefix for backward compatibility
        """
        if v is None:
            return v
        
        return cls._validate_generic_file(v, 'Pastor Letter/Payment Receipt')
    
    @staticmethod
    def _validate_generic_file(file_data: str, field_name: str) -> str:
        """
        Generic file validation for JPEG, PNG, and PDF only
        Returns original value (with or without data URI prefix)
        """
        v = file_data
        original_value = v
        
        # Extract Base64 data from data URI if present
        if v.startswith("data:"):
            try:
                header, b64_data = v.split(",", 1)
                mime_type = header.split(";")[0][5:]  # Extract mime type
                
                # Validate MIME type
                if mime_type not in ALLOWED_FILE_MIMES:
                    raise ValueError(
                        f"{field_name} MIME type '{mime_type}' not allowed. "
                        f"Allowed types: JPEG, PNG, PDF only"
                    )
                
                v = b64_data
            except (IndexError, ValueError) as e:
                raise ValueError(f"{field_name}: Invalid data URI format: {str(e)}")
        
        # Check file size limit
        if len(v) > settings.MAX_BASE64_SIZE_CHARS:
            max_mb = settings.MAX_FILE_SIZE_MB
            raise ValueError(
                f"{field_name} too large. Size: {len(v)} chars. Maximum: {settings.MAX_BASE64_SIZE_CHARS} chars (~{max_mb}MB)"
            )
        
        # Validate Base64 format
        try:
            decoded_data = base64.b64decode(v, validate=True)
        except Exception as e:
            raise ValueError(f"{field_name}: Invalid Base64 data: {str(e)}")
        
        # Validate file signature (magic bytes) - JPEG, PNG, or PDF only
        if not TeamRegistrationRequest._is_valid_file_signature(decoded_data):
            raise ValueError(
                f"{field_name} must be JPEG (.jpg), PNG (.png), or PDF (.pdf) only. "
                "File signature does not match valid formats."
            )
        
        # Return original value (with or without data URI prefix)
        return original_value
    
    @staticmethod
    def _is_valid_file_signature(data: bytes) -> bool:
        """Check if data is JPEG, PNG, or PDF based on file signatures (magic bytes)"""
        signatures = [
            b'\xff\xd8\xff',  # JPEG
            b'\x89PNG\r\n\x1a\n',  # PNG
            b'%PDF-',  # PDF
        ]
        
        for sig in signatures:
            if data.startswith(sig):
                return True
        
        return False

    # File validation for PDF documents (aadhar and subscription files)
    @field_validator('players')
    @classmethod
    def validate_player_files(cls, v: List[PlayerInfo]) -> List[PlayerInfo]:
        """
        Validate files in player data (JPEG, PNG, or PDF only).
        
        Accepts:
        - data:image/jpeg;base64,<base64_data>
        - data:image/png;base64,<base64_data>
        - data:application/pdf;base64,<base64_data>
        - Raw Base64 without data URI prefix for backward compatibility
        """
        for player in v:
            # Validate aadhar file
            if player.aadharFile:
                TeamRegistrationRequest._validate_generic_file(player.aadharFile, 'aadharFile')
            
            # Validate subscription file
            if player.subscriptionFile:
                TeamRegistrationRequest._validate_generic_file(player.subscriptionFile, 'subscriptionFile')
        
        return v


# ============================================================
# Response Schemas
# ============================================================

class PlayerResponse(BaseModel):
    player_id: str
    name: str
    age: int
    phone: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class TeamRegistrationResponse(BaseModel):
    success: bool = True
    message: str
    team_id: str
    team_name: str
    church_name: str
    captain_name: str
    vice_captain_name: str
    player_count: int
    registration_date: datetime

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None
