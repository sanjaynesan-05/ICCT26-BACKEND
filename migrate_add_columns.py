"""
Direct SQL migration script to add new columns using raw SQL
"""
import sys
sys.path.insert(0, '.')

from database import sync_engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("🔄 Starting SQL migration: Adding runs and wickets columns")
    
    with sync_engine.connect() as connection:
        # Check if columns already exist before adding them
        
        # Add team1_first_innings_runs
        try:
            connection.execute(text("""
                ALTER TABLE matches 
                ADD COLUMN team1_first_innings_runs INTEGER;
            """))
            logger.info("✅ Added team1_first_innings_runs column")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                logger.info("⚠️  team1_first_innings_runs column already exists")
            else:
                raise
        
        # Add team1_first_innings_wickets
        try:
            connection.execute(text("""
                ALTER TABLE matches 
                ADD COLUMN team1_first_innings_wickets INTEGER;
            """))
            logger.info("✅ Added team1_first_innings_wickets column")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                logger.info("⚠️  team1_first_innings_wickets column already exists")
            else:
                raise
        
        # Add team2_first_innings_runs
        try:
            connection.execute(text("""
                ALTER TABLE matches 
                ADD COLUMN team2_first_innings_runs INTEGER;
            """))
            logger.info("✅ Added team2_first_innings_runs column")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                logger.info("⚠️  team2_first_innings_runs column already exists")
            else:
                raise
        
        # Add team2_first_innings_wickets
        try:
            connection.execute(text("""
                ALTER TABLE matches 
                ADD COLUMN team2_first_innings_wickets INTEGER;
            """))
            logger.info("✅ Added team2_first_innings_wickets column")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                logger.info("⚠️  team2_first_innings_wickets column already exists")
            else:
                raise
        
        connection.commit()
        logger.info("✅ SQL migration completed!")
        
except Exception as e:
    logger.error(f"❌ SQL migration failed: {str(e)}")
    import traceback
    traceback.print_exc()
