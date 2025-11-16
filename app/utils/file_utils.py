"""
Base64 File Sanitization and URI Formatting Utilities

This module provides functions to sanitize Base64-encoded file data and ensure
proper data URI formatting for image and PDF files. Designed to fix 
net::ERR_INVALID_URL errors in admin dashboard previews.

Functions:
    - sanitize_base64(): Remove whitespace and validate Base64 integrity
    - format_base64_uri(): Add proper data URI prefix (data:image/png;base64,...)
    - fix_file_fields(): Process team/player dictionaries and format all file fields

Usage:
    from app.utils.file_utils import fix_file_fields
    
    # In admin endpoints:
    team_dict = fix_file_fields(team_dict)
    return {"success": True, "team": team_dict}
"""

import re
import base64
from typing import Optional, Dict, Any, List


# Regex to parse existing data URIs
DATA_URI_RE = re.compile(r'^data:(?P<mime>[\w/\-+.]+);base64,(?P<data>.+)$', re.DOTALL)


def sanitize_base64(data: Optional[str]) -> str:
    """
    Remove all whitespace/newlines from Base64 string and validate integrity.
    
    Args:
        data: Base64 string (may contain whitespace, newlines, or be invalid)
        
    Returns:
        Sanitized Base64 string (no whitespace) or empty string if invalid
        
    Examples:
        >>> sanitize_base64("iVBORw0KGgo\\nAAAANS\\nUhEUg==")
        'iVBORw0KGgoAAAANSUhEUg=='
        
        >>> sanitize_base64("invalid!!!base64")
        ''
    """
    if not data:
        return ""
    
    # Remove ALL whitespace characters (spaces, tabs, newlines, carriage returns)
    data = "".join(data.split())
    
    # Validate Base64 integrity
    try:
        base64.b64decode(data, validate=True)
        return data
    except Exception:
        # Invalid Base64 - return empty string
        return ""


def format_base64_uri(data: Optional[str], mime: str = "image/png") -> str:
    """
    Ensure Base64 data has a valid data URI prefix and is sanitized.
    
    Handles multiple cases:
    - Already has data URI prefix → validate and return
    - Raw Base64 → sanitize and add prefix
    - Invalid/empty → return empty string
    
    Args:
        data: Base64 string or data URI
        mime: MIME type hint ("pdf", "image/png", "application/pdf", etc.)
        
    Returns:
        Properly formatted data URI or empty string
        
    Examples:
        >>> format_base64_uri("iVBORw0KGgo...", "image/png")
        'data:image/png;base64,iVBORw0KGgo...'
        
        >>> format_base64_uri("data:image/jpeg;base64,/9j/4AAQ...", "image/png")
        'data:image/jpeg;base64,/9j/4AAQ...'
        
        >>> format_base64_uri("base64data", "pdf")
        'data:application/pdf;base64,base64data'
    """
    if not data:
        return ""
    
    # Already has data URI prefix?
    if data.startswith("data:"):
        # Validate and return as-is (already formatted)
        match = DATA_URI_RE.match(data)
        if match:
            # Valid data URI - return as-is
            return data
        else:
            # Invalid data URI format - try to extract Base64 part
            if ";base64," in data:
                data = data.split(";base64,", 1)[1]
            else:
                # Can't parse - treat as raw Base64
                data = data.replace("data:", "")
    
    # Sanitize the Base64 data
    data = sanitize_base64(data)
    if not data:
        return ""  # Invalid Base64
    
    # Determine MIME type
    if mime == "pdf" or "application/pdf" in mime.lower():
        mime_type = "application/pdf"
    elif mime == "image" or mime.startswith("image/"):
        # Use specific image type if provided, otherwise default to PNG
        mime_type = mime if "/" in mime else "image/png"
    else:
        # Default to PNG for unknown types
        mime_type = "image/png"
    
    # Return properly formatted data URI
    return f"data:{mime_type};base64,{data}"


def fix_file_fields(team: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Add correct MIME prefixes for all file fields in team/player dictionaries.
    
    Processes:
    - Team-level files: payment_receipt (PNG), pastor_letter (PDF), group_photo (PNG/JPEG)
    - Player-level files: aadhar_file (PDF), subscription_file (PDF)
    
    Handles nested player arrays and safely processes NULL/missing fields.
    
    Args:
        team: Dictionary with team data (may include nested 'players' list)
        
    Returns:
        Updated team dictionary with properly formatted data URIs
        
    Examples:
        >>> team = {
        ...     "payment_receipt": "iVBORw0KGgo...",
        ...     "players": [
        ...         {"aadhar_file": "JVBERi0xLjQ..."}
        ...     ]
        ... }
        >>> fixed = fix_file_fields(team)
        >>> fixed["payment_receipt"].startswith("data:image/png;base64,")
        True
        >>> fixed["players"][0]["aadhar_file"].startswith("data:application/pdf;base64,")
        True
    """
    if not team:
        return team
    
    # Team-level files
    if "payment_receipt" in team and team["payment_receipt"]:
        team["payment_receipt"] = format_base64_uri(
            team["payment_receipt"], 
            "image/png"
        )
    
    if "pastor_letter" in team and team["pastor_letter"]:
        team["pastor_letter"] = format_base64_uri(
            team["pastor_letter"], 
            "application/pdf"
        )
    
    if "group_photo" in team and team["group_photo"]:
        # Try to detect if it's PNG or JPEG; default to PNG
        team["group_photo"] = format_base64_uri(
            team["group_photo"], 
            "image/png"
        )
    
    # Player-level files (nested in 'players' array)
    if "players" in team and isinstance(team["players"], list):
        for player in team["players"]:
            if not isinstance(player, dict):
                continue
                
            if "aadhar_file" in player and player["aadhar_file"]:
                player["aadhar_file"] = format_base64_uri(
                    player["aadhar_file"], 
                    "application/pdf"
                )
            
            if "subscription_file" in player and player["subscription_file"]:
                player["subscription_file"] = format_base64_uri(
                    player["subscription_file"], 
                    "application/pdf"
                )
    
    return team


def fix_player_fields(player: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Add correct MIME prefixes for player file fields.
    
    Convenience function for processing individual player dictionaries
    without team context.
    
    Args:
        player: Dictionary with player data
        
    Returns:
        Updated player dictionary with properly formatted data URIs
    """
    if not player:
        return player
    
    if "aadhar_file" in player and player["aadhar_file"]:
        player["aadhar_file"] = format_base64_uri(
            player["aadhar_file"], 
            "application/pdf"
        )
    
    if "subscription_file" in player and player["subscription_file"]:
        player["subscription_file"] = format_base64_uri(
            player["subscription_file"], 
            "application/pdf"
        )
    
    return player


# Export all public functions
__all__ = [
    "sanitize_base64",
    "format_base64_uri", 
    "fix_file_fields",
    "fix_player_fields"
]
