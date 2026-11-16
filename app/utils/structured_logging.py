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


class ConsoleFormatter(logging.Formatter):
    """
    Compact, human-readable one-line formatter for the terminal.

        09:16:18 INFO  startup        | db health ok (10.1s)
        09:16:20 ERROR registration   | Team registration failed [rid=ab12cd34 reason=...]
    """

    LEVEL_COLORS = {
        "DEBUG": "\033[90m",     # grey
        "INFO": "\033[36m",      # cyan
        "WARNING": "\033[33m",   # yellow
        "ERROR": "\033[31m",     # red
        "CRITICAL": "\033[41m",  # red background
    }
    RESET = "\033[0m"

    NAME_ALIASES = {
        "icct26_backend": "app",
        "startup_validation": "validation",
        "race_safe_team_id": "team_id",
        "database_hardening": "db_hardening",
        "global_exception_handler": "exceptions",
        "production_middleware": "middleware",
    }

    def __init__(self, use_color: bool = False):
        super().__init__()
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        level = {"WARNING": "WARN", "CRITICAL": "CRIT"}.get(record.levelname, record.levelname).ljust(5)
        if self.use_color:
            level = f"{self.LEVEL_COLORS.get(record.levelname, '')}{level}{self.RESET}"

        # Short logger name: "app.utils.database_hardening" -> "database_hardening"
        name = record.name.rsplit(".", 1)[-1]
        name = self.NAME_ALIASES.get(name, name)[:14].ljust(14)

        line = f"{ts} {level} {name} | {record.getMessage()}"

        # Append request id / structured extras as compact key=value pairs
        extras = []
        rid = getattr(record, "request_id", None)
        if rid and rid != "N/A":
            extras.append(f"rid={str(rid)[:8]}")
        extra_dict = getattr(record, "extra_dict", None)
        if isinstance(extra_dict, dict):
            extras.extend(f"{k}={v}" for k, v in extra_dict.items())
        if extras:
            line += f" [{' '.join(extras)}]"

        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)
        return line


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
    
    level = getattr(logging, str(log_level).upper(), logging.INFO)

    # Configure the ROOT logger once so every module (database, app.utils.*, routes)
    # shares one handler set. Previously the app logger had its own JSON handler AND
    # propagated to a basicConfig root handler, so every line was printed twice.
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(level)

    # Console: compact text by default; LOG_FORMAT=json for JSON (e.g. log aggregators)
    console_handler = logging.StreamHandler()
    if os.getenv("LOG_FORMAT", "text").lower() == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        stream = getattr(console_handler, "stream", None)
        use_color = bool(stream and hasattr(stream, "isatty") and stream.isatty()) and not os.getenv("NO_COLOR")
        console_handler.setFormatter(ConsoleFormatter(use_color=use_color))
    root.addHandler(console_handler)

    # File: always JSON (machine-parseable)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(JSONFormatter())
        root.addHandler(file_handler)

    # Quiet noisy third-party loggers
    for noisy in ("httpx", "httpcore", "urllib3", "cloudinary", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    # RequestLoggingMiddleware already logs one line per request (method, path, status, ms)
    logging.getLogger("uvicorn.access").disabled = True

    logger = logging.getLogger(app_name)
    logger.setLevel(level)
    for h in list(logger.handlers):
        logger.removeHandler(h)
    logger.propagate = True
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


# Generic logging helper functions for compatibility
def log_info(message: str, **kwargs):
    """Generic info logging helper"""
    logger = logging.getLogger(__name__)
    if kwargs:
        logger.info(f"{message} - {kwargs}")
    else:
        logger.info(message)


def log_error(message: str, **kwargs):
    """Generic error logging helper"""
    logger = logging.getLogger(__name__)
    if kwargs:
        logger.error(f"{message} - {kwargs}")
    else:
        logger.error(message)


def log_warning(message: str, **kwargs):
    """Generic warning logging helper"""
    logger = logging.getLogger(__name__)
    if kwargs:
        logger.warning(f"{message} - {kwargs}")
    else:
        logger.warning(message)
