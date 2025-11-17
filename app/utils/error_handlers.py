"""
Standardized Error Response Utilities
=====================================
Provides consistent error response format across all API endpoints.
"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    message: str,
    detail: Optional[str] = None,
    error_code: Optional[str] = None
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        message: User-friendly error message
        detail: Optional detailed error information
        error_code: Optional error code for client-side handling
    
    Returns:
        JSONResponse with consistent error format
    """
    response_data = {
        "success": False,
        "message": message
    }
    
    if detail:
        response_data["detail"] = detail
    
    if error_code:
        response_data["error_code"] = error_code
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


def create_success_response(
    message: str,
    data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        message: Success message
        data: Optional response data
        **kwargs: Additional fields to include in response
    
    Returns:
        Dictionary with consistent success format
    """
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    # Add any additional fields
    response.update(kwargs)
    
    return response


def handle_validation_error(error: Exception) -> HTTPException:
    """
    Convert validation errors to HTTPException with consistent format.
    
    Args:
        error: Validation error
    
    Returns:
        HTTPException with status 400
    """
    logger.error(f"Validation error: {str(error)}")
    return HTTPException(
        status_code=400,
        detail=str(error)
    )


def handle_cloudinary_error(error: Exception, file_name: str = "file") -> HTTPException:
    """
    Convert Cloudinary errors to user-friendly HTTPException.
    
    Args:
        error: Cloudinary error
        file_name: Name of file that failed to upload
    
    Returns:
        HTTPException with appropriate status code
    """
    error_msg = str(error).lower()
    
    logger.error(f"Cloudinary error for {file_name}: {str(error)}")
    
    if 'invalid' in error_msg or 'unsupported' in error_msg:
        return HTTPException(
            status_code=400,
            detail=f"File format not supported or file is corrupted: {file_name}"
        )
    elif 'size' in error_msg or 'large' in error_msg:
        return HTTPException(
            status_code=400,
            detail=f"File too large: {file_name}. Please compress and try again."
        )
    elif 'quota' in error_msg or 'limit' in error_msg:
        return HTTPException(
            status_code=503,
            detail="Cloud storage quota exceeded. Please contact support."
        )
    else:
        return HTTPException(
            status_code=500,
            detail=f"Cloud storage upload failed for {file_name}. Please try again."
        )


def handle_database_error(error: Exception, operation: str = "operation") -> HTTPException:
    """
    Convert database errors to user-friendly HTTPException.
    
    Args:
        error: Database error
        operation: Description of the operation that failed
    
    Returns:
        HTTPException with status 500
    """
    logger.error(f"Database error during {operation}: {str(error)}", exc_info=True)
    
    error_msg = str(error).lower()
    
    if 'unique' in error_msg or 'duplicate' in error_msg:
        return HTTPException(
            status_code=409,
            detail=f"A record with this information already exists."
        )
    elif 'foreign key' in error_msg or 'constraint' in error_msg:
        return HTTPException(
            status_code=400,
            detail=f"Data validation failed. Please check your input."
        )
    else:
        return HTTPException(
            status_code=500,
            detail=f"Database error during {operation}. Please try again."
        )


def handle_file_upload_error(
    error: Exception,
    file_name: str = "file",
    context: str = "upload"
) -> HTTPException:
    """
    Handle file upload errors with appropriate user messages.
    
    Args:
        error: Upload error
        file_name: Name of file that failed
        context: Context of the operation (e.g., "upload", "validation")
    
    Returns:
        HTTPException with appropriate status code
    """
    logger.error(f"File {context} error for {file_name}: {str(error)}")
    
    # If it's already an HTTPException, return it
    if isinstance(error, HTTPException):
        return error
    
    # Check for common error patterns
    error_msg = str(error).lower()
    
    if 'file type' in error_msg or 'mime' in error_msg:
        return HTTPException(
            status_code=400,
            detail=f"Invalid file type for {file_name}. Please upload a supported format."
        )
    elif 'size' in error_msg or 'large' in error_msg:
        return HTTPException(
            status_code=400,
            detail=f"File too large: {file_name}. Maximum size exceeded."
        )
    elif 'corrupt' in error_msg or 'invalid' in error_msg:
        return HTTPException(
            status_code=400,
            detail=f"File appears to be corrupted: {file_name}. Please try uploading again."
        )
    else:
        return HTTPException(
            status_code=500,
            detail=f"Failed to {context} {file_name}. Please try again."
        )


def log_error_context(
    error: Exception,
    context: str,
    **metadata
):
    """
    Log error with context and metadata.
    
    Args:
        error: The exception
        context: Description of what was being done
        **metadata: Additional context information
    """
    logger.error(f"ERROR in {context}: {str(error)}")
    if metadata:
        logger.error(f"Context: {metadata}")
    logger.error("Stack trace:", exc_info=True)


__all__ = [
    "create_error_response",
    "create_success_response",
    "handle_validation_error",
    "handle_cloudinary_error",
    "handle_database_error",
    "handle_file_upload_error",
    "log_error_context"
]
