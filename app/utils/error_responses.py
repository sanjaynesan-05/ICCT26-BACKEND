"""
Unified Error Response System - ICCT26
=======================================
Consistent error format across all endpoints.

Features:
- Standard error structure
- Error codes for client handling
- Detailed error information
- Logging integration
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# Error code constants
class ErrorCode:
    """Standard error codes"""
    VALIDATION_FAILED = "VALIDATION_FAILED"
    DUPLICATE_SUBMISSION = "DUPLICATE_SUBMISSION"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_MIME_TYPE = "INVALID_MIME_TYPE"
    DB_WRITE_FAILED = "DB_WRITE_FAILED"
    CLOUDINARY_UPLOAD_FAILED = "CLOUDINARY_UPLOAD_FAILED"
    EMAIL_FAILED = "EMAIL_FAILED"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_FOUND = "NOT_FOUND"
    TEAM_ID_GENERATION_FAILED = "TEAM_ID_GENERATION_FAILED"


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> JSONResponse:
    """
    Create standardized error response.
    
    Args:
        error_code: Error code constant
        message: Human-readable error message
        details: Additional error details
        status_code: HTTP status code
    
    Returns:
        JSONResponse: Formatted error response
    """
    response_data = {
        "success": False,
        "error_code": error_code,
        "message": message
    }
    
    if details:
        response_data["details"] = details
    
    logger.error(f"Error response: {error_code} - {message}")
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


def create_validation_error(
    field: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create validation error response.
    
    Args:
        field: Field that failed validation
        message: Validation error message
        details: Additional details
    
    Returns:
        JSONResponse: Validation error
    """
    error_details = {"field": field}
    if details:
        error_details.update(details)
    
    return create_error_response(
        ErrorCode.VALIDATION_FAILED,
        message,
        error_details,
        400
    )


def create_duplicate_error(
    field: str,
    value: str
) -> JSONResponse:
    """
    Create duplicate submission error.
    
    Args:
        field: Duplicate field
        value: Duplicate value
    
    Returns:
        JSONResponse: Duplicate error
    """
    return create_error_response(
        ErrorCode.DUPLICATE_SUBMISSION,
        f"A team with this {field} already exists",
        {"field": field, "value": value},
        409
    )


def create_file_error(
    field: str,
    reason: str,
    max_size: Optional[int] = None
) -> JSONResponse:
    """
    Create file validation error.
    
    Args:
        field: File field name
        reason: Error reason
        max_size: Maximum allowed size
    
    Returns:
        JSONResponse: File error
    """
    details = {"field": field}
    if max_size:
        details["max_size_mb"] = max_size / (1024 * 1024)
    
    error_code = ErrorCode.FILE_TOO_LARGE if max_size else ErrorCode.INVALID_MIME_TYPE
    
    return create_error_response(
        error_code,
        reason,
        details,
        400
    )


def create_database_error(
    operation: str,
    details: Optional[str] = None
) -> JSONResponse:
    """
    Create database error response.
    
    Args:
        operation: Database operation that failed
        details: Error details
    
    Returns:
        JSONResponse: Database error
    """
    return create_error_response(
        ErrorCode.DB_WRITE_FAILED,
        f"Database {operation} failed",
        {"operation": operation, "details": details} if details else {"operation": operation},
        500
    )


def create_upload_error(
    field: str,
    retry_count: int = 0
) -> JSONResponse:
    """
    Create Cloudinary upload error.
    
    Args:
        field: File field that failed
        retry_count: Number of retries attempted
    
    Returns:
        JSONResponse: Upload error
    """
    return create_error_response(
        ErrorCode.CLOUDINARY_UPLOAD_FAILED,
        f"Failed to upload {field} after {retry_count} retries",
        {"field": field, "retry_count": retry_count},
        500
    )


def create_internal_error(
    message: str = "An unexpected error occurred",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create internal server error.
    
    Args:
        message: Error message
        details: Error details
    
    Returns:
        JSONResponse: Internal error
    """
    return create_error_response(
        ErrorCode.INTERNAL_SERVER_ERROR,
        message,
        details,
        500
    )


class ErrorHandler:
    """Central error handler for consistent responses"""
    
    @staticmethod
    async def handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
        """Handle validation errors"""
        error_message = str(exc)
        field = getattr(exc, 'field', 'unknown')
        
        return create_validation_error(field, error_message)
    
    @staticmethod
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        return create_error_response(
            ErrorCode.INTERNAL_SERVER_ERROR,
            exc.detail,
            None,
            exc.status_code
        )
    
    @staticmethod
    async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions"""
        logger.exception(f"Unhandled exception: {exc}")
        return create_internal_error(
            "An unexpected error occurred",
            {"exception_type": type(exc).__name__}
        )
