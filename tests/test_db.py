#!/usr/bin/env python3
"""
Database connection tests for ICCT26 API.

Tests database connectivity and basic operations.
"""

import asyncio
from typing import Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_async_connection() -> bool:
    """Test async database connection."""
    try:
        from database import async_engine
        async with async_engine.connect() as connection:
            result = await connection.execute("SELECT 1")
            assert result is not None
            print("✅ Async database connection test PASSED")
            return True
    except Exception as e:
        print(f"❌ Async database connection test FAILED: {e}")
        return False

async def test_async_session() -> bool:
    """Test async session creation."""
    try:
        from database import async_session
        async with async_session() as session:
            # Just verify session is created
            assert session is not None
            print("✅ Async session creation test PASSED")
            return True
    except Exception as e:
        print(f"❌ Async session creation test FAILED: {e}")
        return False

def test_sync_connection() -> bool:
    """Test sync database connection."""
    try:
        from database import engine
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            assert result is not None
            print("✅ Sync database connection test PASSED")
            return True
    except Exception as e:
        print(f"❌ Sync database connection test FAILED: {e}")
        return False

def test_sync_session() -> bool:
    """Test sync session creation."""
    try:
        from database import SessionLocal
        session = SessionLocal()
        assert session is not None
        session.close()
        print("✅ Sync session creation test PASSED")
        return True
    except Exception as e:
        print(f"❌ Sync session creation test FAILED: {e}")
        return False

async def run_async_tests() -> list:
    """Run all async tests."""
    return [
        await test_async_connection(),
        await test_async_session(),
    ]

def run_all_tests() -> None:
    """Run all database tests."""
    print("\n" + "="*50)
    print("🗄️  ICCT26 Database Connection Tests")
    print("="*50 + "\n")
    
    # Run sync tests
    sync_results = [
        test_sync_connection(),
        test_sync_session(),
    ]
    
    print()
    
    # Run async tests
    async_results = asyncio.run(run_async_tests())
    
    all_results = sync_results + async_results
    passed = sum(all_results)
    total = len(all_results)
    
    print("\n" + "="*50)
    print(f"📊 Results: {passed}/{total} tests PASSED")
    print("="*50 + "\n")
    
    if passed == total:
        print("🎉 All database tests PASSED! Database is connected.\n")
    else:
        print(f"⚠️  {total - passed} test(s) FAILED. Check output above.\n")

if __name__ == "__main__":
    run_all_tests()
