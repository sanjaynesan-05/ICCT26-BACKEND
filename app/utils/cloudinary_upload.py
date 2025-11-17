"""
Async Cloudinary Upload Utility - ICCT26 PRODUCTION
====================================================
Prevents blocking with ThreadPoolExecutor for sync Cloudinary SDK.
Handles all file uploads to Cloudinary asynchronously.
"""

import os
import cloudinary
import cloudinary.uploader
import asyncio
import logging
from fastapi import UploadFile
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Initialize Cloudinary from environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# Thread pool for running sync Cloudinary operations asynchronously
executor = ThreadPoolExecutor(max_workers=4)


def verify_cloudinary_config():
    """Verify that Cloudinary is properly configured"""
    config = cloudinary.config()
    if not all([config.cloud_name, config.api_key, config.api_secret]):
        raise ValueError("Cloudinary credentials not properly configured. Check environment variables.")
    return True


async def upload_file_to_cloudinary_async(file: UploadFile, folder: str) -> str:
    """
    Upload file to Cloudinary asynchronously using ThreadPoolExecutor.
    
    Args:
        file: FastAPI UploadFile object
        folder: Cloudinary folder path (e.g., "ICCT26/pastor_letters/ICCT-001")
    
    Returns:
        str: Secure URL of uploaded file
    
    Raises:
        Exception: If upload fails
    """
    
    def _upload_sync():
        """Synchronous upload function to run in thread pool"""
        try:
            # Reset file pointer to beginning
            file.file.seek(0)
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file.file,
                folder=folder,
                resource_type="auto",  # Auto-detect file type
                use_filename=True,
                unique_filename=True
            )
            
            logger.info(f"✅ Cloudinary upload successful: {result['secure_url'][:50]}...")
            return result["secure_url"]
            
        except Exception as e:
            logger.error(f"❌ Cloudinary upload error: {e}")
            raise
    
    try:
        # Run sync upload in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        secure_url = await loop.run_in_executor(executor, _upload_sync)
        return secure_url
        
    except Exception as e:
        logger.error(f"❌ Async Cloudinary upload failed: {e}")
        raise Exception(f"Cloudinary upload failed: {str(e)}")
