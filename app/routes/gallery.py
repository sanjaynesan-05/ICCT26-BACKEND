"""
Gallery Routes
==============
API endpoints for fetching and downloading images from Cloudinary gallery folder or collection.
Supports both folder-based gallery and Cloudinary Collections.
"""

import logging
import requests
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import cloudinary
import cloudinary.api
from config import settings

logger = logging.getLogger(__name__)

# Initialize Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

router = APIRouter(prefix="/api/gallery", tags=["Gallery"])

# Cloudinary Collection Configuration
# Collection ID from: https://collection.cloudinary.com/dplaeuuqk/b40aac6242ba4cd0c8bedcb520ca1eac
CLOUDINARY_COLLECTION_ID = "b40aac6242ba4cd0c8bedcb520ca1eac"
CLOUDINARY_ACCOUNT_ID = "dplaeuuqk"


# ============================================================
# Response Models
# ============================================================

class GalleryImage(BaseModel):
    """Gallery image metadata"""
    public_id: str
    url: str
    secure_url: str
    filename: str
    width: int
    height: int
    bytes: int
    uploaded_at: str
    format: str

    class Config:
        json_schema_extra = {
            "example": {
                "public_id": "ICCT26/Gallery/tournament-photo-1",
                "url": "http://res.cloudinary.com/...",
                "secure_url": "https://res.cloudinary.com/...",
                "filename": "tournament-photo-1.jpg",
                "width": 1920,
                "height": 1080,
                "bytes": 512000,
                "uploaded_at": "2025-11-23T10:30:00Z",
                "format": "jpg"
            }
        }


class GalleryResponse(BaseModel):
    """Gallery API response"""
    success: bool
    message: str
    count: int
    images: List[GalleryImage]


class DownloadResponse(BaseModel):
    """Download response"""
    success: bool
    message: str
    download_url: Optional[str] = None
    filename: Optional[str] = None


# ============================================================
# Endpoints
# ============================================================

@router.get("/ICCT26/Gallery/images", response_model=GalleryResponse)
async def get_gallery_images(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of images to fetch")
):
    """
    Fetch all images from ICCT26/Gallery folder in Cloudinary.
    
    Returns:
    - List of images with metadata
    - Image count
    - Direct download URLs for each image
    """
    try:
        logger.info(f"Fetching gallery images from ICCT26/Gallery folder (limit: {limit})")
        
        # Use Cloudinary API to search for images in the gallery folder
        result = cloudinary.api.resources(
            type="upload",
            prefix="ICCT26/Gallery",
            max_results=limit,
            resource_type="image"
        )
        
        if not result or 'resources' not in result:
            logger.warning("No images found in ICCT26/Gallery folder")
            return GalleryResponse(
                success=True,
                message="No images found in gallery",
                count=0,
                images=[]
            )
        
        # Parse and format response
        images = []
        for resource in result['resources']:
            # Extract filename from public_id
            filename = resource['public_id'].split('/')[-1]
            
            image = GalleryImage(
                public_id=resource['public_id'],
                url=resource['url'],
                secure_url=resource['secure_url'],
                filename=f"{filename}.{resource['format']}",
                width=resource.get('width', 0),
                height=resource.get('height', 0),
                bytes=resource.get('bytes', 0),
                uploaded_at=resource.get('created_at', ''),
                format=resource.get('format', 'jpg')
            )
            images.append(image)
        
        # Sort by upload date (newest first)
        images.sort(key=lambda x: x.uploaded_at, reverse=True)
        
        logger.info(f"✅ Successfully fetched {len(images)} images from gallery")
        
        return GalleryResponse(
            success=True,
            message=f"Successfully fetched {len(images)} images from gallery",
            count=len(images),
            images=images
        )
        
    except cloudinary.exceptions.Error as e:
        logger.error(f"❌ Cloudinary API error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch gallery images: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"❌ Unexpected error fetching gallery images: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching gallery: {str(e)}"
        )


@router.get("/collection/images", response_model=GalleryResponse)
async def get_collection_images(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of images to fetch")
):
    """
    Fetch all images from Cloudinary Collection.
    
    Collection: https://collection.cloudinary.com/dplaeuuqk/b40aac6242ba4cd0c8bedcb520ca1eac
    
    Returns:
    - List of images with metadata
    - Image count
    - Direct download URLs for each image
    """
    try:
        logger.info(f"Fetching images from Cloudinary Collection {CLOUDINARY_COLLECTION_ID} (limit: {limit})")
        
        # Use Cloudinary Collections API to fetch images
        # Collections API endpoint
        url = f"https://api.cloudinary.com/v2/{settings.CLOUDINARY_CLOUD_NAME}/resources"
        
        # Fetch resources in the collection
        result = cloudinary.api.resources(
            type="upload",
            tags=CLOUDINARY_COLLECTION_ID,
            max_results=limit,
            resource_type="image"
        )
        
        if not result or 'resources' not in result:
            logger.warning(f"No images found in collection {CLOUDINARY_COLLECTION_ID}")
            return GalleryResponse(
                success=True,
                message="No images found in collection",
                count=0,
                images=[]
            )
        
        # Parse and format response
        images = []
        for resource in result['resources']:
            # Extract filename from public_id
            filename = resource['public_id'].split('/')[-1]
            
            image = GalleryImage(
                public_id=resource['public_id'],
                url=resource['url'],
                secure_url=resource['secure_url'],
                filename=f"{filename}.{resource['format']}",
                width=resource.get('width', 0),
                height=resource.get('height', 0),
                bytes=resource.get('bytes', 0),
                uploaded_at=resource.get('created_at', ''),
                format=resource.get('format', 'jpg')
            )
            images.append(image)
        
        # Sort by upload date (newest first)
        images.sort(key=lambda x: x.uploaded_at, reverse=True)
        
        logger.info(f"✅ Successfully fetched {len(images)} images from collection")
        
        return GalleryResponse(
            success=True,
            message=f"Successfully fetched {len(images)} images from collection",
            count=len(images),
            images=images
        )
        
    except cloudinary.exceptions.Error as e:
        logger.error(f"❌ Cloudinary Collection API error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch collection images: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"❌ Unexpected error fetching collection images: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching collection: {str(e)}"
        )


@router.post("/download/single")
async def download_single_image(
    image_url: str = Query(..., description="Cloudinary image URL or public_id"),
    filename: Optional[str] = Query(None, description="Custom filename for download")
):
    """
    Download a single image from gallery.
    
    Returns:
    - Direct Cloudinary download URL
    - Filename for the download
    
    The frontend will use this URL to trigger the browser download.
    """
    try:
        logger.info(f"Processing single image download: {image_url}")
        
        # If it's a public_id, convert to URL
        if not image_url.startswith('http'):
            # It's a public_id, generate secure URL
            download_url = cloudinary.utils.cloudinary_url(
                image_url,
                secure=True
            )[0]
        else:
            download_url = image_url
        
        # Extract filename
        if not filename:
            filename = image_url.split('/')[-1]
            if '.' not in filename:
                filename = f"{filename}.jpg"
        
        logger.info(f"✅ Download prepared: {filename}")
        
        return DownloadResponse(
            success=True,
            message="Download link generated successfully",
            download_url=download_url,
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating download link: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate download link: {str(e)}"
        )


@router.post("/download/bulk")
async def download_bulk_images(
    image_urls: List[str] = Query(..., description="List of image URLs or public_ids to download as ZIP")
):
    """
    Prepare bulk download for multiple images.
    
    Returns:
    - List of download URLs for each image
    - Cloudinary archive URL for bulk download
    
    The frontend will use the archive URL to download all images as ZIP.
    """
    try:
        logger.info(f"Processing bulk download for {len(image_urls)} images")
        
        if not image_urls or len(image_urls) == 0:
            raise HTTPException(
                status_code=400,
                detail="No images selected for download"
            )
        
        if len(image_urls) > 100:
            raise HTTPException(
                status_code=400,
                detail="Maximum 100 images can be downloaded at once"
            )
        
        # Convert to public_ids for Cloudinary archive
        public_ids = []
        download_urls = []
        
        for image_url in image_urls:
            if image_url.startswith('http'):
                # Extract public_id from URL
                # URL format: https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}
                parts = image_url.split('/upload/')
                if len(parts) > 1:
                    public_id = parts[1].split('?')[0]
                    public_ids.append(public_id)
            else:
                public_ids.append(image_url)
            
            # Generate download URL for each image
            if not image_url.startswith('http'):
                download_url = cloudinary.utils.cloudinary_url(image_url, secure=True)[0]
            else:
                download_url = image_url
            
            download_urls.append(download_url)
        
        # Generate archive URL for bulk download
        archive_url = cloudinary.utils.cloudinary_url(
            f"ICCT26_Gallery_{len(public_ids)}_images",
            resource_type="raw",
            type="authenticated",
        )[0]
        
        # Create downloadable archive using Cloudinary API
        try:
            archive_result = cloudinary.api.create_archive(
                resource_type="image",
                public_ids=public_ids,
                fully_qualified=True
            )
            bulk_download_url = archive_result.get('secure_url', archive_result.get('url', ''))
        except:
            # Fallback: generate manual archive URL
            bulk_download_url = f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/multi/upload/ICCT26_Gallery_images.zip"
        
        logger.info(f"✅ Bulk download prepared for {len(public_ids)} images")
        
        return {
            "success": True,
            "message": f"Bulk download ready for {len(public_ids)} images",
            "count": len(public_ids),
            "individual_urls": download_urls,
            "bulk_download_url": bulk_download_url,
            "filename": f"ICCT26_Gallery_{len(public_ids)}_images.zip"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error preparing bulk download: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to prepare bulk download: {str(e)}"
        )


@router.get("/health")
async def gallery_health_check():
    """Health check for gallery endpoints"""
    try:
        cloudinary.api.ping()
        return {
            "success": True,
            "message": "Gallery service is healthy",
            "cloudinary_connected": True
        }
    except Exception as e:
        logger.error(f"Gallery health check failed: {e}")
        return {
            "success": False,
            "message": f"Gallery service error: {str(e)}",
            "cloudinary_connected": False
        }
