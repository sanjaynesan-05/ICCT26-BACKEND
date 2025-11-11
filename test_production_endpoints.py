#!/usr/bin/env python3
"""
Production API Endpoint Test Suite
===================================
Test all endpoints from https://icct26-backend.onrender.com/

Usage: python test_production_endpoints.py
"""

import httpx
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Production URL
BASE_URL = "https://icct26-backend.onrender.com"

# Test results tracker
results = {
    "passed": [],
    "failed": [],
    "total": 0
}


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")


def print_test(name: str, method: str, endpoint: str):
    """Print test description"""
    print(f"{Colors.BLUE}[TEST] {method.upper():6} {endpoint}{Colors.RESET}")
    print(f"       Description: {name}")


def print_result(passed: bool, message: str, status_code: int = None):
    """Print test result"""
    if passed:
        status_str = f" (Status: {status_code})" if status_code else ""
        print(f"{Colors.GREEN}✅ PASS{Colors.RESET}{status_str}: {message}\n")
        results["passed"].append(message)
    else:
        status_str = f" (Status: {status_code})" if status_code else ""
        print(f"{Colors.RED}❌ FAIL{Colors.RESET}{status_str}: {message}\n")
        results["failed"].append(message)
    
    results["total"] += 1


def test_cors_headers(response: httpx.Response) -> Tuple[bool, str]:
    """Verify CORS headers are present"""
    cors_header = response.headers.get("access-control-allow-origin")
    
    if cors_header:
        return True, f"CORS header present: {cors_header}"
    else:
        return False, "Missing CORS header"


# ============================================================================
# HEALTH & DOCS ENDPOINTS
# ============================================================================

def test_health_endpoint():
    """Test: GET /health"""
    print_test("Health check endpoint", "GET", "/health")
    
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                cors_ok, cors_msg = test_cors_headers(response)
                
                print(f"       Response: {json.dumps(data, indent=10)}")
                print(f"       CORS: {cors_msg}")
                
                print_result(True, "Health check successful", response.status_code)
                return True
            else:
                print_result(False, f"Health check failed with status {response.status_code}", response.status_code)
                return False
    except Exception as e:
        print_result(False, f"Health endpoint error: {str(e)}")
        return False


def test_docs_endpoint():
    """Test: GET /docs"""
    print_test("OpenAPI documentation", "GET", "/docs")
    
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(f"{BASE_URL}/docs")
            
            if response.status_code == 200:
                print_result(True, "Swagger UI docs accessible", response.status_code)
                return True
            else:
                print_result(False, f"Docs failed with status {response.status_code}", response.status_code)
                return False
    except Exception as e:
        print_result(False, f"Docs endpoint error: {str(e)}")
        return False


def test_redoc_endpoint():
    """Test: GET /redoc"""
    print_test("ReDoc documentation", "GET", "/redoc")
    
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(f"{BASE_URL}/redoc")
            
            if response.status_code == 200:
                print_result(True, "ReDoc docs accessible", response.status_code)
                return True
            else:
                print_result(False, f"ReDoc failed with status {response.status_code}", response.status_code)
                return False
    except Exception as e:
        print_result(False, f"ReDoc endpoint error: {str(e)}")
        return False


# ============================================================================
# TEAM ENDPOINTS
# ============================================================================

def test_get_all_teams():
    """Test: GET /api/teams"""
    print_test("Get all teams", "GET", "/api/teams")
    
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/api/teams")
            
            if response.status_code == 200:
                data = response.json()
                cors_ok, cors_msg = test_cors_headers(response)
                
                teams_count = len(data.get("teams", []))
                print(f"       Teams found: {teams_count}")
                print(f"       CORS: {cors_msg}")
                
                if teams_count > 0:
                    first_team = data["teams"][0]
                    print(f"       Sample: {json.dumps(first_team, indent=10)[:200]}...")
                
                print_result(True, f"Retrieved {teams_count} teams", response.status_code)
                return True
            else:
                print_result(False, f"Failed to get teams", response.status_code)
                return False
    except Exception as e:
        print_result(False, f"Get teams error: {str(e)}")
        return False


def test_get_team_details():
    """Test: GET /api/teams/{team_id}"""
    print_test("Get specific team details", "GET", "/api/teams/{team_id}")
    
    try:
        with httpx.Client() as client:
            # First get all teams to get a valid team_id
            teams_response = client.get(f"{BASE_URL}/api/teams")
            
            if teams_response.status_code != 200:
                print_result(False, "Could not fetch teams first", teams_response.status_code)
                return False
            
            teams = teams_response.json().get("teams", [])
            if not teams:
                print_result(False, "No teams available for testing", teams_response.status_code)
                return False
            
            team_id = teams[0]["team_id"]
            
            # Now get specific team details
            response = client.get(f"{BASE_URL}/api/teams/{team_id}")
            
            if response.status_code == 200:
                data = response.json()
                cors_ok, cors_msg = test_cors_headers(response)
                
                print(f"       Team ID: {team_id}")
                print(f"       Response keys: {list(data.keys())}")
                print(f"       CORS: {cors_msg}")
                
                print_result(True, f"Retrieved team details for {team_id}", response.status_code)
                return True
            else:
                print_result(False, f"Failed to get team details", response.status_code)
                return False
    except Exception as e:
        print_result(False, f"Get team details error: {str(e)}")
        return False


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

def test_admin_get_all_teams():
    """Test: GET /admin/teams"""
    print_test("Admin: Get all teams", "GET", "/admin/teams")
    
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/admin/teams")
            
            if response.status_code == 200:
                data = response.json()
                cors_ok, cors_msg = test_cors_headers(response)
                
                teams_count = len(data.get("teams", []))
                print(f"       Teams found: {teams_count}")
                print(f"       CORS: {cors_msg}")
                
                if teams_count > 0:
                    first_team = data["teams"][0]
                    print(f"       Sample: {json.dumps(first_team, indent=10)[:200]}...")
                
                print_result(True, f"Retrieved {teams_count} teams via admin", response.status_code)
                return True
            else:
                print_result(False, f"Admin teams failed", response.status_code)
                return False
    except Exception as e:
        print_result(False, f"Admin teams error: {str(e)}")
        return False


def test_admin_get_team_details():
    """Test: GET /admin/teams/{team_id}"""
    print_test("Admin: Get team details", "GET", "/admin/teams/{team_id}")
    
    try:
        with httpx.Client() as client:
            # Get teams first
            teams_response = client.get(f"{BASE_URL}/admin/teams")
            
            if teams_response.status_code != 200:
                print_result(False, "Could not fetch admin teams", teams_response.status_code)
                return False
            
            teams = teams_response.json().get("teams", [])
            if not teams:
                print_result(False, "No teams available for admin test", teams_response.status_code)
                return False
            
            team_id = teams[0]["team_id"]
            
            # Get specific team details
            response = client.get(f"{BASE_URL}/admin/teams/{team_id}")
            
            if response.status_code == 200:
                data = response.json()
                cors_ok, cors_msg = test_cors_headers(response)
                
                print(f"       Team ID: {team_id}")
                print(f"       Response keys: {list(data.keys())}")
                print(f"       CORS: {cors_msg}")
                
                print_result(True, f"Admin retrieved team {team_id}", response.status_code)
                return True
            else:
                print_result(False, f"Admin team details failed", response.status_code)
                return False
    except Exception as e:
        print_result(False, f"Admin team details error: {str(e)}")
        return False


def test_admin_get_player_details():
    """Test: GET /admin/players/{player_id}"""
    print_test("Admin: Get player details", "GET", "/admin/players/{player_id}")
    
    try:
        with httpx.Client() as client:
            # Get teams first
            teams_response = client.get(f"{BASE_URL}/admin/teams")
            
            if teams_response.status_code != 200:
                print_result(False, "Could not fetch teams", teams_response.status_code)
                return False
            
            teams = teams_response.json().get("teams", [])
            if not teams:
                print_result(False, "No teams available", teams_response.status_code)
                return False
            
            # Get team details to find a player
            team_id = teams[0]["team_id"]
            team_response = client.get(f"{BASE_URL}/admin/teams/{team_id}")
            
            if team_response.status_code != 200:
                print_result(False, "Could not fetch team details", team_response.status_code)
                return False
            
            team_data = team_response.json()
            players = team_data.get("players", [])
            
            if not players:
                print_result(False, "No players available", team_response.status_code)
                return False
            
            player_id = players[0]["player_id"]
            
            # Get player details
            response = client.get(f"{BASE_URL}/admin/players/{player_id}")
            
            if response.status_code == 200:
                data = response.json()
                cors_ok, cors_msg = test_cors_headers(response)
                
                print(f"       Player ID: {player_id}")
                print(f"       Response keys: {list(data.keys())}")
                print(f"       CORS: {cors_msg}")
                
                print_result(True, f"Admin retrieved player {player_id}", response.status_code)
                return True
            else:
                print_result(False, f"Admin player details failed", response.status_code)
                return False
    except Exception as e:
        print_result(False, f"Admin player details error: {str(e)}")
        return False


# ============================================================================
# CORS PREFLIGHT TESTS
# ============================================================================

def test_cors_preflight():
    """Test: OPTIONS request for CORS preflight"""
    print_test("CORS preflight request", "OPTIONS", "/api/teams")
    
    try:
        with httpx.Client() as client:
            response = client.options(
                f"{BASE_URL}/api/teams",
                headers={
                    "Origin": "https://icct26.netlify.app",
                    "Access-Control-Request-Method": "GET",
                }
            )
            
            cors_origin = response.headers.get("access-control-allow-origin")
            cors_methods = response.headers.get("access-control-allow-methods")
            cors_headers = response.headers.get("access-control-allow-headers")
            
            print(f"       Origin allowed: {cors_origin}")
            print(f"       Methods allowed: {cors_methods}")
            print(f"       Headers allowed: {cors_headers}")
            
            if cors_origin and cors_methods:
                print_result(True, "CORS preflight successful", response.status_code)
                return True
            else:
                print_result(False, "CORS preflight missing headers", response.status_code)
                return False
    except Exception as e:
        print_result(False, f"CORS preflight error: {str(e)}")
        return False


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    print_header("🧪 ICCT26 BACKEND - PRODUCTION API TEST SUITE")
    print(f"Testing: {BASE_URL}\n")
    
    # Health & Docs
    print_header("📋 Health & Documentation Endpoints")
    test_health_endpoint()
    test_docs_endpoint()
    test_redoc_endpoint()
    
    # Team Endpoints
    print_header("🏏 Team Endpoints")
    test_get_all_teams()
    test_get_team_details()
    
    # Admin Endpoints
    print_header("👨‍💼 Admin Endpoints")
    test_admin_get_all_teams()
    test_admin_get_team_details()
    test_admin_get_player_details()
    
    # CORS Tests
    print_header("🔐 CORS Configuration Tests")
    test_cors_preflight()
    
    # Summary
    print_header("📊 Test Summary")
    passed = len(results["passed"])
    failed = len(results["failed"])
    total = results["total"]
    
    print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}❌ Failed: {failed}{Colors.RESET}")
    print(f"{Colors.BLUE}📊 Total:  {total}{Colors.RESET}\n")
    
    if total > 0:
        pass_rate = (passed / total) * 100
        print(f"{Colors.BOLD}Pass Rate: {pass_rate:.1f}%{Colors.RESET}\n")
    
    if failed > 0:
        print(f"{Colors.YELLOW}Failed tests:{Colors.RESET}")
        for test in results["failed"]:
            print(f"  • {test}")
    
    print_header("✅ Test Execution Complete")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
