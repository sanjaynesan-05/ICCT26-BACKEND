"""
Tests for input validation utilities
"""

import pytest
from io import BytesIO
from fastapi import UploadFile
from app.utils.validation import (
    validate_name,
    validate_team_name,
    validate_phone,
    validate_email,
    validate_file,
    validate_player_data,
    ValidationError
)


# ========== NAME VALIDATION ==========

def test_validate_name_valid():
    """Valid names should pass"""
    assert validate_name("John Doe", "Name") == "John Doe"
    assert validate_name("Mary-Jane O'Connor", "Name") == "Mary-Jane O'Connor"
    # Note: Unicode names may not pass ASCII-only validation


def test_validate_name_invalid():
    """Invalid names should raise ValidationError"""
    with pytest.raises(ValidationError) as exc:
        validate_name("AB", "Name")  # Too short
    assert "at least 3 characters" in exc.value.message
    
    with pytest.raises(ValidationError):
        validate_name("John123", "Name")  # Contains numbers
    
    with pytest.raises(ValidationError):
        validate_name("", "Name")  # Empty


# ========== TEAM NAME VALIDATION ==========

def test_validate_team_name_valid():
    """Valid team names should pass"""
    assert validate_team_name("Warriors") == "Warriors"
    assert validate_team_name("Team Alpha 2024") == "Team Alpha 2024"


def test_validate_team_name_invalid():
    """Invalid team names should raise ValidationError"""
    with pytest.raises(ValidationError) as exc:
        validate_team_name("AB")  # Too short
    assert "at least 3 characters" in exc.value.message
    
    with pytest.raises(ValidationError):
        validate_team_name("A" * 100)  # Too long


# ========== PHONE VALIDATION ==========

def test_validate_phone_valid():
    """Valid phone numbers should pass"""
    assert validate_phone("1234567890", "Phone") == "1234567890"
    assert validate_phone("9876543210", "Phone") == "9876543210"


def test_validate_phone_invalid():
    """Invalid phone numbers should raise ValidationError"""
    with pytest.raises(ValidationError) as exc:
        validate_phone("123456789", "Phone")  # Too short
    assert "exactly 10 digits" in exc.value.message
    
    with pytest.raises(ValidationError):
        validate_phone("12345678901", "Phone")  # Too long
    
    with pytest.raises(ValidationError):
        validate_phone("abcdefghij", "Phone")  # Non-numeric


# ========== EMAIL VALIDATION ==========

def test_validate_email_valid():
    """Valid emails should pass"""
    assert validate_email("test@example.com", "Email") == "test@example.com"
    assert validate_email("user.name+tag@domain.co.uk", "Email") == "user.name+tag@domain.co.uk"


def test_validate_email_invalid():
    """Invalid emails should raise ValidationError"""
    with pytest.raises(ValidationError) as exc:
        validate_email("invalid", "Email")
    assert "valid email" in exc.value.message
    
    with pytest.raises(ValidationError):
        validate_email("@example.com", "Email")
    
    with pytest.raises(ValidationError):
        validate_email("user@", "Email")


# ========== FILE VALIDATION ==========

@pytest.mark.asyncio
async def test_validate_file_valid():
    """Valid files should pass"""
    # PNG file
    png_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
    png_file = UploadFile(filename="test.png", file=BytesIO(png_data))
    filename, mime = await validate_file(png_file, "Test file")
    assert filename == "test.png"
    assert mime.startswith("image/")


@pytest.mark.asyncio
async def test_validate_file_too_large():
    """Files over 5MB should fail"""
    large_data = b'\x00' * (6 * 1024 * 1024)  # 6MB
    large_file = UploadFile(filename="large.png", file=BytesIO(large_data))
    
    with pytest.raises(ValidationError) as exc:
        await validate_file(large_file, "Large file")
    assert "exceeds maximum size" in exc.value.message or "exceed 5MB" in exc.value.message
    assert exc.value.error_code == "FILE_TOO_LARGE"


@pytest.mark.asyncio
async def test_validate_file_invalid_mime():
    """Files with invalid MIME types should fail"""
    # Create a text file
    text_data = b'This is a text file'
    text_file = UploadFile(filename="test.txt", file=BytesIO(text_data))
    
    with pytest.raises(ValidationError) as exc:
        await validate_file(text_file, "Text file")
    assert "Invalid file type" in exc.value.message or "PNG, JPEG, or PDF" in exc.value.message
    assert exc.value.error_code == "INVALID_MIME_TYPE"


# ========== PLAYER DATA VALIDATION ==========

def test_validate_player_data_valid():
    """Valid player data should pass"""
    player = {"name": "John Smith", "role": "Batsman"}
    validated = validate_player_data(player, 1)
    assert validated["name"] == "John Smith"
    assert validated["role"] == "Batsman"


def test_validate_player_data_invalid():
    """Invalid player data should raise ValidationError"""
    with pytest.raises(ValidationError):
        validate_player_data({}, 1)  # Missing fields
    
    with pytest.raises(ValidationError):
        validate_player_data({"name": "AB", "role": "Batsman"}, 1)  # Name too short
    
    # Empty role - should be allowed (defaults to empty or "Player")
    result = validate_player_data({"name": "John Smith", "role": ""}, 1)
    assert result["name"] == "John Smith"
