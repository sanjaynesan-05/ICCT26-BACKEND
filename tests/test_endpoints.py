#!/usr/bin/env python3
"""
Endpoint integration tests for ICCT26 API.

Tests all major endpoints to verify they return correct responses.
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_root_endpoint() -> bool:
    """Test the root endpoint returns API info."""
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "active"
        print("✅ Root endpoint test PASSED")
        return True
    except Exception as e:
        print(f"❌ Root endpoint test FAILED: {e}")
        return False

def test_health_endpoint() -> bool:
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        print("✅ Health endpoint test PASSED")
        return True
    except Exception as e:
        print(f"❌ Health endpoint test FAILED: {e}")
        return False

def test_status_endpoint() -> bool:
    """Test the status endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        print("✅ Status endpoint test PASSED")
        return True
    except Exception as e:
        print(f"❌ Status endpoint test FAILED: {e}")
        return False

def test_admin_teams_endpoint() -> bool:
    """Test the admin teams endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/admin/teams")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "teams" in data
        print("✅ Admin teams endpoint test PASSED")
        return True
    except Exception as e:
        print(f"❌ Admin teams endpoint test FAILED: {e}")
        return False

def test_docs_endpoint() -> bool:
    """Test the API documentation endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
        print("✅ Docs endpoint test PASSED")
        return True
    except Exception as e:
        print(f"❌ Docs endpoint test FAILED: {e}")
        return False

def run_all_tests() -> None:
    """Run all endpoint tests."""
    print("\n" + "="*50)
    print("🧪 ICCT26 API Endpoint Tests")
    print("="*50 + "\n")
    
    tests = [
        test_root_endpoint,
        test_health_endpoint,
        test_status_endpoint,
        test_admin_teams_endpoint,
        test_docs_endpoint,
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("="*50)
    print(f"📊 Results: {passed}/{total} tests PASSED")
    print("="*50 + "\n")
    
    if passed == total:
        print("🎉 All tests PASSED! API is working correctly.\n")
    else:
        print(f"⚠️  {total - passed} test(s) FAILED. Check output above.\n")

if __name__ == "__main__":
    run_all_tests()
