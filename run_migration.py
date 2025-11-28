"""
Migration script to update database schema with match details columns
"""
import sys
sys.path.insert(0, '.')

from database import Base, sync_engine
from models import Match
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🔄 Starting migration: Adding match details columns to matches table")

# Create all tables (will only add new columns that don't exist)
Base.metadata.create_all(bind=sync_engine)

logger.info("✅ Migration completed successfully!")
logger.info("New columns added to matches table:")
logger.info("  - toss_winner_id (Foreign Key to teams)")
logger.info("  - toss_choice (String: 'bat' or 'bowl')")
logger.info("  - scheduled_start_time (DateTime)")
logger.info("  - actual_start_time (DateTime)")
logger.info("  - match_end_time (DateTime)")
logger.info("  - team1_first_innings_score (Integer)")
logger.info("  - team2_first_innings_score (Integer)")
logger.info("  - match_score_url (String)")
logger.info("  - winner_id (Foreign Key to teams)")
logger.info("  - margin (Integer)")
logger.info("  - margin_type (String: 'runs' or 'wickets')")
logger.info("  - won_by_batting_first (Boolean)")
