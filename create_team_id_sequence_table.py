"""
Create team_id_sequence table for race-safe team ID generation
"""
import asyncio
import logging
from database import async_engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_team_id_sequence_table():
    """Create team_id_sequence table if not exists"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS team_id_sequence (
        id SERIAL PRIMARY KEY,
        current_value INTEGER NOT NULL DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    insert_initial_value_sql = """
    INSERT INTO team_id_sequence (current_value) 
    SELECT 0 
    WHERE NOT EXISTS (SELECT 1 FROM team_id_sequence);
    """
    
    try:
        logger.info("🔧 Creating team_id_sequence table...")
        
        async with async_engine.begin() as conn:
            # Create table
            await conn.execute(text(create_table_sql))
            logger.info("   ✅ Table created/verified")
            
            # Insert initial value if table is empty
            await conn.execute(text(insert_initial_value_sql))
            logger.info("   ✅ Initial value inserted")
        
        # Verify table exists
        async with async_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT current_value FROM team_id_sequence LIMIT 1")
            )
            row = result.fetchone()
            if row is not None:
                logger.info(f"   ✅ Table verified - current value: {row[0]}")
            else:
                logger.warning("   ⚠️ Table exists but no data found")
        
        logger.info("✅ team_id_sequence table setup complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating team_id_sequence table: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Main execution"""
    logger.info("="*70)
    logger.info("🚀 Creating team_id_sequence Table")
    logger.info("="*70)
    
    success = await create_team_id_sequence_table()
    
    if success:
        logger.info("\n✅ SUCCESS - Table is ready")
        return 0
    else:
        logger.error("\n❌ FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
