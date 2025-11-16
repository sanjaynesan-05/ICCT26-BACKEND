#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for ICCT26 Backend (Production)
Tests all endpoints including the new group_photo feature
Using the actual Render deployment endpoints

Run with: python test_render_api.py
"""

import requests
import json
import base64
import time
from typing import Dict, Any
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
    png_bytes = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
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
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            results.add_pass("Health Check - API is running")
            print(f"  {response.json()}")
        else:
            results.add_fail("Health Check", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Health Check", str(e))

def test_get_home(results: TestResults):
    """Test 2: Get Home"""
    print_section("Test 2: Get Home Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            results.add_pass("Home Endpoint - Accessible")
        else:
            results.add_fail("Home Endpoint", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Home Endpoint", str(e))

def test_register_team_with_photo(results: TestResults) -> Dict[str, Any]:
    """Test 3: Register Team WITH Group Photo"""
    print_section("Test 3: Register Team WITH Group Photo")
    
    payload = {
        "churchName": "Photo Test Church",
        "teamName": f"Team With Photo {int(time.time())}",
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
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            results.add_pass("Register Team WITH Photo - Success")
            print(f"  Team ID: {data.get('team_id', 'N/A')}")
            print(f"  Message: {data.get('message', 'N/A')}")
            return data
        else:
            results.add_fail(
                "Register Team WITH Photo",
                f"Status: {response.status_code} - {response.text[:150]}"
            )
    except Exception as e:
        results.add_fail("Register Team WITH Photo", str(e))
    
    return {}

def test_register_team_without_photo(results: TestResults) -> Dict[str, Any]:
    """Test 4: Register Team WITHOUT Group Photo"""
    print_section("Test 4: Register Team WITHOUT Group Photo (Optional)")
    
    payload = {
        "churchName": "No Photo Church",
        "teamName": f"Team No Photo {int(time.time())}",
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
            f"{BASE_URL}/api/register/team",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            results.add_pass("Register Team WITHOUT Photo - Success (Optional Field Works)")
            return data
        else:
            results.add_fail(
                "Register Team WITHOUT Photo",
                f"Status: {response.status_code}"
            )
    except Exception as e:
        results.add_fail("Register Team WITHOUT Photo", str(e))
    
    return {}

def test_get_all_teams(results: TestResults):
    """Test 5: Get All Teams"""
    print_section("Test 5: Get All Teams")
    try:
        response = requests.get(f"{BASE_URL}/admin/teams", timeout=TIMEOUT)
        
        if response.status_code == 200:
            teams = response.json()
            if isinstance(teams, list):
                results.add_pass(f"Get All Teams - Retrieved {len(teams)} teams")
                
                # Check for group photo field
                teams_with_photo = sum(1 for t in teams if t.get("groupPhoto"))
                print(f"  Teams with group photo: {teams_with_photo}")
                print(f"  Teams without group photo: {len(teams) - teams_with_photo}")
                
                # Check if groupPhoto field exists in schema
                if teams and "groupPhoto" in teams[0]:
                    results.add_pass("Get All Teams - groupPhoto field present")
                elif teams:
                    results.add_fail("Get All Teams - groupPhoto", "Field missing in response")
                
                # Show first team details
                if teams:
                    t = teams[0]
                    print(f"\n  {Colors.CYAN}First Team:{Colors.RESET}")
                    for key in ['teamId', 'teamName', 'churchName', 'playerCount', 'groupPhoto']:
                        if key in t:
                            val = t[key]
                            if isinstance(val, str) and len(val) > 60:
                                print(f"    {key}: <{len(val)} chars>")
                            else:
                                print(f"    {key}: {val}")
            else:
                results.add_fail("Get All Teams", "Response not a list")
        else:
            results.add_fail("Get All Teams", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Get All Teams", str(e))

def test_get_team_details(results: TestResults, team_data: Dict[str, Any]):
    """Test 6: Get Team Details"""
    print_section("Test 6: Get Team Details")
    
    if not team_data or "team_id" not in team_data:
        results.add_fail("Get Team Details", "No team_id from registration")
        return
    
    team_id = team_data["team_id"]
    
    try:
        response = requests.get(f"{BASE_URL}/admin/teams/{team_id}", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            results.add_pass("Get Team Details - Retrieved successfully")
            
            if "team" in data and "players" in data:
                team = data["team"]
                players = data["players"]
                print(f"  Team: {team.get('teamName')}")
                print(f"  Church: {team.get('churchName')}")
                print(f"  Players: {len(players)}")
                
                # Check groupPhoto
                if "groupPhoto" in team:
                    results.add_pass("Get Team Details - groupPhoto field present")
                    if team["groupPhoto"]:
                        is_data_uri = team["groupPhoto"].startswith("data:")
                        print(f"  Group photo: Present ({len(team['groupPhoto'])} chars, is_data_uri: {is_data_uri})")
                    else:
                        print(f"  Group photo: None (not uploaded)")
                else:
                    results.add_fail("Get Team Details - groupPhoto", "Field missing")
                
                # Show all team fields
                print(f"\n  {Colors.CYAN}Team Fields:{Colors.RESET}")
                for key in team.keys():
                    val = team[key]
                    if isinstance(val, str) and len(val) > 60:
                        print(f"    {key}: <{len(val)} chars>")
                    else:
                        print(f"    {key}: {val}")
        else:
            results.add_fail("Get Team Details", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Get Team Details", str(e))

def test_get_teams_list(results: TestResults):
    """Test 7: Get Teams List (Alternative Endpoint)"""
    print_section("Test 7: Get Teams List (/api/teams)")
    try:
        response = requests.get(f"{BASE_URL}/api/teams", timeout=TIMEOUT)
        
        if response.status_code == 200:
            teams = response.json()
            if isinstance(teams, list):
                results.add_pass(f"Get Teams List - Retrieved {len(teams)} teams")
            else:
                results.add_fail("Get Teams List", "Not a list")
        else:
            results.add_fail("Get Teams List", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Get Teams List", str(e))

def test_status_endpoint(results: TestResults):
    """Test 8: Status Endpoint"""
    print_section("Test 8: Status Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=TIMEOUT)
        
        if response.status_code == 200:
            results.add_pass("Status Endpoint - Accessible")
            print(f"  {response.json()}")
        else:
            results.add_fail("Status Endpoint", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Status Endpoint", str(e))

def test_queue_status(results: TestResults):
    """Test 9: Queue Status"""
    print_section("Test 9: Queue Status")
    try:
        response = requests.get(f"{BASE_URL}/queue/status", timeout=TIMEOUT)
        
        if response.status_code == 200:
            results.add_pass("Queue Status - Accessible")
            print(f"  {response.json()}")
        else:
            results.add_fail("Queue Status", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Queue Status", str(e))

def test_invalid_team(results: TestResults):
    """Test 10: Error Handling (Invalid Team)"""
    print_section("Test 10: Error Handling - Invalid Team")
    try:
        response = requests.get(
            f"{BASE_URL}/admin/teams/NONEXISTENT-TEAM-{int(time.time())}",
            timeout=TIMEOUT
        )
        
        if response.status_code == 404:
            results.add_pass("Error Handling - Correct 404 response")
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
    print(f"{Colors.BOLD}{Colors.CYAN}Production URL: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    
    results = TestResults()
    
    # Run tests
    test_health_check(results)
    test_get_home(results)
    
    team_with_photo = test_register_team_with_photo(results)
    time.sleep(1)
    
    team_without_photo = test_register_team_without_photo(results)
    time.sleep(1)
    
    test_get_all_teams(results)
    test_get_team_details(results, team_with_photo)
    test_get_teams_list(results)
    test_status_endpoint(results)
    test_queue_status(results)
    test_invalid_team(results)
    
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
        print(f"{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)
