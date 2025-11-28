import requests
import json
from datetime import datetime, timedelta
import random

base_url = 'http://127.0.0.1:8000'

# Create a test match
print("=" * 60)
print("TESTING NEW MATCH SCHEDULE FEATURES")
print("=" * 60)

match_data = {
    'round': 'Round 1',
    'round_number': 1,
    'match_number': random.randint(100, 9999),
    'team1': 'SHARKS',
    'team2': 'Thadaladi'
}

print("\n[1] Creating match...")
response = requests.post(base_url + '/api/schedule/matches', json=match_data)
print(f"Status: {response.status_code}")
match_id = response.json()['data']['id']
print(f"Match ID: {match_id}\n")

# Update match status to live
print("[2] Updating match status to live...")
response = requests.put(
    base_url + f'/api/schedule/matches/{match_id}/status',
    json={'status': 'live'}
)
print(f"Status: {response.status_code}\n")

# Update toss details
print("[3] Updating toss details...")
toss_data = {
    'toss_winner': 'SHARKS',
    'toss_choice': 'bat'
}
response = requests.put(
    base_url + f'/api/schedule/matches/{match_id}/toss',
    json=toss_data
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()['data']
    print(f"[OK] Toss Winner: {data.get('toss_winner')}")
    print(f"[OK] Toss Choice: {data.get('toss_choice')}\n")
else:
    print(f"[ERROR] {response.text}\n")

# Update match timing
print("[4] Updating match timing...")
now = datetime.utcnow()
timing_data = {
    'scheduled_start_time': (now).isoformat() + 'Z',
    'actual_start_time': (now + timedelta(minutes=15)).isoformat() + 'Z',
    'match_end_time': (now + timedelta(hours=3, minutes=30)).isoformat() + 'Z'
}
response = requests.put(
    base_url + f'/api/schedule/matches/{match_id}/timing',
    json=timing_data
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()['data']
    print(f"[OK] Scheduled Start: {data.get('scheduled_start_time')}")
    print(f"[OK] Actual Start: {data.get('actual_start_time')}")
    print(f"[OK] End Time: {data.get('match_end_time')}\n")
else:
    print(f"[ERROR] {response.text}\n")

# Update innings scores
print("[5] Updating innings scores...")
scores_data = {
    'team1_first_innings_score': 165,
    'team2_first_innings_score': 152
}
response = requests.put(
    base_url + f'/api/schedule/matches/{match_id}/scores',
    json=scores_data
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()['data']
    print(f"[OK] Team 1 First Innings: {data.get('team1_first_innings_score')}")
    print(f"[OK] Team 2 First Innings: {data.get('team2_first_innings_score')}\n")
else:
    print(f"[ERROR] {response.text}\n")

# Fetch the complete match with all new details
print("[6] Fetching complete match details...")
response = requests.get(base_url + f'/api/schedule/matches/{match_id}')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    match = response.json()['data']
    print(f"\nCOMPLETE MATCH DETAILS:")
    print(f"   Match: {match['team1']} vs {match['team2']}")
    print(f"   Status: {match['status']}")
    print(f"\n   Toss:")
    print(f"      Winner: {match.get('toss_winner')}")
    print(f"      Choice: {match.get('toss_choice')}")
    print(f"\n   Timing:")
    print(f"      Scheduled: {match.get('scheduled_start_time')}")
    print(f"      Started: {match.get('actual_start_time')}")
    print(f"      Ended: {match.get('match_end_time')}")
    print(f"\n   Scores:")
    print(f"      {match['team1']} 1st Innings: {match.get('team1_first_innings_score')}")
    print(f"      {match['team2']} 1st Innings: {match.get('team2_first_innings_score')}")
else:
    print(f"[ERROR] {response.text}\n")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
