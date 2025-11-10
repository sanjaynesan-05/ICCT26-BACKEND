"""
Migration script to create tables in Neon PostgreSQL database
This script will create all necessary tables for the ICCT26 application
"""

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv()

# Import models and Base
from models import Team, Player, Base

# Neon Database Connection String - Get from environment variables
NEON_DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://{user}:{password}@ep-winter-salad-ad6doxno-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'
)

# Convert for sync if needed
if NEON_DATABASE_URL.startswith('postgresql+asyncpg://'):
    NEON_DATABASE_URL = NEON_DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    NEON_DATABASE_URL = NEON_DATABASE_URL.replace('?ssl=require', '?sslmode=require')

# Async version for asyncpg
NEON_DATABASE_URL_ASYNC = NEON_DATABASE_URL
if NEON_DATABASE_URL.startswith('postgresql://'):
    NEON_DATABASE_URL_ASYNC = NEON_DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
    NEON_DATABASE_URL_ASYNC = NEON_DATABASE_URL_ASYNC.replace('?sslmode=require', '?ssl=require')


def create_tables_sync():
    """Create all tables using synchronous connection"""
    print("=" * 70)
    print("🚀 ICCT26 Database Migration to Neon PostgreSQL")
    print("=" * 70)
    print(f"\n📡 Connecting to Neon database...")
    print(f"   Host: ep-winter-salad-ad6doxno-pooler.c-2.us-east-1.aws.neon.tech")
    print(f"   Database: neondb\n")
    
    try:
        # Create synchronous engine
        engine = create_engine(
            NEON_DATABASE_URL,
            pool_pre_ping=True,
            echo=True  # Show SQL statements
        )
        
        print("✅ Connected to Neon database successfully!\n")
        print("=" * 70)
        print("📋 Creating Tables...")
        print("=" * 70)
        
        # Drop all tables first (careful!)
        print("\n⚠️  Dropping existing tables if any...")
        Base.metadata.drop_all(bind=engine)
        print("✅ Existing tables dropped\n")
        
        # Create all tables
        print("🔨 Creating new tables from models...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!\n")
        
        # Verify tables
        print("=" * 70)
        print("🔍 Verifying Tables...")
        print("=" * 70)
        
        with engine.connect() as conn:
            # Check teams table
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'teams'
                ORDER BY ordinal_position
            """))
            
            print("\n📊 TEAMS Table Structure:")
            print("-" * 70)
            teams_columns = result.fetchall()
            for col in teams_columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"   ✓ {col[0]:<25} {col[1]:<20} {nullable}")
            
            # Check players table
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'players'
                ORDER BY ordinal_position
            """))
            
            print("\n📊 PLAYERS Table Structure:")
            print("-" * 70)
            players_columns = result.fetchall()
            for col in players_columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"   ✓ {col[0]:<25} {col[1]:<20} {nullable}")
            
            # Check constraints
            result = conn.execute(text("""
                SELECT tc.constraint_name, tc.constraint_type, tc.table_name
                FROM information_schema.table_constraints tc
                WHERE tc.table_name IN ('teams', 'players')
                ORDER BY tc.table_name, tc.constraint_type
            """))
            
            print("\n🔒 Constraints:")
            print("-" * 70)
            constraints = result.fetchall()
            for constraint in constraints:
                print(f"   ✓ {constraint[2]:<15} {constraint[1]:<20} {constraint[0]}")
            
            conn.commit()
        
        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📝 Summary:")
        print(f"   • Teams table: {len(teams_columns)} columns")
        print(f"   • Players table: {len(players_columns)} columns")
        print(f"   • Total constraints: {len(constraints)}")
        print("\n🎉 Your Neon database is ready for deployment!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ MIGRATION FAILED!")
        print("=" * 70)
        print(f"\n🔴 Error: {str(e)}")
        print("\nPlease check:")
        print("  1. Database connection string is correct")
        print("  2. Network connectivity to Neon")
        print("  3. Database credentials are valid")
        print("  4. SSL requirements are met")
        return False


async def test_async_connection():
    """Test async connection to Neon database"""
    print("\n" + "=" * 70)
    print("🔄 Testing Async Connection...")
    print("=" * 70)
    
    try:
        engine = create_async_engine(
            NEON_DATABASE_URL_ASYNC,
            pool_pre_ping=True,
            echo=False
        )
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"\n✅ Async connection successful!")
            print(f"   PostgreSQL Version: {version[0][:50]}...")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"\n❌ Async connection failed: {str(e)}")
        return False


def main():
    """Main migration function"""
    print("\n")
    
    # Create tables synchronously
    success = create_tables_sync()
    
    if success:
        # Test async connection
        print("\n")
        asyncio.run(test_async_connection())
        
        print("\n" + "=" * 70)
        print("📚 NEXT STEPS:")
        print("=" * 70)
        print("\n1. Update your .env.local file:")
        print("   DATABASE_URL='postgresql+asyncpg://neondb_owner:npg_3ON2HQpSvJBT@ep-winter-salad-ad6doxno-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'")
        print("\n2. Test your application:")
        print("   python main.py")
        print("\n3. Verify endpoints:")
        print("   - http://127.0.0.1:8000/health")
        print("   - http://127.0.0.1:8000/admin/teams")
        print("\n4. Deploy to production!")
        print("=" * 70 + "\n")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
