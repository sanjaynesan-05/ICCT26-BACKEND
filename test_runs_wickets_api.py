"""
Test to show runs and wickets in API response
"""
import requests
import json

try:
    response = requests.get('http://127.0.0.1:8000/api/schedule/matches')
    if response.status_code == 200:
        data = response.json()
        for match in data.get("data", []):
            print(f"Match {match['id']} - Status: {match['status']}")
            print(f"  Team 1 Runs: {match.get('team1_first_innings_runs')}, Wickets: {match.get('team1_first_innings_wickets')}")
            print(f"  Team 2 Runs: {match.get('team2_first_innings_runs')}, Wickets: {match.get('team2_first_innings_wickets')}")
            print()
except Exception as e:
    print(f"Error: {e}")
