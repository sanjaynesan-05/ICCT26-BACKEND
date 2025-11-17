"""
Production Middleware Suite
============================
Request timeout, body size limits, compression, and rate limiting.
"""

import time
import logging
import asyncio
from typing import Callable
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from config import settings

logger = logging.getLogger(__name__)


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """
    Enforce request timeout (default 60 seconds).
    Aborts requests that exceed timeout.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            # Create task with timeout
            task = asyncio.create_task(call_next(request))
            response = await asyncio.wait_for(task, timeout=settings.REQUEST_TIMEOUT)
            
            # Log request duration
            duration = time.time() - start_time
            logger.info(
                f"Request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": round(duration * 1000, 2)
                }
            )
            
            return response
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            logger.error(
                f"Request timeout exceeded ({settings.REQUEST_TIMEOUT}s)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2)
                }
            )
            return Response(
                content='{"success": false, "error_code": "REQUEST_TIMEOUT", "message": "Request timeout exceeded"}',
                status_code=408,
                media_type="application/json"
            )
        except Exception as e:
            logger.exception(f"Unexpected error in timeout middleware: {e}")
            raise


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Enforce maximum request body size (default 10MB).
    Rejects requests exceeding size limit.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check Content-Length header
        if "content-length" in request.headers:
            content_length = int(request.headers["content-length"])
            
            if content_length > settings.MAX_REQUEST_SIZE:
                logger.warning(
                    f"Request body exceeds size limit",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "size": content_length,
                        "max_size": settings.MAX_REQUEST_SIZE
                    }
                )
                return Response(
                    content='{"success": false, "error_code": "BODY_TOO_LARGE", "message": "Request body too large"}',
                    status_code=413,
                    media_type="application/json"
                )
        
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting: 30 requests per minute per IP address.
    """
    
    def __init__(self, app, requests_per_minute: int = 30):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/status"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        now = datetime.now()
        
        # Clean old requests (> 1 minute)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for IP",
                extra={
                    "ip": client_ip,
                    "requests_in_minute": len(self.requests[client_ip])
                }
            )
            return Response(
                content='{"success": false, "error_code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests"}',
                status_code=429,
                media_type="application/json"
            )
        
        # Add current request
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Enhanced request logging with timing and details.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request start
        logger.info(
            f"Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration * 1000, 2)
            }
        )
        
        return response


def setup_middleware(app):
    """
    Setup all production middleware in correct order.
    Order matters: apply in reverse order of desired execution.
    """
    
    # CORS middleware (first to run)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Gzip compression
    if settings.ENABLE_COMPRESSION:
        app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Rate limiting
    if settings.ENABLE_RATE_LIMITING:
        app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_REQUESTS)
    
    # Body size limit
    app.add_middleware(BodySizeLimitMiddleware)
    
    # Request timeout
    app.add_middleware(RequestTimeoutMiddleware)
    
    # Request logging
    app.add_middleware(RequestLoggingMiddleware)
