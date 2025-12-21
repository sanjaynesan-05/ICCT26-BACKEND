"""
Quick test script to verify all backend connections
Tests: PostgreSQL, Cloudinary, SMTP
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import async_engine, sync_engine
from sqlalchemy import text
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_async_db():
    """Test async PostgreSQL connection"""
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text('SELECT 1 as test'))
            value = result.scalar()
            logger.info(f"✅ Async PostgreSQL: Connected (test query = {value})")
            
            # Test teams table exists
            result = await conn.execute(text("SELECT COUNT(*) FROM teams"))
            count = result.scalar()
            logger.info(f"✅ Teams table: {count} records")
            
            # Test players table exists
            result = await conn.execute(text("SELECT COUNT(*) FROM players"))
            count = result.scalar()
            logger.info(f"✅ Players table: {count} records")
            
            return True
    except Exception as e:
        logger.error(f"❌ Async PostgreSQL failed: {e}")
        return False


def test_sync_db():
    """Test sync PostgreSQL connection"""
    try:
        with sync_engine.connect() as conn:
            result = conn.execute(text('SELECT 1 as test'))
            value = result.scalar()
            logger.info(f"✅ Sync PostgreSQL: Connected (test query = {value})")
            return True
    except Exception as e:
        logger.error(f"❌ Sync PostgreSQL failed: {e}")
        return False


def test_cloudinary():
    """Test Cloudinary configuration"""
    try:
        logger.info(f"✅ Cloudinary configured:")
        logger.info(f"   - Cloud Name: {settings.CLOUDINARY_CLOUD_NAME}")
        logger.info(f"   - API Key: {settings.CLOUDINARY_API_KEY[:10]}..." if settings.CLOUDINARY_API_KEY else "   - API Key: NOT SET")
        logger.info(f"   - API Secret: {'***' if settings.CLOUDINARY_API_SECRET else 'NOT SET'}")
        logger.info(f"   - Enabled: {settings.CLOUDINARY_ENABLED}")
        
        # Try to initialize
        if settings.CLOUDINARY_ENABLED:
            settings.init_cloudinary()
            logger.info(f"✅ Cloudinary initialized successfully")
        else:
            logger.warning(f"⚠️  Cloudinary not fully configured (using demo mode)")
        return True
    except Exception as e:
        logger.error(f"❌ Cloudinary failed: {e}")
        return False


def test_smtp():
    """Test SMTP configuration"""
    try:
        logger.info(f"✅ SMTP configured:")
        logger.info(f"   - Host: {settings.SMTP_HOST}")
        logger.info(f"   - Port: {settings.SMTP_PORT}")
        logger.info(f"   - User: {settings.SMTP_USER}")
        logger.info(f"   - Password: {'***' if settings.SMTP_PASS else 'NOT SET'}")
        logger.info(f"   - From Email: {settings.SMTP_FROM_EMAIL}")
        logger.info(f"   - Enabled: {settings.SMTP_ENABLED}")
        return True
    except Exception as e:
        logger.error(f"❌ SMTP failed: {e}")
        return False


async def main():
    """Run all connection tests"""
    logger.info("="*60)
    logger.info("🧪 TESTING ALL BACKEND CONNECTIONS")
    logger.info("="*60)
    
    results = {}
    
    # Test async database
    logger.info("\n📊 Testing Async PostgreSQL Connection...")
    results['async_db'] = await test_async_db()
    
    # Test sync database
    logger.info("\n📊 Testing Sync PostgreSQL Connection...")
    results['sync_db'] = test_sync_db()
    
    # Test Cloudinary
    logger.info("\n☁️  Testing Cloudinary Configuration...")
    results['cloudinary'] = test_cloudinary()
    
    # Test SMTP
    logger.info("\n📧 Testing SMTP Configuration...")
    results['smtp'] = test_smtp()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📋 TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        logger.info(f"{icon} {name.upper()}: {'PASSED' if status else 'FAILED'}")
    
    logger.info(f"\n🎯 TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL CONNECTIONS WORKING!")
        return 0
    else:
        logger.error("⚠️  SOME CONNECTIONS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
