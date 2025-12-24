"""
Routes package - Contains all API endpoints organized by feature
"""

from fastapi import APIRouter

from app.routes.registration_production import router as registration_production_router
from app.routes.admin import router as admin_router
from app.routes.health import router as health_router
from app.routes.team import router as team_router
from app.routes.gallery import router as gallery_router
from app.routes.schedule import router as schedule_router
from app.routes.churches import router as churches_router

# Create main router
main_router = APIRouter()

# Include sub-routers
main_router.include_router(health_router, tags=["Health & Status"])
main_router.include_router(registration_production_router, prefix="/api", tags=["Registration-Production"])
main_router.include_router(gallery_router, tags=["Gallery"])
main_router.include_router(schedule_router, tags=["Schedule"])
main_router.include_router(team_router, tags=["Team Management"])
main_router.include_router(churches_router, tags=["Churches"])
main_router.include_router(admin_router, prefix="/admin", tags=["Admin Panel"])

__all__ = ["main_router"]
