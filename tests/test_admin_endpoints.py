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

import pytest
import pytest_asyncio
import httpx
import sys
import os
import json
from datetime import datetime
from starlette.testclient import TestClient
from main import app

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

    @pytest_asyncio.fixture
    async def client(self):
        """Create test client"""
        from starlette.testclient import TestClient
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
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
        assert "data" in data, "Missing 'data' field"
        teams = data.get("data", [])
        assert isinstance(teams, list), "'data' should be a list"
        
        print(f"✅ Retrieved {len(teams)} teams")
        print(f"   Response structure valid")
        return True

    @pytest.mark.asyncio
    async def test_get_all_teams_response_format(self, client):
        """Test: GET /admin/teams - Response format validation"""
        print("\n[TEST] GET /admin/teams - Response format")
        
        response = await client.get(f"{ADMIN_BASE}/teams")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        teams = data.get("data", [])
        # If teams exist, validate team structure
        if teams:
            team = teams[0]
            # API returns camelCase field names
            required_fields = ["teamId", "teamName", "churchName"]
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
        teams = teams_response.json().get("data", [])
        
        if not teams:
            print("⚠️  No teams available for testing")
            return True
        
        # Test with first team (use camelCase field name)
        team_id = teams[0].get("teamId") or teams[0].get("team_id")
        response = await client.get(f"{ADMIN_BASE}/teams/{team_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        team = data.get("data", data)  # Handle both wrapped and direct response
        
        # Check for camelCase or snake_case field names
        assert "teamId" in team or "team_id" in team, "Missing team_id"
        assert "teamName" in team or "team_name" in team, "Missing team_name"
        assert "players" in team, "Missing players array"
        
        print(f"✅ Retrieved team details for {team_id}")
        team_name = team.get("teamName") or team.get("team_name")
        print(f"   Team: {team_name}")
        print(f"   Players: {len(team.get('players', []))}")
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
        teams = teams_response.json().get("data", [])
        
        if not teams:
            print("⚠️  No teams available for testing")
            return True
        
        team_id = teams[0].get("teamId") or teams[0].get("team_id")
        response = await client.get(f"{ADMIN_BASE}/teams/{team_id}")
        data = response.json()
        team = data.get("data", data)  # Handle both wrapped and direct response
        
        # Validate structure (camelCase or snake_case)
        required_fields = [
            ("teamId", "team_id"), 
            ("teamName", "team_name"), 
            ("churchName", "church_name"), 
            ("captain", "captain"), 
            ("viceCaptain", "vice_captain"), 
            ("players", "players")
        ]
        for camel_case, snake_case in required_fields:
            assert camel_case in team or snake_case in team, f"Missing required field: {camel_case}/{snake_case}"
        
        # Validate captain structure
        captain = team.get("captain")
        if captain:
            captain_fields = ["name", "email", "phone"]
            for field in captain_fields:
                assert field in captain, f"Captain missing {field}"
        
        print(f"✅ Team structure valid")
        print(f"   Fields: {list(team.keys())}")
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
        teams = teams_response.json().get("data", [])
        
        if not teams:
            print("⚠️  No teams available for testing")
            return True
        
        # Get team details to find players
        team_id = teams[0].get("teamId") or teams[0].get("team_id")
        team_response = await client.get(f"{ADMIN_BASE}/teams/{team_id}")
        team_data = team_response.json()
        team = team_data.get("data", team_data)  # Handle both wrapped and direct
        players = team.get("players", [])
        
        if not players:
            print("⚠️  No players available for testing")
            return True
        
        # Test with first player (use either camelCase or snake_case)
        player_id = players[0].get("playerId") or players[0].get("player_id")
        response = await client.get(f"{ADMIN_BASE}/players/{player_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        player = data.get("data", data)  # Handle both wrapped and direct
        
        assert "playerId" in player or "player_id" in player, "Missing player_id"
        assert "name" in player, "Missing name"
        assert "teamId" in player or "team_id" in player, "Missing team_id"
        
        print(f"✅ Retrieved player details for ID {player_id}")
        print(f"   Player: {player.get('name')}")
        team_id_val = player.get("teamId") or player.get("team_id")
        print(f"   Team: {team_id_val}")
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
        teams = teams_response.json().get("data", [])
        
        if not teams:
            print("⚠️  No teams available")
            return True
        
        team_id = teams[0].get("teamId") or teams[0].get("team_id")
        team_response = await client.get(f"{ADMIN_BASE}/teams/{team_id}")
        team_data = team_response.json()
        team = team_data.get("data", team_data)
        players = team.get("players", [])
        
        if not players:
            print("⚠️  No players available")
            return True
        
        player_id = players[0].get("playerId") or players[0].get("player_id")
        response = await client.get(f"{ADMIN_BASE}/players/{player_id}")
        data = response.json()
        player = data.get("data", data)
        
        # Validate structure (handle both camelCase and snake_case)
        required_fields = [
            ("playerId", "player_id"), 
            ("name", "name"), 
            ("age", "age"), 
            ("phone", "phone"), 
            ("role", "role"), 
            ("teamId", "team_id")
        ]
        for camel_case, snake_case in required_fields:
            assert camel_case in player or snake_case in player, f"Missing required field: {camel_case}/{snake_case}"
        
        print(f"✅ Player structure valid")
        print(f"   Fields: {list(player.keys())}")
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
        
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        
        print("✅ Health check passed")
        return True

    def test_admin_teams_sync(self):
        """Test: GET /admin/teams (sync)"""
        print("\n[SYNC] GET /admin/teams")
        
        client = TestClient(app)
        response = client.get(f"/admin/teams")
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get("data", [])
            print(f"✅ Retrieved {len(teams)} teams")
            return True
        else:
            print(f"⚠️  Got status {response.status_code}")
            return response.status_code == 200

    def test_admin_teams_response_sync(self):
        """Test: Validate teams response format"""
        print("\n[SYNC] Teams response format")
        
        client = TestClient(app)
        response = client.get(f"/admin/teams")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        teams = data.get("data", [])
        assert isinstance(teams, list)
        
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
