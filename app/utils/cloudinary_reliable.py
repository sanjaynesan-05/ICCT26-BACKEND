"""
Reliable Cloudinary Upload Service - ICCT26
============================================
Upload files to Cloudinary with retry logic and exponential backoff.

Features:
- Exponential backoff (0.5s → 1.0s → 2.0s)
- Max 3 retries
- Handles network errors, DNS errors, 5xx responses
- Detailed error logging
"""

import asyncio
import logging
from typing import Optional
from fastapi import UploadFile
import cloudinary.uploader
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException, ConnectionError, Timeout

logger = logging.getLogger(__name__)

# Thread pool for async operations
executor = ThreadPoolExecutor(max_workers=4)


class CloudinaryUploadError(Exception):
    """Custom exception for Cloudinary upload failures"""
    def __init__(self, message: str, retry_count: int = 0):
        self.message = message
        self.retry_count = retry_count
        super().__init__(message)


async def upload_with_retry(
    file: UploadFile,
    folder: str,
    public_id: Optional[str] = None,
    max_retries: int = 3,
    initial_delay: float = 0.5,
    resource_type: str = "auto"
) -> str:
    """
    Upload file to Cloudinary with exponential backoff retry logic.
    
    Args:
        file: File to upload
        folder: Cloudinary folder path
        public_id: Custom public ID for the file (optional)
        max_retries: Maximum retry attempts (default 3)
        initial_delay: Initial retry delay in seconds (default 0.5s)
        resource_type: Resource type (default "auto")
    
    Returns:
        str: Secure URL of uploaded file
    
    Raises:
        CloudinaryUploadError: If all retries fail
    """
    retry_count = 0
    last_error = None
    
    while retry_count <= max_retries:
        try:
            logger.info(f"📤 Uploading to Cloudinary (attempt {retry_count + 1}/{max_retries + 1}): {folder}")
            
            # Upload in thread pool to avoid blocking
            secure_url = await _upload_sync_in_executor(file, folder, public_id, resource_type)
            
            logger.info(f"✅ Upload successful: {secure_url[:50]}...")
            return secure_url
            
        except (ConnectionError, Timeout, RequestException) as e:
            # Network-related errors - retry
            last_error = e
            retry_count += 1
            
            if retry_count <= max_retries:
                delay = initial_delay * (2 ** (retry_count - 1))
                logger.warning(
                    f"⚠️ Upload failed (attempt {retry_count}/{max_retries + 1}): {str(e)}"
                    f" - Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"❌ Upload failed after {max_retries + 1} attempts")
                
        except Exception as e:
            # Non-retryable error
            logger.error(f"❌ Upload failed with non-retryable error: {str(e)}")
            raise CloudinaryUploadError(
                f"Upload failed: {str(e)}",
                retry_count
            )
    
    # All retries exhausted
    error_msg = f"Upload failed after {max_retries + 1} attempts: {str(last_error)}"
    raise CloudinaryUploadError(error_msg, max_retries + 1)


async def _upload_sync_in_executor(
    file: UploadFile, 
    folder: str, 
    public_id: Optional[str] = None,
    resource_type: str = "auto"
) -> str:
    """
    Execute synchronous Cloudinary upload in thread pool.
    
    Args:
        file: File to upload
        folder: Cloudinary folder
        public_id: Custom public ID (optional)
        resource_type: Resource type
    
    Returns:
        str: Secure URL
    """
    def _upload():
        """Sync upload function"""
        try:
            # Reset file pointer
            file.file.seek(0)
            
            # Build upload parameters
            upload_params = {
                "folder": folder,
                "resource_type": resource_type,
                "timeout": 30
            }
            
            if public_id:
                upload_params["public_id"] = public_id
            else:
                upload_params["use_filename"] = True
                upload_params["unique_filename"] = True
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file.file,
                **upload_params
            )
            
            return result["secure_url"]
            
        except Exception as e:
            logger.error(f"❌ Cloudinary SDK error: {str(e)}")
            raise
    
    # Run in thread pool
    loop = asyncio.get_event_loop()
    secure_url = await loop.run_in_executor(executor, _upload)
    return secure_url


async def upload_multiple_with_retry(
    files: dict,
    base_folder: str,
    max_retries: int = 3
) -> dict:
    """
    Upload multiple files concurrently with retry logic.
    
    Args:
        files: Dict of {field_name: UploadFile}
        base_folder: Base Cloudinary folder
        max_retries: Max retries per file
    
    Returns:
        dict: {field_name: secure_url or None}
    """
    upload_tasks = {}
    
    for field_name, upload_file in files.items():
        if upload_file:
            folder = f"{base_folder}/{field_name}"
            upload_tasks[field_name] = upload_with_retry(
                upload_file,
                folder,
                max_retries
            )
    
    # Upload all concurrently
    results = await asyncio.gather(*upload_tasks.values(), return_exceptions=True)
    
    # Map results back
    urls = {}
    for field_name, result in zip(upload_tasks.keys(), results):
        if isinstance(result, Exception):
            logger.error(f"❌ Failed to upload {field_name}: {result}")
            urls[field_name] = None
        else:
            urls[field_name] = result
    
    return urls
