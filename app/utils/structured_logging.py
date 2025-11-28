"""
Structured JSON Logging System
===============================
Production-grade logging with JSON format, file output, and request tracking.
"""

import logging
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import uuid


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs JSON-structured logs.
    Includes request tracking, timestamps, and contextual data.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        """
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "N/A"),
        }
        
        # Add extra fields if provided
        if hasattr(record, "extra_dict"):
            log_data.update(record.extra_dict)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_data)


class StructuredLogger(logging.LoggerAdapter):
    """
    Custom logger adapter that adds structured context.
    """
    
    def process(self, msg: str, kwargs: Dict) -> tuple:
        """
        Process message and add request_id to every log.
        """
        # Get request_id from extra context
        request_id = self.extra.get("request_id", str(uuid.uuid4()))
        
        # Create structured dict for extra data
        extra_dict = self.extra.copy()
        extra_dict.pop("request_id", None)
        
        # Attach to record
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        kwargs["extra"]["request_id"] = request_id
        if extra_dict:
            kwargs["extra"]["extra_dict"] = extra_dict
        
        return msg, kwargs


def setup_logging(app_name: str, log_file: str = None, log_level: str = "INFO") -> logging.Logger:
    """
    Setup structured JSON logging for the application.
    
    Args:
        app_name: Name of the application
        log_file: Optional path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger
    """
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str, request_id: str = None) -> StructuredLogger:
    """
    Get a structured logger with request context.
    
    Args:
        name: Logger name
        request_id: Optional request ID for tracking
    
    Returns:
        StructuredLogger with context
    """
    
    logger = logging.getLogger(name)
    
    if not request_id:
        request_id = str(uuid.uuid4())
    
    return StructuredLogger(logger, {"request_id": request_id})


# Log event types
class LogEvents:
    """Standard log event types"""
    REGISTRATION_SUCCESS = "REGISTRATION_SUCCESS"
    REGISTRATION_FAILED = "REGISTRATION_FAILED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RETRY_ATTEMPT = "RETRY_ATTEMPT"
    RETRY_FAILED = "RETRY_FAILED"
    UPLOAD_STARTED = "UPLOAD_STARTED"
    UPLOAD_SUCCESS = "UPLOAD_SUCCESS"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    EMAIL_SENT = "EMAIL_SENT"
    EMAIL_FAILED = "EMAIL_FAILED"
    DB_CONNECTION_ERROR = "DB_CONNECTION_ERROR"
    RATE_LIMIT_HIT = "RATE_LIMIT_HIT"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"


def log_registration_success(logger: StructuredLogger, team_id: str, team_name: str, duration_ms: float):
    """Log successful registration"""
    logger.info(
        f"Team registration successful: {team_name}",
        extra={
            "extra_dict": {
                "event": LogEvents.REGISTRATION_SUCCESS,
                "team_id": team_id,
                "team_name": team_name,
                "duration_ms": duration_ms
            }
        }
    )


def log_registration_failed(logger: StructuredLogger, reason: str, duration_ms: float, error_code: str):
    """Log failed registration"""
    logger.error(
        f"Team registration failed: {reason}",
        extra={
            "extra_dict": {
                "event": LogEvents.REGISTRATION_FAILED,
                "reason": reason,
                "error_code": error_code,
                "duration_ms": duration_ms
            }
        }
    )


def log_retry_attempt(logger: StructuredLogger, operation: str, attempt: int, max_attempts: int):
    """Log retry attempt"""
    logger.warning(
        f"Retrying operation: {operation} (attempt {attempt}/{max_attempts})",
        extra={
            "extra_dict": {
                "event": LogEvents.RETRY_ATTEMPT,
                "operation": operation,
                "attempt": attempt,
                "max_attempts": max_attempts
            }
        }
    )


def log_retry_exhausted(logger: StructuredLogger, operation: str, reason: str):
    """Log when all retries exhausted"""
    logger.error(
        f"Retry exhausted for: {operation}",
        extra={
            "extra_dict": {
                "event": LogEvents.RETRY_FAILED,
                "operation": operation,
                "reason": reason
            }
        }
    )


def log_upload_success(logger: StructuredLogger, filename: str, size: int, duration_ms: float):
    """Log successful file upload"""
    logger.info(
        f"File uploaded: {filename}",
        extra={
            "extra_dict": {
                "event": LogEvents.UPLOAD_SUCCESS,
                "filename": filename,
                "size": size,
                "duration_ms": duration_ms
            }
        }
    )


def log_upload_failed(logger: StructuredLogger, filename: str, reason: str):
    """Log failed file upload"""
    logger.error(
        f"File upload failed: {filename}",
        extra={
            "extra_dict": {
                "event": LogEvents.UPLOAD_FAILED,
                "filename": filename,
                "reason": reason
            }
        }
    )
