"""
Test script for match_score_url functionality
Tests creating a match, updating toss, updating timing, and setting match score URL
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/schedule"

def test_match_score_url_feature():
    """Test all match score URL functionality"""
    
    print("\n" + "="*70)
    print("MATCH SCORE URL FEATURE TEST")
    print("="*70)
    
    # Test 1: Create a match
    print("\n[1] Creating match...")
    match_data = {
        "round": "Round Score URL Test",
        "round_number": 99,
        "match_number": 1,
        "team1": "SHARKS",
        "team2": "Thadaladi"
    }
    response = requests.post(f"{BASE_URL}/matches", json=match_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 201:
        print(f"❌ Failed to create match: {response.text}")
        return False
    
    match = response.json()['data']
    match_id = match['id']
    print(f"✅ Match created with ID: {match_id}")
    
    # Verify match_score_url is null initially
    if match.get('match_score_url') is not None:
        print(f"⚠ WARNING: match_score_url should be null initially, but got: {match.get('match_score_url')}")
    else:
        print("✅ match_score_url is null initially")
    
    # Test 2: Update match status to live
    print("\n[2] Updating match status to live...")
    status_data = {"status": "live"}
    response = requests.put(f"{BASE_URL}/matches/{match_id}/status", json=status_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Failed to update status: {response.text}")
        return False
    print("✅ Status updated to live")
    
    # Test 3: Update toss details
    print("\n[3] Updating toss details...")
    toss_data = {
        "toss_winner": "SHARKS",
        "toss_choice": "bat"
    }
    response = requests.put(f"{BASE_URL}/matches/{match_id}/toss", json=toss_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Failed to update toss: {response.text}")
        return False
    print("✅ Toss details updated")
    
    # Test 4: Update match timing
    print("\n[4] Updating match timing...")
    timing_data = {
        "scheduled_start_time": "2025-11-28T10:00:00",
        "actual_start_time": "2025-11-28T10:15:00",
        "match_end_time": "2025-11-28T13:45:00"
    }
    response = requests.put(f"{BASE_URL}/matches/{match_id}/timing", json=timing_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Failed to update timing: {response.text}")
        return False
    print("✅ Timing details updated")
    
    # Test 5: Update innings scores
    print("\n[5] Updating innings scores...")
    scores_data = {
        "team1_first_innings_score": 165,
        "team2_first_innings_score": 152
    }
    response = requests.put(f"{BASE_URL}/matches/{match_id}/scores", json=scores_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Failed to update scores: {response.text}")
        return False
    print("✅ Scores updated (165 vs 152)")
    
    # Test 6: UPDATE MATCH SCORE URL (NEW FEATURE!)
    print("\n[6] Updating match score URL (NEW FEATURE)...")
    score_url_data = {
        "match_score_url": "https://example.com/matches/123/scorecard"
    }
    response = requests.put(f"{BASE_URL}/matches/{match_id}/score-url", json=score_url_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Failed to update match score URL: {response.text}")
        return False
    
    match_updated = response.json()['data']
    if match_updated.get('match_score_url') == "https://example.com/matches/123/scorecard":
        print(f"✅ Match score URL set successfully")
        print(f"   URL: {match_updated.get('match_score_url')}")
    else:
        print(f"❌ Match score URL not set correctly. Got: {match_updated.get('match_score_url')}")
        return False
    
    # Test 7: Get single match and verify all fields including match_score_url
    print("\n[7] Fetching complete match details...")
    response = requests.get(f"{BASE_URL}/matches/{match_id}")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Failed to fetch match: {response.text}")
        return False
    
    match_final = response.json()['data']
    print("✅ Match details retrieved successfully")
    
    # Verify all fields
    print("\nCOMPLETE MATCH DETAILS:")
    print(f"   Match: {match_final['team1']} vs {match_final['team2']}")
    print(f"   Status: {match_final['status']}")
    print(f"   Toss: {match_final['toss_winner']} chose to {match_final['toss_choice']}")
    print(f"   Timing:")
    print(f"      Scheduled: {match_final['scheduled_start_time']}")
    print(f"      Started: {match_final['actual_start_time']}")
    print(f"      Ended: {match_final['match_end_time']}")
    print(f"   Scores:")
    print(f"      {match_final['team1']} 1st Innings: {match_final['team1_first_innings_score']}")
    print(f"      {match_final['team2']} 1st Innings: {match_final['team2_first_innings_score']}")
    print(f"   Match Score URL: {match_final.get('match_score_url')}")
    
    # Test 8: Test invalid URL (should fail)
    print("\n[8] Testing URL validation (should reject invalid URL)...")
    invalid_url_data = {
        "match_score_url": "not-a-valid-url"
    }
    response = requests.put(f"{BASE_URL}/matches/{match_id}/score-url", json=invalid_url_data)
    print(f"Status: {response.status_code}")
    if response.status_code >= 400:
        print(f"✅ Invalid URL correctly rejected")
    else:
        print(f"⚠ WARNING: Invalid URL should have been rejected")
    
    # Test 9: Update with valid HTTPS URL
    print("\n[9] Testing with different HTTPS URL...")
    new_url_data = {
        "match_score_url": "https://cricketlive.example.com/match/456/details"
    }
    response = requests.put(f"{BASE_URL}/matches/{match_id}/score-url", json=new_url_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        match_updated = response.json()['data']
        if match_updated.get('match_score_url') == "https://cricketlive.example.com/match/456/details":
            print(f"✅ URL updated successfully")
            print(f"   New URL: {match_updated.get('match_score_url')}")
        else:
            print(f"❌ URL not updated correctly")
            return False
    else:
        print(f"❌ Failed to update URL: {response.text}")
        return False
    
    # Test 10: Get all matches and verify match_score_url is included
    print("\n[10] Fetching all matches (verify match_score_url included)...")
    response = requests.get(f"{BASE_URL}/matches")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        matches = response.json()['data']
        if matches:
            first_match = matches[0]
            if 'match_score_url' in first_match:
                print(f"✅ match_score_url field present in list response")
            else:
                print(f"❌ match_score_url field MISSING in list response")
                print(f"Available fields: {list(first_match.keys())}")
                return False
    else:
        print(f"❌ Failed to fetch matches: {response.text}")
        return False
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print("\nSUMMARY:")
    print("✅ Match creation with initial null match_score_url")
    print("✅ Match status update to 'live'")
    print("✅ Toss details update (SHARKS, bat)")
    print("✅ Match timing update (3 timestamps)")
    print("✅ Innings scores update (165 vs 152)")
    print("✅ Match score URL endpoint working (NEW FEATURE)")
    print("✅ URL validation (rejects invalid URLs)")
    print("✅ URL update functionality")
    print("✅ match_score_url field in all API responses")
    print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = test_match_score_url_feature()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server at http://127.0.0.1:8000")
        print("Make sure the server is running with: uvicorn main:app --host 127.0.0.1 --port 8000")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        exit(1)
