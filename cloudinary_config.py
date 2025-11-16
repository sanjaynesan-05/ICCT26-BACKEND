"""
Cloudinary Configuration for ICCT26 Backend
Initializes Cloudinary with credentials from environment variables
"""

import cloudinary
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True  # Always use HTTPS URLs
)

# Verify configuration
def verify_cloudinary_config():
    """Verify that Cloudinary is configured correctly"""
    config = cloudinary.config()
    if not config.cloud_name or not config.api_key or not config.api_secret:
        raise ValueError(
            "Cloudinary configuration incomplete. "
            "Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in .env"
        )
    return True
