"""
Direct SQL migration to add new columns to matches table
"""

from database import SessionLocal
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    db = SessionLocal()
    
    try:
        logger.info("Adding new columns to matches table...")
        
        # List of columns to add
        migrations = [
            ("toss_winner_id", "ALTER TABLE matches ADD COLUMN toss_winner_id INTEGER REFERENCES teams(id) ON DELETE SET NULL"),
            ("toss_choice", "ALTER TABLE matches ADD COLUMN toss_choice VARCHAR(10)"),
            ("scheduled_start_time", "ALTER TABLE matches ADD COLUMN scheduled_start_time TIMESTAMP"),
            ("actual_start_time", "ALTER TABLE matches ADD COLUMN actual_start_time TIMESTAMP"),
            ("match_end_time", "ALTER TABLE matches ADD COLUMN match_end_time TIMESTAMP"),
            ("team1_first_innings_score", "ALTER TABLE matches ADD COLUMN team1_first_innings_score INTEGER"),
            ("team2_first_innings_score", "ALTER TABLE matches ADD COLUMN team2_first_innings_score INTEGER"),
            ("team1_second_innings_score", "ALTER TABLE matches ADD COLUMN team1_second_innings_score INTEGER"),
            ("team2_second_innings_score", "ALTER TABLE matches ADD COLUMN team2_second_innings_score INTEGER"),
        ]
        
        for col_name, sql in migrations:
            try:
                db.execute(text(sql))
                db.commit()
                logger.info(f"✅ Added column: {col_name}")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info(f"⏭️  Column {col_name} already exists, skipping...")
                else:
                    logger.warning(f"Error adding {col_name}: {str(e)}")
                db.rollback()
        
        logger.info("✅ Migration completed!")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
