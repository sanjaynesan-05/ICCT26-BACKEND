"""
Sync team_sequence with actual teams in database
=================================================
Fixes the sequence to match the highest team ID
"""

import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from database import sync_engine

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def sync_sequence():
    """Sync team_sequence with actual teams"""
    logger.info("=" * 70)
    logger.info("SYNCING TEAM SEQUENCE")
    logger.info("=" * 70)
    logger.info("")
    
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        # 1. Check current sequence
        logger.info("1️⃣ Current Sequence State:")
        logger.info("-" * 70)
        result = session.execute(text("SELECT last_number FROM team_sequence WHERE id = 1"))
        current_seq = result.fetchone()[0]
        logger.info(f"Current sequence value: {current_seq}")
        logger.info("")
        
        # 2. Get all teams and find max team number
        logger.info("2️⃣ Checking Existing Teams:")
        logger.info("-" * 70)
        result = session.execute(text("SELECT team_id FROM teams ORDER BY team_id"))
        teams = result.fetchall()
        
        if not teams:
            logger.info("No teams found - sequence is correct at 0")
            session.close()
            return
        
        logger.info(f"Found {len(teams)} team(s):")
        max_number = 0
        for team in teams:
            team_id = team[0]
            logger.info(f"  - {team_id}")
            
            # Extract number from team_id (e.g., "ICCT-001" -> 1)
            if team_id.startswith("ICCT-"):
                try:
                    number = int(team_id.split("-")[1])
                    if number > max_number:
                        max_number = number
                except:
                    pass
        
        logger.info("")
        logger.info(f"Highest team number: {max_number}")
        logger.info("")
        
        # 3. Update sequence if needed
        logger.info("3️⃣ Updating Sequence:")
        logger.info("-" * 70)
        
        if current_seq == max_number:
            logger.info(f"✅ Sequence is already correct at {current_seq}")
        else:
            logger.info(f"⚠️  Sequence mismatch detected!")
            logger.info(f"   Current: {current_seq}")
            logger.info(f"   Should be: {max_number}")
            logger.info("")
            logger.info(f"Updating sequence to {max_number}...")
            
            session.execute(
                text("UPDATE team_sequence SET last_number = :new_value WHERE id = 1"),
                {"new_value": max_number}
            )
            session.commit()
            
            logger.info(f"✅ Sequence updated successfully!")
        
        logger.info("")
        
        # 4. Verify
        logger.info("4️⃣ Verification:")
        logger.info("-" * 70)
        result = session.execute(text("SELECT last_number FROM team_sequence WHERE id = 1"))
        updated_seq = result.fetchone()[0]
        next_number = updated_seq + 1
        next_team_id = f"ICCT-{next_number:03d}"
        
        logger.info(f"Current sequence: {updated_seq}")
        logger.info(f"Next team ID will be: {next_team_id}")
        logger.info("")
        
        logger.info("=" * 70)
        logger.info("✅ SYNC COMPLETE!")
        logger.info("=" * 70)
        logger.info(f"Sequence: {updated_seq}")
        logger.info(f"Next registration: {next_team_id}")
        logger.info("=" * 70)
        
        session.close()
        
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        session.close()


if __name__ == "__main__":
    asyncio.run(sync_sequence())
