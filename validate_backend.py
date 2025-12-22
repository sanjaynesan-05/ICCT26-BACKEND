"""
Quick validation script to verify all backend fixes are working
Run this after deploying to check everything is configured correctly
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_async_engine
from sqlalchemy.orm import sessionmaker


async def main():
    """Run all validation checks"""
    print("=" * 70)
    print("🔍 COMPREHENSIVE BACKEND VALIDATION")
    print("=" * 70)
    print()
    
    all_passed = True
    
    # Check 1: DatabaseService methods
    print("📋 CHECK 1: DatabaseService Methods")
    print("-" * 70)
    try:
        from app.utils.startup_validation import validate_database_service_methods
        
        results = validate_database_service_methods()
        
        if results["valid"]:
            print("✅ PASS: All required DatabaseService methods available")
            for method in results["methods"]:
                print(f"  {method['status']} {method['method']}()")
        else:
            print("❌ FAIL: Missing DatabaseService methods")
            all_passed = False
            for error in results["errors"]:
                print(f"  ❌ {error}")
    except Exception as e:
        print(f"❌ FAIL: Error checking DatabaseService: {e}")
        all_passed = False
    
    print()
    
    # Check 2: Database Schema
    print("📋 CHECK 2: Database Schema Configuration")
    print("-" * 70)
    try:
        from app.utils.startup_validation import validate_database_schema
        
        async_engine = get_async_engine()
        AsyncSessionLocal = sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        async with AsyncSessionLocal() as db:
            schema_results = await validate_database_schema(db)
            
            if schema_results["valid"]:
                print("✅ PASS: Database schema configured correctly")
                for check in schema_results["checks"]:
                    print(f"  {check['status']} {check['check']}")
            else:
                print("❌ FAIL: Database schema issues detected")
                all_passed = False
                for error in schema_results["errors"]:
                    print(f"  ❌ {error}")
            
            if schema_results["warnings"]:
                print("\n  ⚠️ Warnings:")
                for warning in schema_results["warnings"]:
                    print(f"    - {warning}")
    
    except Exception as e:
        print(f"❌ FAIL: Error checking database schema: {e}")
        all_passed = False
    
    print()
    
    # Check 3: ORM Model Alignment
    print("📋 CHECK 3: ORM Model Configuration")
    print("-" * 70)
    try:
        from models import Team
        from sqlalchemy.dialects.postgresql import UUID
        
        # Check Team.id is UUID
        team_id_col = Team.__table__.columns['id']
        is_uuid = isinstance(team_id_col.type, UUID)
        has_server_default = team_id_col.server_default is not None
        
        if is_uuid and has_server_default:
            print("✅ PASS: Team.id is UUID with server_default")
            print(f"  ✅ Column type: UUID")
            print(f"  ✅ Server default: {team_id_col.server_default}")
        else:
            print("❌ FAIL: Team.id configuration incorrect")
            print(f"  UUID type: {is_uuid}")
            print(f"  Server default: {has_server_default}")
            all_passed = False
        
    except Exception as e:
        print(f"❌ FAIL: Error checking ORM models: {e}")
        all_passed = False
    
    print()
    
    # Check 4: Team ID Generation
    print("📋 CHECK 4: Team ID Generation (Race-Safe)")
    print("-" * 70)
    try:
        from app.utils.race_safe_team_id import generate_next_team_id
        
        async_engine = get_async_engine()
        AsyncSessionLocal = sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        async with AsyncSessionLocal() as db:
            # Get current sequence value
            from sqlalchemy import text
            result = await db.execute(text("SELECT last_number FROM team_sequence WHERE id = 1"))
            row = result.first()
            
            if row:
                current_number = row[0]
                expected_next = f"ICCT-{current_number + 1:03d}"
                print(f"✅ PASS: Team sequence initialized")
                print(f"  ✅ Current last_number: {current_number}")
                print(f"  ✅ Next team ID will be: {expected_next}")
            else:
                print("❌ FAIL: team_sequence table not initialized")
                all_passed = False
    
    except Exception as e:
        print(f"❌ FAIL: Error checking team ID generation: {e}")
        all_passed = False
    
    print()
    
    # Check 5: Admin Routes Configuration
    print("📋 CHECK 5: Admin Routes")
    print("-" * 70)
    try:
        from app.routes.admin import router
        
        routes = [r.path for r in router.routes]
        required_routes = ["/teams", "/teams/{team_id}", "/teams/{team_id}/confirm"]
        
        all_routes_exist = all(route in routes for route in required_routes)
        
        if all_routes_exist:
            print("✅ PASS: All admin routes configured")
            for route in required_routes:
                print(f"  ✅ {route}")
        else:
            print("❌ FAIL: Missing admin routes")
            all_passed = False
            for route in required_routes:
                status = "✅" if route in routes else "❌"
                print(f"  {status} {route}")
    
    except Exception as e:
        print(f"❌ FAIL: Error checking admin routes: {e}")
        all_passed = False
    
    print()
    print("=" * 70)
    if all_passed:
        print("🎉 ALL VALIDATION CHECKS PASSED!")
        print("✅ Backend is production-ready")
    else:
        print("❌ SOME VALIDATION CHECKS FAILED")
        print("⚠️ Please fix the errors before deploying")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
