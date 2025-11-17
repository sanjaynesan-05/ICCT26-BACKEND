"""
File Validation and Sanitization Utilities
==========================================
Comprehensive file validation for team registration uploads.
Validates file types, sizes, and sanitizes URLs.
"""

from fastapi import UploadFile, HTTPException
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# File type configurations
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/webp"
]

ALLOWED_PDF_TYPES = [
    "application/pdf"
]

ALLOWED_DOCUMENT_TYPES = ALLOWED_PDF_TYPES + ALLOWED_IMAGE_TYPES

# File size limits (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_PDF_SIZE = 15 * 1024 * 1024    # 15 MB
MAX_FILE_SIZE = 15 * 1024 * 1024   # 15 MB (general limit)


def validate_file_type(
    file: Optional[UploadFile],
    allowed_types: List[str],
    field_name: str
) -> bool:
    """
    Validate file MIME type.
    
    Args:
        file: UploadFile object to validate
        allowed_types: List of allowed MIME types
        field_name: Name of the field (for error messages)
    
    Returns:
        True if valid
    
    Raises:
        HTTPException: If validation fails
    """
    if not file or not file.filename:
        # Empty files are allowed (optional fields)
        return True
    
    content_type = file.content_type
    
    if not content_type:
        raise HTTPException(
            status_code=400,
            detail=f"Could not determine file type for {field_name}"
        )
    
    # Normalize content type (lowercase)
    content_type = content_type.lower()
    
    if content_type not in [t.lower() for t in allowed_types]:
        allowed_str = ", ".join(allowed_types)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type for {field_name}. Got '{content_type}'. Allowed types: {allowed_str}"
        )
    
    logger.info(f"✅ File type validation passed for {field_name}: {content_type}")
    return True


def validate_file_size(
    file: Optional[UploadFile],
    max_size: int,
    field_name: str
) -> bool:
    """
    Validate file size.
    
    Args:
        file: UploadFile object to validate
        max_size: Maximum allowed size in bytes
        field_name: Name of the field (for error messages)
    
    Returns:
        True if valid
    
    Raises:
        HTTPException: If validation fails
    """
    if not file or not file.filename:
        return True
    
    # Get file size
    file_size = file.size if hasattr(file, 'size') else None
    
    if file_size and file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File too large for {field_name}. Max: {max_mb:.1f}MB, Got: {actual_mb:.1f}MB"
        )
    
    logger.info(f"✅ File size validation passed for {field_name}")
    return True


def validate_image_file(file: Optional[UploadFile], field_name: str) -> bool:
    """
    Validate image file (JPEG, PNG, WebP).
    
    Args:
        file: UploadFile object
        field_name: Field name for error messages
    
    Returns:
        True if valid
    
    Raises:
        HTTPException: If validation fails
    """
    if not file or not file.filename:
        return True
    
    validate_file_type(file, ALLOWED_IMAGE_TYPES, field_name)
    validate_file_size(file, MAX_IMAGE_SIZE, field_name)
    return True


def validate_pdf_file(file: Optional[UploadFile], field_name: str) -> bool:
    """
    Validate PDF file.
    
    Args:
        file: UploadFile object
        field_name: Field name for error messages
    
    Returns:
        True if valid
    
    Raises:
        HTTPException: If validation fails
    """
    if not file or not file.filename:
        return True
    
    validate_file_type(file, ALLOWED_PDF_TYPES, field_name)
    validate_file_size(file, MAX_PDF_SIZE, field_name)
    return True


def validate_document_file(file: Optional[UploadFile], field_name: str) -> bool:
    """
    Validate document file (PDF or image).
    
    Args:
        file: UploadFile object
        field_name: Field name for error messages
    
    Returns:
        True if valid
    
    Raises:
        HTTPException: If validation fails
    """
    if not file or not file.filename:
        return True
    
    validate_file_type(file, ALLOWED_DOCUMENT_TYPES, field_name)
    validate_file_size(file, MAX_FILE_SIZE, field_name)
    return True


def validate_team_files(
    pastor_letter: Optional[UploadFile] = None,
    payment_receipt: Optional[UploadFile] = None,
    group_photo: Optional[UploadFile] = None
) -> bool:
    """
    Validate all team-level files.
    
    Args:
        pastor_letter: PDF file
        payment_receipt: Image or PDF file
        group_photo: Image file
    
    Returns:
        True if all valid
    
    Raises:
        HTTPException: If any validation fails
    """
    logger.info("Validating team files...")
    
    # Pastor letter (PDF only)
    validate_pdf_file(pastor_letter, "Pastor Letter")
    
    # Payment receipt (image or PDF)
    validate_document_file(payment_receipt, "Payment Receipt")
    
    # Group photo (image only)
    validate_image_file(group_photo, "Group Photo")
    
    logger.info("✅ All team files validated")
    return True


def validate_player_files(
    aadhar_files: List[UploadFile],
    subscription_files: List[UploadFile],
    expected_count: int
) -> bool:
    """
    Validate all player files.
    
    Args:
        aadhar_files: List of Aadhar card files (PDF or image)
        subscription_files: List of subscription files (PDF or image)
        expected_count: Expected number of players
    
    Returns:
        True if all valid
    
    Raises:
        HTTPException: If any validation fails
    """
    logger.info(f"Validating player files for {expected_count} players...")
    
    # Check counts
    if len(aadhar_files) != expected_count:
        raise HTTPException(
            status_code=400,
            detail=f"Aadhar file count mismatch. Expected {expected_count}, got {len(aadhar_files)}"
        )
    
    if len(subscription_files) != expected_count:
        raise HTTPException(
            status_code=400,
            detail=f"Subscription file count mismatch. Expected {expected_count}, got {len(subscription_files)}"
        )
    
    # Validate each player's files
    for idx, (aadhar, subscription) in enumerate(zip(aadhar_files, subscription_files), start=1):
        validate_document_file(aadhar, f"Player {idx} Aadhar Card")
        validate_document_file(subscription, f"Player {idx} Subscription Form")
    
    logger.info(f"✅ All player files validated for {expected_count} players")
    return True


def sanitize_url(url: Optional[str]) -> str:
    """
    Sanitize and validate URL string.
    
    Args:
        url: URL string to sanitize
    
    Returns:
        Clean URL or empty string
    """
    if not url:
        return ""
    
    url_str = str(url).strip()
    
    if not url_str:
        return ""
    
    # Only accept valid HTTP/HTTPS URLs
    if url_str.startswith("https://") or url_str.startswith("http://"):
        return url_str
    
    # Invalid URL format
    return ""


def sanitize_cloudinary_url(url: Optional[str]) -> str:
    """
    Sanitize and validate Cloudinary URL.
    
    Args:
        url: Cloudinary URL to sanitize
    
    Returns:
        Clean Cloudinary URL or empty string
    """
    if not url:
        return ""
    
    url_str = str(url).strip()
    
    if not url_str:
        return ""
    
    # Only accept Cloudinary URLs
    if url_str.startswith("https://res.cloudinary.com/"):
        return url_str
    
    # Convert HTTP to HTTPS
    if url_str.startswith("http://res.cloudinary.com/"):
        return url_str.replace("http://", "https://", 1)
    
    # Invalid Cloudinary URL
    logger.warning(f"Invalid Cloudinary URL format: {url_str[:50]}...")
    return ""


def validate_required_fields(data: dict, required_fields: List[str]) -> bool:
    """
    Validate required fields in data dictionary.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
    
    Returns:
        True if all required fields present
    
    Raises:
        HTTPException: If any required field is missing
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    return True


__all__ = [
    "validate_image_file",
    "validate_pdf_file",
    "validate_document_file",
    "validate_team_files",
    "validate_player_files",
    "sanitize_url",
    "sanitize_cloudinary_url",
    "validate_required_fields",
    "ALLOWED_IMAGE_TYPES",
    "ALLOWED_PDF_TYPES",
    "ALLOWED_DOCUMENT_TYPES",
    "MAX_IMAGE_SIZE",
    "MAX_PDF_SIZE",
    "MAX_FILE_SIZE"
]
