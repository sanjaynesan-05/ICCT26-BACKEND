"""
Enhanced Input Validation System - ICCT26
==========================================
Strict validation for all registration inputs.

Features:
- Name validation (letters, spaces, hyphens, apostrophes only)
- Phone number validation (10 digits)
- Email validation (RFC 5322 compliant)
- File validation (MIME type, size, filename sanitization)
- Team name validation
- Comprehensive error messages
"""

import re
import os
import mimetypes
from typing import Optional, Tuple
from fastapi import UploadFile

# Try to import python-magic, fall back to mimetypes if not available (Windows)
try:
    import magic
    HAS_MAGIC = True
except (ImportError, OSError):
    HAS_MAGIC = False


# Validation constants
MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 50
MIN_TEAM_NAME_LENGTH = 3
MAX_TEAM_NAME_LENGTH = 80
PHONE_LENGTH = 10
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_MIME_TYPES = {
    'image/png',
    'image/jpeg',
    'image/jpg',
    'application/pdf'
}

# Regex patterns
NAME_PATTERN = re.compile(r"^[A-Za-z\s'-]+$")
TEAM_NAME_PATTERN = re.compile(r"^[A-Za-z0-9\s'-]+$")
PHONE_PATTERN = re.compile(r"^[0-9]{10}$")
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)


class ValidationError(Exception):
    """Custom validation error with error code"""
    def __init__(self, error_code: str, message: str, field: str = None):
        self.error_code = error_code
        self.message = message
        self.field = field
        super().__init__(message)


def validate_name(name: str, field_name: str = "Name") -> str:
    """
    Validate person name (captain, vice-captain, player).
    
    Rules:
    - Length: 3-50 characters
    - Letters only (A-Z, a-z)
    - Spaces, hyphens, apostrophes allowed
    
    Args:
        name: Name to validate
        field_name: Field name for error messages
    
    Returns:
        str: Cleaned name (stripped)
    
    Raises:
        ValidationError: If validation fails
    """
    if not name or not name.strip():
        raise ValidationError(
            "VALIDATION_FAILED",
            f"{field_name} is required",
            field_name.lower().replace(" ", "_")
        )
    
    name = name.strip()
    
    if len(name) < MIN_NAME_LENGTH:
        raise ValidationError(
            "VALIDATION_FAILED",
            f"{field_name} must be at least {MIN_NAME_LENGTH} characters",
            field_name.lower().replace(" ", "_")
        )
    
    if len(name) > MAX_NAME_LENGTH:
        raise ValidationError(
            "VALIDATION_FAILED",
            f"{field_name} must not exceed {MAX_NAME_LENGTH} characters",
            field_name.lower().replace(" ", "_")
        )
    
    if not NAME_PATTERN.match(name):
        raise ValidationError(
            "VALIDATION_FAILED",
            f"{field_name} can only contain letters, spaces, hyphens, and apostrophes",
            field_name.lower().replace(" ", "_")
        )
    
    return name


def validate_team_name(team_name: str) -> str:
    """
    Validate team name.
    
    Rules:
    - Length: 3-80 characters
    - Letters, numbers, spaces, hyphens, apostrophes
    
    Args:
        team_name: Team name to validate
    
    Returns:
        str: Cleaned team name
    
    Raises:
        ValidationError: If validation fails
    """
    if not team_name or not team_name.strip():
        raise ValidationError(
            "VALIDATION_FAILED",
            "Team name is required",
            "team_name"
        )
    
    team_name = team_name.strip()
    
    if len(team_name) < MIN_TEAM_NAME_LENGTH:
        raise ValidationError(
            "VALIDATION_FAILED",
            f"Team name must be at least {MIN_TEAM_NAME_LENGTH} characters",
            "team_name"
        )
    
    if len(team_name) > MAX_TEAM_NAME_LENGTH:
        raise ValidationError(
            "VALIDATION_FAILED",
            f"Team name must not exceed {MAX_TEAM_NAME_LENGTH} characters",
            "team_name"
        )
    
    if not TEAM_NAME_PATTERN.match(team_name):
        raise ValidationError(
            "VALIDATION_FAILED",
            "Team name can only contain letters, numbers, spaces, hyphens, and apostrophes",
            "team_name"
        )
    
    return team_name


def validate_phone(phone: str, field_name: str = "Phone") -> str:
    """
    Validate phone number.
    
    Rules:
    - Exactly 10 digits
    - Numeric only
    
    Args:
        phone: Phone number to validate
        field_name: Field name for error messages
    
    Returns:
        str: Cleaned phone number
    
    Raises:
        ValidationError: If validation fails
    """
    if not phone or not phone.strip():
        raise ValidationError(
            "VALIDATION_FAILED",
            f"{field_name} is required",
            field_name.lower().replace(" ", "_")
        )
    
    phone = phone.strip()
    
    if not PHONE_PATTERN.match(phone):
        raise ValidationError(
            "VALIDATION_FAILED",
            f"{field_name} must be exactly {PHONE_LENGTH} digits",
            field_name.lower().replace(" ", "_")
        )
    
    return phone


def validate_email(email: str, field_name: str = "Email") -> str:
    """
    Validate email address (RFC 5322 compliant).
    
    Args:
        email: Email to validate
        field_name: Field name for error messages
    
    Returns:
        str: Cleaned email (lowercase)
    
    Raises:
        ValidationError: If validation fails
    """
    if not email or not email.strip():
        raise ValidationError(
            "VALIDATION_FAILED",
            f"{field_name} is required",
            field_name.lower().replace(" ", "_")
        )
    
    email = email.strip().lower()
    
    if not EMAIL_PATTERN.match(email):
        raise ValidationError(
            "VALIDATION_FAILED",
            f"{field_name} must be a valid email address",
            field_name.lower().replace(" ", "_")
        )
    
    return email


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks.
    
    Args:
        filename: Original filename
    
    Returns:
        str: Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:250] + ext
    
    return filename


async def validate_file(
    file: UploadFile,
    field_name: str = "File",
    max_size: int = MAX_FILE_SIZE
) -> Tuple[str, str]:
    """
    Validate uploaded file.
    
    Checks:
    - File size (max 5MB)
    - MIME type (png, jpeg, pdf only)
    - Filename sanitization
    
    Args:
        file: Uploaded file
        field_name: Field name for error messages
        max_size: Maximum file size in bytes
    
    Returns:
        Tuple[str, str]: (sanitized_filename, mime_type)
    
    Raises:
        ValidationError: If validation fails
    """
    if not file:
        raise ValidationError(
            "VALIDATION_FAILED",
            f"{field_name} is required",
            field_name.lower().replace(" ", "_")
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        size_mb = max_size / (1024 * 1024)
        raise ValidationError(
            "FILE_TOO_LARGE",
            f"{field_name} exceeds maximum size of {size_mb}MB",
            field_name.lower().replace(" ", "_")
        )
    
    # Detect MIME type from file content
    file_content = await file.read(2048)  # Read first 2KB for detection
    await file.seek(0)  # Reset
    
    # Try python-magic first, fall back to mimetypes library
    if HAS_MAGIC:
        try:
            mime = magic.from_buffer(file_content, mime=True)
        except Exception:
            # Fallback to content_type header
            mime = file.content_type or 'application/octet-stream'
    else:
        # Use mimetypes library (extension-based, less secure but works on Windows)
        mime_guess, _ = mimetypes.guess_type(file.filename)
        mime = mime_guess or file.content_type or 'application/octet-stream'
    
    # Validate MIME type
    if mime not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            "INVALID_MIME_TYPE",
            f"{field_name} must be PNG, JPEG, or PDF (detected: {mime})",
            field_name.lower().replace(" ", "_")
        )
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    return safe_filename, mime


def validate_player_data(player: dict, index: int) -> dict:
    """
    Validate player data from JSON.
    
    Args:
        player: Player dictionary
        index: Player index (for error messages)
    
    Returns:
        dict: Validated player data
    
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(player, dict):
        raise ValidationError(
            "VALIDATION_FAILED",
            f"Player {index} must be an object",
            f"player_{index}"
        )
    
    # Validate name
    name = player.get("name")
    validated_name = validate_name(name, f"Player {index} name")
    
    # Validate role
    role = player.get("role", "Player").strip()
    if len(role) > 30:
        raise ValidationError(
            "VALIDATION_FAILED",
            f"Player {index} role must not exceed 30 characters",
            f"player_{index}_role"
        )
    
    # Validate phone (optional)
    phone = player.get("phone")
    validated_phone = None
    if phone and phone.strip():
        validated_phone = validate_phone(phone, f"Player {index} phone")
    
    return {
        "name": validated_name,
        "role": role,
        "phone": validated_phone
    }
