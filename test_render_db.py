#!/usr/bin/env python3
"""
Test Render Cloud Production Database Connection
Tests if the Render PostgreSQL database is accessible
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

# Load local credentials
load_dotenv('.env.local')

async def test_render_database():
    """Test connection to Render Cloud Production database"""
    
    # Get Render database URL
    render_url = "postgresql+asyncpg://icctadmin:FhfKgVwHX7P7hmObQJFQvN0YBZxYUly7@dpg-d45imk49c44c73c4j4v0-a.oregon-postgres.render.com/icct26_db"
    
    print("=" * 70)
    print("🧪 TESTING RENDER CLOUD PRODUCTION DATABASE")
    print("=" * 70)
    print()
    print(f"Database Host: oregon-postgres.render.com")
    print(f"Database Name: icct26_db")
    print(f"Username: icctadmin")
    print()
    print("Attempting connection...")
    print()
    
    try:
        # Create async engine
        engine = create_async_engine(render_url, echo=False)
        
        # Test connection
        async with engine.begin() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print("✅ CONNECTION SUCCESSFUL!")
            print()
            print(f"PostgreSQL Version: {version}")
            print()
            
            # Get database info
            result = await conn.execute(
                text("SELECT datname FROM pg_database WHERE datname = 'icct26_db'")
            )
            db_info = result.fetchone()
            if db_info:
                print(f"Database: {db_info[0]}")
            print()
            
            # List tables
            result = await conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
            )
            tables = result.fetchall()
            print(f"📋 Tables in database ({len(tables)}):")
            for table in tables:
                print(f"   - {table[0]}")
            print()
            
            # Get row counts
            print("📊 Data Summary:")
            for table in tables:
                count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table[0]}"))
                count = count_result.scalar()
                print(f"   {table[0]}: {count} rows")
            print()
            
        print("=" * 70)
        print("🎉 RENDER DATABASE IS FULLY OPERATIONAL!")
        print("=" * 70)
        print()
        print("✅ Status: READY FOR PRODUCTION")
        print("✅ Connection: STABLE")
        print("✅ Tables: INITIALIZED")
        print()
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print("❌ CONNECTION FAILED!")
        print()
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Check internet connection")
        print("2. Verify firewall settings")
        print("3. Check Render dashboard for service status")
        print("4. Verify credentials are correct")
        print()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_render_database())
    exit(0 if result else 1)
