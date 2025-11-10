#!/usr/bin/env python3
"""
Test file upload validation with size limits and file type checking
Tests the new validation rules for images and PDFs
"""

import sys
import os
import base64
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.schemas_team import TeamRegistrationRequest
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_image_base64(size_kb: int = 50) -> str:
    """Create a test JPEG image as Base64"""
    # Create a minimal valid JPEG header + padding to reach desired size
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xc0\x00\x11\x08\x00\x10\x00\x10\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4'
    padding_size = (size_kb * 1024) - len(jpeg_header)
    if padding_size > 0:
        jpeg_data = jpeg_header + b'\x00' * padding_size
    else:
        jpeg_data = jpeg_header
    
    return base64.b64encode(jpeg_data).decode('utf-8')

def create_test_pdf_base64(size_kb: int = 50) -> str:
    """Create a test PDF as Base64"""
    # Minimal valid PDF content
    pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000200 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF'
    
    # Add padding to reach desired size
    padding_size = (size_kb * 1024) - len(pdf_content)
    if padding_size > 0:
        pdf_data = pdf_content + b'\n' + b' ' * padding_size
    else:
        pdf_data = pdf_content
    
    return base64.b64encode(pdf_data).decode('utf-8')

def test_file_size_limits():
    """Test file size limit validation"""
    logger.info("🧪 TESTING FILE SIZE LIMITS")
    
    # Test 1: Small file (should pass)
    logger.info("Test 1: Small image file (50KB)")
    small_image = create_test_image_base64(50)  # 50KB
    logger.info(f"   File size: {len(small_image)} characters")
    
    try:
        request = TeamRegistrationRequest(
            churchName="Test Church",
            teamName="Test Team",
            pastorLetter=small_image,
            captain={
                "name": "John Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "john@example.com"
            },
            viceCaptain={
                "name": "Jane Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "jane@example.com"
            },
            players=[{
                "name": "Player 1",
                "age": 25,
                "phone": "+1234567890",
                "role": "Batsman"
            }]
        )
        logger.info("   ✅ PASSED - Small file accepted")
    except Exception as e:
        logger.error(f"   ❌ FAILED - Small file rejected: {e}")
        return False
    
    # Test 2: Large file (should fail)
    logger.info("Test 2: Large image file (6MB)")
    large_image = create_test_image_base64(6000)  # 6MB
    logger.info(f"   File size: {len(large_image)} characters")
    
    try:
        request = TeamRegistrationRequest(
            churchName="Test Church",
            teamName="Test Team",
            pastorLetter=large_image,
            captain={
                "name": "John Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "john@example.com"
            },
            viceCaptain={
                "name": "Jane Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "jane@example.com"
            },
            players=[{
                "name": "Player 1",
                "age": 25,
                "phone": "+1234567890",
                "role": "Batsman"
            }]
        )
        logger.error("   ❌ FAILED - Large file should have been rejected")
        return False
    except ValueError as e:
        if "too large" in str(e):
            logger.info("   ✅ PASSED - Large file correctly rejected")
        else:
            logger.error(f"   ❌ FAILED - Wrong error message: {e}")
            return False
    except Exception as e:
        logger.error(f"   ❌ FAILED - Unexpected error: {e}")
        return False
    
    return True

def test_file_type_validation():
    """Test file type validation"""
    logger.info("🧪 TESTING FILE TYPE VALIDATION")
    
    # Test 1: Valid image (should pass)
    logger.info("Test 1: Valid JPEG image")
    valid_image = create_test_image_base64(100)
    
    try:
        request = TeamRegistrationRequest(
            churchName="Test Church",
            teamName="Test Team",
            pastorLetter=valid_image,
            captain={
                "name": "John Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "john@example.com"
            },
            viceCaptain={
                "name": "Jane Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "jane@example.com"
            },
            players=[{
                "name": "Player 1",
                "age": 25,
                "phone": "+1234567890",
                "role": "Batsman"
            }]
        )
        logger.info("   ✅ PASSED - Valid image accepted")
    except Exception as e:
        logger.error(f"   ❌ FAILED - Valid image rejected: {e}")
        return False
    
    # Test 2: Invalid Base64 (should fail)
    logger.info("Test 2: Invalid Base64 data")
    invalid_base64 = "not-valid-base64-data!!!"
    
    try:
        request = TeamRegistrationRequest(
            churchName="Test Church",
            teamName="Test Team",
            pastorLetter=invalid_base64,
            captain={
                "name": "John Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "john@example.com"
            },
            viceCaptain={
                "name": "Jane Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "jane@example.com"
            },
            players=[{
                "name": "Player 1",
                "age": 25,
                "phone": "+1234567890",
                "role": "Batsman"
            }]
        )
        logger.error("   ❌ FAILED - Invalid Base64 should have been rejected")
        return False
    except ValueError as e:
        if "Invalid Base64" in str(e) or "Invalid image" in str(e):
            logger.info("   ✅ PASSED - Invalid Base64 correctly rejected")
        else:
            logger.error(f"   ❌ FAILED - Wrong error message: {e}")
            return False
    except Exception as e:
        logger.error(f"   ❌ FAILED - Unexpected error: {e}")
        return False
    
    # Test 3: Valid PDF (should pass)
    logger.info("Test 3: Valid PDF document")
    valid_pdf = create_test_pdf_base64(100)
    
    try:
        request = TeamRegistrationRequest(
            churchName="Test Church",
            teamName="Test Team",
            captain={
                "name": "John Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "john@example.com"
            },
            viceCaptain={
                "name": "Jane Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "jane@example.com"
            },
            players=[{
                "name": "Player 1",
                "age": 25,
                "phone": "+1234567890",
                "role": "Batsman",
                "aadharFile": valid_pdf
            }]
        )
        logger.info("   ✅ PASSED - Valid PDF accepted")
    except Exception as e:
        logger.error(f"   ❌ FAILED - Valid PDF rejected: {e}")
        return False
    
    # Test 4: Invalid PDF (should fail)
    logger.info("Test 4: Invalid PDF (fake data)")
    invalid_pdf = base64.b64encode(b"This is not a PDF file").decode('utf-8')
    
    try:
        request = TeamRegistrationRequest(
            churchName="Test Church",
            teamName="Test Team",
            captain={
                "name": "John Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "john@example.com"
            },
            viceCaptain={
                "name": "Jane Doe",
                "phone": "+1234567890",
                "whatsapp": "1234567890",
                "email": "jane@example.com"
            },
            players=[{
                "name": "Player 1",
                "age": 25,
                "phone": "+1234567890",
                "role": "Batsman",
                "aadharFile": invalid_pdf
            }]
        )
        logger.error("   ❌ FAILED - Invalid PDF should have been rejected")
        return False
    except ValueError as e:
        if "must be a valid PDF" in str(e):
            logger.info("   ✅ PASSED - Invalid PDF correctly rejected")
        else:
            logger.error(f"   ❌ FAILED - Wrong error message: {e}")
            return False
    except Exception as e:
        logger.error(f"   ❌ FAILED - Unexpected error: {e}")
        return False
    
    return True

def main():
    """Run all validation tests"""
    logger.info("🚀 STARTING FILE UPLOAD VALIDATION TESTS")
    logger.info(f"Configuration: MAX_FILE_SIZE_MB = {settings.MAX_FILE_SIZE_MB}")
    logger.info(f"Configuration: MAX_BASE64_SIZE_CHARS = {settings.MAX_BASE64_SIZE_CHARS}")
    
    tests_passed = 0
    total_tests = 2
    
    # Test file size limits
    if test_file_size_limits():
        tests_passed += 1
        logger.info("✅ File size limits test: PASSED")
    else:
        logger.error("❌ File size limits test: FAILED")
    
    # Test file type validation
    if test_file_type_validation():
        tests_passed += 1
        logger.info("✅ File type validation test: PASSED")
    else:
        logger.error("❌ File type validation test: FAILED")
    
    logger.info(f"\n📊 TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    
    if tests_passed == total_tests:
        logger.info("🎉 ALL TESTS PASSED - File validation is working correctly!")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED - Check the validation logic")
        return 1

if __name__ == "__main__":
    sys.exit(main())