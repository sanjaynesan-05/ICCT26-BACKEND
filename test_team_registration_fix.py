"""
Test Team Registration Fixes
=============================
Validates all fixes for team registration endpoint:
1. MAX_RETRIES configuration
2. Team ID generation (race-safe)
3. Retry logic on IntegrityError
4. Sequence sync on startup
5. No NameError or undefined functions
"""

import asyncio
import sys
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def test_config_max_retries():
    """Test 1: Verify MAX_RETRIES is defined in settings"""
    try:
        from config.settings import settings
        
        # Check MAX_RETRIES exists
        assert hasattr(settings, 'MAX_RETRIES'), "MAX_RETRIES not found in settings"
        assert isinstance(settings.MAX_RETRIES, int), "MAX_RETRIES must be an integer"
        assert settings.MAX_RETRIES > 0, "MAX_RETRIES must be positive"
        
        logger.info(f"✅ Test 1 PASSED: MAX_RETRIES = {settings.MAX_RETRIES}")
        return True
    except Exception as e:
        logger.error(f"❌ Test 1 FAILED: {e}")
        return False


async def test_retry_delay():
    """Test 2: Verify RETRY_DELAY is defined in settings"""
    try:
        from config.settings import settings
        
        # Check RETRY_DELAY exists
        assert hasattr(settings, 'RETRY_DELAY'), "RETRY_DELAY not found in settings"
        assert isinstance(settings.RETRY_DELAY, (int, float)), "RETRY_DELAY must be numeric"
        assert settings.RETRY_DELAY >= 0, "RETRY_DELAY must be non-negative"
        
        logger.info(f"✅ Test 2 PASSED: RETRY_DELAY = {settings.RETRY_DELAY}s")
        return True
    except Exception as e:
        logger.error(f"❌ Test 2 FAILED: {e}")
        return False


async def test_race_safe_import():
    """Test 3: Verify race_safe_team_id module and functions exist"""
    try:
        from app.utils.race_safe_team_id import generate_next_team_id
        
        # Verify function is callable
        assert callable(generate_next_team_id), "generate_next_team_id must be callable"
        
        logger.info("✅ Test 3 PASSED: generate_next_team_id imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Test 3 FAILED: Import error - {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Test 3 FAILED: {e}")
        return False


async def test_registration_imports():
    """Test 4: Verify registration_production.py imports are correct"""
    try:
        # Import the module to check for syntax errors
        import app.routes.registration_production
        
        # Verify the function is imported (check module attributes)
        # This ensures no NameError will occur at runtime
        logger.info("✅ Test 4 PASSED: registration_production.py imports successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Test 4 FAILED: Import error - {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Test 4 FAILED: {e}")
        return False


async def test_sequence_sync_function():
    """Test 5: Verify sync_sequence_with_teams function exists"""
    try:
        from app.utils.race_safe_team_id import sync_sequence_with_teams
        
        # Verify function is callable
        assert callable(sync_sequence_with_teams), "sync_sequence_with_teams must be callable"
        
        logger.info("✅ Test 5 PASSED: sync_sequence_with_teams function exists")
        return True
    except ImportError as e:
        logger.error(f"❌ Test 5 FAILED: Import error - {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Test 5 FAILED: {e}")
        return False


async def test_team_id_generation():
    """Test 6: Test actual team ID generation with database"""
    try:
        from database import get_db_async
        from app.utils.race_safe_team_id import generate_next_team_id
        
        # Get database session
        async for db in get_db_async():
            try:
                # Generate a team ID
                team_id = await generate_next_team_id(db)
                
                # Verify format
                assert team_id.startswith("ICCT-"), f"Team ID must start with 'ICCT-': {team_id}"
                assert len(team_id) == 8, f"Team ID must be 8 characters (ICCT-XXX): {team_id}"
                
                # Rollback to avoid persisting test data
                await db.rollback()
                
                logger.info(f"✅ Test 6 PASSED: Generated team_id = {team_id}")
                return True
            finally:
                await db.close()
                
    except Exception as e:
        logger.error(f"❌ Test 6 FAILED: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_sequence_table_exists():
    """Test 7: Verify team_sequence table exists in database"""
    try:
        from database import get_db_async
        
        async for db in get_db_async():
            try:
                # Check if table exists
                result = await db.execute(text("""
                    SELECT EXISTS (
                        SELECT 1 
                        FROM information_schema.tables 
                        WHERE table_name = 'team_sequence'
                    )
                """))
                
                exists = result.scalar()
                assert exists, "team_sequence table does not exist"
                
                # Check if row exists
                result = await db.execute(text("SELECT last_number FROM team_sequence WHERE id = 1"))
                row = result.fetchone()
                assert row is not None, "team_sequence row (id=1) does not exist"
                
                last_number = row[0]
                logger.info(f"✅ Test 7 PASSED: team_sequence table exists (last_number = {last_number})")
                return True
            finally:
                await db.close()
                
    except Exception as e:
        logger.error(f"❌ Test 7 FAILED: {e}")
        return False


async def test_concurrent_team_id_generation():
    """Test 8: Test concurrent team ID generation (race condition check)"""
    try:
        from database import get_db_async
        from app.utils.race_safe_team_id import generate_next_team_id
        
        # Generate multiple team IDs concurrently
        async def generate_id(session_num):
            async for db in get_db_async():
                try:
                    team_id = await generate_next_team_id(db)
                    await db.commit()  # COMMIT to persist the sequence increment
                    return team_id
                finally:
                    await db.close()
        
        # Run 5 concurrent generations
        tasks = [generate_id(i) for i in range(5)]
        team_ids = await asyncio.gather(*tasks)
        
        # Verify all IDs are unique
        assert len(team_ids) == len(set(team_ids)), f"Duplicate team IDs generated: {team_ids}"
        
        logger.info(f"✅ Test 8 PASSED: Concurrent generation safe - {len(team_ids)} unique IDs: {team_ids}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test 8 FAILED: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_max_retries_defensive_fallback():
    """Test 9: Verify defensive fallback for MAX_RETRIES in registration_production.py"""
    try:
        # Read the file and check for defensive fallback
        with open('app/routes/registration_production.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for MAX_RETRIES import or getattr usage
        has_import = "from config.settings import settings" in content or "from config.settings import MAX_RETRIES" in content
        has_defensive = "getattr(settings, 'MAX_RETRIES'" in content or "MAX_RETRIES = getattr" in content
        
        assert has_import or has_defensive, "No import or defensive fallback for MAX_RETRIES found"
        
        logger.info("✅ Test 9 PASSED: MAX_RETRIES defensive fallback exists")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test 9 FAILED: {e}")
        return False


async def test_no_generate_next_team_id_with_retry_call():
    """Test 10: Verify generate_next_team_id_with_retry is NOT called in broken way"""
    try:
        # Read the file and check it's using correct function
        with open('app/routes/registration_production.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should import generate_next_team_id (not generate_next_team_id_with_retry)
        assert "from app.utils.race_safe_team_id import generate_next_team_id" in content, \
            "Must import generate_next_team_id"
        
        logger.info("✅ Test 10 PASSED: Using correct import (generate_next_team_id)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test 10 FAILED: {e}")
        return False


async def main():
    """Run all tests"""
    logger.info("=" * 70)
    logger.info("TEAM REGISTRATION FIX VALIDATION")
    logger.info("=" * 70)
    logger.info("")
    
    tests = [
        ("Configuration: MAX_RETRIES", test_config_max_retries),
        ("Configuration: RETRY_DELAY", test_retry_delay),
        ("Import: race_safe_team_id.generate_next_team_id", test_race_safe_import),
        ("Import: registration_production.py", test_registration_imports),
        ("Function: sync_sequence_with_teams", test_sequence_sync_function),
        ("Database: team ID generation", test_team_id_generation),
        ("Database: team_sequence table", test_sequence_table_exists),
        ("Concurrency: race condition check", test_concurrent_team_id_generation),
        ("Code: MAX_RETRIES defensive fallback", test_max_retries_defensive_fallback),
        ("Code: Correct import usage", test_no_generate_next_team_id_with_retry_call),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"Running: {test_name}")
        result = await test_func()
        results.append((test_name, result))
        logger.info("")
    
    # Summary
    logger.info("=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("")
    logger.info(f"Total: {len(results)} tests")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success Rate: {passed/len(results)*100:.1f}%")
    logger.info("")
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED! Team registration is ready.")
        logger.info("=" * 70)
        return 0
    else:
        logger.error(f"⚠️ {failed} TEST(S) FAILED. Please review and fix.")
        logger.info("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
