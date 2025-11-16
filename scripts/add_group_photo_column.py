#!/usr/bin/env python3
"""
Migration script to add group_photo column to teams table in Neon database
Run with: python scripts/add_group_photo_column.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://icctadmin:FhfKgVwHX7P7hmObQJFQvN0YBZxYUly7@dpg-d45imk49c44c73c4j4v0-a/icct26_db'
)

# Convert to asyncpg URL if needed
if DATABASE_URL.startswith('postgresql://'):
    async_database_url = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
else:
    async_database_url = DATABASE_URL

async def add_group_photo_column():
    """Add group_photo column to teams table"""
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        # Create async engine
        engine = create_async_engine(async_database_url, echo=False)
        
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            print("Connecting to Neon database...")
            
            # Check if column already exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='teams' AND column_name='group_photo'
            """)
            
            result = await session.execute(check_query)
            column_exists = result.scalar() is not None
            
            if column_exists:
                print("✓ group_photo column already exists in teams table")
                return True
            
            # Add the column
            alter_query = text("""
                ALTER TABLE teams 
                ADD COLUMN group_photo TEXT
            """)
            
            print("Adding group_photo column to teams table...")
            await session.execute(alter_query)
            await session.commit()
            
            print("✓ Successfully added group_photo column to teams table")
            return True
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(add_group_photo_column())
    sys.exit(0 if success else 1)
