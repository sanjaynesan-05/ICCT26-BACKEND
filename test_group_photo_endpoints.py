#!/usr/bin/env python3
"""
Test script to verify group_photo field is being fetched and sent by all endpoints
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

def print_result(test_name: str, response: Dict[str, Any], success: bool):
    """Print test results in a formatted way"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    print(f"Status Code: {response.get('status_code', 'N/A')}")
    if 'data' in response:
        print(f"Response:\n{json.dumps(response['data'], indent=2)}")
    if 'error' in response:
        print(f"Error: {response['error']}")

def test_health_check():
    """Test 1: Health Check"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print_result("Health Check", {
            'status_code': r.status_code,
            'data': r.json()
        }, r.status_code == 200)
    except Exception as e:
        print_result("Health Check", {'error': str(e)}, False)

def test_get_all_teams():
    """Test 2: GET /api/teams - Should return all teams with group_photo"""
    try:
        r = requests.get(f"{BASE_URL}/api/teams", timeout=5)
        data = r.json()
        
        has_group_photo = False
        if r.status_code == 200 and 'teams' in data:
            teams = data['teams']
            if teams:
                first_team = teams[0]
                has_group_photo = 'group_photo' in first_team
                print(f"\n✅ GET /api/teams")
                print(f"Status Code: {r.status_code}")
                print(f"Total Teams: {data.get('total_teams', 0)}")
                print(f"First Team Structure:")
                print(json.dumps(first_team, indent=2))
                print(f"\n{'✅' if has_group_photo else '❌'} group_photo field present: {has_group_photo}")
                if has_group_photo and first_team.get('group_photo'):
                    print(f"   Group Photo URL: {first_team['group_photo'][:80]}...")
            else:
                print(f"\n⚠️  GET /api/teams - No teams in database")
        else:
            print(f"\n❌ GET /api/teams - Error: {data}")
    except Exception as e:
        print(f"\n❌ GET /api/teams - Exception: {str(e)}")

def test_get_team_by_id():
    """Test 3: GET /api/teams/{team_id} - Should return single team with group_photo"""
    # First get a team_id
    try:
        r_list = requests.get(f"{BASE_URL}/api/teams", timeout=5)
        data_list = r_list.json()
        
        if r_list.status_code == 200 and 'teams' in data_list and data_list['teams']:
            team_id = data_list['teams'][0]['team_id']
            
            r = requests.get(f"{BASE_URL}/api/teams/{team_id}", timeout=5)
            data = r.json()
            
            if r.status_code == 200 and 'team' in data:
                team = data['team']
                has_group_photo = 'group_photo' in team
                print(f"\n✅ GET /api/teams/{team_id}")
                print(f"Status Code: {r.status_code}")
                print(f"Team Structure:")
                print(json.dumps({k: v if k != 'players' else f"[{len(v)} players]" for k, v in team.items()}, indent=2))
                print(f"\n{'✅' if has_group_photo else '❌'} group_photo field present: {has_group_photo}")
                if has_group_photo and team.get('group_photo'):
                    print(f"   Group Photo URL: {team['group_photo'][:80]}...")
            else:
                print(f"\n❌ GET /api/teams/{team_id} - Error: {data}")
        else:
            print(f"\n⚠️  No teams available to test GET /api/teams/{'{team_id}'}")
    except Exception as e:
        print(f"\n❌ GET /api/teams/{{team_id}} - Exception: {str(e)}")

def test_admin_get_teams():
    """Test 4: GET /admin/teams - Should return all teams with group_photo"""
    try:
        r = requests.get(f"{BASE_URL}/admin/teams", timeout=5)
        data = r.json()
        
        if r.status_code == 200 and 'teams' in data:
            teams = data['teams']
            if teams:
                first_team = teams[0]
                has_group_photo = 'group_photo' in first_team
                print(f"\n✅ GET /admin/teams")
                print(f"Status Code: {r.status_code}")
                print(f"Total Teams: {len(teams)}")
                print(f"First Team Structure:")
                print(json.dumps(first_team, indent=2))
                print(f"\n{'✅' if has_group_photo else '❌'} group_photo field present: {has_group_photo}")
                if has_group_photo and first_team.get('group_photo'):
                    print(f"   Group Photo URL: {first_team['group_photo'][:80]}...")
            else:
                print(f"\n⚠️  GET /admin/teams - No teams in database")
        else:
            print(f"\n❌ GET /admin/teams - Error: {data}")
    except Exception as e:
        print(f"\n❌ GET /admin/teams - Exception: {str(e)}")

def test_database_check():
    """Test 5: Check if group_photo column exists in database"""
    try:
        from database import sync_engine
        from sqlalchemy import text
        
        with sync_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='teams' AND column_name='group_photo'
            """)).fetchone()
            
            if result:
                print(f"\n✅ Database Check")
                print(f"group_photo column exists in teams table")
            else:
                print(f"\n❌ Database Check")
                print(f"group_photo column NOT found in teams table")
    except Exception as e:
        print(f"\n❌ Database Check - Exception: {str(e)}")

def main():
    print("=" * 80)
    print("ICCT26 Backend - Group Photo Field Test Suite")
    print("=" * 80)
    
    # Run all tests
    test_health_check()
    test_get_all_teams()
    test_get_team_by_id()
    test_admin_get_teams()
    test_database_check()
    
    print("\n" + "=" * 80)
    print("Test Suite Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
