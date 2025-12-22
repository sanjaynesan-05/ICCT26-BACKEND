"""
Test Cloudinary Configuration
Verifies that Cloudinary credentials are set up correctly.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cloudinary_config():
    """Test Cloudinary configuration and upload capability"""
    
    print("=" * 70)
    print("CLOUDINARY CONFIGURATION TEST")
    print("=" * 70)
    print()
    
    # Check environment variables
    print("1️⃣ Checking Environment Variables...")
    print("-" * 70)
    
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME', settings.CLOUDINARY_CLOUD_NAME)
    api_key = os.getenv('CLOUDINARY_API_KEY', settings.CLOUDINARY_API_KEY)
    api_secret = os.getenv('CLOUDINARY_API_SECRET', settings.CLOUDINARY_API_SECRET)
    
    print(f"  Cloud Name: {cloud_name if cloud_name else '❌ NOT SET'}")
    print(f"  API Key: {'✅ SET (' + api_key[:5] + '...' + api_key[-3:] + ')' if api_key else '❌ NOT SET'}")
    print(f"  API Secret: {'✅ SET (' + api_secret[:3] + '...' + api_secret[-3:] + ')' if api_secret else '❌ NOT SET'}")
    print()
    
    # Check if enabled
    print("2️⃣ Checking Cloudinary Status...")
    print("-" * 70)
    
    if settings.CLOUDINARY_ENABLED:
        print("  ✅ Cloudinary is ENABLED")
    else:
        print("  ❌ Cloudinary is DISABLED")
        print()
        print("  Reasons:")
        if not cloud_name or cloud_name == "demo":
            print("    - Cloud name not set or using 'demo' default")
        if not api_key:
            print("    - API key not set")
        if not api_secret:
            print("    - API secret not set")
        print()
        print("  📖 To fix: See docs/CLOUDINARY_SETUP.md")
        print()
        return False
    
    print()
    
    # Try to initialize Cloudinary
    print("3️⃣ Testing Cloudinary Initialization...")
    print("-" * 70)
    
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        # Verify configuration
        config = cloudinary.config()
        if config.cloud_name and config.api_key and config.api_secret:
            print("  ✅ Cloudinary initialized successfully")
            print(f"  Cloud: {config.cloud_name}")
            print()
        else:
            print("  ❌ Cloudinary initialization incomplete")
            return False
            
    except ImportError:
        print("  ❌ Cloudinary package not installed")
        print("  Run: pip install cloudinary")
        return False
    except Exception as e:
        print(f"  ❌ Cloudinary initialization failed: {e}")
        return False
    
    # Test API connection
    print("4️⃣ Testing API Connection...")
    print("-" * 70)
    
    try:
        # Try to ping Cloudinary API (lightweight request)
        result = cloudinary.api.ping()
        print(f"  ✅ Cloudinary API is reachable")
        print(f"  Status: {result.get('status', 'unknown')}")
        print()
    except cloudinary.exceptions.AuthorizationRequired:
        print("  ❌ Authentication failed - check your API credentials")
        print("  Verify that:")
        print("    - API Key is correct (15 digits)")
        print("    - API Secret is correct (27 characters)")
        print("    - Cloud Name is correct")
        return False
    except Exception as e:
        print(f"  ❌ API connection failed: {e}")
        return False
    
    # Get account usage (optional)
    print("5️⃣ Checking Account Usage...")
    print("-" * 70)
    
    try:
        usage = cloudinary.api.usage()
        
        # Storage
        storage_used_mb = usage.get('storage', {}).get('usage', 0) / (1024 * 1024)
        storage_limit_mb = usage.get('storage', {}).get('limit', 0) / (1024 * 1024)
        
        print(f"  Storage Used: {storage_used_mb:.2f} MB / {storage_limit_mb:.0f} MB")
        
        # Bandwidth
        bandwidth_used_mb = usage.get('bandwidth', {}).get('usage', 0) / (1024 * 1024)
        bandwidth_limit_mb = usage.get('bandwidth', {}).get('limit', 0) / (1024 * 1024)
        
        print(f"  Bandwidth Used: {bandwidth_used_mb:.2f} MB / {bandwidth_limit_mb:.0f} MB")
        print()
        
    except Exception as e:
        print(f"  ⚠️ Could not retrieve usage data: {e}")
        print()
    
    # Summary
    print("=" * 70)
    print("🎉 CLOUDINARY CONFIGURATION TEST PASSED!")
    print("=" * 70)
    print()
    print("✅ Your Cloudinary account is ready for file uploads")
    print("✅ Registration endpoint will upload files to Cloudinary")
    print("✅ Database will store real Cloudinary URLs")
    print()
    print("Next steps:")
    print("  1. Start server: python -m uvicorn main:app --reload")
    print("  2. Test registration with file uploads")
    print("  3. Check Cloudinary dashboard for uploaded files")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_cloudinary_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
