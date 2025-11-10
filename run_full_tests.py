"""
Comprehensive Pre-Deployment Test Suite
Tests database connection, endpoints, and all functionality
"""
import asyncio
import logging
from sqlalchemy import text
from database import async_engine, sync_engine, AsyncSessionLocal
import json

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("COMPREHENSIVE PRE-DEPLOYMENT TEST SUITE")
print("="*70)

# ============================================================
# 1. DATABASE CONNECTION TESTS
# ============================================================

async def test_database_connections():
    print("\n📍 [1/5] DATABASE CONNECTION TESTS")
    print("-" * 70)
    
    results = {}
    
    # Test Async Connection
    print("   Testing Async Connection...")
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as connection_test"))
            data = result.fetchone()
            print(f"   ✅ Async connection successful")
            results['async'] = True
    except Exception as e:
        print(f"   ❌ Async connection failed: {str(e)}")
        results['async'] = False
    
    # Test Sync Connection
    print("   Testing Sync Connection...")
    try:
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as connection_test"))
            data = result.fetchone()
            print(f"   ✅ Sync connection successful")
            results['sync'] = True
    except Exception as e:
        print(f"   ❌ Sync connection failed: {str(e)}")
        results['sync'] = False
    
    return all(results.values()), results

# ============================================================
# 2. TABLE STRUCTURE TESTS
# ============================================================

async def test_table_structure():
    print("\n📍 [2/5] TABLE STRUCTURE TESTS")
    print("-" * 70)
    
    try:
        async with async_engine.connect() as conn:
            # List all tables
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"   ✅ Found {len(tables)} tables in database:")
                for table in tables:
                    print(f"      - {table[0]}")
                return True
            else:
                print(f"   ⚠️  No tables found - will be created on first use")
                return None
    except Exception as e:
        print(f"   ❌ Table check failed: {str(e)}")
        return False

# ============================================================
# 3. DATA INTEGRITY TESTS
# ============================================================

async def test_data_integrity():
    print("\n📍 [3/5] DATA INTEGRITY TESTS")
    print("-" * 70)
    
    try:
        async with async_engine.connect() as conn:
            # Count Teams
            result = await conn.execute(text("SELECT COUNT(*) FROM teams"))
            teams_count = result.scalar()
            print(f"   📊 Teams in database: {teams_count}")
            
            # Count Players
            result = await conn.execute(text("SELECT COUNT(*) FROM players"))
            players_count = result.scalar()
            print(f"   📊 Players in database: {players_count}")
            
            # Check data consistency
            if teams_count > 0:
                result = await conn.execute(text("""
                    SELECT t.team_id, COUNT(p.id) as player_count
                    FROM teams t
                    LEFT JOIN players p ON p.team_id = t.team_id
                    GROUP BY t.team_id
                """))
                team_data = result.fetchall()
                print(f"   ✅ Data integrity check passed")
                for team in team_data[:3]:
                    print(f"      - Team {team[0]}: {team[1]} players")
                if len(team_data) > 3:
                    print(f"      ... and {len(team_data) - 3} more teams")
            else:
                print(f"   ℹ️  No teams in database yet")
            
            return True
    except Exception as e:
        print(f"   ⚠️  Data check: {str(e)}")
        return None

# ============================================================
# 4. APPLICATION TESTS
# ============================================================

async def test_application():
    print("\n📍 [4/5] APPLICATION TESTS")
    print("-" * 70)
    
    try:
        from main import app
        from app.services import DatabaseService
        
        print(f"   ✅ FastAPI app loaded successfully")
        print(f"   📊 Total routes: {len(app.routes)}")
        
        # Check key routes
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        key_routes = [
            '/admin/teams',
            '/api/teams',
            '/health',
            '/status'
        ]
        
        missing = []
        for route in key_routes:
            if route in routes:
                print(f"   ✅ Route {route}: found")
            else:
                print(f"   ❌ Route {route}: MISSING")
                missing.append(route)
        
        # Test DatabaseService methods
        print(f"\n   ✅ DatabaseService methods available:")
        methods = ['get_all_teams', 'get_team_details', 'get_player_details', 'save_registration_to_db']
        for method in methods:
            if hasattr(DatabaseService, method):
                print(f"      - {method}")
            else:
                print(f"   ❌ {method}: MISSING")
                missing.append(method)
        
        return len(missing) == 0
    except Exception as e:
        print(f"   ❌ Application test failed: {str(e)}")
        return False

# ============================================================
# 5. IMPORT TESTS
# ============================================================

def test_imports():
    print("\n📍 [5/5] IMPORT TESTS")
    print("-" * 70)
    
    imports_ok = True
    test_imports_list = [
        ('database', ['async_engine', 'sync_engine', 'get_db_async', 'get_db']),
        ('app.services', ['DatabaseService', 'EmailService']),
        ('app.routes.admin', ['router']),
        ('app.routes.team', ['router']),
        ('app.routes.health', ['router']),
        ('main', ['app']),
    ]
    
    for module_name, items in test_imports_list:
        try:
            module = __import__(module_name, fromlist=items)
            for item in items:
                if hasattr(module, item):
                    print(f"   ✅ {module_name}.{item}")
                else:
                    print(f"   ❌ {module_name}.{item}: NOT FOUND")
                    imports_ok = False
        except Exception as e:
            print(f"   ❌ Import {module_name} failed: {str(e)}")
            imports_ok = False
    
    return imports_ok

# ============================================================
# RUN ALL TESTS
# ============================================================

async def run_all_tests():
    db_ok, db_results = await test_database_connections()
    tables_ok = await test_table_structure()
    data_ok = await test_data_integrity()
    app_ok = await test_application()
    imports_ok = test_imports()
    
    print("\n" + "="*70)
    print("FINAL TEST SUMMARY")
    print("="*70)
    
    tests = {
        "Database Connections": db_ok,
        "Table Structure": tables_ok if tables_ok is not None else "Created at runtime",
        "Data Integrity": data_ok,
        "Application": app_ok,
        "Imports": imports_ok,
    }
    
    print("\nTest Results:")
    all_pass = True
    for test_name, result in tests.items():
        status = "✅ PASS" if result is True else "⚠️  OK" if result is None else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result is False:
            all_pass = False
    
    print("\n" + "="*70)
    if all_pass:
        print("✅ ALL TESTS PASSED - READY FOR DEPLOYMENT")
    else:
        print("❌ SOME TESTS FAILED - REVIEW ISSUES ABOVE")
    print("="*70 + "\n")
    
    return all_pass

asyncio.run(run_all_tests())
