"""
Migration to add toss, timing, and innings score columns to matches table
"""

from database import sync_engine
from models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    logger.info("Starting migration...")
    
    # This will create all tables and add any missing columns
    Base.metadata.create_all(bind=sync_engine)
    
    logger.info("✅ Migration completed!")

if __name__ == "__main__":
    run_migration()
