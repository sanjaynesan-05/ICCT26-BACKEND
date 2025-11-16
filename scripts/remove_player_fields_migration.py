#!/usr/bin/env python3
"""
Migration Script: Remove age, phone, jersey_number from players table
Date: 2025-11-17
Usage: python scripts/remove_player_fields_migration.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from database import get_async_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def remove_player_fields():
    """Remove age, phone, jersey_number columns from players table"""
    
    try:
        # Get async engine
        engine = get_async_engine()
        
        # Create async session
        async_session = sessionmaker(
            engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        async with async_session() as session:
            logger.info("🔧 Starting migration: Removing player fields (age, phone, jersey_number)")
            
            # Check if columns exist before dropping
            check_columns_query = text("""
                SELECT column_name
                FROM information_schema.columns 
                WHERE table_name = 'players' 
                AND column_name IN ('age', 'phone', 'jersey_number')
            """)
            
            result = await session.execute(check_columns_query)
            existing_columns = [row[0] for row in result.fetchall()]
            
            if not existing_columns:
                logger.info("✅ No columns to remove - already clean!")
                return
            
            logger.info(f"📋 Found columns to remove: {', '.join(existing_columns)}")
            
            # Drop age column
            if 'age' in existing_columns:
                logger.info("Dropping 'age' column...")
                await session.execute(text("ALTER TABLE players DROP COLUMN IF EXISTS age"))
                logger.info("✅ Dropped 'age' column")
            
            # Drop phone column
            if 'phone' in existing_columns:
                logger.info("Dropping 'phone' column...")
                await session.execute(text("ALTER TABLE players DROP COLUMN IF EXISTS phone"))
                logger.info("✅ Dropped 'phone' column")
            
            # Drop jersey_number column
            if 'jersey_number' in existing_columns:
                logger.info("Dropping 'jersey_number' column...")
                await session.execute(text("ALTER TABLE players DROP COLUMN IF EXISTS jersey_number"))
                logger.info("✅ Dropped 'jersey_number' column")
            
            # Commit changes
            await session.commit()
            logger.info("✅ Migration committed successfully")
            
            # Verify final structure
            logger.info("\n📊 Final players table structure:")
            verify_query = text("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable
                FROM 
                    information_schema.columns 
                WHERE 
                    table_name = 'players'
                ORDER BY 
                    ordinal_position
            """)
            
            result = await session.execute(verify_query)
            columns = result.fetchall()
            
            for col in columns:
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                logger.info(f"  - {col[0]}: {col[1]} ({nullable})")
            
            logger.info("\n✅ Migration completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(remove_player_fields())
