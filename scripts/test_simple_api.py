#!/usr/bin/env python3
"""
Test script for simple FastAPI backend with PostgreSQL
"""
import requests
import json

BASE_URL = "http://localhost:8001"

print("🧪 Testing ICCT26 Simple Backend with PostgreSQL")
print("=" * 60)

# Test 1: Root endpoint
print("\n1️⃣ Testing root endpoint...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Register team
print("\n2️⃣ Testing team registration...")
try:
    response = requests.post(
        f"{BASE_URL}/register/team",
        params={
            "name": "Test Warriors",
            "captain": "John Doe"
        }
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
    print(f"   ✅ Team registered with ID: {result['id']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Register another team
print("\n3️⃣ Testing second team registration...")
try:
    response = requests.post(
        f"{BASE_URL}/register/team",
        params={
            "name": "Cricket Champions",
            "captain": "Jane Smith"
        }
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
    print(f"   ✅ Team registered with ID: {result['id']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Testing complete!")
print("\n💡 Next steps:")
print("   1. Check PostgreSQL: psql -U postgres -d icct26_db -c 'SELECT * FROM teams;'")
print("   2. Open Swagger UI: http://localhost:8001/docs")
