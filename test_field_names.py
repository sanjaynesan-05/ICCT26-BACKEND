import requests
import json

base_url = 'http://127.0.0.1:8000'

# First, create a match
match_data = {
    'round': 'Round 1',
    'round_number': 1,
    'match_number': 2,
    'team1': 'SHARKS',
    'team2': 'Thadaladi'
}

response = requests.post(base_url + '/api/schedule/matches', json=match_data)
match_id = response.json()['data']['id']
print('Created match ID: ' + str(match_id))

# Update status to live
requests.put(base_url + '/api/schedule/matches/' + str(match_id) + '/status', json={'status': 'live'})
print('Match status updated to live')

# Now test setting result with camelCase
result_data = {
    'winner': 'Thadaladi',
    'margin': 10,
    'marginType': 'wickets',
    'wonByBattingFirst': False
}

response = requests.post(base_url + '/api/schedule/matches/' + str(match_id) + '/result', json=result_data)
print('Result API response status: ' + str(response.status_code))

if response.status_code == 200:
    result = response.json()['data']['result']
    print('SUCCESS! Result saved:')
    print('  Winner: ' + result.get('winner'))
    print('  Margin: ' + str(result.get('margin')) + ' ' + result.get('margin_type'))
    print('  Won by batting first: ' + str(result.get('won_by_batting_first')))
else:
    print('Error: ' + str(response.status_code))
    print('Response: ' + response.text[:500])
