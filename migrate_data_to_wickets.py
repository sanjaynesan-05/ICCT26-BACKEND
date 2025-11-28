"""
Data migration script to populate runs and wickets from legacy score fields
For matches with scores recorded, we'll copy runs to new columns.
Wickets will default to reasonable values since we don't have that data.
"""
import sys
sys.path.insert(0, '.')

from database import SessionLocal
from models import Match
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SessionLocal()

try:
    logger.info("🔄 Starting data migration: Populating new runs/wickets columns")
    
    # Get all matches with scores recorded
    matches = db.query(Match).filter(
        (Match.team1_first_innings_score != None) | (Match.team2_first_innings_score != None)
    ).all()
    
    logger.info(f"Found {len(matches)} matches with scores")
    
    migrated_count = 0
    for match in matches:
        try:
            # Copy team1 score
            if match.team1_first_innings_score is not None and match.team1_first_innings_runs is None:
                match.team1_first_innings_runs = match.team1_first_innings_score
                # Default wickets to a reasonable value (8 out of 10 batsmen lost)
                if match.team1_first_innings_wickets is None:
                    match.team1_first_innings_wickets = 8
                migrated_count += 1
            
            # Copy team2 score
            if match.team2_first_innings_score is not None and match.team2_first_innings_runs is None:
                match.team2_first_innings_runs = match.team2_first_innings_score
                # Default wickets to a reasonable value (8 out of 10 batsmen lost)
                if match.team2_first_innings_wickets is None:
                    match.team2_first_innings_wickets = 8
                migrated_count += 1
            
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error migrating match {match.id}: {str(e)}")
    
    logger.info(f"✅ Data migration completed!")
    logger.info(f"   Migrated {migrated_count} team scores to new runs/wickets columns")
    logger.info(f"   Wickets default: 8 (out of 10) for all migrated scores")
    
except Exception as e:
    db.rollback()
    logger.error(f"❌ Data migration failed: {str(e)}")
finally:
    db.close()
