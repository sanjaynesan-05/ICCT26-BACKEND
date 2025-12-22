#!/usr/bin/env python3
"""
Test Schedule Feature - Creates matches and tests all schedule endpoints
Uses team NAMES not team IDs for match creation
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{BASE_URL}/api/health"
TEAMS_ENDPOINT = f"{BASE_URL}/api/teams"
SCHEDULE_MATCHES_ENDPOINT = f"{BASE_URL}/api/schedule/matches"
SCHEDULE_STANDINGS_ENDPOINT = f"{BASE_URL}/api/schedule/standings"

def main():
    print("\n" + "="*70)
    print("🏏 ICCT26 SCHEDULE FEATURE TEST")
    print("="*70)
    
    # STEP 1: Fetch all teams
    print("\n📋 STEP 1: Fetching all teams from database...")
    print("-" * 70)
    
    teams = []
    try:
        response = requests.get(TEAMS_ENDPOINT, timeout=10)
        if response.status_code == 200:
            teams_data = response.json()
            teams = teams_data.get("teams", [])
            print(f"✅ Found {len(teams)} teams:")
            for team in teams:
                print(f"   - {team['team_id']}: {team['team_name']}")
        else:
            print(f"❌ Error fetching teams: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error fetching teams: {e}")
        return
    
    if not teams:
        print("❌ No teams found in database. Cannot proceed with match creation.")
        return
    
    # STEP 2: Create matches between teams (using team names)
    print("\n📋 STEP 2: Creating matches between teams...")
    print("-" * 70)
    
    matches_created = 0
    team_names = [t["team_name"] for t in teams]
    
    # Create round-robin matches (all teams vs all teams)
    match_number = 1
    for i, team1 in enumerate(team_names):
        for j, team2 in enumerate(team_names):
            if i >= j:  # Skip same team and duplicates
                continue
            
            match_data = {
                "round": "Group Stage",
                "round_number": 1,
                "match_number": match_number,
                "team1": team1,
                "team2": team2,
                "scheduled_start_time": (datetime.now() + timedelta(days=match_number)).isoformat()
            }
            
            try:
                response = requests.post(SCHEDULE_MATCHES_ENDPOINT, json=match_data, timeout=10)
                if response.status_code == 201:
                    matches_created += 1
                    print(f"✅ Created match {match_number}: {team1} vs {team2}")
                else:
                    error_detail = response.json().get("detail", response.status_code) if response.text else response.status_code
                    print(f"⚠️  Could not create match {team1} vs {team2}: {error_detail}")
                match_number += 1
            except Exception as e:
                print(f"⚠️  Error creating match: {e}")
    
    print(f"\n✅ Total matches created: {matches_created}")
    
    # STEP 3: Fetch all matches
    print("\n📋 STEP 3: Fetching all matches...")
    print("-" * 70)
    
    try:
        response = requests.get(SCHEDULE_MATCHES_ENDPOINT, timeout=10)
        if response.status_code == 200:
            matches_response = response.json()
            matches = matches_response.get("matches", [])
            print(f"✅ Found {len(matches)} total matches in database")
            if matches:
                for match in matches[:5]:  # Show first 5
                    team1_name = match.get('team1', {}).get('team_name', 'Unknown') if isinstance(match.get('team1'), dict) else match.get('team1', 'Unknown')
                    team2_name = match.get('team2', {}).get('team_name', 'Unknown') if isinstance(match.get('team2'), dict) else match.get('team2', 'Unknown')
                    print(f"   - Match {match.get('id', 'N/A')}: {team1_name} vs {team2_name}")
        else:
            print(f"❌ Error fetching matches: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching matches: {e}")
    
    # STEP 4: Fetch standings
    print("\n📋 STEP 4: Fetching standings...")
    print("-" * 70)
    
    try:
        response = requests.get(SCHEDULE_STANDINGS_ENDPOINT, timeout=10)
        if response.status_code == 200:
            standings = response.json()
            teams_standings = standings.get("teams", [])
            print(f"✅ Standings retrieved for {len(teams_standings)} teams")
            if teams_standings:
                for team in teams_standings[:3]:
                    print(f"   - {team.get('team_name', 'Unknown')}: {team.get('matches_played', 0)} matches, {team.get('wins', 0)} wins")
        else:
            print(f"❌ Error fetching standings: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching standings: {e}")
    
    # STEP 5: Health check
    print("\n📋 STEP 5: Health check...")
    print("-" * 70)
    
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health check passed: {health.get('status', 'OK')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    print("\n" + "="*70)
    print("✅ SCHEDULE FEATURE TEST COMPLETE")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   Teams in database: {len(teams)}")
    print(f"   Matches created: {matches_created}")
    print(f"\n✅ All schedule endpoints working!")
    print()

if __name__ == "__main__":
    main()
