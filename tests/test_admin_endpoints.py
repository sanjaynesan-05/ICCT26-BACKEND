#!/usr/bin/env python3
"""
Admin API Endpoints Test Suite
================================
Comprehensive testing for all admin side API endpoints

Tests:
  1. GET /admin/teams - Get all teams
  2. GET /admin/teams/{team_id} - Get specific team details
  3. GET /admin/players/{player_id} - Get player details
  4. Error handling for invalid inputs
  5. Database connectivity
  6. Response format validation
  7. Status codes verification

Run: python tests/test_admin_endpoints.py
"""

import httpx
import sys
import os
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_BASE = f"{BASE_URL}/admin"

# Test results tracker
test_results = {
    "passed": [],
    "failed": [],
    "skipped": [],
    "errors": []
}


class TestAdminEndpoints:
    """Test suite for all admin API endpoints"""

    @pytest.fixture
    async def client(self):
        """Create test client"""
        async with httpx.AsyncClient(app=app, base_url=BASE_URL) as client:
            yield client

    # ========================================================
    # ADMIN TEAMS ENDPOINTS
    # ========================================================

    @pytest.mark.asyncio
    async def test_get_all_teams_success(self, client):
        """Test: GET /admin/teams - Success"""
        print("\n[TEST] GET /admin/teams - Success")
        
        response = await client.get(f"{ADMIN_BASE}/teams")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert "success" in data, "Missing 'success' field"
        assert "teams" in data, "Missing 'teams' field"
        assert isinstance(data["teams"], list), "'teams' should be a list"
        
        print(f"✅ Retrieved {len(data['teams'])} teams")
        print(f"   Response: {data}")
        return True

    @pytest.mark.asyncio
    async def test_get_all_teams_response_format(self, client):
        """Test: GET /admin/teams - Response format validation"""
        print("\n[TEST] GET /admin/teams - Response format")
        
        response = await client.get(f"{ADMIN_BASE}/teams")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        # If teams exist, validate team structure
        if data["teams"]:
            team = data["teams"][0]
            required_fields = ["team_id", "team_name", "church_name"]
            for field in required_fields:
                assert field in team, f"Missing required field: {field}"
            
            print(f"✅ Team structure valid")
            print(f"   Fields: {list(team.keys())}")
        
        return True

    @pytest.mark.asyncio
    async def test_get_team_details_valid_id(self, client):
        """Test: GET /admin/teams/{team_id} - Valid ID"""
        print("\n[TEST] GET /admin/teams/{team_id} - Valid ID")
        
        # First get all teams to find a valid ID
        teams_response = await client.get(f"{ADMIN_BASE}/teams")
        teams = teams_response.json()["teams"]
        
        if not teams:
            print("⚠️  No teams available for testing")
            return True
        
        # Test with first team
        team_id = teams[0]["team_id"]
        response = await client.get(f"{ADMIN_BASE}/teams/{team_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "team_id" in data, "Missing team_id"
        assert "team_name" in data, "Missing team_name"
        assert "players" in data, "Missing players array"
        
        print(f"✅ Retrieved team details for {team_id}")
        print(f"   Team: {data['team_name']}")
        print(f"   Players: {len(data.get('players', []))}")
        return True

    @pytest.mark.asyncio
    async def test_get_team_details_invalid_id(self, client):
        """Test: GET /admin/teams/{team_id} - Invalid ID (404)"""
        print("\n[TEST] GET /admin/teams/{team_id} - Invalid ID")
        
        invalid_team_id = "ICCT26-INVALID-9999"
        response = await client.get(f"{ADMIN_BASE}/teams/{invalid_team_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Missing error detail"
        
        print(f"✅ Correctly returned 404 for invalid team")
        print(f"   Error: {data['detail']}")
        return True

    @pytest.mark.asyncio
    async def test_get_team_details_structure(self, client):
        """Test: GET /admin/teams/{team_id} - Response structure"""
        print("\n[TEST] GET /admin/teams/{team_id} - Structure validation")
        
        teams_response = await client.get(f"{ADMIN_BASE}/teams")
        teams = teams_response.json()["teams"]
        
        if not teams:
            print("⚠️  No teams available for testing")
            return True
        
        team_id = teams[0]["team_id"]
        response = await client.get(f"{ADMIN_BASE}/teams/{team_id}")
        data = response.json()
        
        # Validate structure
        required_fields = [
            "team_id", "team_name", "church_name", 
            "captain", "vice_captain", "players"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate captain structure
        if data["captain"]:
            captain_fields = ["name", "email", "phone"]
            for field in captain_fields:
                assert field in data["captain"], f"Captain missing {field}"
        
        print(f"✅ Team structure valid")
        print(f"   Fields: {list(data.keys())}")
        return True

    # ========================================================
    # ADMIN PLAYERS ENDPOINTS
    # ========================================================

    @pytest.mark.asyncio
    async def test_get_player_details_valid_id(self, client):
        """Test: GET /admin/players/{player_id} - Valid ID"""
        print("\n[TEST] GET /admin/players/{player_id} - Valid ID")
        
        # First get a team with players
        teams_response = await client.get(f"{ADMIN_BASE}/teams")
        teams = teams_response.json()["teams"]
        
        if not teams:
            print("⚠️  No teams available for testing")
            return True
        
        # Get team details to find players
        team_id = teams[0]["team_id"]
        team_response = await client.get(f"{ADMIN_BASE}/teams/{team_id}")
        team_data = team_response.json()
        players = team_data.get("players", [])
        
        if not players:
            print("⚠️  No players available for testing")
            return True
        
        # Test with first player
        player_id = players[0]["player_id"]
        response = await client.get(f"{ADMIN_BASE}/players/{player_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "player_id" in data, "Missing player_id"
        assert "name" in data, "Missing name"
        assert "team_id" in data, "Missing team_id"
        
        print(f"✅ Retrieved player details for ID {player_id}")
        print(f"   Player: {data.get('name')}")
        print(f"   Team: {data.get('team_id')}")
        return True

    @pytest.mark.asyncio
    async def test_get_player_details_invalid_id(self, client):
        """Test: GET /admin/players/{player_id} - Invalid ID (404)"""
        print("\n[TEST] GET /admin/players/{player_id} - Invalid ID")
        
        invalid_player_id = 99999
        response = await client.get(f"{ADMIN_BASE}/players/{invalid_player_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Missing error detail"
        
        print(f"✅ Correctly returned 404 for invalid player")
        print(f"   Error: {data['detail']}")
        return True

    @pytest.mark.asyncio
    async def test_get_player_details_structure(self, client):
        """Test: GET /admin/players/{player_id} - Response structure"""
        print("\n[TEST] GET /admin/players/{player_id} - Structure validation")
        
        # Get a player
        teams_response = await client.get(f"{ADMIN_BASE}/teams")
        teams = teams_response.json()["teams"]
        
        if not teams:
            print("⚠️  No teams available")
            return True
        
        team_response = await client.get(f"{ADMIN_BASE}/teams/{teams[0]['team_id']}")
        team_data = team_response.json()
        players = team_data.get("players", [])
        
        if not players:
            print("⚠️  No players available")
            return True
        
        player_id = players[0]["player_id"]
        response = await client.get(f"{ADMIN_BASE}/players/{player_id}")
        data = response.json()
        
        # Validate structure
        required_fields = ["player_id", "name", "age", "phone", "role", "team_id"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"✅ Player structure valid")
        print(f"   Fields: {list(data.keys())}")
        return True

    # ========================================================
    # ERROR HANDLING TESTS
    # ========================================================

    @pytest.mark.asyncio
    async def test_error_invalid_player_id_type(self, client):
        """Test: Invalid player_id type"""
        print("\n[TEST] Invalid player_id type")
        
        # Try non-integer player_id
        response = await client.get(f"{ADMIN_BASE}/players/invalid")
        
        # Should either be 422 (validation error) or 404
        assert response.status_code in [422, 404], f"Expected 422 or 404, got {response.status_code}"
        
        print(f"✅ Correctly handled invalid player_id type")
        print(f"   Status: {response.status_code}")
        return True

    @pytest.mark.asyncio
    async def test_empty_team_id(self, client):
        """Test: Empty team_id"""
        print("\n[TEST] Empty team_id")
        
        response = await client.get(f"{ADMIN_BASE}/teams/")
        
        # Should be 404 or method not allowed
        assert response.status_code != 200, f"Should not return 200"
        
        print(f"✅ Correctly handled empty team_id")
        print(f"   Status: {response.status_code}")
        return True

    # ========================================================
    # DATABASE TESTS
    # ========================================================

    @pytest.mark.asyncio
    async def test_database_connectivity(self, client):
        """Test: Database connectivity"""
        print("\n[TEST] Database connectivity")
        
        # Try to get teams - this will fail if DB is down
        response = await client.get(f"{ADMIN_BASE}/teams")
        
        # Should not be 500 (server error)
        assert response.status_code != 500, "Database connectivity failed"
        
        print(f"✅ Database is connected")
        print(f"   Response status: {response.status_code}")
        return True


class TestAdminEndpointsSync:
    """Synchronous test suite for admin endpoints"""

    def test_health_check(self):
        """Test: Health endpoint before admin tests"""
        print("\n[SANITY] Health check")
        
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            
            print("✅ Health check passed")
            return True

    def test_admin_teams_sync(self):
        """Test: GET /admin/teams (sync)"""
        print("\n[SYNC] GET /admin/teams")
        
        with httpx.Client() as client:
            response = client.get(f"{ADMIN_BASE}/teams")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Retrieved {len(data['teams'])} teams")
                return True
            else:
                print(f"⚠️  Got status {response.status_code}")
                return response.status_code == 200

    def test_admin_teams_response_sync(self):
        """Test: Validate teams response format"""
        print("\n[SYNC] Teams response format")
        
        with httpx.Client() as client:
            response = client.get(f"{ADMIN_BASE}/teams")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert isinstance(data["teams"], list)
            
            print("✅ Response format valid")
            return True


def run_all_tests():
    """Run all tests without pytest"""
    print("=" * 80)
    print("ADMIN API ENDPOINTS - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    tests_passed = 0
    tests_failed = 0
    
    # Test with sync client
    print("\n[PHASE 1] Synchronous Tests")
    print("-" * 80)
    
    try:
        sync_tests = TestAdminEndpointsSync()
        
        if sync_tests.test_health_check():
            tests_passed += 1
        else:
            tests_failed += 1
        
        if sync_tests.test_admin_teams_sync():
            tests_passed += 1
        else:
            tests_failed += 1
        
        if sync_tests.test_admin_teams_response_sync():
            tests_passed += 1
        else:
            tests_failed += 1
            
    except Exception as e:
        print(f"❌ Sync test error: {e}")
        tests_failed += 3

    print("\n" + "=" * 80)
    print(f"TEST RESULTS")
    print("=" * 80)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"📊 Total:  {tests_passed + tests_failed}")
    print(f"📈 Pass Rate: {(tests_passed / (tests_passed + tests_failed) * 100):.1f}%")
    print("=" * 80)


if __name__ == "__main__":
    # Run synchronous tests
    run_all_tests()
    
    print("\n" + "=" * 80)
    print("For async tests, run: pytest tests/test_admin_endpoints.py -v")
    print("=" * 80)
