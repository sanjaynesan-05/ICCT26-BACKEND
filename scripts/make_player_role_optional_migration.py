"""
Migration Script: Make Player Role Optional
==========================================
This script updates the database schema to make the player role column nullable.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.config import get_async_engine
from app.utils.structured_logging import setup_logging

logger = setup_logging("make_player_role_optional_migration")


async def migrate_player_role_optional():
    """Make player role column nullable in the database"""
    
    engine = get_async_engine()
    
    try:
        async with engine.begin() as conn:
            logger.info("Starting migration: Make player role optional")
            
            # Check current state
            result = await conn.execute(text("""
                SELECT column_name, is_nullable, data_type
                FROM information_schema.columns 
                WHERE table_name = 'players' 
                AND column_name = 'role'
            """))
            
            current_state = result.fetchone()
            if current_state:
                logger.info(f"Current state: {dict(current_state._mapping)}")
                
                if current_state.is_nullable == 'YES':
                    logger.info("✅ Role column is already nullable. No migration needed.")
                    return True
            
            # Make role column nullable
            logger.info("Making role column nullable...")
            await conn.execute(text("""
                ALTER TABLE players 
                ALTER COLUMN role DROP NOT NULL
            """))
            
            # Add comment
            await conn.execute(text("""
                COMMENT ON COLUMN players.role IS 
                'Player role (optional) - e.g., Batsman, Bowler, All-Rounder, Wicket-Keeper'
            """))
            
            logger.info("✅ Migration completed successfully")
            
            # Verify the change
            result = await conn.execute(text("""
                SELECT column_name, is_nullable, data_type
                FROM information_schema.columns 
                WHERE table_name = 'players' 
                AND column_name = 'role'
            """))
            
            new_state = result.fetchone()
            logger.info(f"New state: {dict(new_state._mapping)}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        await engine.dispose()


async def rollback_migration():
    """Rollback: Make player role column required again"""
    
    engine = get_async_engine()
    
    try:
        async with engine.begin() as conn:
            logger.info("Rolling back migration: Make player role required")
            
            # First, set empty roles to a default value
            await conn.execute(text("""
                UPDATE players 
                SET role = 'Player' 
                WHERE role IS NULL OR role = ''
            """))
            
            # Make role column required
            await conn.execute(text("""
                ALTER TABLE players 
                ALTER COLUMN role SET NOT NULL
            """))
            
            logger.info("✅ Rollback completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Rollback failed: {str(e)}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("🔄 Rolling back migration...")
        asyncio.run(rollback_migration())
    else:
        print("🚀 Running migration...")
        asyncio.run(migrate_player_role_optional())
