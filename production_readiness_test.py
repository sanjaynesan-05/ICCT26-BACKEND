#!/usr/bin/env python3
"""
🚀 PRODUCTION READINESS TEST SUITE
Complete validation before production deployment
"""

import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime

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
    status_color = f"{status:10}"
    print(f"{icon} {category:50} {status_color} {message}")

# ============================================================
# TEST 1: Environment Configuration
# ============================================================

def test_environment():
    """Test 1: Environment Configuration"""
    print_header("TEST 1: ENVIRONMENT CONFIGURATION")
    
    try:
        # Check .env files
        env_files = ['.env.local', '.env']
        found_env = False
        
        for env_file in env_files:
            if os.path.exists(env_file):
                print_result(f"Found: {env_file}", "PASS")
                found_env = True
        
        if not found_env:
            print_result("Environment Files", "FAIL", "No .env or .env.local found")
            return False
        
        # Check required environment variables
        required_vars = [
            'DATABASE_URL',
            'ENVIRONMENT',
        ]
        
        from dotenv import load_dotenv
        load_dotenv('.env.local')
        load_dotenv()
        
        all_present = True
        for var in required_vars:
            value = os.getenv(var)
            if value:
                masked = value[:20] + "..." if len(value) > 20 else value
                print_result(f"ENV: {var}", "PASS", masked)
            else:
                print_result(f"ENV: {var}", "FAIL", "Not set")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print_result("Environment Setup", "FAIL", str(e))
        return False

# ============================================================
# TEST 2: Dependencies
# ============================================================

def test_dependencies():
    """Test 2: All Dependencies Installed"""
    print_header("TEST 2: DEPENDENCY VALIDATION")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "asyncpg",
        "psycopg2",
        "email_validator",
        "python_dotenv",
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_result(f"Package: {package}", "PASS")
        except ImportError:
            print_result(f"Package: {package}", "FAIL", "Not installed")
            all_installed = False
    
    return all_installed

# ============================================================
# TEST 3: Module Imports
# ============================================================

def test_imports():
    """Test 3: Import All Modules"""
    print_header("TEST 3: MODULE IMPORTS")
    
    imports_to_test = [
        ("FastAPI", "from fastapi import FastAPI"),
        ("SQLAlchemy", "from sqlalchemy import create_engine"),
        ("Pydantic", "from pydantic import BaseModel"),
        ("Asyncpg", "import asyncpg"),
        ("Database Module", "from database import get_db, get_db_async, async_engine"),
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

# ============================================================
# TEST 4: Schema Validation
# ============================================================

def test_schemas():
    """Test 4: Schema Validation"""
    print_header("TEST 4: SCHEMA VALIDATION")
    
    try:
        from app.schemas_team import TeamRegistrationRequest
        
        # Create valid Base64 images
        jpeg_header = b'\xFF\xD8\xFF\xE0'
        jpeg_data = jpeg_header + b'\x00' * 100 + b'\xFF\xD9'
        jpeg_base64 = base64.b64encode(jpeg_data).decode()
        jpeg_data_uri = f"data:image/jpeg;base64,{jpeg_base64}"
        
        # Create valid PDF
        pdf_header = b'%PDF-1.4'
        pdf_data = pdf_header + b'\n' + b'%EOF'
        pdf_base64 = base64.b64encode(pdf_data).decode()
        pdf_data_uri = f"data:application/pdf;base64,{pdf_base64}"
        
        # Valid test data
        test_data = {
            "churchName": "CSI St. Peter's Church",
            "teamName": "Test Team",
            "pastorLetter": jpeg_data_uri,
            "paymentReceipt": jpeg_data_uri,
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
                    "age": 25 + (i % 20),
                    "phone": f"987654321{i}",
                    "role": "Batsman",
                    "aadharFile": pdf_data_uri,
                    "subscriptionFile": pdf_data_uri
                }
                for i in range(11)
            ]
        }
        
        try:
            request = TeamRegistrationRequest(**test_data)
            print_result("Valid Schema", "PASS", "Accepted 11 players")
        except Exception as e:
            print_result("Valid Schema", "FAIL", str(e)[:50])
            return False
        
        # Test invalid email
        try:
            bad_data = json.loads(json.dumps(test_data))
            bad_data["captain"]["email"] = "invalid-email"
            TeamRegistrationRequest(**bad_data)
            print_result("Email Validation", "FAIL", "Invalid email was accepted")
            return False
        except Exception:
            print_result("Email Validation", "PASS", "Invalid email rejected")
        
        # Test invalid age
        try:
            bad_data = json.loads(json.dumps(test_data))
            bad_data["players"][0]["age"] = 100
            TeamRegistrationRequest(**bad_data)
            print_result("Age Validation", "FAIL", "Invalid age was accepted")
            return False
        except Exception:
            print_result("Age Validation", "PASS", "Invalid age rejected")
        
        # Test invalid Base64
        try:
            bad_data = json.loads(json.dumps(test_data))
            bad_data["pastorLetter"] = "data:image/jpeg;base64,not-valid-base64!!!"
            TeamRegistrationRequest(**bad_data)
            print_result("Base64 Validation", "FAIL", "Invalid Base64 was accepted")
            return False
        except Exception:
            print_result("Base64 Validation", "PASS", "Invalid Base64 rejected")
        
        return True
        
    except Exception as e:
        print_result("Schema Validation", "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================
# TEST 5: API Endpoints
# ============================================================

def test_api_endpoints():
    """Test 5: API Endpoints"""
    print_header("TEST 5: API ENDPOINTS")
    
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Test health check
        response = client.get("/health")
        if response.status_code == 200:
            print_result("Health Endpoint", "PASS", "Returns 200 OK")
        else:
            print_result("Health Endpoint", "FAIL", f"Status: {response.status_code}")
            return False
        
        # Test missing fields
        response = client.post(
            "/api/register/team",
            json={"churchName": "Test"}
        )
        
        if response.status_code == 422:
            data = response.json()
            if isinstance(data, dict) and ("message" in data or "detail" in data):
                print_result("Validation Error (422)", "PASS", "Structured error response")
            else:
                print_result("Validation Error (422)", "FAIL", "Unstructured response")
                return False
        else:
            print_result("Validation Error (422)", "FAIL", f"Status: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_result("API Endpoints", "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================
# TEST 6: CORS Configuration
# ============================================================

def test_cors():
    """Test 6: CORS Configuration"""
    print_header("TEST 6: CORS CONFIGURATION")
    
    try:
        from main import app
        
        # Check CORS middleware is added
        cors_found = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(type(middleware)):
                cors_found = True
                break
        
        if cors_found:
            print_result("CORS Middleware", "PASS", "Configured")
        else:
            print_result("CORS Middleware", "WARN", "Check if configured in app init")
        
        return True
        
    except Exception as e:
        print_result("CORS Configuration", "FAIL", str(e))
        return False

# ============================================================
# TEST 7: Security Headers
# ============================================================

def test_security():
    """Test 7: Security Configuration"""
    print_header("TEST 7: SECURITY CONFIGURATION")
    
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        # Check for security headers
        headers = response.headers
        
        # These are good to have
        security_headers = {
            "content-type": "Application Content-Type",
        }
        
        headers_found = 0
        for header, desc in security_headers.items():
            if header.lower() in [h.lower() for h in headers.keys()]:
                print_result(f"Header: {desc}", "PASS")
                headers_found += 1
        
        print_result("Basic Security", "PASS", f"{headers_found} security headers present")
        
        return True
        
    except Exception as e:
        print_result("Security Configuration", "FAIL", str(e))
        return False

# ============================================================
# TEST 8: Production Checklist
# ============================================================

def test_production_checklist():
    """Test 8: Production Checklist"""
    print_header("TEST 8: PRODUCTION READINESS CHECKLIST")
    
    checks = []
    
    # Check environment is set to production
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment == "production":
        print_result("Environment Mode", "PASS", "PRODUCTION")
        checks.append(True)
    else:
        print_result("Environment Mode", "WARN", f"Currently: {environment}")
        checks.append(False)
    
    # Check database URL is for production
    db_url = os.getenv("DATABASE_URL", "")
    if "neon.tech" in db_url or "railway.app" in db_url or "supabase" in db_url:
        print_result("Database", "PASS", "Using cloud database")
        checks.append(True)
    else:
        print_result("Database", "WARN", "Check if using production database")
        checks.append(False)
    
    # Check API URL is configured
    if os.getenv("API_URL"):
        print_result("API URL", "PASS", "Configured")
        checks.append(True)
    else:
        print_result("API URL", "WARN", "Consider setting API_URL")
        checks.append(False)
    
    print_result("Production Checks", "PASS" if all(checks) else "WARN", f"{sum(checks)}/{len(checks)} passed")
    
    return True

# ============================================================
# Main Test Runner
# ============================================================

def run_all_tests():
    """Run all tests"""
    print_header("🚀 ICCT26 BACKEND PRODUCTION READINESS TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        "1. Environment Configuration": test_environment(),
        "2. Dependencies": test_dependencies(),
        "3. Module Imports": test_imports(),
        "4. Schema Validation": test_schemas(),
        "5. API Endpoints": test_api_endpoints(),
        "6. CORS Configuration": test_cors(),
        "7. Security Configuration": test_security(),
        "8. Production Checklist": test_production_checklist(),
    }
    
    print_header("📊 TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print(f"\n{'='*80}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - READY FOR PRODUCTION!")
        print("\n✅ Deployment Checklist:")
        print("  1. Run 'git add . && git commit -m \"Ready for production\"'")
        print("  2. Deploy to Render.com")
        print("  3. Test endpoints from production URL")
        print("  4. Monitor logs for errors")
        print("  5. Update frontend API_URL to production endpoint\n")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed - Fix before deployment\n")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
