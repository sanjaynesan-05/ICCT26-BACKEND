"""
Church Management API
Read-only endpoints for church information and availability status.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_async
from app.utils.church_limit_validator import get_church_availability
from app.utils.error_responses import ErrorCode, create_error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/churches", tags=["Churches"])


@router.get("/availability")
async def get_churches_availability(db: AsyncSession = Depends(get_db_async)):
    """
    Availability for every church in settings.CHURCH_LIST.

    Returns:
        {
            "churches": [{"church_name": "...", "team_count": 0, "locked": false}, ...],
            "summary": {"total_churches": N, "locked_churches": N, "available_churches": N}
        }

    church_name is spelled exactly as in CHURCH_LIST (the frontend matches with ===).
    A church is locked once it has one team (each church gets one entry).
    """
    try:
        churches = await get_church_availability(db)
    except Exception:
        logger.exception("Error fetching church availability")
        return create_error_response(
            ErrorCode.DATABASE_ERROR, "Failed to fetch church availability", status_code=500
        )

    locked = sum(1 for church in churches if church["locked"])
    return {
        "churches": churches,
        "summary": {
            "total_churches": len(churches),
            "locked_churches": locked,
            "available_churches": len(churches) - locked,
        },
    }
