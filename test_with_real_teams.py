import requests
import json

base_url = 'http://127.0.0.1:8000'

# Test 1: Check if teams exist
print("1. Checking teams...")
response = requests.get(base_url + '/api/teams')
print(f"Teams Status: {response.status_code}")
teams_list = response.json()['teams'] if 'teams' in response.json() else []
team_names = [t['team_name'] for t in teams_list[:5]]
print(f"Available teams: {team_names}\n")

# Test 2: Create match
if team_names and len(team_names) >= 2:
    match_data = {
        'round': 'Test Round',
        'round_number': 99,
        'match_number': 9999,
        'team1': team_names[0],
        'team2': team_names[1]
    }
    print(f"2. Creating match with teams: {match_data['team1']} vs {match_data['team2']}")
    response = requests.post(base_url + '/api/schedule/matches', json=match_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
else:
    print("Not enough teams to create a match")
