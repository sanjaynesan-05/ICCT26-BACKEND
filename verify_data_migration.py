"""
Verify database has the new runs and wickets columns populated
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
    # Get all matches
    matches = db.query(Match).all()
    
    logger.info(f"Checking {len(matches)} matches in database...")
    
    for match in matches:
        logger.info(f"\nMatch ID: {match.id} ({match.round} Match {match.match_number})")
        logger.info(f"  Status: {match.status}")
        logger.info(f"  Team 1: runs={match.team1_first_innings_runs}, wickets={match.team1_first_innings_wickets}")
        logger.info(f"  Team 2: runs={match.team2_first_innings_runs}, wickets={match.team2_first_innings_wickets}")
        
        if match.team1_first_innings_runs or match.team2_first_innings_runs:
            logger.info(f"  ✅ Populated with runs and wickets data!")
    
except Exception as e:
    logger.error(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
