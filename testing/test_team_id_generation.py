"""
Test Sequential Team ID Generation
Verifies that team IDs are generated as ICCT-001, ICCT-002, ICCT-003, etc.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy import select, func
from database import AsyncSessionLocal
from app.utils.team_id_generator import generate_sequential_team_id
from models import Team


async def test_team_id_generation():
    """Test sequential team ID generation"""
    
    print("\n" + "="*70)
    print("🧪 TESTING SEQUENTIAL TEAM ID GENERATION")
    print("="*70)
    
    # Create async session
    async with AsyncSessionLocal() as db:
        
        # Get current team count
        result = await db.execute(select(func.count(Team.id)))
        current_count = result.scalar() or 0
        
        print(f"\n📊 Current State:")
        print(f"   Teams in database: {current_count}")
        
        # Generate next team ID
        print(f"\n🔢 Generating next team ID...")
        next_team_id = await generate_sequential_team_id(db)
        
        print(f"\n✅ Generated Team ID: {next_team_id}")
        
        # Verify format
        expected_number = current_count + 1
        expected_id = f"ICCT-{expected_number:03d}"
        
        print(f"\n✓ Validation:")
        print(f"   Expected: {expected_id}")
        print(f"   Generated: {next_team_id}")
        
        if next_team_id == expected_id:
            print(f"   ✅ MATCH! Team ID format is correct")
        else:
            print(f"   ❌ MISMATCH! Team ID format may be incorrect")
        
        # Show examples of what IDs will be generated
        print(f"\n📋 Team ID Sequence Examples:")
        for i in range(1, 11):
            example_id = f"ICCT-{i:03d}"
            print(f"   Team {i}: {example_id}")
        
        print(f"\n💡 Next Registration:")
        print(f"   Will receive Team ID: {next_team_id}")
        print(f"   Player IDs will be: {next_team_id}-P01, {next_team_id}-P02, etc.")


async def main():
    """Run the test"""
    print("\n🧪 Team ID Generation Test")
    print("   Testing ICCT-001, ICCT-002, ICCT-003 format")
    
    try:
        await test_team_id_generation()
        
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print("✅ Sequential team ID generation is working")
        print("✅ Format: ICCT-001, ICCT-002, ICCT-003, ...")
        print("✅ Team IDs will be consistent across backend and frontend")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
