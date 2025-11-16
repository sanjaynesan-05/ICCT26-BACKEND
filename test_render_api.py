#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for ICCT26 Backend
Tests all endpoints and functionalities including the new group_photo feature

Run with: python test_production_api.py
"""

import requests
import json
import base64
import time
from typing import Dict, Any, Tuple
from pathlib import Path
import sys

# Configuration
BASE_URL = "https://icct26-backend.onrender.com"
TIMEOUT = 30

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.failures = []

    def add_pass(self, test_name: str):
        self.passed += 1
        self.total += 1
        print(f"{Colors.GREEN}✓ {test_name}{Colors.RESET}")

    def add_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.total += 1
        self.failures.append((test_name, reason))
        print(f"{Colors.RED}✗ {test_name}{Colors.RESET}")
        print(f"  {Colors.YELLOW}Reason: {reason}{Colors.RESET}")

    def print_summary(self):
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Test Summary{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}Passed: {self.passed}/{self.total}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}/{self.total}{Colors.RESET}")
        if self.failures:
            print(f"\n{Colors.BOLD}Failed Tests:{Colors.RESET}")
            for test_name, reason in self.failures:
                print(f"  - {test_name}: {reason}")
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}")
        return self.failed == 0

def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")

def create_test_image_base64() -> str:
    """Create a minimal valid PNG image as base64"""
    # Minimal valid PNG (1x1 transparent pixel)
    png_bytes = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
        0x42, 0x60, 0x82
    ])
    return base64.b64encode(png_bytes).decode('utf-8')

def create_test_pdf_base64() -> str:
    """Create a minimal valid PDF as base64"""
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000260 00000 n
0000000347 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
441
%%EOF"""
    return base64.b64encode(pdf_content).decode('utf-8')

def test_health_check(results: TestResults):
    """Test 1: Health Check"""
    print_section("Test 1: Health Check")
    try:
        response = requests.get(
            f"{BASE_URL}/health",
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            results.add_pass("Health Check - API is running")
            print(f"  Response: {response.json()}")
        else:
            results.add_fail("Health Check", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Health Check", str(e))

def test_api_info(results: TestResults):
    """Test 2: API Info"""
    print_section("Test 2: API Info")
    try:
        response = requests.get(
            f"{BASE_URL}/docs",
            timeout=TIMEOUT,
            allow_redirects=True
        )
        if response.status_code == 200:
            results.add_pass("API Info - OpenAPI docs accessible")
        else:
            results.add_fail("API Info", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("API Info", str(e))

def test_team_registration(results: TestResults) -> Dict[str, Any]:
    """Test 3: Team Registration"""
    print_section("Test 3: Team Registration (with Group Photo)")
    
    registration_data = {
        "churchName": "Test Church",
        "teamName": "Test Team",
        "pastorLetter": create_test_pdf_base64(),
        "paymentReceipt": create_test_image_base64(),
        "groupPhoto": create_test_image_base64(),  # NEW FIELD
        "captain": {
            "name": "Captain John",
            "phone": "9876543210",
            "email": "captain@test.com",
            "whatsapp": "9876543210"
        },
        "viceCaptain": {
            "name": "Vice Captain Jane",
            "phone": "9876543211",
            "email": "vicecaptain@test.com",
            "whatsapp": "9876543211"
        },
        "players": [
            {
                "name": f"Player {i}",
                "role": "Batsman" if i % 2 == 0 else "Bowler",
                "aadharFile": create_test_pdf_base64(),
                "subscriptionFile": create_test_pdf_base64()
            }
            for i in range(1, 12)
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/register/team",
            json=registration_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            if "team_id" in data:
                results.add_pass("Team Registration - Registration successful")
                print(f"  Team ID: {data['team_id']}")
                print(f"  Message: {data.get('message', 'N/A')}")
                return data
            else:
                results.add_fail("Team Registration", "Team ID not in response")
        else:
            results.add_fail(
                "Team Registration",
                f"Status code: {response.status_code} - {response.text[:200]}"
            )
    except Exception as e:
        results.add_fail("Team Registration", str(e))
    
    return {}

def test_team_registration_without_group_photo(results: TestResults) -> Dict[str, Any]:
    """Test 4: Team Registration Without Group Photo (Optional Field)"""
    print_section("Test 4: Team Registration Without Group Photo")
    
    registration_data = {
        "churchName": "Church Without Photo",
        "teamName": "Team Without Photo",
        "pastorLetter": create_test_pdf_base64(),
        "paymentReceipt": create_test_image_base64(),
        # groupPhoto intentionally omitted
        "captain": {
            "name": "Captain Bob",
            "phone": "8765432109",
            "email": "bob@test.com",
            "whatsapp": "8765432109"
        },
        "viceCaptain": {
            "name": "Vice Captain Alice",
            "phone": "8765432108",
            "email": "alice@test.com",
            "whatsapp": "8765432108"
        },
        "players": [
            {
                "name": f"Player {i}",
                "role": "Batsman" if i % 2 == 0 else "Bowler",
                "aadharFile": create_test_pdf_base64(),
                "subscriptionFile": create_test_pdf_base64()
            }
            for i in range(1, 12)
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/register",
            json=registration_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 201:
            data = response.json()
            results.add_pass("Registration Without Photo - Optional field works")
            return data
        else:
            results.add_fail(
                "Registration Without Photo",
                f"Status code: {response.status_code}"
            )
    except Exception as e:
        results.add_fail("Registration Without Photo", str(e))
    
    return {}

def test_get_all_teams(results: TestResults):
    """Test 5: Get All Teams (Check Group Photo in Response)"""
    print_section("Test 5: Get All Teams")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/teams",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            teams = response.json()
            if isinstance(teams, list):
                results.add_pass(f"Get All Teams - Retrieved {len(teams)} teams")
                
                # Check for group photo in response
                teams_with_photo = sum(1 for team in teams if team.get("groupPhoto"))
                teams_without_photo = len(teams) - teams_with_photo
                
                print(f"  Teams with group photo: {teams_with_photo}")
                print(f"  Teams without group photo: {teams_without_photo}")
                
                # Show first team structure
                if teams:
                    first_team = teams[0]
                    print(f"\n  {Colors.CYAN}First team structure:{Colors.RESET}")
                    for key in first_team.keys():
                        value = first_team[key]
                        if isinstance(value, str) and len(str(value)) > 50:
                            print(f"    - {key}: <{len(str(value))} characters>")
                        else:
                            print(f"    - {key}: {value}")
                
                # Check if groupPhoto field exists
                if any("groupPhoto" in team for team in teams):
                    results.add_pass("Get All Teams - groupPhoto field present in response")
                else:
                    results.add_fail("Get All Teams - groupPhoto", "groupPhoto field missing in response")
            else:
                results.add_fail("Get All Teams", "Response is not a list")
        else:
            results.add_fail("Get All Teams", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Get All Teams", str(e))

def test_get_team_details(results: TestResults, team_data: Dict[str, Any]):
    """Test 6: Get Team Details (Check Group Photo in Response)"""
    print_section("Test 6: Get Team Details")
    
    if not team_data or "team_id" not in team_data:
        results.add_fail("Get Team Details", "No valid team_id from registration")
        return
    
    team_id = team_data["team_id"]
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/teams/{team_id}",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            results.add_pass("Get Team Details - Retrieved team details")
            
            # Check structure
            if "team" in data and "players" in data:
                print(f"  Team name: {data['team'].get('teamName')}")
                print(f"  Players count: {len(data['players'])}")
                
                # Check for group photo
                if "groupPhoto" in data["team"]:
                    group_photo = data["team"]["groupPhoto"]
                    if group_photo:
                        is_data_uri = isinstance(group_photo, str) and group_photo.startswith("data:")
                        if is_data_uri:
                            results.add_pass("Get Team Details - groupPhoto is properly formatted as data URI")
                            print(f"  Group photo format: data URI (length: {len(group_photo)} chars)")
                        else:
                            results.add_fail("Get Team Details - groupPhoto", "Not a data URI")
                    else:
                        print(f"  Group photo: None (not uploaded)")
                else:
                    results.add_fail("Get Team Details - groupPhoto", "groupPhoto field missing")
                
                # Check other fields
                print(f"\n  {Colors.CYAN}Team object fields:{Colors.RESET}")
                for key in data["team"].keys():
                    value = data["team"][key]
                    if isinstance(value, str) and len(str(value)) > 50:
                        print(f"    - {key}: <{len(str(value))} characters>")
                    else:
                        print(f"    - {key}: {value}")
            else:
                results.add_fail("Get Team Details", "Invalid response structure")
        else:
            results.add_fail("Get Team Details", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Get Team Details", str(e))

def test_get_team_players(results: TestResults, team_data: Dict[str, Any]):
    """Test 7: Get Team Players"""
    print_section("Test 7: Get Team Players")
    
    if not team_data or "team_id" not in team_data:
        results.add_fail("Get Team Players", "No valid team_id from registration")
        return
    
    team_id = team_data["team_id"]
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/teams/{team_id}/players",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            players = response.json()
            if isinstance(players, list):
                results.add_pass(f"Get Team Players - Retrieved {len(players)} players")
                if players:
                    first_player = players[0]
                    print(f"  First player: {first_player.get('name')}")
                    print(f"  Role: {first_player.get('role')}")
            else:
                results.add_fail("Get Team Players", "Response is not a list")
        else:
            results.add_fail("Get Team Players", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Get Team Players", str(e))

def test_invalid_registration(results: TestResults):
    """Test 8: Invalid Registration (Missing Required Fields)"""
    print_section("Test 8: Invalid Registration")
    
    invalid_data = {
        "churchName": "Test Church"
        # Missing teamName and other required fields
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/register",
            json=invalid_data,
            timeout=TIMEOUT
        )
        
        if response.status_code >= 400:
            results.add_pass("Invalid Registration - Properly rejected invalid data")
            print(f"  Status code: {response.status_code}")
            print(f"  Response: {response.json()}")
        else:
            results.add_fail("Invalid Registration", "Should have rejected invalid data")
    except Exception as e:
        results.add_fail("Invalid Registration", str(e))

def test_cors_headers(results: TestResults):
    """Test 9: CORS Headers"""
    print_section("Test 9: CORS Headers")
    try:
        response = requests.options(
            f"{BASE_URL}/api/v1/admin/teams",
            timeout=TIMEOUT
        )
        
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
            'access-control-allow-headers': response.headers.get('access-control-allow-headers')
        }
        
        if any(cors_headers.values()):
            results.add_pass("CORS Headers - CORS is configured")
            for key, value in cors_headers.items():
                if value:
                    print(f"  {key}: {value}")
        else:
            print("  CORS headers not found in OPTIONS response (may be configured in middleware)")
    except Exception as e:
        results.add_fail("CORS Headers", str(e))

def test_error_handling(results: TestResults):
    """Test 10: Error Handling (Non-existent Team)"""
    print_section("Test 10: Error Handling")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/teams/INVALID-TEAM-ID",
            timeout=TIMEOUT
        )
        
        if response.status_code == 404:
            results.add_pass("Error Handling - 404 for non-existent team")
            print(f"  Response: {response.json()}")
        else:
            results.add_fail(
                "Error Handling",
                f"Expected 404, got {response.status_code}"
            )
    except Exception as e:
        results.add_fail("Error Handling", str(e))

def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}ICCT26 Backend API Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}Testing: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    
    results = TestResults()
    
    # Run tests
    test_health_check(results)
    test_api_info(results)
    
    team_data = test_team_registration(results)
    time.sleep(1)  # Brief delay between requests
    
    test_team_registration_without_group_photo(results)
    time.sleep(1)
    
    test_get_all_teams(results)
    test_get_team_details(results, team_data)
    test_get_team_players(results, team_data)
    
    test_invalid_registration(results)
    test_cors_headers(results)
    test_error_handling(results)
    
    # Print summary
    success = results.print_summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)
