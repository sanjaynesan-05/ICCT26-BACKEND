"""
Verify Database Upload - Check what was stored in the database
"""
import asyncio
from database import get_db_async, async_engine
from models import Team, Player
from sqlalchemy import select

async def verify_uploads():
    """Check database for recent uploads"""
    print("=" * 80)
    print("🔍 VERIFYING DATABASE UPLOADS")
    print("=" * 80)
    
    async for db in get_db_async():
        # Get most recent team
        result = await db.execute(
            select(Team).order_by(Team.id.desc()).limit(3)
        )
        teams = result.scalars().all()
        
        if not teams:
            print("\n❌ No teams found in database")
            return
        
        for team in teams:
            print(f"\n📋 Team: {team.team_id} - {team.team_name}")
            print(f"   Created: {team.created_at}")
            print(f"   Pastor Letter: {team.pastor_letter[:80] if team.pastor_letter else 'None'}...")
            print(f"   Payment Receipt: {team.payment_receipt[:80] if team.payment_receipt else 'None'}...")
            print(f"   Group Photo: {team.group_photo[:80] if team.group_photo else 'None'}...")
            
            # Get players for this team
            player_result = await db.execute(
                select(Player).where(Player.team_id == team.team_id).order_by(Player.id)
            )
            players = player_result.scalars().all()
            
            print(f"\n   Players ({len(players)}):")
            for player in players:
                print(f"   ├─ {player.player_id}: {player.name} ({player.role})")
                print(f"   │  Aadhar: {player.aadhar_file[:80] if player.aadhar_file else 'NULL'}...")
                print(f"   │  Subscription: {player.subscription_file[:80] if player.subscription_file else 'NULL'}...")
                
                # Extract folder path from URL
                if player.aadhar_file:
                    # Cloudinary URLs look like: https://res.cloudinary.com/{cloud}/image/upload/{folder}/{filename}
                    parts = player.aadhar_file.split('/upload/')
                    if len(parts) > 1:
                        folder_and_file = parts[1]
                        print(f"   │  📁 Aadhar folder path: {folder_and_file}")
                
                if player.subscription_file:
                    parts = player.subscription_file.split('/upload/')
                    if len(parts) > 1:
                        folder_and_file = parts[1]
                        print(f"   │  📁 Subscription folder path: {folder_and_file}")
            
            print("   " + "-" * 76)

if __name__ == "__main__":
    asyncio.run(verify_uploads())
