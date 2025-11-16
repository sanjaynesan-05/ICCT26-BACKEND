"""
Cloudinary Upload Utilities for ICCT26 Backend
Handles file uploads to Cloudinary cloud storage
"""

from cloudinary.uploader import upload
from cloudinary.exceptions import Error
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def upload_to_cloudinary(file_data: str, folder: str) -> str:
    """
    Upload file to Cloudinary and return secure URL.
    
    Args:
        file_data: Base64 encoded file with data URI prefix (e.g., "data:image/png;base64,...")
                   or raw Base64 string
        folder: Cloudinary folder path (e.g., "ICCT26/pastor_letters")
    
    Returns:
        str: Secure HTTPS URL of uploaded file
    
    Raises:
        Exception: If upload fails
    
    Supported file types:
        - Images: JPEG, PNG, GIF, WebP
        - Documents: PDF
        - Auto-detection via resource_type="auto"
    """
    try:
        if not file_data:
            raise ValueError("File data is empty")
        
        logger.info(f"Uploading file to Cloudinary folder: {folder}")
        
        # Cloudinary accepts base64 directly (with or without data URI prefix)
        response = upload(
            file_data,
            folder=folder,
            resource_type="auto",  # Automatically detects file type (image, pdf, etc.)
            overwrite=False,       # Don't overwrite existing files
            use_filename=False,    # Generate unique filename
            unique_filename=True   # Ensure unique names
        )
        
        secure_url = response.get("secure_url")
        
        if not secure_url:
            raise Exception("Cloudinary upload succeeded but no URL returned")
        
        logger.info(f"✅ File uploaded successfully: {secure_url}")
        return secure_url
    
    except Error as e:
        logger.error(f"❌ Cloudinary Upload Error: {str(e)}")
        raise Exception(f"Cloudinary upload failed: {str(e)}")
    
    except Exception as e:
        logger.error(f"❌ Upload Error: {str(e)}")
        raise Exception(f"File upload failed: {str(e)}")


def upload_multiple_files(files: dict, base_folder: str = "ICCT26") -> dict:
    """
    Upload multiple files to Cloudinary.
    
    Args:
        files: Dictionary of {field_name: file_data}
        base_folder: Base folder in Cloudinary (default: "ICCT26")
    
    Returns:
        dict: Dictionary of {field_name: secure_url}
    
    Example:
        files = {
            "pastor_letter": "data:application/pdf;base64,...",
            "payment_receipt": "data:image/png;base64,..."
        }
        
        urls = upload_multiple_files(files)
        # Returns:
        # {
        #     "pastor_letter": "https://res.cloudinary.com/.../pastor_letter.pdf",
        #     "payment_receipt": "https://res.cloudinary.com/.../payment_receipt.png"
        # }
    """
    uploaded_urls = {}
    
    for field_name, file_data in files.items():
        if file_data:  # Only upload if file data exists
            folder = f"{base_folder}/{field_name}s"  # e.g., "ICCT26/pastor_letters"
            try:
                url = upload_to_cloudinary(file_data, folder)
                uploaded_urls[field_name] = url
            except Exception as e:
                logger.error(f"Failed to upload {field_name}: {str(e)}")
                uploaded_urls[field_name] = None
        else:
            uploaded_urls[field_name] = None
    
    return uploaded_urls


def delete_from_cloudinary(public_id: str) -> bool:
    """
    Delete a file from Cloudinary.
    
    Args:
        public_id: The public ID of the file to delete
    
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        from cloudinary.uploader import destroy
        result = destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        logger.error(f"Failed to delete from Cloudinary: {str(e)}")
        return False
