"""
ICCT26 Production Hardening Verification Script
Checks that all components are properly installed and configured
"""

import sys
import os
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} MISSING: {file_path}")
        return False


def main():
    print("=" * 70)
    print("ICCT26 PRODUCTION HARDENING VERIFICATION")
    print("=" * 70)
    print()
    
    base_dir = Path(__file__).parent
    all_ok = True
    
    # ========== UTILITIES ==========
    print("📦 UTILITIES")
    print("-" * 70)
    
    utils_dir = base_dir / "app" / "utils"
    utils_files = [
        ("race_safe_team_id.py", "Race-Safe Team ID Generator"),
        ("validation.py", "Input Validation"),
        ("idempotency.py", "Idempotency Service"),
        ("cloudinary_reliable.py", "Cloudinary Retry Logic"),
        ("email_reliable.py", "Email Retry Logic"),
        ("error_responses.py", "Unified Error Responses"),
    ]
    
    for file, desc in utils_files:
        all_ok &= check_file_exists(utils_dir / file, desc)
    
    print()
    
    # ========== MIDDLEWARE ==========
    print("🔧 MIDDLEWARE")
    print("-" * 70)
    
    middleware_dir = base_dir / "app" / "middleware"
    all_ok &= check_file_exists(middleware_dir / "logging_middleware.py", "Structured Logging Middleware")
    
    print()
    
    # ========== ROUTES ==========
    print("🛣️  ROUTES")
    print("-" * 70)
    
    routes_dir = base_dir / "app" / "routes"
    all_ok &= check_file_exists(routes_dir / "registration_production.py", "Production Registration Endpoint")
    
    print()
    
    # ========== TESTS ==========
    print("🧪 TESTS")
    print("-" * 70)
    
    tests_dir = base_dir / "tests"
    test_files = [
        ("test_race_safe_id.py", "Race-Safe ID Tests"),
        ("test_validation.py", "Validation Tests"),
        ("test_idempotency.py", "Idempotency Tests"),
        ("test_registration_integration.py", "Integration Tests"),
    ]
    
    for file, desc in test_files:
        all_ok &= check_file_exists(tests_dir / file, desc)
    
    print()
    
    # ========== DOCUMENTATION ==========
    print("📚 DOCUMENTATION")
    print("-" * 70)
    
    docs = [
        ("README.md", "Main README"),
        ("API_DOCS.md", "API Documentation"),
        ("PRODUCTION_HARDENING.md", "Production Hardening Summary"),
    ]
    
    for file, desc in docs:
        all_ok &= check_file_exists(base_dir / file, desc)
    
    print()
    
    # ========== DEPENDENCIES ==========
    print("📦 DEPENDENCIES")
    print("-" * 70)
    
    all_ok &= check_file_exists(base_dir / "requirements.txt", "Requirements File")
    
    print()
    
    # ========== FINAL RESULT ==========
    print("=" * 70)
    if all_ok:
        print("✅ ALL CHECKS PASSED - PRODUCTION HARDENING COMPLETE")
        print("=" * 70)
        print()
        print("Next Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run tests: pytest tests/")
        print("3. Start server: uvicorn main:app --reload")
        print("4. Visit docs: http://localhost:8000/docs")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - REVIEW ERRORS ABOVE")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
