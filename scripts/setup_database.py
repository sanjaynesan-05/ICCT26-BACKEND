#!/usr/bin/env python3
"""
Database setup and testing script for ICCT26
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://username:password@localhost/icct26_db')

async def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)

        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False

async def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    print("\n🏗️  Checking/creating database...")

    # Connect to default postgres database to create our database
    default_url = DATABASE_URL.replace('/icct26_db', '/postgres')

    try:
        engine = create_async_engine(default_url, echo=False)

        async with engine.begin() as conn:
            # Check if database exists
            result = await conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'icct26_db'"))
            exists = result.fetchone()

            if not exists:
                await conn.execute(text("CREATE DATABASE icct26_db"))
                print("✅ Database 'icct26_db' created")
            else:
                print("✅ Database 'icct26_db' already exists")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        print("\n💡 PostgreSQL Setup Instructions:")
        print("1. Install PostgreSQL from: https://www.postgresql.org/download/")
        print("2. Start PostgreSQL service")
        print("3. Set a password for the 'postgres' user:")
        print("   psql -U postgres -c \"ALTER USER postgres PASSWORD 'password';\"")
        print("4. Create the database:")
        print("   createdb -U postgres icct26_db")
        print("5. Or update DATABASE_URL in .env with your actual credentials")
        return False

async def main():
    """Main setup function"""
    print("🚀 ICCT26 Database Setup")
    print("=" * 40)

    # Test connection to default database and create our database
    if not await create_database_if_not_exists():
        return

    # Test connection to our database
    if await test_database_connection():
        print("\n✅ Database setup complete!")
        print("\n📋 Next steps:")
        print("1. Update DATABASE_URL in .env with your actual PostgreSQL credentials")
        print("2. Run: python main.py (this will create tables automatically)")
        print("3. Test registration: python scripts/test_registration_simple.py")
    else:
        print("\n❌ Database setup failed. Please check your PostgreSQL installation.")

if __name__ == "__main__":
    asyncio.run(main())