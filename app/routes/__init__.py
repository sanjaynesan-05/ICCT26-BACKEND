"""
Routes package - Contains all API endpoints organized by feature
"""

from fastapi import APIRouter

from app.routes.registration import router as registration_router
from app.routes.admin import router as admin_router
from app.routes.health import router as health_router

# Create main router
main_router = APIRouter()

# Include sub-routers
main_router.include_router(health_router, tags=["Health & Status"])
main_router.include_router(registration_router, tags=["Registration"])
main_router.include_router(admin_router, prefix="/admin", tags=["Admin Panel"])

__all__ = ["main_router"]
