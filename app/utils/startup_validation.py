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
    
    logger.debug("🔍 Starting database schema validation...")
    
    # Check 1: teams.id has DEFAULT gen_random_uuid()
    try:
        query = text("""
            SELECT column_name, column_default, is_nullable, data_type
            FROM information_schema.columns
            WHERE table_schema = current_schema() AND table_name = 'teams' AND column_name = 'id'
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
                logger.debug("✅ teams.id has DEFAULT gen_random_uuid() - NULL constraint errors prevented")
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
            WHERE table_schema = current_schema() AND table_name = 'teams' AND column_name = 'registration_status'
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
            logger.debug(f"✅ registration_status column found - Type: {row['data_type']}, Default: {row['column_default']}")
            
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
    
    # Check 4: Verify teams.team_id has UNIQUE constraint
    try:
        query = text("""
            SELECT tc.constraint_name, tc.constraint_type
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.table_schema = current_schema()
                AND tc.table_name = 'teams'
                AND kcu.column_name = 'team_id'
                AND tc.constraint_type = 'UNIQUE'
        """)
        result = await db.execute(query)
        constraints = result.fetchall()
        
        if len(constraints) > 0:
            results["checks"].append({
                "check": "teams.team_id UNIQUE constraint",
                "status": "✅ PASS",
                "details": f"UNIQUE constraint exists (prevents duplicate ICCT-XXX)"
            })
            logger.debug("✅ teams.team_id has UNIQUE constraint - duplicate team_id prevented")
        else:
            warning = "teams.team_id may not have UNIQUE constraint - duplicate IDs possible"
            results["warnings"].append(warning)
            results["checks"].append({
                "check": "teams.team_id UNIQUE constraint",
                "status": "⚠️ WARNING",
                "details": warning
            })
            logger.warning(f"⚠️ {warning}")
            
    except Exception as e:
        error = f"Failed to check team_id UNIQUE constraint: {str(e)}"
        results["warnings"].append(error)
        logger.warning(f"⚠️ {error}")
    
    # Check 5: Verify generate_next_team_id function exists
    try:
        from app.utils.race_safe_team_id import generate_next_team_id
        
        results["checks"].append({
            "check": "generate_next_team_id() function exists",
            "status": "✅ PASS",
            "details": "Team ID generation function available"
        })
        logger.debug("✅ generate_next_team_id() function exists")
        
    except ImportError as e:
        error = "generate_next_team_id() function not found - team registration will fail"
        results["errors"].append(error)
        results["valid"] = False
        results["checks"].append({
            "check": "generate_next_team_id() function exists",
            "status": "❌ FAIL",
            "details": error
        })
        logger.error(f"❌ {error}")
    
    # Check 6: team_sequence table exists (legacy check - now optional)
    try:
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = current_schema() AND table_name = 'team_sequence'
        """)
        result = await db.execute(query)
        row = result.first()
        
        if row:
            results["checks"].append({
                "check": "team_sequence table exists",
                "status": "✅ PASS",
                "details": "Sequential team ID generation table present"
            })
            logger.debug("✅ team_sequence table exists for ICCT-001, ICCT-002 generation")
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
            WHERE table_schema = current_schema() AND table_name = 'teams' AND column_name IN ('status', 'registration_status')
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
            logger.debug("✅ No duplicate status columns - using registration_status")
        
    except Exception as e:
        error = f"Failed to check duplicate columns: {str(e)}"
        results["warnings"].append(error)
        logger.warning(f"⚠️ {error}")
    
    passed = len([c for c in results["checks"] if "PASS" in c["status"]])
    logger.debug(f"Schema validation: {passed}/{len(results['checks'])} checks passed, "
                 f"{len(results['errors'])} errors, {len(results['warnings'])} warnings")

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
    
    logger.debug("🔍 Validating DatabaseService methods...")
    
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
            logger.debug(f"✅ DatabaseService.{method_name}() available")
        else:
            error = f"Missing method: DatabaseService.{method_name}()"
            results["errors"].append(error)
            results["valid"] = False
            results["methods"].append({
                "method": method_name,
                "status": "❌ MISSING"
            })
            logger.error(f"❌ {error}")
    
    return results


async def validate_sequence_table(db: AsyncSession) -> dict:
    """
    Validate team_sequence table configuration
    
    Returns:
        dict: Validation results for sequence table
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "checks": []
    }
    
    logger.debug("🔍 Validating team_sequence table...")
    
    try:
        # Check 1: Table exists
        query = text("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = current_schema() AND table_name = 'team_sequence'
            )
        """)
        result = await db.execute(query)
        table_exists = result.scalar()
        
        if not table_exists:
            error = "team_sequence table does not exist"
            results["errors"].append(error)
            results["valid"] = False
            results["checks"].append({
                "check": "team_sequence table exists",
                "status": "❌ FAIL",
                "details": error
            })
            logger.error(f"❌ {error}")
            return results
        else:
            results["checks"].append({
                "check": "team_sequence table exists",
                "status": "✅ PASS"
            })
            logger.debug("✅ team_sequence table exists")
        
        # Check 2: Columns exist and have correct types
        query = text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = current_schema() AND table_name = 'team_sequence'
            ORDER BY ordinal_position
        """)
        result = await db.execute(query)
        columns = {row[0]: (row[1], row[2]) for row in result}
        
        required_columns = {
            'id': 'integer',
            'last_number': 'integer',
            'updated_at': ('timestamp without time zone', 'timestamp with time zone')
        }
        
        for col_name, expected_type in required_columns.items():
            if col_name not in columns:
                error = f"Column '{col_name}' missing from team_sequence"
                results["errors"].append(error)
                results["valid"] = False
                logger.error(f"❌ {error}")
            else:
                actual_type = columns[col_name][0]
                if isinstance(expected_type, tuple):
                    type_match = actual_type in expected_type
                else:
                    type_match = actual_type == expected_type
                
                if type_match:
                    results["checks"].append({
                        "check": f"team_sequence.{col_name}",
                        "status": "✅ PASS",
                        "details": f"Type: {actual_type}"
                    })
                    logger.debug(f"✅ Column {col_name}: {actual_type}")
                else:
                    error = f"Column {col_name} has wrong type: {actual_type} (expected {expected_type})"
                    results["errors"].append(error)
                    results["valid"] = False
                    logger.error(f"❌ {error}")
        
        # Check 3: Initial row exists
        query = text("SELECT last_number FROM team_sequence WHERE id = 1")
        result = await db.execute(query)
        row = result.scalar_one_or_none()
        
        if row is not None:
            results["checks"].append({
                "check": "team_sequence initial row (id=1)",
                "status": "✅ PASS",
                "details": f"Current sequence: {row}"
            })
            logger.debug(f"✅ Initial sequence row exists (current: {row}, next: ICCT-{row + 1:03d})")
        else:
            warning = "Initial sequence row (id=1) not found - will be created on first use"
            results["warnings"].append(warning)
            logger.warning(f"⚠️ {warning}")
        
    except Exception as e:
        error = f"Failed to validate sequence table: {str(e)}"
        results["errors"].append(error)
        results["valid"] = False
        logger.error(f"❌ {error}")
    
    return results