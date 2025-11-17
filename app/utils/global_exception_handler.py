"""
Global Exception Handler
=========================
Unified error handling for all exception types.
All responses follow the standard error format.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.responses import JSONResponse
from app.utils.error_responses import ErrorCode

logger = logging.getLogger(__name__)


def create_standard_error_response(
    error_code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standard error response format"""
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": None  # Will be set by logging middleware if needed
        }
    }
    if details:
        response["error"]["details"] = details
    return response


class GlobalExceptionHandlers:
    """Collection of global exception handlers"""
    
    @staticmethod
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic ValidationError"""
        logger.error(
            f"Validation error: {exc}",
            extra={
                "error_type": "ValidationError",
                "path": request.url.path,
                "errors": exc.errors()
            }
        )
        
        error_response = create_standard_error_response(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Input validation failed",
            status_code=422,
            details={"errors": [str(e) for e in exc.errors()]}
        )
        
        return JSONResponse(
            status_code=422,
            content=error_response
        )
    
    @staticmethod
    async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle FastAPI RequestValidationError"""
        logger.error(
            f"Request validation error: {exc}",
            extra={
                "error_type": "RequestValidationError",
                "path": request.url.path,
                "errors": exc.errors()
            }
        )
        
        # Extract field-level errors
        field_errors = {}
        for error in exc.errors():
            field = ".".join(str(x) for x in error.get("loc", []))
            field_errors[field] = error.get("msg", "Unknown error")
        
        error_response = create_standard_error_response(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed",
            status_code=422,
            details=field_errors
        )
        
        return JSONResponse(
            status_code=422,
            content=error_response
        )
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTPException"""
        logger.warning(
            f"HTTP exception: {exc.detail}",
            extra={
                "error_type": "HTTPException",
                "path": request.url.path,
                "status_code": exc.status_code
            }
        )
        
        # Map common HTTP exceptions to our error codes
        error_code_map = {
            400: ErrorCode.BAD_REQUEST,
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            409: ErrorCode.CONFLICT,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
            500: ErrorCode.INTERNAL_SERVER_ERROR,
        }
        
        error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
        
        error_response = create_standard_error_response(
            error_code=error_code,
            message=str(exc.detail),
            status_code=exc.status_code
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )
    
    @staticmethod
    async def runtime_error_handler(request: Request, exc: RuntimeError) -> JSONResponse:
        """Handle RuntimeError"""
        logger.error(
            f"Runtime error: {exc}",
            extra={
                "error_type": "RuntimeError",
                "path": request.url.path
            },
            exc_info=True
        )
        
        error_response = create_standard_error_response(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Internal server error occurred",
            status_code=500
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )
    
    @staticmethod
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle any unhandled exception"""
        logger.error(
            f"Unhandled exception: {exc}",
            extra={
                "error_type": type(exc).__name__,
                "path": request.url.path
            },
            exc_info=True
        )
        
        # Don't expose internal details in production
        error_response = create_standard_error_response(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            status_code=500
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )


def setup_global_exception_handlers(app: FastAPI):
    """
    Setup all global exception handlers.
    Must be called after creating FastAPI app.
    """
    
    # Pydantic validation errors
    app.add_exception_handler(
        ValidationError,
        GlobalExceptionHandlers.validation_error_handler
    )
    
    # FastAPI request validation errors
    app.add_exception_handler(
        RequestValidationError,
        GlobalExceptionHandlers.request_validation_error_handler
    )
    
    # HTTP exceptions
    app.add_exception_handler(
        HTTPException,
        GlobalExceptionHandlers.http_exception_handler
    )
    
    # Runtime errors
    app.add_exception_handler(
        RuntimeError,
        GlobalExceptionHandlers.runtime_error_handler
    )
    
    # Generic exception handler (catch-all)
    app.add_exception_handler(
        Exception,
        GlobalExceptionHandlers.generic_exception_handler
    )
    
    logger.info("✅ Global exception handlers registered")
