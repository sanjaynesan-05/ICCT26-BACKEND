#!/usr/bin/env python
"""
Quick endpoint verification test
Tests key routes with mock requests
"""

import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("\n" + "="*70)
print("ENDPOINT VERIFICATION TESTS")
print("="*70 + "\n")

tests = [
    {
        "name": "Health Check",
        "method": "GET",
        "path": "/health",
        "expected_status": 200
    },
    {
        "name": "Status Check",
        "method": "GET",
        "path": "/status",
        "expected_status": 200
    },
    {
        "name": "List Teams (Admin)",
        "method": "GET",
        "path": "/admin/teams",
        "expected_status": 200
    },
    {
        "name": "List Teams (API)",
        "method": "GET",
        "path": "/api/teams",
        "expected_status": 200
    },
    {
        "name": "API Docs",
        "method": "GET",
        "path": "/docs",
        "expected_status": 200
    },
    {
        "name": "ReDoc",
        "method": "GET",
        "path": "/redoc",
        "expected_status": 200
    }
]

print("Testing core endpoints:\n")

passed = 0
failed = 0

for test in tests:
    try:
        if test["method"] == "GET":
            response = client.get(test["path"])
        elif test["method"] == "POST":
            response = client.post(test["path"], json=test.get("data", {}))
        
        status_ok = response.status_code == test["expected_status"]
        status_symbol = "✅" if status_ok else "❌"
        
        print(f"{status_symbol} {test['name']}")
        print(f"   Path: {test['path']}")
        print(f"   Status: {response.status_code} (expected {test['expected_status']})")
        
        if status_ok:
            passed += 1
        else:
            failed += 1
        
        print()
    except Exception as e:
        print(f"❌ {test['name']}")
        print(f"   Error: {str(e)}\n")
        failed += 1

print("="*70)
print(f"ENDPOINT TEST RESULTS: {passed} passed, {failed} failed")
print("="*70 + "\n")

if failed == 0:
    print("✅ ALL ENDPOINT TESTS PASSED\n")
else:
    print(f"⚠️  {failed} endpoint(s) failed\n")
