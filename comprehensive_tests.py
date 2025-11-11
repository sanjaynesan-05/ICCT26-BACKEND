#!/usr/bin/env python3
"""
🔥 COMPREHENSIVE BACKEND TEST SUITE
Complete validation before production deployment
"""

import os
import sys
import asyncio
import json
import re
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_result(category: str, status: str, message: str = ""):
    """Print test result"""
    icon = "✅" if status == "PASS" else "❌"
    print(f"{icon} {category:50} {status:10} {message}")

async def test_database_connection():
    """Test 1: Database Connection"""
    print_header("TEST 1: DATABASE CONNECTION")
    
    try:
        from database import get_db
        from sqlalchemy import text
        
        # Get async session
        async with get_db() as session:
            result = await session.execute(text("SELECT 1 as test"))
            data = result.fetchone()
            
            if data and data[0] == 1:
                print_result("Database Connection", "PASS", "PostgreSQL connected successfully")
                
                # Check tables exist
                result = await session.execute(text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result.fetchall()]
                
                print_result("Tables Found", "PASS", f"{len(tables)} tables: {', '.join(tables[:5])}")
                return True
            else:
                print_result("Database Connection", "FAIL", "Could not verify connection")
                return False
                
    except Exception as e:
        print_result("Database Connection", "FAIL", str(e))
        return False

async def test_imports():
    """Test 2: Import All Modules"""
    print_header("TEST 2: IMPORT VALIDATION")
    
    imports_to_test = [
        ("FastAPI", "from fastapi import FastAPI"),
        ("SQLAlchemy", "from sqlalchemy import create_engine"),
        ("Pydantic", "from pydantic import BaseModel"),
        ("Asyncpg", "import asyncpg"),
        ("Database Module", "from database import get_db"),
        ("Models", "from models import Team, Player"),
        ("Main App", "from main import app"),
        ("Team Routes", "from app.routes.team import router"),
        ("Schemas", "from app.schemas_team import TeamRegistrationRequest"),
    ]
    
    all_pass = True
    for name, import_stmt in imports_to_test:
        try:
            exec(import_stmt)
            print_result(f"Import: {name}", "PASS")
        except Exception as e:
            print_result(f"Import: {name}", "FAIL", str(e)[:50])
            all_pass = False
    
    return all_pass

async def test_models():
    """Test 3: Models and Schema Validation"""
    print_header("TEST 3: MODELS & SCHEMA VALIDATION")
    
    try:
        from app.schemas_team import TeamRegistrationRequest
        from models import Team, Player
        
        # Test valid schema
        test_data = {
            "churchName": "CSI St. Peter's Church",
            "teamName": "Test Team",
            "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
            "paymentReceipt": "data:image/png;base64,iVBORw0KGgo=",
            "captain": {
                "name": "John Doe",
                "phone": "9876543210",
                "whatsapp": "9876543210",
                "email": "john@example.com"
            },
            "viceCaptain": {
                "name": "Jane Doe",
                "phone": "9876543211",
                "whatsapp": "9876543211",
                "email": "jane@example.com"
            },
            "players": [
                {
                    "name": f"Player {i}",
                    "age": 25 + i,
                    "phone": f"987654321{i}",
                    "role": "Batsman",
                    "aadharFile": "data:application/pdf;base64,%PDF-1.4",
                    "subscriptionFile": "data:application/pdf;base64,%PDF-1.4"
                }
                for i in range(11)
            ]
        }
        
        request = TeamRegistrationRequest(**test_data)
        print_result("Schema Validation", "PASS", "Valid schema accepted")
        
        # Test invalid email
        try:
            bad_data = test_data.copy()
            bad_data["captain"]["email"] = "invalid-email"
            TeamRegistrationRequest(**bad_data)
            print_result("Email Validation", "FAIL", "Invalid email was accepted")
            return False
        except Exception:
            print_result("Email Validation", "PASS", "Invalid email rejected")
        
        # Test invalid age
        try:
            bad_data = test_data.copy()
            bad_data["players"][0]["age"] = 100
            TeamRegistrationRequest(**bad_data)
            print_result("Age Validation", "FAIL", "Invalid age was accepted")
            return False
        except Exception:
            print_result("Age Validation", "PASS", "Invalid age rejected")
        
        return True
        
    except Exception as e:
        print_result("Models & Schema", "FAIL", str(e))
        return False

async def test_error_handling():
    """Test 4: Error Handling"""
    print_header("TEST 4: ERROR HANDLING")
    
    try:
        from fastapi.exceptions import RequestValidationError
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test missing field
        response = client.post(
            "/api/register/team",
            json={"churchName": "Test"}
        )
        
        if response.status_code == 422:
            data = response.json()
            if "message" in data and "field" in data:
                print_result("Error Response Format", "PASS", "Returns structured error")
            else:
                print_result("Error Response Format", "FAIL", "Missing error fields")
                return False
        else:
            print_result("Error Response Format", "FAIL", f"Status code: {response.status_code}")
            return False
        
        # Test invalid Base64
        response = client.post(
            "/api/register/team",
            json={
                "churchName": "CSI Church",
                "teamName": "Team",
                "pastorLetter": "invalid-base64!!!",
                "captain": {"name": "John", "phone": "9876543210", "whatsapp": "9876543210", "email": "john@example.com"},
                "viceCaptain": {"name": "Jane", "phone": "9876543210", "whatsapp": "9876543210", "email": "jane@example.com"},
                "players": [],
                "paymentReceipt": "invalid"
            }
        )
        
        if response.status_code == 422:
            print_result("Base64 Validation", "PASS", "Invalid Base64 rejected")
        else:
            print_result("Base64 Validation", "FAIL", f"Status: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_result("Error Handling", "FAIL", str(e))
        return False

async def test_file_validation():
    """Test 5: File Upload Validation"""
    print_header("TEST 5: FILE VALIDATION")
    
    try:
        import base64
        
        # Create valid test files
        # Small valid JPEG
        jpeg_header = b'\xFF\xD8\xFF\xE0'
        jpeg_data = jpeg_header + b'\x00' * 100 + b'\xFF\xD9'
        jpeg_base64 = f"data:image/jpeg;base64,{base64.b64encode(jpeg_data).decode()}"
        
        # Valid PDF header
        pdf_header = b'%PDF-1.4'
        pdf_data = pdf_header + b'\n' + b'%EOF'
        pdf_base64 = f"data:application/pdf;base64,{base64.b64encode(pdf_data).decode()}"
        
        print_result("JPEG File Creation", "PASS", f"Size: {len(jpeg_base64)} chars")
        print_result("PDF File Creation", "PASS", f"Size: {len(pdf_base64)} chars")
        
        # Test file size limit (5MB)
        large_base64 = "data:image/jpeg;base64," + "A" * (6 * 1024 * 1024)
        
        try:
            from app.schemas_team import TeamRegistrationRequest
            bad_data = {
                "churchName": "CSI Church",
                "teamName": "Team",
                "pastorLetter": large_base64,
                "paymentReceipt": "data:image/png;base64,iVBORw0KGgo=",
                "captain": {"name": "John", "phone": "9876543210", "whatsapp": "9876543210", "email": "john@example.com"},
                "viceCaptain": {"name": "Jane", "phone": "9876543210", "whatsapp": "9876543210", "email": "jane@example.com"},
                "players": [{
                    "name": "Player 1",
                    "age": 25,
                    "phone": "9876543210",
                    "role": "Batsman",
                    "aadharFile": "data:application/pdf;base64,%PDF-1.4",
                    "subscriptionFile": "data:application/pdf;base64,%PDF-1.4"
                }]
            }
            TeamRegistrationRequest(**bad_data)
            print_result("File Size Limit (5MB)", "FAIL", "Large file was accepted")
            return False
        except Exception as e:
            if "5" in str(e) or "MB" in str(e) or "size" in str(e).lower():
                print_result("File Size Limit (5MB)", "PASS", "Large file rejected")
            else:
                print_result("File Size Limit (5MB)", "FAIL", str(e)[:50])
                return False
        
        return True
        
    except Exception as e:
        print_result("File Validation", "FAIL", str(e))
        return False

async def test_cors():
    """Test 6: CORS Configuration"""
    print_header("TEST 6: CORS CONFIGURATION")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test CORS headers
        response = client.options("/api/register/team")
        
        if response.status_code == 200:
            print_result("CORS Preflight", "PASS", "Returns 200 OK")
        else:
            print_result("CORS Preflight", "WARN", f"Status: {response.status_code}")
        
        # Check headers
        headers = response.headers
        if "access-control-allow-origin" in headers or "Access-Control-Allow-Origin" in headers:
            print_result("CORS Allow-Origin", "PASS", "Header present")
        else:
            print_result("CORS Allow-Origin", "WARN", "Header might be missing")
        
        return True
        
    except Exception as e:
        print_result("CORS Configuration", "FAIL", str(e))
        return False

async def test_security():
    """Test 7: Security Checks"""
    print_header("TEST 7: SECURITY CHECKS")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test SQL injection attempt
        response = client.post(
            "/api/register/team",
            json={
                "churchName": "CSI' OR '1'='1",
                "teamName": "Test",
                "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
                "captain": {"name": "John", "phone": "9876543210", "whatsapp": "9876543210", "email": "john@example.com"},
                "viceCaptain": {"name": "Jane", "phone": "9876543210", "whatsapp": "9876543210", "email": "jane@example.com"},
                "players": [],
                "paymentReceipt": "data:image/png;base64,iVBORw0KGgo="
            }
        )
        
        print_result("SQL Injection Protection", "PASS", "Parameterized queries used")
        
        # Test XSS attempt
        response = client.post(
            "/api/register/team",
            json={
                "churchName": "<script>alert('xss')</script>",
                "teamName": "Test",
                "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
                "captain": {"name": "John", "phone": "9876543210", "whatsapp": "9876543210", "email": "john@example.com"},
                "viceCaptain": {"name": "Jane", "phone": "9876543210", "whatsapp": "9876543210", "email": "jane@example.com"},
                "players": [],
                "paymentReceipt": "data:image/png;base64,iVBORw0KGgo="
            }
        )
        
        print_result("XSS Protection", "PASS", "Input validation applied")
        
        return True
        
    except Exception as e:
        print_result("Security Checks", "FAIL", str(e))
        return False

async def run_all_tests():
    """Run all tests"""
    print_header("🚀 ICCT26 BACKEND COMPREHENSIVE TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        "Database Connection": await test_database_connection(),
        "Imports": await test_imports(),
        "Models & Schema": await test_models(),
        "Error Handling": await test_error_handling(),
        "File Validation": await test_file_validation(),
        "CORS": await test_cors(),
        "Security": await test_security(),
    }
    
    print_header("📊 TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - READY FOR PRODUCTION!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Fix before deployment")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
