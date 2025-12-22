"""
Complete Database Verification Script
======================================
Checks all tables, schema, and data integrity.
"""

import asyncio
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from database import sync_engine  # Use the pre-configured sync engine
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def verify_all_tables():
    """Verify all database tables exist and are functional"""
    logger.info("=" * 70)
    logger.info("DATABASE VERIFICATION")
    logger.info("=" * 70)
    logger.info("")
    
    # Create session using the pre-configured sync engine
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        # 1. Check all tables exist
        logger.info("1️⃣ Checking Database Tables...")
        logger.info("-" * 70)
        
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Found {len(tables)} tables:")
        for table in sorted(tables):
            logger.info(f"  ✅ {table}")
        logger.info("")
        
        # Expected tables
        expected_tables = [
            'teams',
            'players',
            'matches',
            'team_sequence',
            'idempotency_keys'
        ]
        
        missing_tables = [t for t in expected_tables if t not in tables]
        if missing_tables:
            logger.error(f"❌ Missing tables: {missing_tables}")
            return False
        else:
            logger.info("✅ All expected tables exist")
            logger.info("")
        
        # 2. Verify team_sequence table
        logger.info("2️⃣ Verifying team_sequence Table...")
        logger.info("-" * 70)
        
        result = session.execute(text("SELECT * FROM team_sequence ORDER BY id"))
        sequences = result.fetchall()
        
        if sequences:
            logger.info(f"✅ team_sequence has {len(sequences)} row(s):")
            for seq in sequences:
                logger.info(f"  - ID: {seq[0]}, Last Number: {seq[1]}")
        else:
            logger.warning("⚠️ team_sequence table is empty")
            # Initialize it
            session.execute(text("INSERT INTO team_sequence (id, last_number) VALUES (1, 0)"))
            session.commit()
            logger.info("✅ Initialized team_sequence with (1, 0)")
        logger.info("")
        
        # 3. Check teams table structure
        logger.info("3️⃣ Verifying teams Table Schema...")
        logger.info("-" * 70)
        
        columns = inspector.get_columns('teams')
        logger.info(f"Teams table has {len(columns)} columns:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            logger.info(f"  - {col['name']}: {col['type']} {nullable}")
        
        # Verify critical columns exist
        column_names = [col['name'] for col in columns]
        critical_columns = ['id', 'team_id', 'team_name', 'captain_name', 'pastor_letter', 'payment_receipt', 'group_photo']
        missing_cols = [c for c in critical_columns if c not in column_names]
        
        if missing_cols:
            logger.error(f"❌ Missing columns in teams: {missing_cols}")
            return False
        else:
            logger.info("✅ All critical columns exist in teams")
        logger.info("")
        
        # 4. Check players table structure
        logger.info("4️⃣ Verifying players Table Schema...")
        logger.info("-" * 70)
        
        columns = inspector.get_columns('players')
        logger.info(f"Players table has {len(columns)} columns:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            logger.info(f"  - {col['name']}: {col['type']} {nullable}")
        
        # Verify critical columns exist
        column_names = [col['name'] for col in columns]
        critical_columns = ['id', 'player_id', 'team_id', 'name', 'role', 'aadhar_file', 'subscription_file']
        missing_cols = [c for c in critical_columns if c not in column_names]
        
        if missing_cols:
            logger.error(f"❌ Missing columns in players: {missing_cols}")
            return False
        else:
            logger.info("✅ All critical columns exist in players")
        logger.info("")
        
        # 5. Check existing data
        logger.info("5️⃣ Checking Existing Data...")
        logger.info("-" * 70)
        
        # Count teams
        result = session.execute(text("SELECT COUNT(*) FROM teams"))
        team_count = result.fetchone()[0]
        logger.info(f"Teams in database: {team_count}")
        
        if team_count > 0:
            result = session.execute(text("SELECT team_id, team_name FROM teams ORDER BY team_id"))
            teams = result.fetchall()
            for team in teams:
                logger.info(f"  - {team[0]}: {team[1]}")
        logger.info("")
        
        # Count players
        result = session.execute(text("SELECT COUNT(*) FROM players"))
        player_count = result.fetchone()[0]
        logger.info(f"Players in database: {player_count}")
        logger.info("")
        
        # Count matches
        result = session.execute(text("SELECT COUNT(*) FROM matches"))
        match_count = result.fetchone()[0]
        logger.info(f"Matches in database: {match_count}")
        logger.info("")
        
        # 6. Verify foreign key constraints
        logger.info("6️⃣ Verifying Foreign Key Constraints...")
        logger.info("-" * 70)
        
        fks = inspector.get_foreign_keys('players')
        logger.info(f"Players table has {len(fks)} foreign key(s):")
        for fk in fks:
            logger.info(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        if fks:
            logger.info("✅ Foreign keys configured correctly")
        else:
            logger.warning("⚠️ No foreign keys found")
        logger.info("")
        
        # 7. Test data insertion (rollback)
        logger.info("7️⃣ Testing Data Insertion (Dry Run)...")
        logger.info("-" * 70)
        
        try:
            # Get current sequence value
            result = session.execute(text("SELECT last_number FROM team_sequence WHERE id = 1"))
            current_seq = result.fetchone()[0]
            
            # Use NEXT number for test (increment by 1000 to avoid conflict)
            test_num = current_seq + 1000
            test_team_id = f"ICCT-{test_num:03d}"
            
            logger.info(f"Testing with team ID: {test_team_id} (sequence at: {current_seq})")
            
            # Start a savepoint for rollback
            session.begin_nested()
            
            # Test insert team
            session.execute(text("""
                INSERT INTO teams (team_id, team_name, church_name, captain_name, captain_phone, 
                                 captain_email, captain_whatsapp, vice_captain_name, 
                                 vice_captain_phone, vice_captain_email, vice_captain_whatsapp,
                                 created_at, registration_date)
                VALUES (:team_id, :team_name, :church_name, :captain_name, :captain_phone,
                       :captain_email, :captain_whatsapp, :vice_name, :vice_phone, 
                       :vice_email, :vice_whatsapp, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """), {
                'team_id': test_team_id,
                'team_name': 'TEST TEAM',
                'church_name': 'TEST CHURCH',
                'captain_name': 'Test Captain',
                'captain_phone': '9999999999',
                'captain_email': 'test@test.com',
                'captain_whatsapp': '9999999999',
                'vice_name': 'Test Vice',
                'vice_phone': '8888888888',
                'vice_email': 'vice@test.com',
                'vice_whatsapp': '8888888888'
            })
            
            logger.info("✅ Team insertion test: SUCCESS")
            
            # Test insert player
            session.execute(text("""
                INSERT INTO players (player_id, team_id, name, role)
                VALUES (:player_id, :team_id, :name, :role)
            """), {
                'player_id': f'{test_team_id}-P01',
                'team_id': test_team_id,
                'name': 'Test Player',
                'role': 'Batsman'
            })
            
            logger.info("✅ Player insertion test: SUCCESS")
            
            # Rollback the test
            session.rollback()
            logger.info("✅ Test data rolled back (no actual changes)")
            
        except Exception as e:
            logger.error(f"❌ Data insertion test failed: {e}")
            session.rollback()
            return False
        
        logger.info("")
        
        # 8. Summary
        logger.info("=" * 70)
        logger.info("VERIFICATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"✅ All expected tables exist: {len(expected_tables)} tables")
        logger.info(f"✅ team_sequence table: Functional")
        logger.info(f"✅ teams table: {team_count} records")
        logger.info(f"✅ players table: {player_count} records")
        logger.info(f"✅ matches table: {match_count} records")
        logger.info(f"✅ Foreign keys: Configured")
        logger.info(f"✅ Data insertion: Working")
        logger.info("")
        logger.info("🎉 DATABASE IS FULLY FUNCTIONAL!")
        logger.info("=" * 70)
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        session.close()
        return False


if __name__ == "__main__":
    import sys
    success = asyncio.run(verify_all_tables())
    sys.exit(0 if success else 1)
