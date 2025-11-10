"""
Pydantic schemas for team registration matching frontend JSON structure.
Accepts both camelCase (frontend) and snake_case (raw/postman) inputs via aliases.

File Validation:
- Images (pastorLetter, paymentReceipt): JPEG, PNG, GIF, WebP, JXL
- Documents (aadharFile, subscriptionFile): PDF only
- Size limit: 5MB per file (configurable)
- Base64 format required with data:mime/type; prefix
"""

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import base64
from app.config import settings

# Allowed MIME types for different file types
ALLOWED_IMAGE_MIMES = ["image/jpeg", "image/png", "image/gif", "image/webp", "image/jxl"]
ALLOWED_DOCUMENT_MIMES = ["application/pdf"]


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

    # File validation for images (pastor letter and payment receipt)
    @field_validator('pastorLetter', 'paymentReceipt')
    @classmethod
    def validate_image_file(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate image files (Base64 encoded with data URI format)
        
        Accepts formats:
        - data:image/jpeg;base64,<base64_data>
        - data:image/png;base64,<base64_data>
        - data:image/gif;base64,<base64_data>
        - data:image/webp;base64,<base64_data>
        - data:image/jxl;base64,<base64_data>
        
        Also accepts raw Base64 without data URI prefix for backward compatibility
        """
        if v is None:
            return v
        
        original_value = v
        
        # Extract Base64 data from data URI if present
        if v.startswith("data:"):
            try:
                header, b64_data = v.split(",", 1)
                mime_type = header.split(";")[0][5:]  # Extract mime type
                
                # Validate MIME type
                if mime_type not in ALLOWED_IMAGE_MIMES:
                    raise ValueError(
                        f"Image MIME type '{mime_type}' not allowed. "
                        f"Allowed types: {', '.join(ALLOWED_IMAGE_MIMES)}"
                    )
                
                v = b64_data
            except (IndexError, ValueError) as e:
                raise ValueError(f"Invalid data URI format: {str(e)}")
        
        # Check file size limit
        if len(v) > settings.MAX_BASE64_SIZE_CHARS:
            max_mb = settings.MAX_FILE_SIZE_MB
            raise ValueError(
                f"File too large. Size: {len(v)} chars. Maximum: {settings.MAX_BASE64_SIZE_CHARS} chars (~{max_mb}MB)"
            )
        
        # Validate Base64 format
        try:
            decoded_data = base64.b64decode(v, validate=True)
        except Exception as e:
            raise ValueError(f"Invalid Base64 data: {str(e)}")
        
        # Validate image file signature (magic bytes)
        if not cls._is_valid_image(decoded_data):
            raise ValueError(
                "File must be a valid image. "
                "Accepted formats: JPEG (.jpg), PNG (.png), GIF (.gif), WebP (.webp), JXL (.jxl)"
            )
        
        # Return original value (with or without data URI prefix)
        return original_value
    
    @staticmethod
    def _is_valid_image(data: bytes) -> bool:
        """Check if data is a valid image based on file signatures (magic bytes)"""
        signatures = [
            (b'\xff\xd8\xff', "JPEG"),
            (b'\x89PNG\r\n\x1a\n', "PNG"),
            (b'GIF8', "GIF"),
            (b'RIFF', "WebP"),  # WebP starts with RIFF
            (b'\x00\x00\x00\x0cJXL\x20', "JXL"),
        ]
        
        for sig, fmt in signatures:
            if data.startswith(sig):
                return True
        
        return False

    # File validation for PDF documents (aadhar and subscription files)
    @field_validator('players')
    @classmethod
    def validate_player_files(cls, v: List[PlayerInfo]) -> List[PlayerInfo]:
        """
        Validate PDF files in player data.
        
        Accepts:
        - data:application/pdf;base64,<base64_data>
        - Raw Base64 without data URI prefix for backward compatibility
        
        All PDFs must start with %PDF- header
        """
        for player in v:
            # Validate aadhar file
            if player.aadharFile:
                cls._validate_pdf_file(player.aadharFile, 'aadharFile')
            
            # Validate subscription file
            if player.subscriptionFile:
                cls._validate_pdf_file(player.subscriptionFile, 'subscriptionFile')
        
        return v
    
    @staticmethod
    def _validate_pdf_file(file_data: str, field_name: str) -> None:
        """Helper method to validate PDF files with data URI and raw Base64 support"""
        v = file_data
        
        # Extract Base64 data from data URI if present
        if v.startswith("data:"):
            try:
                header, b64_data = v.split(",", 1)
                mime_type = header.split(";")[0][5:]  # Extract mime type
                
                # Validate MIME type
                if mime_type not in ALLOWED_DOCUMENT_MIMES:
                    raise ValueError(
                        f"{field_name} MIME type '{mime_type}' not allowed. "
                        f"Allowed types: {', '.join(ALLOWED_DOCUMENT_MIMES)}"
                    )
                
                v = b64_data
            except (IndexError, ValueError) as e:
                raise ValueError(f"{field_name}: Invalid data URI format: {str(e)}")
        
        # Check file size limit
        if len(v) > settings.MAX_BASE64_SIZE_CHARS:
            max_mb = settings.MAX_FILE_SIZE_MB
            raise ValueError(
                f'{field_name} too large. Size: {len(v)} chars. '
                f'Maximum: {settings.MAX_BASE64_SIZE_CHARS} chars (~{max_mb}MB)'
            )
        
        # Validate Base64 format
        try:
            decoded_data = base64.b64decode(v, validate=True)
        except Exception as e:
            raise ValueError(f'{field_name}: Invalid Base64 data: {str(e)}')
        
        # Validate it's actually a PDF
        if not decoded_data.startswith(b'%PDF-'):
            raise ValueError(f'{field_name} must be a valid PDF document (must start with %PDF-)')


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
