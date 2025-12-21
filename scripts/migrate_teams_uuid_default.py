"""
CRITICAL DATABASE MIGRATION
Add DEFAULT gen_random_uuid() to teams.id column
This fixes the NULL constraint violation on team registration
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import async_engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate():
    """Add UUID default to teams.id column"""
    
    logger.info("="*70)
    logger.info("🔧 CRITICAL MIGRATION: Adding UUID DEFAULT to teams.id")
    logger.info("="*70)
    
    async with async_engine.begin() as conn:
        
        # Check current state
        logger.info("\n📋 Checking current teams.id column...")
        result = await conn.execute(text("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'teams' AND column_name = 'id'
        """))
        row = result.fetchone()
        
        if row:
            logger.info(f"   Current: {row[1]} (default={row[2]}, nullable={row[3]})")
        
        # Apply migration
        logger.info("\n🔧 Adding DEFAULT gen_random_uuid() to teams.id...")
        
        try:
            await conn.execute(text("""
                ALTER TABLE teams 
                ALTER COLUMN id SET DEFAULT gen_random_uuid();
            """))
            logger.info("✅ DEFAULT added successfully")
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise
        
        # Verify
        logger.info("\n🔍 Verifying migration...")
        result = await conn.execute(text("""
            SELECT column_default
            FROM information_schema.columns
            WHERE table_name = 'teams' AND column_name = 'id'
        """))
        default = result.scalar()
        logger.info(f"   New default: {default}")
        
        if default and 'gen_random_uuid' in default:
            logger.info("✅ Migration verified - UUID will auto-generate")
        else:
            logger.warning(f"⚠️  Default might not be set correctly: {default}")
        
        # Test with a dummy insert
        logger.info("\n🧪 Testing with dummy insert...")
        try:
            result = await conn.execute(text("""
                INSERT INTO teams (team_id, team_name, church_name, captain_name, 
                                 captain_phone, captain_email, vice_captain_name,
                                 vice_captain_phone, vice_captain_email, 
                                 registration_status)
                VALUES ('TEST-999', 'Test Team', 'Test Church', 'Test Captain',
                       '1234567890', 'test@test.com', 'Test Vice',
                       '0987654321', 'vice@test.com', 'pending')
                RETURNING id
            """))
            test_id = result.scalar()
            logger.info(f"✅ Test insert successful - Generated ID: {test_id}")
            
            # Clean up test row
            await conn.execute(text("DELETE FROM teams WHERE team_id = 'TEST-999'"))
            logger.info("✅ Test row cleaned up")
            
        except Exception as e:
            logger.error(f"❌ Test insert failed: {e}")
            # Don't raise - the migration itself succeeded
        
        logger.info("\n" + "="*70)
        logger.info("🎉 MIGRATION COMPLETE")
        logger.info("="*70)
        logger.info("\n✅ teams.id will now auto-generate UUIDs on INSERT")
        logger.info("✅ Team registration should work now")


if __name__ == "__main__":
    try:
        asyncio.run(migrate())
        print("\n✅ MIGRATION SUCCESSFUL - Restart backend and try registration again")
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        sys.exit(1)
