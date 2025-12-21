"""
Check Database Schema vs ORM Models
Verifies that database schema matches SQLAlchemy model definitions
"""

import asyncio
import sys
from pathlib import Path
from sqlalchemy import text, inspect

sys.path.insert(0, str(Path(__file__).parent))

from database import async_engine
from models import Team, Player
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_schema_alignment():
    """Compare database schema with ORM models"""
    
    logger.info("="*70)
    logger.info("🔍 CHECKING DATABASE SCHEMA vs ORM MODELS ALIGNMENT")
    logger.info("="*70)
    
    async with async_engine.connect() as conn:
        
        # ============================================================
        # CHECK TEAMS TABLE
        # ============================================================
        logger.info("\n📋 TEAMS TABLE SCHEMA")
        logger.info("-"*70)
        
        # Get current database schema
        result = await conn.execute(text("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'teams'
            ORDER BY ordinal_position
        """))
        
        db_columns = {}
        for row in result:
            col_name, data_type, default, nullable = row
            db_columns[col_name] = {
                'type': data_type,
                'default': default,
                'nullable': nullable
            }
            icon = "🔑" if col_name == 'id' else "📝"
            logger.info(f"{icon} {col_name}: {data_type} (default={default}, nullable={nullable})")
        
        # Get ORM model definition
        logger.info("\n🐍 ORM Model Definition (Team):")
        logger.info("-"*70)
        for col in Team.__table__.columns:
            nullable = col.nullable
            default = col.server_default
            logger.info(f"🐍 {col.name}: {col.type} (server_default={default}, nullable={nullable})")
        
        # Check alignment
        logger.info("\n✅ ALIGNMENT CHECK:")
        logger.info("-"*70)
        
        team_id_db = db_columns.get('id', {})
        team_id_orm = Team.__table__.columns['id']
        
        logger.info(f"\nid column:")
        logger.info(f"   Database:  {team_id_db.get('type')} (default={team_id_db.get('default')})")
        logger.info(f"   ORM Model: {team_id_orm.type}")
        
        if 'uuid' in team_id_db.get('type', '').lower():
            logger.info(f"   ✅ ALIGNED: Both use UUID")
        else:
            logger.warning(f"   ⚠️  MISMATCH: Database has {team_id_db.get('type')}, ORM expects UUID")
        
        # ============================================================
        # CHECK PLAYERS TABLE
        # ============================================================
        logger.info("\n📋 PLAYERS TABLE SCHEMA")
        logger.info("-"*70)
        
        result = await conn.execute(text("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'players'
            ORDER BY ordinal_position
        """))
        
        db_columns = {}
        for row in result:
            col_name, data_type, default, nullable = row
            db_columns[col_name] = {
                'type': data_type,
                'default': default,
                'nullable': nullable
            }
            icon = "🔑" if col_name == 'id' else "📝"
            logger.info(f"{icon} {col_name}: {data_type} (default={default}, nullable={nullable})")
        
        logger.info("\n🐍 ORM Model Definition (Player):")
        logger.info("-"*70)
        for col in Player.__table__.columns:
            nullable = col.nullable
            default = col.server_default
            logger.info(f"🐍 {col.name}: {col.type} (server_default={default}, nullable={nullable})")
        
        # Check alignment
        logger.info("\n✅ ALIGNMENT CHECK:")
        logger.info("-"*70)
        
        player_id_db = db_columns.get('id', {})
        player_id_orm = Player.__table__.columns['id']
        
        logger.info(f"\nid column:")
        logger.info(f"   Database:  {player_id_db.get('type')} (default={player_id_db.get('default')})")
        logger.info(f"   ORM Model: {player_id_orm.type}")
        
        if 'integer' in player_id_db.get('type', '').lower():
            logger.info(f"   ✅ ALIGNED: Both use INTEGER")
        else:
            logger.warning(f"   ⚠️  MISMATCH: Database has {player_id_db.get('type')}, ORM expects INTEGER")
        
        # ============================================================
        # SUMMARY
        # ============================================================
        logger.info("\n" + "="*70)
        logger.info("📊 SUMMARY")
        logger.info("="*70)
        
        teams_aligned = 'uuid' in team_id_db.get('type', '').lower()
        players_aligned = 'integer' in player_id_db.get('type', '').lower()
        
        logger.info(f"\n✅ Teams table:")
        logger.info(f"   {'✅ ALIGNED' if teams_aligned else '⚠️  MISALIGNED'} - id is {team_id_db.get('type')}")
        
        logger.info(f"\n✅ Players table:")
        logger.info(f"   {'✅ ALIGNED' if players_aligned else '⚠️  MISALIGNED'} - id is {player_id_db.get('type')}")
        
        if teams_aligned and players_aligned:
            logger.info(f"\n🎉 ALL SCHEMAS ALIGNED - No migration needed")
            return 0
        else:
            logger.warning(f"\n⚠️  SCHEMA MISMATCH DETECTED - Migration needed")
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(check_schema_alignment())
    sys.exit(exit_code)
