"""
Cloud-First Cloudinary Upload Utility - ICCT26 PRODUCTION
==========================================================
All files stored in Cloudinary immediately:
- Pending files: /pending/{team_id}/ (temporary)
- Confirmed files: /confirmed/{team_id}/ (with Team ID in filename)
- Rejected files: Deleted instantly from Cloudinary
"""

import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, List
from fastapi import UploadFile
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Thread pool for running sync Cloudinary operations asynchronously
executor = ThreadPoolExecutor(max_workers=4)


class CloudinaryUploader:
    """
    Cloud-First Upload Manager
    - Upload to /pending/ on registration
    - Move to /confirmed/ with Team ID in filename on approval
    - Delete from /pending/ on rejection
    """
    
    def __init__(self):
        self.cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    
    async def upload_pending_file(
        self,
        file_content: bytes,
        team_id: str,
        file_field_name: str,
        original_filename: str
    ) -> Optional[str]:
        """
        Upload file to Cloudinary PENDING folder
        
        Args:
            file_content: File bytes
            team_id: Team ID (e.g., "ICCT26-dda9")
            file_field_name: Field name (payment_receipt, pastor_letter, group_photo)
            original_filename: Original filename
        
        Returns:
            Cloudinary URL or None if failed
        """
        try:
            # Public ID: icct26-tournament/pending/ICCT26-dda9/payment_receipt
            public_id = f"icct26-tournament/pending/{team_id}/{file_field_name}"
            
            logger.info(f"📤 Uploading pending file: {public_id}")
            
            # Upload to Cloudinary (sync call in executor)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: cloudinary.uploader.upload(
                    file_content,
                    public_id=public_id,
                    resource_type="auto",
                    overwrite=True
                )
            )
            
            url = result.get('secure_url')
            logger.info(f"✅ Uploaded to pending: {url}")
            
            return url
        
        except Exception as e:
            logger.error(f"❌ Error uploading pending file: {e}")
            return None
    
    async def move_to_confirmed(
        self,
        team_id: str,
        file_field_name: str
    ) -> Optional[str]:
        """
        Move file from PENDING to CONFIRMED folder with Team ID in filename
        
        Args:
            team_id: Team ID
            file_field_name: Field name
        
        Returns:
            New Cloudinary URL with Team ID in filename
        """
        try:
            # Source: pending file
            old_public_id = f"icct26-tournament/pending/{team_id}/{file_field_name}"
            
            # Destination: confirmed with Team ID in filename
            new_public_id = f"icct26-tournament/confirmed/{team_id}/{team_id}_{file_field_name}"
            
            logger.info(f"🔄 Moving file: {old_public_id} → {new_public_id}")
            
            # Rename (move) in Cloudinary
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: cloudinary.uploader.rename(
                    old_public_id,
                    new_public_id,
                    resource_type="image",
                    overwrite=True
                )
            )
            
            new_url = result.get('secure_url')
            logger.info(f"✅ Moved to confirmed: {new_url}")
            
            return new_url
        
        except Exception as e:
            logger.error(f"❌ Error moving file to confirmed: {e}")
            return None
    
    async def delete_pending_files(self, team_id: str) -> bool:
        """
        Delete ALL pending files for a team (when rejected)
        
        Args:
            team_id: Team ID
        
        Returns:
            True if deleted successfully
        """
        try:
            file_fields = ["payment_receipt", "pastor_letter", "group_photo"]
            deleted_count = 0
            
            loop = asyncio.get_event_loop()
            
            for field_name in file_fields:
                public_id = f"icct26-tournament/pending/{team_id}/{field_name}"
                
                try:
                    result = await loop.run_in_executor(
                        executor,
                        lambda pid=public_id: cloudinary.uploader.destroy(pid)
                    )
                    if result.get('result') == 'ok':
                        deleted_count += 1
                        logger.info(f"🗑️ Deleted: {public_id}")
                except Exception as e:
                    logger.warning(f"⚠️ File not found or error: {public_id} - {e}")
            
            logger.info(f"✅ Deleted {deleted_count} files for team {team_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error deleting pending files: {e}")
            return False
    
    async def upload_file(
        self,
        file_content: bytes,
        folder: str,
        filename: str = None
    ) -> Optional[str]:
        """
        Generic file upload method for compatibility
        
        Args:
            file_content: File bytes
            folder: Cloudinary folder path
            filename: Optional filename
        
        Returns:
            Cloudinary URL or None if failed
        """
        try:
            public_id = f"{folder}/{filename}" if filename else folder
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: cloudinary.uploader.upload(
                    file_content,
                    public_id=public_id,
                    resource_type="auto",
                    overwrite=True
                )
            )
            
            return result.get('secure_url')
        except Exception as e:
            logger.error(f"❌ Error uploading file: {e}")
            return None
    
    async def delete_file(self, public_id: str) -> bool:
        """
        Delete file from Cloudinary by public_id
        
        Args:
            public_id: Cloudinary public_id (e.g., "icct26-tournament/pending/ICCT-001/payment_receipt")
        
        Returns:
            True if deleted successfully
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: cloudinary.uploader.destroy(public_id)
            )
            
            if result.get('result') == 'ok':
                logger.info(f"✅ Deleted file: {public_id}")
                return True
            else:
                logger.warning(f"⚠️ File not found: {public_id}")
                return False
        except Exception as e:
            logger.error(f"❌ Error deleting file {public_id}: {e}")
            return False


# Global uploader instance
cloudinary_uploader = CloudinaryUploader()


async def upload_file_to_cloudinary_async(file: UploadFile, folder: str) -> str:
    """
    Legacy function for backward compatibility
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
