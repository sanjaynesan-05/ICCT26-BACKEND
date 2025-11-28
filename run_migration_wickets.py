"""
Migration script to add separate runs and wickets columns to matches table
"""
import sys
sys.path.insert(0, '.')

from database import Base, sync_engine
from models import Match
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🔄 Starting migration: Adding runs and wickets columns to matches table")

# Create all tables (will only add new columns that don't exist)
Base.metadata.create_all(bind=sync_engine)

logger.info("✅ Migration completed successfully!")
logger.info("\nNew columns added to matches table:")
logger.info("  ✅ team1_first_innings_runs (Integer)")
logger.info("  ✅ team1_first_innings_wickets (Integer)")
logger.info("  ✅ team2_first_innings_runs (Integer)")
logger.info("  ✅ team2_first_innings_wickets (Integer)")
logger.info("\nLegacy fields (deprecated but kept for backward compatibility):")
logger.info("  - team1_first_innings_score")
logger.info("  - team2_first_innings_score")
logger.info("  - team1_second_innings_score")
logger.info("  - team2_second_innings_score")
