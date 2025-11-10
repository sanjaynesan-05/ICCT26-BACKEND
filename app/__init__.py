"""
ICCT26 Cricket Tournament Registration API - Package initialization
"""

__version__ = "1.0.0"
__author__ = "ICCT26 Team"
__description__ = "Team registration system for ICCT26 Cricket Tournament with email notifications and admin panel"

# Import these from app.py to make them available for circular import resolution
try:
    from app.config import settings
    from app.schemas import (
        TeamRegistration,
        PlayerDetails,
        CaptainInfo,
        ViceCaptainInfo,
        RegistrationResponse
    )
    
    __all__ = [
        "settings",
        "TeamRegistration",
        "PlayerDetails",
        "CaptainInfo",
        "ViceCaptainInfo",
        "RegistrationResponse"
    ]
except ImportError:
    # During initial import, these might not be available yet
    pass
