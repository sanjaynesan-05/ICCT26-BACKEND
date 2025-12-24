"""
Church Management API
Read-only endpoints for church information and availability status.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_async
from app.utils.church_limit_validator import get_church_availability
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/churches", tags=["Churches"])


@router.get("/availability")
async def get_churches_availability(db: AsyncSession = Depends(get_db_async)):
    """
    Get availability status for all churches.
    
    Returns:
        {
            "churches": [
                {
                    "church_name": "Grace Church",
                    "team_count": 1,
                    "locked": false
                },
                {
                    "church_name": "Holy Trinity",
                    "team_count": 2,
                    "locked": true
                }
            ]
        }
    
    This endpoint is read-only and does not affect registration logic.
    A church is "locked" when it has 2 or more teams registered.
    """
    
    try:
        logger.info("Fetching church availability status...")
        churches = await get_church_availability(db)
        
        logger.info(f"✅ Retrieved availability for {len(churches)} churches")
        
        return {
            "churches": churches,
            "summary": {
                "total_churches": len(churches),
                "locked_churches": sum(1 for c in churches if c["locked"]),
                "available_churches": sum(1 for c in churches if not c["locked"])
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching church availability: {str(e)}")
        return {
            "error": "Failed to fetch church availability",
            "detail": str(e)
        }
