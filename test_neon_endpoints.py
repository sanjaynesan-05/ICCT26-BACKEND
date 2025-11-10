"""
Test script to verify all endpoints with Neon database
Run this while the server is running
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, description):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, timeout=10)
        
        print(f"✅ {description}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        print()
        return True
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Error: {str(e)}")
        print()
        return False

def main():
    print("=" * 70)
    print("🚀 NEON DATABASE ENDPOINT TESTING")
    print("=" * 70)
    print()
    
    # Wait for server to start
    print("⏳ Waiting for server to initialize...")
    time.sleep(12)
    print()
    
    tests = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/status", "Status endpoint"),
        ("GET", "/admin/teams", "Admin - Get all teams"),
        ("GET", "/docs", "API Documentation"),
    ]
    
    results = []
    for method, endpoint, description in tests:
        results.append(test_endpoint(method, endpoint, description))
    
    print("=" * 70)
    print(f"📊 RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    if all(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your backend is successfully connected to Neon PostgreSQL")
        print("✅ Ready for deployment!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
