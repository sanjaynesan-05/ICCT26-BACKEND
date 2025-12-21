"""
Check and sync team_sequence with existing teams in database
Ensures ICCT-001, ICCT-002 continues from last registered team
"""

import asyncio
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import async_engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_and_sync_sequence():
    """Check current state and sync sequence if needed"""
    
    logger.info("="*70)
    logger.info("🔍 CHECKING TEAM SEQUENCE ALIGNMENT")
    logger.info("="*70)
    
    async with async_engine.begin() as conn:
        
        # Check if team_sequence table exists
        logger.info("\n📋 Checking team_sequence table...")
        result = await conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'team_sequence'
            )
        """))
        sequence_exists = result.scalar()
        
        if sequence_exists:
            result = await conn.execute(text("""
                SELECT last_number FROM team_sequence WHERE id = 1
            """))
            current_seq = result.scalar()
            logger.info(f"✅ team_sequence exists: last_number = {current_seq}")
        else:
            current_seq = None
            logger.warning("⚠️  team_sequence table does NOT exist yet")
        
        # Check existing teams
        logger.info("\n📋 Checking existing teams in database...")
        result = await conn.execute(text("""
            SELECT team_id FROM teams 
            WHERE team_id LIKE 'ICCT-%'
            ORDER BY team_id
        """))
        teams = result.fetchall()
        
        if teams:
            logger.info(f"✅ Found {len(teams)} existing teams:")
            for team in teams:
                logger.info(f"   - {team[0]}")
            
            # Extract highest number
            max_number = 0
            for team in teams:
                team_id = team[0]
                match = re.search(r'ICCT-(\d+)', team_id)
                if match:
                    num = int(match.group(1))
                    max_number = max(max_number, num)
            
            logger.info(f"\n📊 Highest team number: {max_number}")
            logger.info(f"   Next team should be: ICCT-{max_number + 1:03d}")
            
        else:
            max_number = 0
            logger.info("📋 No existing teams found")
            logger.info("   Next team will be: ICCT-001")
        
        # Check alignment
        logger.info("\n" + "="*70)
        logger.info("🔄 ALIGNMENT CHECK")
        logger.info("="*70)
        
        if current_seq is None:
            logger.warning("\n⚠️  SEQUENCE NOT INITIALIZED")
            logger.info(f"   Database has {len(teams)} teams")
            logger.info(f"   Sequence will be created on first registration")
            logger.info(f"   Next team will be: ICCT-001")
            
            if max_number > 0:
                logger.error(f"\n❌ MISMATCH DETECTED!")
                logger.error(f"   Teams exist up to ICCT-{max_number:03d}")
                logger.error(f"   But sequence will start at ICCT-001")
                logger.error(f"   This will cause DUPLICATE team IDs!")
                
                # Offer to fix
                logger.info(f"\n🔧 FIXING: Setting sequence to {max_number}...")
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS team_sequence (
                        id INTEGER PRIMARY KEY,
                        last_number INTEGER NOT NULL DEFAULT 0
                    )
                """))
                await conn.execute(text(f"""
                    INSERT INTO team_sequence (id, last_number)
                    VALUES (1, {max_number})
                    ON CONFLICT (id) DO UPDATE SET last_number = {max_number}
                """))
                logger.info(f"✅ Sequence synchronized to {max_number}")
                logger.info(f"✅ Next team will be: ICCT-{max_number + 1:03d}")
                
        elif current_seq < max_number:
            logger.error(f"\n❌ SEQUENCE OUT OF SYNC!")
            logger.error(f"   Sequence: {current_seq}")
            logger.error(f"   Max team: {max_number}")
            logger.error(f"   Next team would be: ICCT-{current_seq + 1:03d}")
            logger.error(f"   But ICCT-{current_seq + 1:03d} might already exist!")
            
            logger.info(f"\n🔧 FIXING: Updating sequence to {max_number}...")
            await conn.execute(text(f"""
                UPDATE team_sequence 
                SET last_number = {max_number}
                WHERE id = 1
            """))
            logger.info(f"✅ Sequence synchronized to {max_number}")
            logger.info(f"✅ Next team will be: ICCT-{max_number + 1:03d}")
            
        elif current_seq == max_number:
            logger.info(f"\n✅ SEQUENCE PERFECTLY ALIGNED")
            logger.info(f"   Sequence: {current_seq}")
            logger.info(f"   Max team: {max_number}")
            logger.info(f"   Next team will be: ICCT-{current_seq + 1:03d}")
            
        else:  # current_seq > max_number
            logger.info(f"\n✅ SEQUENCE AHEAD (OK)")
            logger.info(f"   Sequence: {current_seq}")
            logger.info(f"   Max team: {max_number}")
            logger.info(f"   Next team will be: ICCT-{current_seq + 1:03d}")
            logger.info(f"   (Gaps are OK - teams might have been deleted)")
        
        logger.info("\n" + "="*70)
        logger.info("✅ SEQUENCE CHECK COMPLETE")
        logger.info("="*70)


if __name__ == "__main__":
    asyncio.run(check_and_sync_sequence())
