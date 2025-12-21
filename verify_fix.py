"""
Verify the teams.id DEFAULT is permanently set
Ensures the NULL constraint error won't happen again
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import async_engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_fix():
    """Verify teams.id has DEFAULT gen_random_uuid()"""
    
    logger.info("="*70)
    logger.info("🔍 VERIFYING NULL CONSTRAINT FIX")
    logger.info("="*70)
    
    async with async_engine.connect() as conn:
        
        # Check teams.id column default
        logger.info("\n📋 Checking teams.id column configuration...")
        result = await conn.execute(text("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'teams' AND column_name = 'id'
        """))
        row = result.fetchone()
        
        if row:
            col_name, data_type, default, nullable = row
            logger.info(f"   Column: {col_name}")
            logger.info(f"   Type: {data_type}")
            logger.info(f"   Default: {default}")
            logger.info(f"   Nullable: {nullable}")
            
            # Verify fix is in place
            logger.info("\n" + "="*70)
            logger.info("✅ FIX STATUS")
            logger.info("="*70)
            
            if default and 'gen_random_uuid' in str(default):
                logger.info("\n✅ DEFAULT gen_random_uuid() IS SET")
                logger.info("✅ PostgreSQL will auto-generate UUIDs")
                logger.info("✅ NULL constraint error WILL NOT HAPPEN")
                logger.info("\n🎉 The fix is PERMANENT and ACTIVE")
                return True
            else:
                logger.error("\n❌ DEFAULT NOT SET!")
                logger.error(f"   Current default: {default}")
                logger.error("⚠️  NULL constraint error COULD HAPPEN AGAIN")
                return False
        else:
            logger.error("❌ teams.id column not found!")
            return False


if __name__ == "__main__":
    success = asyncio.run(verify_fix())
    sys.exit(0 if success else 1)
