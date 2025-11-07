"""
Test the ICCT26 Admin Endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_status():
    """Test status endpoint"""
    print("\n" + "="*60)
    print("🔍 Testing /status endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_admin_teams():
    """Test admin teams endpoint"""
    print("\n" + "="*60)
    print("🔍 Testing /admin/teams endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/admin/teams")
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_admin_team_detail(team_id):
    """Test admin team detail endpoint"""
    print("\n" + "="*60)
    print(f"🔍 Testing /admin/teams/{team_id} endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/admin/teams/{team_id}")
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_admin_player_detail(player_id):
    """Test admin player detail endpoint"""
    print("\n" + "="*60)
    print(f"🔍 Testing /admin/players/{player_id} endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/admin/players/{player_id}")
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 ICCT26 ADMIN ENDPOINTS TEST")
    print("="*60)
    
    # Test status
    test_status()
    
    # Test admin teams
    teams_data = test_admin_teams()
    
    # If we have teams, test team detail and player detail
    if teams_data and teams_data.get("teams"):
        first_team = teams_data["teams"][0]
        team_id = first_team["teamId"]
        
        test_admin_team_detail(team_id)
        
        # Try to test a player (player ID 1 if exists)
        test_admin_player_detail(1)
    
    print("\n" + "="*60)
    print("✅ Test Complete!")
    print("="*60)
