"""
Routes package - Contains all API endpoints organized by feature
"""

from fastapi import APIRouter

from app.routes.registration_production import router as registration_production_router
from app.routes.admin import router as admin_router
from app.routes.payment_admin import router as payment_admin_router
from app.routes.health import router as health_router
from app.routes.team import router as team_router
from app.routes.gallery import router as gallery_router
from app.routes.schedule import router as schedule_router

# Payment UPI endpoints
try:
    from app.routes.payment import router as payment_router
except ImportError:
    payment_router = None

# Create main router
main_router = APIRouter()

# Include sub-routers
main_router.include_router(health_router, tags=["Health & Status"])
main_router.include_router(registration_production_router, prefix="/api", tags=["Registration-Production"])
main_router.include_router(gallery_router, tags=["Gallery"])
main_router.include_router(schedule_router, tags=["Schedule"])
main_router.include_router(team_router, tags=["Team Management"])

# Payment routes
if payment_router:
    main_router.include_router(payment_router, prefix="/api", tags=["Payment - UPI"])
main_router.include_router(payment_admin_router, tags=["Admin - Payment Approval"])

# Admin routes (includes admin payment approval)
main_router.include_router(admin_router, prefix="/admin", tags=["Admin Panel"])

__all__ = ["main_router"]
