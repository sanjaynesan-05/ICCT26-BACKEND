"""
Complete Backend Verification Test
Tests all systems after file upload fix
"""

import asyncio
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_imports():
    """Test 1: Core imports"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1/6: CORE IMPORTS")
    logger.info("="*70)
    
    try:
        logger.info("Importing database module...")
        from database import async_engine, sync_engine
        logger.info("[OK] Database module")
        
        logger.info("Importing models...")
        from models import Team, Player
        logger.info("[OK] Models")
        
        logger.info("Importing services...")
        from app.services import DatabaseService
        logger.info("[OK] Services")
        
        logger.info("Importing routes...")
        from app.routes.team import router
        logger.info("[OK] Routes")
        
        logger.info("Importing main app...")
        from main import app
        logger.info("[OK] Main app")
        
        logger.info("\n[PASS] TEST 1: All imports successful\n")
        return True
    except Exception as e:
        logger.error(f"[FAIL] TEST 1: {str(e)}")
        return False


async def test_database():
    """Test 2: Database connectivity"""
    logger.info("="*70)
    logger.info("TEST 2/6: DATABASE CONNECTIVITY")
    logger.info("="*70)
    
    try:
        from database import async_engine, sync_engine
        from sqlalchemy import text
        
        # Test async
        logger.info("Testing async connection...")
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("[OK] Async connection")
        
        # Test sync
        logger.info("Testing sync connection...")
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("[OK] Sync connection")
        
        logger.info("\n[PASS] TEST 2: Database connectivity verified\n")
        return True
    except Exception as e:
        logger.error(f"[FAIL] TEST 2: {str(e)}")
        return False


async def test_file_columns():
    """Test 3: File column types"""
    logger.info("="*70)
    logger.info("TEST 3/6: FILE COLUMN TYPES")
    logger.info("="*70)
    
    try:
        from models import Team, Player
        from sqlalchemy import Text
        
        team_columns = Team.__table__.columns
        player_columns = Player.__table__.columns
        
        # Check Team columns
        logger.info("Team table file columns:")
        logger.info(f"  payment_receipt: {team_columns.payment_receipt.type}")
        logger.info(f"  pastor_letter: {team_columns.pastor_letter.type}")
        
        # Check Player columns
        logger.info("Player table file columns:")
        logger.info(f"  aadhar_file: {player_columns.aadhar_file.type}")
        logger.info(f"  subscription_file: {player_columns.subscription_file.type}")
        
        # Verify types
        all_text = all([
            isinstance(team_columns.payment_receipt.type, Text),
            isinstance(team_columns.pastor_letter.type, Text),
            isinstance(player_columns.aadhar_file.type, Text),
            isinstance(player_columns.subscription_file.type, Text),
        ])
        
        if all_text:
            logger.info("\n[PASS] TEST 3: All file columns are TEXT type\n")
            return True
        else:
            logger.error("[FAIL] Some columns are not TEXT type")
            return False
            
    except Exception as e:
        logger.error(f"[FAIL] TEST 3: {str(e)}")
        return False


async def test_routes():
    """Test 4: API routes"""
    logger.info("="*70)
    logger.info("TEST 4/6: API ROUTES")
    logger.info("="*70)
    
    try:
        from main import app
        
        routes = [route.path for route in app.routes]
        logger.info(f"Total routes registered: {len(routes)}")
        
        critical_routes = [
            '/health',
            '/status',
            '/admin/teams',
            '/api/teams',
            '/api/register/team'
        ]
        
        found_critical = 0
        for route in critical_routes:
            if any(route in r for r in routes):
                logger.info(f"  [OK] {route}")
                found_critical += 1
            else:
                logger.warning(f"  [MISSING] {route}")
        
        logger.info(f"\nCritical routes found: {found_critical}/{len(critical_routes)}")
        
        if found_critical == len(critical_routes):
            logger.info("\n[PASS] TEST 4: All critical routes present\n")
            return True
        else:
            logger.error(f"[FAIL] Only found {found_critical}/{len(critical_routes)} routes")
            return False
            
    except Exception as e:
        logger.error(f"[FAIL] TEST 4: {str(e)}")
        return False


async def test_schema_validation():
    """Test 5: Pydantic schema validation"""
    logger.info("="*70)
    logger.info("TEST 5/6: PYDANTIC SCHEMA VALIDATION")
    logger.info("="*70)
    
    try:
        import base64
        from app.schemas_team import TeamRegistrationRequest
        
        # Create proper test image data (JPEG header)
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xc0\x00\x11\x08\x00\x10\x00\x10\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4'
        padding_size = 10000 - len(jpeg_header)
        if padding_size > 0:
            image_data = jpeg_header + b'\x00' * padding_size
        else:
            image_data = jpeg_header
        
        base64_image = base64.b64encode(image_data).decode()
        
        # Create proper test PDF data
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000200 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF'
        padding_size = 10000 - len(pdf_content)
        if padding_size > 0:
            pdf_data = pdf_content + b'\n' + b' ' * padding_size
        else:
            pdf_data = pdf_content
        
        base64_pdf = base64.b64encode(pdf_data).decode()
        
        logger.info(f"Testing with Base64 image: {len(base64_image)} characters")
        logger.info(f"Testing with Base64 PDF: {len(base64_pdf)} characters")
        
        test_payload = {
            "churchName": "Test Church",
            "teamName": "Test Team",
            "pastorLetter": base64_image,
            "paymentReceipt": base64_image,
            "captain": {
                "name": "Captain",
                "phone": "+919876543210",
                "whatsapp": "919876543210",
                "email": "capt@test.com"
            },
            "viceCaptain": {
                "name": "Vice Captain",
                "phone": "+919876543210",
                "whatsapp": "919876543210",
                "email": "vc@test.com"
            },
            "players": [
                {
                    "name": "Player 1",
                    "age": 25,
                    "phone": "+919876543210",
                    "role": "Batsman",
                    "aadharFile": base64_pdf,
                    "subscriptionFile": base64_pdf
                }
            ]
        }
        
        # Validate
        req = TeamRegistrationRequest(**test_payload)
        logger.info(f"Pastor letter size: {len(req.pastorLetter)} chars - OK")
        logger.info(f"Payment receipt size: {len(req.paymentReceipt)} chars - OK")
        logger.info(f"Player files size: {len(req.players[0].aadharFile)} chars - OK")
        
        logger.info("\n[PASS] TEST 5: Schema validation with large files\n")
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] TEST 5: {str(e)}")
        return False


async def test_debug_endpoint():
    """Test 6: Debug endpoint"""
    logger.info("="*70)
    logger.info("TEST 6/6: DEBUG ENDPOINT")
    logger.info("="*70)
    
    try:
        from main import app
        
        # Check if debug endpoint exists
        routes = [route.path for route in app.routes]
        if '/debug/create-tables' in routes:
            logger.info("[OK] Debug endpoint /debug/create-tables exists")
            logger.info("\n[PASS] TEST 6: Debug endpoint available\n")
            return True
        else:
            logger.error("[FAIL] Debug endpoint not found")
            return False
            
    except Exception as e:
        logger.error(f"[FAIL] TEST 6: {str(e)}")
        return False


async def main():
    """Run all tests"""
    logger.info("\n" + "="*70)
    logger.info("FILE UPLOAD FIX - COMPLETE BACKEND VERIFICATION")
    logger.info("="*70)
    
    results = []
    
    # Run tests
    results.append(await test_imports())
    results.append(await test_database())
    results.append(await test_file_columns())
    results.append(await test_routes())
    results.append(await test_schema_validation())
    results.append(await test_debug_endpoint())
    
    # Summary
    logger.info("="*70)
    logger.info("FINAL TEST SUMMARY")
    logger.info("="*70)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"\nTests Passed: {passed}/{total}")
    logger.info(f"Tests Failed: {total - passed}/{total}")
    logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if all(results):
        logger.info("\n" + "="*70)
        logger.info("[SUCCESS] ALL TESTS PASSED - FILE UPLOAD FIX VERIFIED")
        logger.info("="*70 + "\n")
        return 0
    else:
        logger.info("\n" + "="*70)
        logger.info("[FAILURE] SOME TESTS FAILED")
        logger.info("="*70 + "\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
