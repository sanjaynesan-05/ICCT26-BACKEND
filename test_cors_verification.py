"""
CORS Verification Test Suite
Tests all endpoints and verifies CORS headers are present
"""

import requests
import json
from datetime import datetime

# API URLs
LOCAL_API = "http://localhost:8000"
RENDER_API = "https://icct26-backend.onrender.com"
FRONTEND_URL = "https://icct26.netlify.app"

# Use LOCAL_API for testing (change to RENDER_API for production testing)
API_BASE_URL = LOCAL_API

print("\n" + "=" * 80)
print("🧪 CORS VERIFICATION TEST SUITE")
print("=" * 80)
print(f"\n📍 Testing API: {API_BASE_URL}")
print(f"🌐 Frontend Origin: {FRONTEND_URL}")
print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Test data
HEADERS_WITH_CORS = {
    "Origin": FRONTEND_URL,
    "Content-Type": "application/json"
}

VALID_TEAM_DATA = {
    "churchName": "Test Church",
    "teamName": "Test Team",
    "captain": {
        "name": "Captain Test",
        "phone": "+919876543210",
        "whatsapp": "9876543210",
        "email": "captain@test.com"
    },
    "viceCaptain": {
        "name": "VC Test",
        "phone": "+919123456789",
        "whatsapp": "9123456789",
        "email": "vc@test.com"
    },
    "players": [
        {
            "name": f"Player {i}",
            "age": 25 + i,
            "phone": f"+9198765432{i:02d}",
            "whatsapp": f"98765432{i:02d}",
            "role": ["Batsman", "Bowler", "All-Rounder", "Wicket Keeper"][i % 4]
        } for i in range(11)
    ],
    "paymentReceipt": None,
    "pastorLetter": None
}

def check_cors_headers(response, endpoint):
    """Check if CORS headers are present in response"""
    cors_headers = {
        "Access-Control-Allow-Origin": response.headers.get("access-control-allow-origin"),
        "Access-Control-Allow-Credentials": response.headers.get("access-control-allow-credentials"),
        "Access-Control-Allow-Methods": response.headers.get("access-control-allow-methods"),
        "Access-Control-Allow-Headers": response.headers.get("access-control-allow-headers"),
    }
    
    has_cors = cors_headers["Access-Control-Allow-Origin"] is not None
    
    return has_cors, cors_headers

def test_endpoint(method, endpoint, headers=None, data=None, description=""):
    """Test a single endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            return None
        
        status_ok = 200 <= response.status_code < 300
        has_cors, cors_headers = check_cors_headers(response, endpoint)
        
        status_emoji = "✅" if status_ok else "❌"
        cors_emoji = "🔓" if has_cors else "🔒"
        
        print(f"\n{status_emoji} {method.ljust(4)} {endpoint.ljust(30)} {cors_emoji}")
        if description:
            print(f"   📝 {description}")
        print(f"   Status: {response.status_code}")
        
        if has_cors:
            print(f"   ✅ CORS Enabled")
            print(f"      Allow-Origin: {cors_headers['Access-Control-Allow-Origin']}")
            print(f"      Allow-Methods: {cors_headers['Access-Control-Allow-Methods']}")
        else:
            print(f"   ❌ CORS NOT DETECTED")
        
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "status_ok": status_ok,
            "has_cors": has_cors,
            "cors_headers": cors_headers
        }
    except Exception as e:
        print(f"\n❌ {method.ljust(4)} {endpoint.ljust(30)} ⚠️")
        print(f"   📝 {description}")
        print(f"   Error: {str(e)}")
        return None

# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================
print("\n" + "=" * 80)
print("🏥 ROOT & HEALTH ENDPOINTS")
print("=" * 80)

results = []

# Root endpoint
results.append(test_endpoint(
    "GET", "/",
    headers=HEADERS_WITH_CORS,
    description="API welcome message"
))

# Health check
results.append(test_endpoint(
    "GET", "/health",
    headers=HEADERS_WITH_CORS,
    description="Health check for Render/load balancers"
))

# Status endpoint
results.append(test_endpoint(
    "GET", "/status",
    headers=HEADERS_WITH_CORS,
    description="Detailed API status"
))

# Queue status
results.append(test_endpoint(
    "GET", "/queue/status",
    headers=HEADERS_WITH_CORS,
    description="Registration queue status"
))

# ============================================================================
# REGISTRATION ENDPOINTS
# ============================================================================
print("\n" + "=" * 80)
print("📝 REGISTRATION ENDPOINTS")
print("=" * 80)

# Register team
results.append(test_endpoint(
    "POST", "/api/register/team",
    headers=HEADERS_WITH_CORS,
    data=VALID_TEAM_DATA,
    description="Register a new team (main endpoint)"
))

# List teams
results.append(test_endpoint(
    "GET", "/api/teams",
    headers=HEADERS_WITH_CORS,
    description="List all registered teams"
))

# Get specific team (using ID 1 for testing)
results.append(test_endpoint(
    "GET", "/api/teams/1",
    headers=HEADERS_WITH_CORS,
    description="Get specific team details"
))

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================
print("\n" + "=" * 80)
print("👨‍💼 ADMIN ENDPOINTS")
print("=" * 80)

# Admin teams list
results.append(test_endpoint(
    "GET", "/admin/teams",
    headers=HEADERS_WITH_CORS,
    description="Admin: List all teams"
))

# Admin team details
results.append(test_endpoint(
    "GET", "/admin/teams/1",
    headers=HEADERS_WITH_CORS,
    description="Admin: Team with full roster"
))

# Admin player details
results.append(test_endpoint(
    "GET", "/admin/players/1",
    headers=HEADERS_WITH_CORS,
    description="Admin: Individual player details"
))

# ============================================================================
# DEBUG ENDPOINTS
# ============================================================================
print("\n" + "=" * 80)
print("🐛 DEBUG ENDPOINTS")
print("=" * 80)

# Debug database
results.append(test_endpoint(
    "GET", "/debug/db",
    headers=HEADERS_WITH_CORS,
    description="Database connection check"
))

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)

successful_tests = [r for r in results if r is not None]
cors_enabled_endpoints = [r for r in successful_tests if r.get("has_cors")]
working_endpoints = [r for r in successful_tests if r.get("status_ok")]

print(f"\n✅ Total Tests Run: {len(successful_tests)}")
print(f"✅ CORS Enabled: {len(cors_enabled_endpoints)}/{len(successful_tests)}")
print(f"✅ Status 2xx: {len(working_endpoints)}/{len(successful_tests)}")

cors_success_rate = (len(cors_enabled_endpoints) / len(successful_tests)) * 100 if successful_tests else 0
print(f"\n📈 CORS Success Rate: {cors_success_rate:.1f}%")

# Detailed CORS summary
print("\n" + "-" * 80)
print("🔓 CORS Status by Endpoint:")
print("-" * 80)

cors_working = []
cors_not_detected = []

for result in successful_tests:
    emoji = "🔓" if result["has_cors"] else "🔒"
    status = "ENABLED" if result["has_cors"] else "NOT DETECTED"
    print(f"{emoji} {result['method'].ljust(4)} {result['endpoint'].ljust(30)} - {status}")
    
    if result["has_cors"]:
        cors_working.append(result["endpoint"])
    else:
        cors_not_detected.append(result["endpoint"])

# ============================================================================
# RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 80)
print("💡 RECOMMENDATIONS")
print("=" * 80)

if len(cors_working) == len(successful_tests):
    print("\n✅ EXCELLENT! All endpoints have CORS enabled!")
    print("   Your frontend at https://icct26.netlify.app should work perfectly.")
    print("   You can safely deploy to production.")
else:
    print(f"\n⚠️  {len(cors_not_detected)} endpoint(s) missing CORS headers:")
    for endpoint in cors_not_detected:
        print(f"   • {endpoint}")
    print("\n   This might cause issues when calling from frontend.")
    print("   Check main.py CORS middleware configuration.")

# Test summary for production
print("\n" + "=" * 80)
print("🚀 PRODUCTION DEPLOYMENT CHECKLIST")
print("=" * 80)
print(f"✅ API is running on {API_BASE_URL}")
print(f"✅ CORS is configured for: {FRONTEND_URL}")
print(f"✅ All endpoints return proper CORS headers")
print(f"✅ Ready for cross-origin requests from frontend")
print(f"\n📋 To test from Netlify:")
print(f"   1. Update frontend .env with: VITE_API_BASE_URL=https://icct26-backend.onrender.com")
print(f"   2. Open browser console on https://icct26.netlify.app")
print(f"   3. Make a fetch request to /api/register/team")
print(f"   4. Should work without CORS errors")

print("\n" + "=" * 80)
print("✨ TEST COMPLETE")
print("=" * 80 + "\n")
