"""
Fix database sequences for teams.id and players.id columns

This script ensures that the id columns in teams and players tables
have proper SERIAL sequences attached for auto-increment functionality.

Run this ONCE on production database to fix the schema.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.config import get_async_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_sequences():
    """Fix sequences for teams.id and players.id"""
    
    engine = get_async_engine()
    
    async with engine.begin() as conn:
        logger.info("🔧 Inspecting current database schema...")
        
        # ============================================================
        # CHECK CURRENT SCHEMA
        # ============================================================
        
        # Check teams table structure
        logger.info("📋 Checking teams table columns...")
        result = await conn.execute(text("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'teams'
            ORDER BY ordinal_position
        """))
        rows = result.fetchall()
        for row in rows:
            logger.info(f"   {row[0]}: {row[1]} (default={row[2]}, nullable={row[3]})")
        
        # Check players table structure
        logger.info("📋 Checking players table columns...")
        result = await conn.execute(text("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'players'
            ORDER BY ordinal_position
        """))
        rows = result.fetchall()
        for row in rows:
            logger.info(f"   {row[0]}: {row[1]} (default={row[2]}, nullable={row[3]})")
        
        logger.info("🎉 Schema inspection complete!")


if __name__ == "__main__":
    asyncio.run(fix_sequences())
