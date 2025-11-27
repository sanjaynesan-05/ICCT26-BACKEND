import requests
import json

base_url = 'http://127.0.0.1:8000'

# First, create a match
import random
match_data = {
    'round': 'Round 1',
    'round_number': 1,
    'match_number': random.randint(100, 9999),
    'team1': 'SHARKS',
    'team2': 'Thadaladi'
}

print('Creating match...')
response = requests.post(base_url + '/api/schedule/matches', json=match_data)
print('Status:', response.status_code)
print('Response:', json.dumps(response.json(), indent=2))

if response.status_code in [200, 201]:
    match_id = response.json()['data']['id']
    print('Match ID:', match_id)
else:
    exit(1)

# Update status to live
print('\nUpdating status to live...')
response = requests.put(base_url + '/api/schedule/matches/' + str(match_id) + '/status', json={'status': 'live'})
print('Status:', response.status_code)

# Now test setting result with camelCase
print('\nSetting result with camelCase fields...')
result_data = {
    'winner': 'Thadaladi',
    'margin': 10,
    'marginType': 'wickets',
    'wonByBattingFirst': False
}

response = requests.post(base_url + '/api/schedule/matches/' + str(match_id) + '/result', json=result_data)
print('Status:', response.status_code)
print('Response:', json.dumps(response.json(), indent=2))

if response.status_code == 200:
    print('\n✅ SUCCESS! Field name conversion is working!')
else:
    print('\n❌ FAILED')
