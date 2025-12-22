"""
Structured Logging Middleware - ICCT26
=======================================
Comprehensive logging with request tracking and monitoring.

Features:
- JSON structured logs
- Request ID tracking
- Request/response logging
- Performance monitoring
- Error tracking
"""

import json
import logging
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)


class StructuredLogger:
    """Structured logging with consistent format"""
    
    @staticmethod
    def log_event(
        level: str,
        event_code: str,
        message: str,
        request_id: str = None,
        **kwargs
    ) -> None:
        """
        Log structured event.
        
        Args:
            level: Log level (INFO, WARN, ERROR)
            event_code: Event code for categorization
            message: Log message
            request_id: Request ID for tracking
            **kwargs: Additional fields
        """
        log_data = {
            "timestamp": time.time(),
            "level": level,
            "event_code": event_code,
            "message": message,
            "request_id": request_id,
            **kwargs
        }
        
        # Log based on level
        if level == "ERROR":
            logger.error(json.dumps(log_data))
        elif level == "WARN":
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
    
    @staticmethod
    def log_registration_started(request_id: str, team_name: str, ip: str) -> None:
        """Log registration start"""
        StructuredLogger.log_event(
            "INFO",
            "REGISTRATION_STARTED",
            f"Registration started for team: {team_name}",
            request_id=request_id,
            team_name=team_name,
            client_ip=ip
        )
    
    @staticmethod
    def log_validation_error(request_id: str, field: str, error: str) -> None:
        """Log validation error"""
        StructuredLogger.log_event(
            "WARN",
            "VALIDATION_ERROR",
            f"Validation failed for {field}: {error}",
            request_id=request_id,
            field=field,
            error=error
        )
    
    @staticmethod
    def log_file_upload(request_id: str, field: str, status: str, url: str = None) -> None:
        """Log file upload result"""
        StructuredLogger.log_event(
            "INFO" if status == "success" else "ERROR",
            "FILE_UPLOAD",
            f"File upload {status}: {field}",
            request_id=request_id,
            field=field,
            status=status,
            url=url
        )
    
    @staticmethod
    def log_db_operation(request_id: str, operation: str, status: str, team_id: str = None) -> None:
        """Log database operation"""
        StructuredLogger.log_event(
            "INFO" if status == "success" else "ERROR",
            "DB_OPERATION",
            f"Database {operation} {status}",
            request_id=request_id,
            operation=operation,
            status=status,
            team_id=team_id
        )
    
    @staticmethod
    def log_email_sent(request_id: str, to_email: str, status: str) -> None:
        """Log email send result"""
        StructuredLogger.log_event(
            "INFO" if status == "success" else "WARN",
            "EMAIL_SENT",
            f"Email send {status}: {to_email}",
            request_id=request_id,
            to_email=to_email,
            status=status
        )
    
    @staticmethod
    def log_exception(request_id: str, exception: Exception) -> None:
        """Log exception with traceback"""
        import traceback
        StructuredLogger.log_event(
            "ERROR",
            "EXCEPTION",
            f"Exception occurred: {str(exception)}",
            request_id=request_id,
            exception_type=type(exception).__name__,
            traceback=traceback.format_exc()
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all requests and responses.
    Adds X-Request-ID header for tracking.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
        
        Returns:
            Response: Response object
        """
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Log incoming request
        start_time = time.time()
        
        StructuredLogger.log_event(
            "INFO",
            "REQUEST_RECEIVED",
            f"{method} {path}",
            request_id=request_id,
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=request.headers.get("User-Agent", "")
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            StructuredLogger.log_event(
                "INFO",
                "REQUEST_COMPLETED",
                f"{method} {path} - {response.status_code}",
                request_id=request_id,
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=int(duration * 1000),
                client_ip=client_ip
            )
            
            # Add request ID to response headers
            if isinstance(response, StreamingResponse):
                response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log exception
            duration = time.time() - start_time
            
            StructuredLogger.log_exception(request_id, e)
            
            StructuredLogger.log_event(
                "ERROR",
                "REQUEST_FAILED",
                f"{method} {path} - Failed",
                request_id=request_id,
                method=method,
                path=path,
                duration_ms=int(duration * 1000),
                exception=str(e)
            )
            
            raise


# Alias for backward compatibility
LoggingMiddleware = RequestLoggingMiddleware
