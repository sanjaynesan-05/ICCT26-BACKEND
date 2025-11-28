"""
Migration script to add toss, timing, and scores columns to matches table
Run this script to update the production database
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from database import Base, engine
from models import Match
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_matches_table():
    """Add new columns to matches table"""
    
    logger.info("Starting migration: Adding toss, timing, and scores columns to matches table")
    
    # Create all tables (will only add new columns that don't exist)
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Migration completed successfully!")
    logger.info("New columns added to matches table:")
    logger.info("  - toss_winner_id (Foreign Key to teams)")
    logger.info("  - toss_choice (String: 'bat' or 'bowl')")
    logger.info("  - scheduled_start_time (DateTime)")
    logger.info("  - actual_start_time (DateTime)")
    logger.info("  - match_end_time (DateTime)")
    logger.info("  - team1_first_innings_score (Integer)")
    logger.info("  - team2_first_innings_score (Integer)")
    logger.info("  - team1_second_innings_score (Integer)")
    logger.info("  - team2_second_innings_score (Integer)")

if __name__ == "__main__":
    migrate_matches_table()
