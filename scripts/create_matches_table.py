"""
Database migration script to create matches table
Run this once to set up the matches table in the database
"""

import asyncio
import logging
import sys
import os

# Add parent directory to Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import sync_engine
from models import Base, Match, Team

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_matches_table():
    """Create matches table if it doesn't exist"""
    try:
        logger.info("Creating matches table...")
        
        # Create all tables (SQLAlchemy will only create missing ones)
        Base.metadata.create_all(bind=sync_engine)
        
        logger.info("✅ Matches table created successfully")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error creating matches table: {str(e)}")
        return False


if __name__ == "__main__":
    # Run migration
    result = asyncio.run(create_matches_table())
    if result:
        print("\n✅ Database migration completed successfully!")
        print("Matches table is now ready for use.")
    else:
        print("\n❌ Database migration failed. Check logs above.")
