"""
Check database tables and create match_details as alias/view if needed
"""
import asyncio
import logging
from database import async_engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_and_fix_match_details():
    """Check if match_details table exists and create as view if needed"""
    
    logger.info("="*70)
    logger.info("🔍 Checking match_details table status")
    logger.info("="*70)
    
    try:
        async with async_engine.connect() as conn:
            # Check if match_details table exists
            result = await conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'match_details'
                    )
                """)
            )
            table_exists = result.fetchone()[0]
            
            if table_exists:
                logger.info("✅ match_details table already exists")
                
                # Check what it is (table or view)
                result = await conn.execute(
                    text("""
                        SELECT table_type 
                        FROM information_schema.tables 
                        WHERE table_name = 'match_details'
                    """)
                )
                table_type = result.fetchone()[0]
                logger.info(f"   Type: {table_type}")
                return True
            
            # Check if matches table exists
            result = await conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'matches'
                    )
                """)
            )
            matches_exists = result.fetchone()[0]
            
            if not matches_exists:
                logger.error("❌ matches table does not exist! Cannot create match_details view")
                return False
            
            logger.info("📋 matches table exists")
            logger.info("💡 Creating match_details as a VIEW (alias) to matches table...")
            
            # Create match_details as a view (alias) to matches table
            create_view_sql = """
                CREATE OR REPLACE VIEW match_details AS
                SELECT * FROM matches;
            """
            
            async with async_engine.begin() as conn:
                await conn.execute(text(create_view_sql))
                logger.info("✅ match_details view created successfully")
                logger.info("   (match_details is now an alias for matches table)")
            
            # Verify the view was created
            async with async_engine.connect() as conn:
                result = await conn.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.views 
                            WHERE table_name = 'match_details'
                        )
                    """)
                )
                view_exists = result.fetchone()[0]
                
                if view_exists:
                    logger.info("✅ Verification successful - match_details view exists")
                    
                    # Count records
                    result = await conn.execute(text("SELECT COUNT(*) FROM match_details"))
                    count = result.fetchone()[0]
                    logger.info(f"   Records accessible: {count}")
                    return True
                else:
                    logger.error("❌ Verification failed - view was not created")
                    return False
        
    except Exception as e:
        logger.error(f"❌ Error checking/creating match_details: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Main execution"""
    logger.info("\n🚀 Match Details Table Check and Fix")
    logger.info("="*70)
    
    success = await check_and_fix_match_details()
    
    logger.info("\n" + "="*70)
    if success:
        logger.info("✅ SUCCESS - match_details is ready")
        logger.info("\nNote: match_details is a VIEW (database alias) that points to")
        logger.info("      the matches table. Both can be used interchangeably.")
        return 0
    else:
        logger.error("❌ FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
