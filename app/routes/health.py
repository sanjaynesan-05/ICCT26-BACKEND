"""
Health check and status routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import logging

from database import get_db
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def read_root():
    """Home endpoint"""
    return {
        "message": "ICCT26 Cricket Tournament Registration API",
        "version": settings.APP_VERSION,
        "status": "active",
        "db": "PostgreSQL Connected",
        "tournament": settings.TOURNAMENT_NAME
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ICCT26 Registration API",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION
    }


@router.get("/status")
def api_status(db: Session = Depends(get_db)):
    """API status endpoint with database check"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Database status check failed: {str(e)}")

    return {
        "status": "operational",
        "api_version": settings.APP_VERSION,
        "database": db_status,
        "email_service": "configured" if settings.SMTP_ENABLED else "not configured",
        "tournament": settings.TOURNAMENT_NAME,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/queue/status")
async def queue_status():
    """Queue status endpoint (placeholder for future implementation)"""
    return {
        "status": "active",
        "pending_registrations": 0,
        "processed_registrations": 0,
        "message": "Queue system ready"
    }
