import requests
import json

base_url = 'http://127.0.0.1:8000'

match_data = {
    'round': 'Round 1',
    'round_number': 1,
    'match_number': 5555,
    'team1': 'SHARKS',
    'team2': 'Thadaladi'
}

print("Creating match...")
response = requests.post(base_url + '/api/schedule/matches', json=match_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
