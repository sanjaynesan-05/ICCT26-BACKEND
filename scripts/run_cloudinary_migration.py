"""
Database Migration Script for Cloudinary Integration
Converts file columns from Base64 storage to URL storage (TEXT type)

Usage:
    python scripts/run_cloudinary_migration.py

IMPORTANT: Backup your database before running this script!
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from database import async_engine


async def run_migration():
    """Execute the Cloudinary migration SQL script"""
    
    print("=" * 60)
    print("🌩️  CLOUDINARY MIGRATION SCRIPT")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will modify your database schema!")
    print("   - Teams table: pastor_letter, payment_receipt, group_photo → TEXT")
    print("   - Players table: aadhar_file, subscription_file → TEXT")
    print()
    print("📋 Make sure you have:")
    print("   ✅ Backed up your database")
    print("   ✅ Tested on a staging environment first")
    print()
    
    # Ask for confirmation
    response = input("Continue with migration? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Migration cancelled by user")
        return
    
    print()
    print("🔄 Starting migration...")
    print()
    
    try:
        # Read migration SQL file
        migration_file = Path(__file__).parent / "migrate_to_cloudinary.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            print("   Expected location: scripts/migrate_to_cloudinary.sql")
            return
        
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        print("📄 Migration SQL loaded")
        print()
        
        # Execute migration - Split statements since asyncpg doesn't support multiple commands
        async with async_engine.begin() as conn:
            print("🔌 Connected to database")
            print("⚙️  Executing migration...")
            
            # Split SQL by semicolon and execute each statement separately
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            
            for i, stmt in enumerate(statements, 1):
                # Skip comment-only statements
                if stmt.startswith('--'):
                    continue
                
                try:
                    await conn.execute(text(stmt))
                    print(f"  ✓ Statement {i} executed")
                except Exception as e:
                    # Skip if column is already the correct type
                    if "is already of type" in str(e) or "already exists" in str(e):
                        print(f"  ℹ️  Statement {i} skipped (already done)")
                    else:
                        raise
            
            print("✅ Migration executed successfully!")
        
        print()
        print("🔍 Verifying migration...")
        print()
        
        # Verify migration
        async with async_engine.connect() as conn:
            # Check teams table
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'teams' 
                  AND column_name IN ('pastor_letter', 'payment_receipt', 'group_photo')
                ORDER BY column_name;
            """))
            
            teams_columns = result.fetchall()
            
            print("Teams table columns:")
            for col_name, data_type in teams_columns:
                status = "✅" if data_type == "text" else "❌"
                print(f"  {status} {col_name}: {data_type}")
            
            print()
            
            # Check players table
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'players' 
                  AND column_name IN ('aadhar_file', 'subscription_file')
                ORDER BY column_name;
            """))
            
            players_columns = result.fetchall()
            
            print("Players table columns:")
            for col_name, data_type in players_columns:
                status = "✅" if data_type == "text" else "❌"
                print(f"  {status} {col_name}: {data_type}")
            
            print()
            
            # Check if all columns are TEXT
            all_text = (
                all(dt == "text" for _, dt in teams_columns) and
                all(dt == "text" for _, dt in players_columns)
            )
            
            if all_text:
                print("=" * 60)
                print("✅ MIGRATION SUCCESSFUL!")
                print("=" * 60)
                print()
                print("Next steps:")
                print("  1. Restart your backend: uvicorn main:app --reload")
                print("  2. Test registration endpoint with Postman")
                print("  3. Verify files upload to Cloudinary")
                print("  4. Check Cloudinary dashboard for uploaded files")
                print()
            else:
                print("=" * 60)
                print("⚠️  MIGRATION COMPLETED WITH WARNINGS")
                print("=" * 60)
                print()
                print("Some columns may not be TEXT type.")
                print("This could be due to:")
                print("  - Database permissions")
                print("  - Existing data constraints")
                print("  - Column already correct type")
                print()
                print("Please verify manually in your database.")
                print()
    
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ MIGRATION FAILED!")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  1. Check database connection in .env")
        print("  2. Verify you have ALTER TABLE permissions")
        print("  3. Check if columns already exist")
        print("  4. Review error message above")
        print()
        print("Database should be unchanged if migration failed.")
        print()
        raise


async def check_migration_status():
    """Check if migration has already been run"""
    
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'teams' 
                  AND column_name IN ('pastor_letter', 'payment_receipt', 'group_photo')
                ORDER BY column_name;
            """))
            
            teams_columns = result.fetchall()
            
            # Check if all are already TEXT
            if teams_columns and all(dt == "text" for _, dt in teams_columns):
                print()
                print("ℹ️  Migration appears to have already been run!")
                print()
                print("Current column types:")
                for col_name, data_type in teams_columns:
                    print(f"  ✅ {col_name}: {data_type}")
                print()
                
                response = input("Run migration again anyway? (yes/no): ").strip().lower()
                
                if response != 'yes':
                    print("❌ Migration cancelled by user")
                    return False
                
                print()
                return True
            
            return True
    
    except Exception as e:
        print(f"⚠️  Could not check migration status: {str(e)}")
        print("   Proceeding with migration...")
        print()
        return True


async def main():
    """Main entry point"""
    
    # Check if migration already run
    should_continue = await check_migration_status()
    
    if not should_continue:
        return
    
    # Run migration
    await run_migration()
    
    # Close engine
    await async_engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        print("❌ Migration cancelled by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)
