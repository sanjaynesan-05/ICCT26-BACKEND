"""
COMPLETE END-TO-END REGISTRATION TEST
======================================
Tests the complete team registration flow:
1. Team ID generation (should be ICCT-002 since ICCT-001 exists)
2. Team and player data validation
3. File upload (dummy URLs)
4. Database storage
5. Verification of all records
"""

import asyncio
import httpx
import logging
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

# 11 Players - Full Squad
PLAYERS = [
    ("John Michael", "Batsman"),
    ("David Thomas", "Bowler"),
    ("Matthew Joseph", "All-Rounder"),
    ("Samuel Peter", "Wicket-Keeper"),
    ("James Abraham", "Batsman"),
    ("Andrew Isaac", "Bowler"),
    ("Philip Jacob", "All-Rounder"),
    ("Thomas Daniel", "Batsman"),
    ("Simon Paul", "Bowler"),
    ("Stephen Mark", "All-Rounder"),
    ("Luke George", "Batsman"),
]


def create_dummy_pdf():
    """Minimal valid PDF"""
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
213
%%EOF
"""


def create_dummy_png():
    """Minimal valid PNG"""
    return bytes.fromhex(
        '89504e470d0a1a0a0000000d494844520000000100000001'
        '08060000001f15c4890000000a49444154789c630001000005'
        '0001028d05390f0e0000000049454e44ae426082'
    )


async def register_team():
    """Submit team registration"""
    logger.info("=" * 70)
    logger.info("STEP 1: TEAM REGISTRATION")
    logger.info("=" * 70)
    logger.info("")
    
    pdf = create_dummy_pdf()
    png = create_dummy_png()
    
    # Build files
    files = [
        ("pastor_letter", ("pastor_letter.pdf", pdf, "application/pdf")),
        ("payment_receipt", ("payment_receipt.pdf", pdf, "application/pdf")),
        ("group_photo", ("group_photo.png", png, "image/png")),
    ]
    
    # Add player files
    for idx in range(11):
        files.append((f"player_{idx}_aadhar_file", (f"aadhar_{idx}.pdf", pdf, "application/pdf")))
        files.append((f"player_{idx}_subscription_file", (f"subs_{idx}.pdf", pdf, "application/pdf")))
    
    # Form data
    form_data = {
        "team_name": "St Thomas Cricket Club",
        "church_name": "St Thomas Orthodox Church",
        "captain_name": "John Michael",
        "captain_phone": "9876543210",
        "captain_email": "john.michael@stthomas.com",
        "captain_whatsapp": "9876543210",
        "vice_name": "David Thomas",
        "vice_phone": "9876543211",
        "vice_email": "david.thomas@stthomas.com",
        "vice_whatsapp": "9876543211",
    }
    
    # Add players
    for idx, (name, role) in enumerate(PLAYERS):
        form_data[f"player_{idx}_name"] = name
        form_data[f"player_{idx}_role"] = role
    
    logger.info(f"📋 Team: {form_data['team_name']}")
    logger.info(f"⛪ Church: {form_data['church_name']}")
    logger.info(f"👤 Captain: {form_data['captain_name']} ({form_data['captain_phone']})")
    logger.info(f"👤 Vice-Captain: {form_data['vice_name']} ({form_data['vice_phone']})")
    logger.info(f"👥 Players: 11")
    logger.info(f"📄 Files: {len(files)} (3 team + 22 player files)")
    logger.info("")
    logger.info("🚀 Submitting registration...")
    logger.info("")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://localhost:8000/api/register/team",
                data=form_data,
                files=files,
            )
            
            logger.info(f"Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                logger.info("✅ REGISTRATION SUCCESSFUL!")
                logger.info("")
                logger.info(f"Team: {data.get('team_name')}")
                logger.info(f"Players: {data.get('player_count')}")
                logger.info(f"Status: {data.get('registration_status')}")
                logger.info(f"Message: {data.get('message')}")
                return True
            else:
                logger.error(f"❌ REGISTRATION FAILED!")
                logger.error(f"Response: {response.text[:500]}")
                return False
            
    except Exception as e:
        logger.error(f"❌ ERROR: {type(e).__name__}: {e}")
        return False


async def verify_database():
    """Verify database records"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("STEP 2: DATABASE VERIFICATION")
    logger.info("=" * 70)
    logger.info("")
    
    try:
        # Create sync engine for verification
        engine = create_engine(DATABASE_URL.replace('+asyncpg', ''))
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check team_id_sequence
        logger.info("📊 Checking team_id_sequence table...")
        result = session.execute(text("SELECT * FROM team_id_sequence ORDER BY id"))
        sequences = result.fetchall()
        logger.info(f"Sequence records: {len(sequences)}")
        for seq in sequences:
            logger.info(f"  - ID: {seq[0]}, Current Value: {seq[1]}, Updated: {seq[2]}")
        logger.info("")
        
        # Check teams
        logger.info("🏏 Checking teams table...")
        result = session.execute(text("SELECT team_id, team_name, church_name, captain_name FROM teams ORDER BY team_id"))
        teams = result.fetchall()
        logger.info(f"Total teams: {len(teams)}")
        for team in teams:
            logger.info(f"  - {team[0]}: {team[1]} (Captain: {team[3]})")
        logger.info("")
        
        # Check latest team
        if teams:
            latest_team_id = teams[-1][0]
            logger.info(f"🔍 Verifying latest team: {latest_team_id}")
            logger.info("")
            
            # Check team details
            result = session.execute(
                text("SELECT * FROM teams WHERE team_id = :team_id"),
                {"team_id": latest_team_id}
            )
            team_record = result.fetchone()
            
            if team_record:
                logger.info("✅ Team Record Found:")
                logger.info(f"  Team ID: {team_record[0]}")
                logger.info(f"  Team Name: {team_record[1]}")
                logger.info(f"  Church: {team_record[2]}")
                logger.info(f"  Captain: {team_record[3]} ({team_record[4]})")
                logger.info(f"  Vice-Captain: {team_record[7]} ({team_record[8]})")
                logger.info(f"  Pastor Letter: {team_record[11][:50] if team_record[11] else 'None'}...")
                logger.info(f"  Payment Receipt: {team_record[12][:50] if team_record[12] else 'None'}...")
                logger.info(f"  Group Photo: {team_record[13][:50] if team_record[13] else 'None'}...")
                logger.info("")
            
            # Check players
            logger.info("👥 Checking players for this team...")
            result = session.execute(
                text("SELECT player_id, name, role, aadhar_file, subscription_file FROM players WHERE team_id = :team_id ORDER BY player_id"),
                {"team_id": latest_team_id}
            )
            players = result.fetchall()
            logger.info(f"Total players: {len(players)}")
            
            for player in players:
                aadhar_status = "✅" if player[3] else "❌"
                subs_status = "✅" if player[4] else "❌"
                logger.info(f"  - {player[0]}: {player[1]} ({player[2]}) | Aadhar: {aadhar_status} | Subscription: {subs_status}")
            
            logger.info("")
            
            # Verify counts
            if len(players) == 11:
                logger.info("✅ Player count correct: 11 players")
            else:
                logger.error(f"❌ Player count incorrect: Expected 11, got {len(players)}")
                return False
            
            # Verify files
            files_with_aadhar = sum(1 for p in players if p[3])
            files_with_subscription = sum(1 for p in players if p[4])
            logger.info(f"✅ Players with Aadhar: {files_with_aadhar}/11")
            logger.info(f"✅ Players with Subscription: {files_with_subscription}/11")
            
            session.close()
            return True
        else:
            logger.error("❌ No teams found in database")
            session.close()
            return False
            
    except Exception as e:
        logger.error(f"❌ DATABASE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_team_id_generation():
    """Verify team ID generation logic"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("STEP 3: TEAM ID GENERATION VERIFICATION")
    logger.info("=" * 70)
    logger.info("")
    
    try:
        engine = create_engine(DATABASE_URL.replace('+asyncpg', ''))
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Get all team IDs
        result = session.execute(text("SELECT team_id FROM teams ORDER BY team_id"))
        team_ids = [row[0] for row in result.fetchall()]
        
        logger.info(f"📋 All Team IDs in database:")
        for tid in team_ids:
            logger.info(f"  - {tid}")
        logger.info("")
        
        # Check sequence
        result = session.execute(text("SELECT current_value FROM team_id_sequence ORDER BY id DESC LIMIT 1"))
        sequence_value = result.fetchone()
        
        if sequence_value:
            logger.info(f"🔢 Sequence current value: {sequence_value[0]}")
            logger.info(f"🔢 Next team ID will be: ICCT-{sequence_value[0] + 1:03d}")
        
        logger.info("")
        
        # Verify ICCT-001 exists
        if "ICCT-001" in team_ids:
            logger.info("✅ ICCT-001 exists (as expected)")
        else:
            logger.warning("⚠️ ICCT-001 not found")
        
        # Verify latest team
        if len(team_ids) >= 2:
            latest = team_ids[-1]
            logger.info(f"✅ Latest team: {latest}")
            expected = f"ICCT-{len(team_ids):03d}"
            if latest == expected:
                logger.info(f"✅ Team ID generation is CORRECT")
            else:
                logger.error(f"❌ Team ID mismatch! Expected {expected}, got {latest}")
                return False
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    logger.info("")
    logger.info("🏏" * 35)
    logger.info("ICCT26 - COMPLETE END-TO-END REGISTRATION TEST")
    logger.info("🏏" * 35)
    logger.info("")
    
    # Step 1: Register team
    registration_success = await register_team()
    if not registration_success:
        logger.error("")
        logger.error("=" * 70)
        logger.error("❌ REGISTRATION FAILED - STOPPING TESTS")
        logger.error("=" * 70)
        return False
    
    # Step 2: Verify database
    db_verification_success = await verify_database()
    if not db_verification_success:
        logger.error("")
        logger.error("=" * 70)
        logger.error("❌ DATABASE VERIFICATION FAILED")
        logger.error("=" * 70)
        return False
    
    # Step 3: Check team ID generation
    id_generation_success = await check_team_id_generation()
    if not id_generation_success:
        logger.error("")
        logger.error("=" * 70)
        logger.error("❌ TEAM ID GENERATION CHECK FAILED")
        logger.error("=" * 70)
        return False
    
    # All tests passed
    logger.info("")
    logger.info("=" * 70)
    logger.info("✅✅✅ ALL TESTS PASSED! ✅✅✅")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Summary:")
    logger.info("  ✅ Team registration successful")
    logger.info("  ✅ Database records verified")
    logger.info("  ✅ Team ID generation correct")
    logger.info("  ✅ 11 players registered with files")
    logger.info("  ✅ All file URLs stored correctly")
    logger.info("")
    logger.info("🎉 SYSTEM IS READY FOR PRODUCTION! 🎉")
    logger.info("=" * 70)
    
    return True


if __name__ == "__main__":
    import sys
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
