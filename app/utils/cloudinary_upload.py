"""
Cloudinary File Upload Utility - STEP 13 Enhanced
==================================================
Handles all file uploads to Cloudinary with organized folder structure.
Supports images (JPEG, PNG) and PDFs via UploadFile.

Folder Structure:
    icct26/
        teams/
            payments/
            pastorLetters/
            groupPhotos/
            aadhar/
            subscriptions/
        players/
            photos/
            aadhar/
            idCards/
"""

import os
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from fastapi import UploadFile, HTTPException
from typing import Optional
import uuid
import time
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

# Initialize Cloudinary from environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def verify_cloudinary_config():
    """Verify that Cloudinary is properly configured"""
    config = cloudinary.config()
    if not all([config.cloud_name, config.api_key, config.api_secret]):
        raise ValueError("Cloudinary credentials not properly configured. Check environment variables.")
    return True


def extract_public_id_from_url(cloudinary_url: str) -> Optional[str]:
    """
    Extract the public_id from a Cloudinary URL.
    
    Args:
        cloudinary_url: Full Cloudinary URL
    
    Returns:
        Public ID (folder/filename without extension) or None
    
    Example:
        https://res.cloudinary.com/demo/image/upload/v1234/icct26/teams/payments/TEAM001_payment_1234567890.pdf
        Returns: icct26/teams/payments/TEAM001_payment_1234567890
    """
    if not cloudinary_url or not isinstance(cloudinary_url, str):
        return None
    
    try:
        # Pattern: .../upload/v{version}/{public_id}.{extension}
        # or: .../upload/{public_id}.{extension}
        pattern = r'/upload/(?:v\d+/)?(.+?)\.\w+$'
        match = re.search(pattern, cloudinary_url)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        logger.error(f"Failed to extract public_id from URL: {str(e)}")
        return None


def delete_file_from_cloudinary(cloudinary_url: str) -> bool:
    """
    Delete a file from Cloudinary by extracting public_id from URL.
    
    Args:
        cloudinary_url: Full Cloudinary URL
    
    Returns:
        True if successful, False otherwise
    """
    if not cloudinary_url:
        return False
    
    public_id = extract_public_id_from_url(cloudinary_url)
    if not public_id:
        logger.warning(f"Could not extract public_id from URL: {cloudinary_url}")
        return False
    
    try:
        # Determine resource type from public_id
        resource_type = 'image'
        if any(ext in public_id.lower() for ext in ['.pdf', 'raw', 'document']):
            resource_type = 'raw'
        
        logger.info(f"🗑️ Deleting from Cloudinary: {public_id} (type: {resource_type})")
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        
        success = result.get('result') == 'ok'
        if success:
            logger.info(f"✅ Successfully deleted: {public_id}")
        else:
            logger.warning(f"⚠️ Delete result: {result.get('result')} for {public_id}")
        
        return success
    except Exception as e:
        logger.error(f"❌ Failed to delete {public_id} from Cloudinary: {str(e)}")
        return False

async def upload_file_to_cloudinary(
    file: UploadFile,
    folder: str,
    public_id: Optional[str] = None,
    overwrite: bool = True
) -> str:
    """
    Upload a file to Cloudinary and return the secure URL.
    
    STEP 13 Enhanced:
    - Organized folder structure: icct26/teams/{type} or icct26/players/{type}
    - Unique public_id with timestamp to avoid collisions
    - Optional overwrite support for updates
    - Returns only secure_url (clean URLs)
    
    Args:
        file: FastAPI UploadFile object
        folder: Cloudinary folder path (e.g., "icct26/teams/payments")
        public_id: Optional custom filename (e.g., "TEAM001_payment_1700000000")
        overwrite: Whether to overwrite existing file with same public_id
    
    Returns:
        Secure Cloudinary URL (HTTPS) - clean URL only
    
    Raises:
        HTTPException: If upload fails with user-friendly error messages
    
    Example:
        url = await upload_file_to_cloudinary(
            file=payment_receipt,
            folder="icct26/teams/payments",
            public_id="TEAM001_payment_1700000000"
        )
    """
    try:
        # Verify Cloudinary is configured
        verify_cloudinary_config()
        
        # Generate unique filename if not provided
        if not public_id:
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4())[:8]
            public_id = f"file_{timestamp}_{unique_id}"
        
        # Read file content
        file_content = await file.read()
        
        # Reset file pointer for potential reuse
        await file.seek(0)
        
        # Determine resource type based on file content type
        resource_type = 'auto'  # Cloudinary auto-detects
        if file.content_type:
            if 'pdf' in file.content_type.lower():
                resource_type = 'raw'
            elif 'image' in file.content_type.lower():
                resource_type = 'image'
        
        logger.info(f"📤 Uploading to Cloudinary: {folder}/{public_id} (type: {resource_type})")
        
        # Upload to Cloudinary with organized folder structure
        upload_result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            public_id=public_id,
            resource_type=resource_type,
            overwrite=overwrite,
            unique_filename=False,  # We control uniqueness via public_id
            use_filename=False      # Use our public_id, not original filename
        )
        
        # Return ONLY secure URL (clean URL, no metadata)
        secure_url = upload_result.get('secure_url')
        
        if not secure_url:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get URL from Cloudinary for file: {file.filename}"
            )
        
        logger.info(f"✅ Upload successful: {secure_url}")
        return secure_url
    
    except cloudinary.exceptions.Error as e:
        logger.error(f"❌ Cloudinary error uploading {file.filename}: {str(e)}")
        
        # Convert Cloudinary-specific errors to user-friendly messages
        error_msg = str(e).lower()
        
        if 'invalid' in error_msg or 'unsupported' in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"File format not supported or file is corrupted: {file.filename}"
            )
        elif 'size' in error_msg or 'large' in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file.filename}. Please compress the file and try again."
            )
        elif 'quota' in error_msg or 'limit' in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Cloud storage quota exceeded. Please contact support."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Cloud storage upload failed for {file.filename}. Please try again."
            )
    
    except HTTPException:
        # Re-raise HTTPExceptions (already formatted)
        raise
    
    except Exception as e:
        logger.error(f"❌ Unexpected error uploading {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while uploading {file.filename}. Please try again."
        )


async def upload_team_files(
    team_id: str,
    pastor_letter: Optional[UploadFile] = None,
    payment_receipt: Optional[UploadFile] = None,
    group_photo: Optional[UploadFile] = None
) -> dict:
    """
    Upload all team-level files to Cloudinary with STEP 13 folder structure.
    
    Folder Structure:
        - Pastor Letter → icct26/teams/pastorLetters
        - Payment Receipt → icct26/teams/payments
        - Group Photo → icct26/teams/groupPhotos
    
    Args:
        team_id: Unique team identifier (e.g., "TEAM-20251117-ABC123")
        pastor_letter: PDF file
        payment_receipt: Image or PDF file
        group_photo: Image file
    
    Returns:
        Dictionary with Cloudinary URLs for each file
    """
    urls = {}
    timestamp = int(time.time())
    
    # Upload pastor letter
    if pastor_letter and pastor_letter.filename:
        public_id = f"{team_id}_pastorLetter_{timestamp}"
        urls['pastor_letter_url'] = await upload_file_to_cloudinary(
            file=pastor_letter,
            folder="icct26/teams/pastorLetters",
            public_id=public_id
        )
    else:
        urls['pastor_letter_url'] = None
    
    # Upload payment receipt
    if payment_receipt and payment_receipt.filename:
        public_id = f"{team_id}_payment_{timestamp}"
        urls['payment_receipt_url'] = await upload_file_to_cloudinary(
            file=payment_receipt,
            folder="icct26/teams/payments",
            public_id=public_id
        )
    else:
        urls['payment_receipt_url'] = None
    
    # Upload group photo
    if group_photo and group_photo.filename:
        public_id = f"{team_id}_groupPhoto_{timestamp}"
        urls['group_photo_url'] = await upload_file_to_cloudinary(
            file=group_photo,
            folder="icct26/teams/groupPhotos",
            public_id=public_id
        )
    else:
        urls['group_photo_url'] = None
    
    return urls


async def upload_player_files(
    team_id: str,
    player_id: str,
    aadhar_file: Optional[UploadFile] = None,
    subscription_file: Optional[UploadFile] = None
) -> dict:
    """
    Upload player-level files to Cloudinary with STEP 13 folder structure.
    
    Folder Structure:
        - Aadhar → icct26/teams/aadhar (team-level since players belong to teams)
        - Subscription → icct26/teams/subscriptions
    
    Args:
        team_id: Team identifier (e.g., "TEAM-20251117-ABC123")
        player_id: Player identifier (e.g., "TEAM-20251117-ABC123-P01")
        aadhar_file: Aadhar PDF/image file
        subscription_file: Subscription PDF/image file
    
    Returns:
        Dictionary with Cloudinary URLs for player files
    """
    urls = {}
    timestamp = int(time.time())
    
    # Upload Aadhar file
    if aadhar_file and aadhar_file.filename:
        public_id = f"{player_id}_aadhar_{timestamp}"
        urls['aadhar_url'] = await upload_file_to_cloudinary(
            file=aadhar_file,
            folder="icct26/teams/aadhar",
            public_id=public_id
        )
    else:
        urls['aadhar_url'] = None
    
    # Upload subscription file
    if subscription_file and subscription_file.filename:
        public_id = f"{player_id}_subscription_{timestamp}"
        urls['subscription_url'] = await upload_file_to_cloudinary(
            file=subscription_file,
            folder="icct26/teams/subscriptions",
            public_id=public_id
        )
    else:
        urls['subscription_url'] = None
    
    return urls


def delete_from_cloudinary(public_id: str, resource_type: str = 'image') -> bool:
    """
    Delete a file from Cloudinary by public_id.
    
    DEPRECATED: Use delete_file_from_cloudinary(url) instead.
    This function is kept for backward compatibility.
    
    Args:
        public_id: The Cloudinary public ID (path without extension)
        resource_type: Type of resource ('image', 'raw', 'video')
    
    Returns:
        True if successful, False otherwise
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result.get('result') == 'ok'
    except Exception as e:
        logger.error(f"❌ Failed to delete {public_id} from Cloudinary: {str(e)}")
        return False

