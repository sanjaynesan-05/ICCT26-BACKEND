"""
Startup validation for database schema and configuration
Runs on application startup to ensure everything is configured correctly
"""

import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def validate_database_schema(db: AsyncSession) -> dict:
    """
    Validate critical database schema configurations
    
    Returns:
        dict: Validation results with status and details
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "checks": []
    }
    
    logger.info("🔍 Starting database schema validation...")
    
    # Check 1: teams.id has DEFAULT gen_random_uuid()
    try:
        query = text("""
            SELECT column_name, column_default, is_nullable, data_type
            FROM information_schema.columns
            WHERE table_name = 'teams' AND column_name = 'id'
        """)
        result = await db.execute(query)
        row = result.mappings().first()
        
        if row:
            has_default = row['column_default'] and 'gen_random_uuid' in row['column_default']
            is_not_null = row['is_nullable'] == 'NO'
            is_uuid = row['data_type'] == 'uuid'
            
            if has_default and is_not_null and is_uuid:
                results["checks"].append({
                    "check": "teams.id DEFAULT gen_random_uuid()",
                    "status": "✅ PASS",
                    "details": f"Column: {row['data_type']}, Default: {row['column_default']}, Nullable: {row['is_nullable']}"
                })
                logger.info("✅ teams.id has DEFAULT gen_random_uuid() - NULL constraint errors prevented")
            else:
                error = f"teams.id configuration issue - Default: {row['column_default']}, Nullable: {row['is_nullable']}, Type: {row['data_type']}"
                results["errors"].append(error)
                results["valid"] = False
                results["checks"].append({
                    "check": "teams.id DEFAULT gen_random_uuid()",
                    "status": "❌ FAIL",
                    "details": error
                })
                logger.error(f"❌ {error}")
        else:
            error = "teams.id column not found in database"
            results["errors"].append(error)
            results["valid"] = False
            results["checks"].append({
                "check": "teams.id exists",
                "status": "❌ FAIL",
                "details": error
            })
            logger.error(f"❌ {error}")
            
    except Exception as e:
        error = f"Failed to check teams.id: {str(e)}"
        results["errors"].append(error)
        results["valid"] = False
        logger.error(f"❌ {error}")
    
    # Check 2: registration_status column exists and has correct type
    try:
        query = text("""
            SELECT column_name, column_default, is_nullable, data_type
            FROM information_schema.columns
            WHERE table_name = 'teams' AND column_name = 'registration_status'
        """)
        result = await db.execute(query)
        row = result.mappings().first()
        
        if row:
            has_default = row['column_default'] and 'pending' in row['column_default']
            
            results["checks"].append({
                "check": "teams.registration_status column",
                "status": "✅ PASS",
                "details": f"Type: {row['data_type']}, Default: {row['column_default']}, Nullable: {row['is_nullable']}"
            })
            logger.info(f"✅ registration_status column found - Type: {row['data_type']}, Default: {row['column_default']}")
            
            if not has_default:
                warning = "registration_status has no default value - may cause issues"
                results["warnings"].append(warning)
                logger.warning(f"⚠️ {warning}")
        else:
            error = "registration_status column not found in teams table"
            results["errors"].append(error)
            results["valid"] = False
            results["checks"].append({
                "check": "teams.registration_status exists",
                "status": "❌ FAIL",
                "details": error
            })
            logger.error(f"❌ {error}")
            
    except Exception as e:
        error = f"Failed to check registration_status: {str(e)}"
        results["errors"].append(error)
        results["valid"] = False
        logger.error(f"❌ {error}")
    
    # Check 3: team_sequence table exists
    try:
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'team_sequence'
        """)
        result = await db.execute(query)
        row = result.first()
        
        if row:
            results["checks"].append({
                "check": "team_sequence table exists",
                "status": "✅ PASS",
                "details": "Sequential team ID generation table present"
            })
            logger.info("✅ team_sequence table exists for ICCT-001, ICCT-002 generation")
        else:
            warning = "team_sequence table not found - team ID generation may fail"
            results["warnings"].append(warning)
            results["checks"].append({
                "check": "team_sequence table exists",
                "status": "⚠️ WARNING",
                "details": warning
            })
            logger.warning(f"⚠️ {warning}")
            
    except Exception as e:
        error = f"Failed to check team_sequence: {str(e)}"
        results["warnings"].append(error)
        logger.warning(f"⚠️ {error}")
    
    # Check 4: Verify no duplicate column names (status vs registration_status)
    try:
        query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'teams' AND column_name IN ('status', 'registration_status')
            ORDER BY column_name
        """)
        result = await db.execute(query)
        columns = [row[0] for row in result.fetchall()]
        
        if len(columns) > 1:
            warning = f"Multiple status columns found: {columns} - potential duplication issue"
            results["warnings"].append(warning)
            results["checks"].append({
                "check": "No duplicate status columns",
                "status": "⚠️ WARNING",
                "details": warning
            })
            logger.warning(f"⚠️ {warning}")
        elif 'registration_status' in columns:
            results["checks"].append({
                "check": "No duplicate status columns",
                "status": "✅ PASS",
                "details": "Only registration_status column exists (correct)"
            })
            logger.info("✅ No duplicate status columns - using registration_status")
        
    except Exception as e:
        error = f"Failed to check duplicate columns: {str(e)}"
        results["warnings"].append(error)
        logger.warning(f"⚠️ {error}")
    
    # Summary
    logger.info("=" * 60)
    logger.info("📋 STARTUP VALIDATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Status: {'✅ VALID' if results['valid'] else '❌ INVALID'}")
    logger.info(f"Checks passed: {len([c for c in results['checks'] if '✅' in c['status']])}/{len(results['checks'])}")
    
    if results["errors"]:
        logger.error(f"Errors: {len(results['errors'])}")
        for error in results["errors"]:
            logger.error(f"  - {error}")
    
    if results["warnings"]:
        logger.warning(f"Warnings: {len(results['warnings'])}")
        for warning in results["warnings"]:
            logger.warning(f"  - {warning}")
    
    logger.info("=" * 60)
    
    return results


def validate_database_service_methods():
    """
    Validate that DatabaseService has all required methods
    
    Returns:
        dict: Validation results
    """
    from app.services import DatabaseService
    
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "methods": []
    }
    
    logger.info("🔍 Validating DatabaseService methods...")
    
    required_methods = [
        "get_team_by_team_id",
        "confirm_team_registration",
        "get_team_details",
        "get_all_teams",
        "save_registration_to_db",
        "get_player_details"
    ]
    
    for method_name in required_methods:
        if hasattr(DatabaseService, method_name):
            results["methods"].append({
                "method": method_name,
                "status": "✅ AVAILABLE"
            })
            logger.info(f"✅ DatabaseService.{method_name}() available")
        else:
            error = f"Missing method: DatabaseService.{method_name}()"
            results["errors"].append(error)
            results["valid"] = False
            results["methods"].append({
                "method": method_name,
                "status": "❌ MISSING"
            })
            logger.error(f"❌ {error}")
    
    logger.info("=" * 60)
    logger.info("📋 DATABASESERVICE VALIDATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Status: {'✅ VALID' if results['valid'] else '❌ INVALID'}")
    logger.info(f"Methods available: {len([m for m in results['methods'] if '✅' in m['status']])}/{len(required_methods)}")
    logger.info("=" * 60)
    
    return results
