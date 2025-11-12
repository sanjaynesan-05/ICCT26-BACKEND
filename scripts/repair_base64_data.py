"""
Database Repair Script - Fix Base64 File Data

This script repairs all existing Base64-encoded file data in the database by:
1. Adding proper data URI prefixes (data:image/png;base64,...)
2. Sanitizing Base64 strings (removing whitespace/newlines)
3. Validating Base64 integrity

Run this script ONCE after deploying the file_utils module to fix historical data.

Usage:
    python scripts/repair_base64_data.py

Environment Variables Required:
    DATABASE_URL - PostgreSQL connection string (from .env or Render)
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.utils.file_utils import format_base64_uri, sanitize_base64


async def repair_database():
    """
    Repair all Base64 file data in the database.
    """
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("   Set it in .env file or export it:")
        print("   export DATABASE_URL='postgresql+asyncpg://user:pass@host/db'")
        return False
    
    # Convert postgres:// to postgresql+asyncpg:// if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    print(f"🔗 Connecting to database...")
    print(f"   URL: {database_url[:50]}...")
    
    # Create async engine
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            print("\n📊 Step 1: Fetching teams data...")
            
            # Fetch all teams
            teams_query = text("""
                SELECT team_id, payment_receipt, pastor_letter
                FROM teams
                WHERE payment_receipt IS NOT NULL OR pastor_letter IS NOT NULL
            """)
            result = await session.execute(teams_query)
            teams_data = result.mappings().all()
            
            print(f"   Found {len(teams_data)} teams with file data")
            
            # Update teams
            teams_updated = 0
            for team in teams_data:
                team_id = team["team_id"]
                updates = {}
                
                # Fix payment_receipt
                if team["payment_receipt"]:
                    fixed_receipt = format_base64_uri(team["payment_receipt"], "image/png")
                    if fixed_receipt and fixed_receipt != team["payment_receipt"]:
                        updates["payment_receipt"] = fixed_receipt
                
                # Fix pastor_letter
                if team["pastor_letter"]:
                    fixed_letter = format_base64_uri(team["pastor_letter"], "application/pdf")
                    if fixed_letter and fixed_letter != team["pastor_letter"]:
                        updates["pastor_letter"] = fixed_letter
                
                # Update if needed
                if updates:
                    update_query = text("""
                        UPDATE teams
                        SET payment_receipt = COALESCE(:payment_receipt, payment_receipt),
                            pastor_letter = COALESCE(:pastor_letter, pastor_letter)
                        WHERE team_id = :team_id
                    """)
                    await session.execute(update_query, {
                        "team_id": team_id,
                        "payment_receipt": updates.get("payment_receipt"),
                        "pastor_letter": updates.get("pastor_letter")
                    })
                    teams_updated += 1
                    print(f"   ✓ Fixed team {team_id}")
            
            print(f"\n✅ Updated {teams_updated} teams")
            
            print("\n📊 Step 2: Fetching players data...")
            
            # Fetch all players
            players_query = text("""
                SELECT id, player_id, aadhar_file, subscription_file
                FROM players
                WHERE aadhar_file IS NOT NULL OR subscription_file IS NOT NULL
            """)
            result = await session.execute(players_query)
            players_data = result.mappings().all()
            
            print(f"   Found {len(players_data)} players with file data")
            
            # Update players
            players_updated = 0
            for player in players_data:
                player_id = player["id"]
                updates = {}
                
                # Fix aadhar_file
                if player["aadhar_file"]:
                    fixed_aadhar = format_base64_uri(player["aadhar_file"], "application/pdf")
                    if fixed_aadhar and fixed_aadhar != player["aadhar_file"]:
                        updates["aadhar_file"] = fixed_aadhar
                
                # Fix subscription_file
                if player["subscription_file"]:
                    fixed_subscription = format_base64_uri(player["subscription_file"], "application/pdf")
                    if fixed_subscription and fixed_subscription != player["subscription_file"]:
                        updates["subscription_file"] = fixed_subscription
                
                # Update if needed
                if updates:
                    update_query = text("""
                        UPDATE players
                        SET aadhar_file = COALESCE(:aadhar_file, aadhar_file),
                            subscription_file = COALESCE(:subscription_file, subscription_file)
                        WHERE id = :player_id
                    """)
                    await session.execute(update_query, {
                        "player_id": player_id,
                        "aadhar_file": updates.get("aadhar_file"),
                        "subscription_file": updates.get("subscription_file")
                    })
                    players_updated += 1
                    if players_updated % 10 == 0:
                        print(f"   ... {players_updated} players fixed")
            
            print(f"\n✅ Updated {players_updated} players")
            
            # Commit all changes
            print("\n💾 Committing changes...")
            await session.commit()
            
            print("\n✅ SUCCESS! Database repair completed.")
            print(f"   Teams updated: {teams_updated}")
            print(f"   Players updated: {players_updated}")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()


def main():
    """
    Main entry point for the repair script.
    """
    print("=" * 60)
    print("🔧 Base64 Database Repair Script")
    print("=" * 60)
    print()
    print("This script will:")
    print("  1. Add data URI prefixes to all file fields")
    print("  2. Sanitize Base64 strings (remove whitespace)")
    print("  3. Validate Base64 integrity")
    print()
    print("⚠️  WARNING: This will modify database records!")
    print()
    
    # Confirm before proceeding
    confirm = input("Type 'YES' to proceed: ")
    if confirm != "YES":
        print("\n❌ Aborted by user.")
        return
    
    print("\n🚀 Starting repair process...\n")
    
    # Run async repair
    success = asyncio.run(repair_database())
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Repair completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Repair failed. Check errors above.")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
