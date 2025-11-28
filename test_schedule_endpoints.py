"""
Test script to verify schedule endpoints work after migration
"""
import requests
import json

print("=" * 60)
print("TESTING SCHEDULE ENDPOINTS - RUNS & WICKETS")
print("=" * 60)

# Test the health check
try:
    response = requests.get('http://127.0.0.1:8000/api/health')
    print(f'\n✅ Health Check: {response.status_code}')
except Exception as e:
    print(f'\n⚠️  Health Check: {e}')

# Test getting all matches
try:
    response = requests.get('http://127.0.0.1:8000/api/schedule/matches')
    print(f'\n✅ Get All Matches: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {len(data.get("data", []))} matches')
        if data.get("data"):
            match = data["data"][0]
            print(f'\n   Sample Match Response:')
            print(f'   - ID: {match.get("id")}')
            print(f'   - Team 1: {match.get("team1")} vs Team 2: {match.get("team2")}')
            print(f'   - Status: {match.get("status")}')
            print(f'\n   Runs & Wickets Fields:')
            print(f'   - team1_first_innings_runs: {match.get("team1_first_innings_runs")}')
            print(f'   - team1_first_innings_wickets: {match.get("team1_first_innings_wickets")}')
            print(f'   - team2_first_innings_runs: {match.get("team2_first_innings_runs")}')
            print(f'   - team2_first_innings_wickets: {match.get("team2_first_innings_wickets")}')
            print(f'\n   Result:')
            if match.get("result"):
                print(json.dumps(match["result"], indent=4))
            else:
                print("   No result recorded yet (match not done)")
except Exception as e:
    print(f'\n❌ Get Matches Failed: {e}')

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)

