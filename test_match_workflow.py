"""
Comprehensive test suite for 4-Stage Match Workflow
Tests the complete match lifecycle:
1. CREATE MATCH (Stage 1)
2. START MATCH (Stage 2)
3. UPDATE FIRST INNINGS SCORE (Stage 3A)
4. UPDATE SECOND INNINGS SCORE (Stage 3B)
5. FINISH MATCH (Stage 4)
"""

import requests
import json
import random
from datetime import datetime, timedelta, timezone

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/schedule"
HEADERS = {"Content-Type": "application/json"}

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


def print_test(num, title):
    """Print test title"""
    print(f"{BOLD}[{num}] {title}...{RESET}")


def print_success(message):
    """Print success message"""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    """Print error message"""
    print(f"{RED}❌ {message}{RESET}")


def print_info(message):
    """Print info message"""
    print(f"{YELLOW}ℹ️  {message}{RESET}")


def print_json(data):
    """Pretty print JSON"""
    print(json.dumps(data, indent=2, default=str))


# ============================================================
# TEST 1: CREATE MATCH (Stage 1)
# ============================================================

def test_create_match():
    """Test creating a new match (scheduled status)"""
    print_test(1, "Creating match in 'scheduled' status")
    
    # Use random round number to avoid conflicts
    random_round = random.randint(10000, 99999)
    
    payload = {
        "round": f"Workflow Test Round {random_round}",
        "round_number": random_round,
        "match_number": 1,
        "team1": "SHARKS",
        "team2": "Thadaladi"
    }
    
    response = requests.post(f"{BASE_URL}/matches", json=payload, headers=HEADERS)
    
    if response.status_code != 201:
        print_error(f"Expected 201, got {response.status_code}")
        print_json(response.json())
        return None
    
    data = response.json()
    match = data["data"]
    match_id = match["id"]
    
    # Verify initial state
    if match["status"] != "scheduled":
        print_error(f"Expected status 'scheduled', got '{match['status']}'")
        return None
    
    if match["toss_winner"] is not None:
        print_error("Expected toss_winner to be null")
        return None
    
    if match["team1_first_innings_score"] is not None:
        print_error("Expected team1_first_innings_score to be null")
        return None
    
    print_success(f"Match created successfully (ID: {match_id})")
    print_info(f"Status: {match['status']}")
    print_info(f"Teams: {match['team1']} vs {match['team2']}")
    
    return match_id


# ============================================================
# TEST 2: START MATCH (Stage 2)
# ============================================================

def test_start_match(match_id):
    """Test starting a match (scheduled → live)"""
    print_test(2, "Starting match (Stage 2 - scheduled → live)")
    
    now = datetime.now(timezone.utc)
    
    payload = {
        "toss_winner": "SHARKS",
        "toss_choice": "bat",
        "match_score_url": "https://example.com/match/workflow/scorecard",
        "actual_start_time": now.isoformat()
    }
    
    response = requests.put(
        f"{BASE_URL}/matches/{match_id}/start",
        json=payload,
        headers=HEADERS
    )
    
    if response.status_code != 200:
        print_error(f"Expected 200, got {response.status_code}")
        print_json(response.json())
        return False
    
    data = response.json()
    match = data["data"]
    
    # Verify state transition
    if match["status"] != "live":
        print_error(f"Expected status 'live', got '{match['status']}'")
        return False
    
    if match["toss_winner"] != "SHARKS":
        print_error(f"Expected toss_winner 'SHARKS', got '{match['toss_winner']}'")
        return False
    
    if match["toss_choice"] != "bat":
        print_error(f"Expected toss_choice 'bat', got '{match['toss_choice']}'")
        return False
    
    if match["match_score_url"] != "https://example.com/match/workflow/scorecard":
        print_error("Scorecard URL not set correctly")
        return False
    
    print_success("Match started successfully (Status: live)")
    print_info(f"Toss: {match['toss_winner']} won, chose to {match['toss_choice']}")
    print_info(f"Scorecard: {match['match_score_url']}")
    
    return True


# ============================================================
# TEST 3: FIRST INNINGS SCORE (Stage 3A)
# ============================================================

def test_first_innings_score(match_id):
    """Test updating first innings score (live → in-progress)"""
    print_test(3, "Updating first innings score (Stage 3A - live → in-progress)")
    
    payload = {
        "batting_team": "SHARKS",
        "score": 165
    }
    
    response = requests.put(
        f"{BASE_URL}/matches/{match_id}/first-innings-score",
        json=payload,
        headers=HEADERS
    )
    
    if response.status_code != 200:
        print_error(f"Expected 200, got {response.status_code}")
        print_json(response.json())
        return False
    
    data = response.json()
    match = data["data"]
    
    # Verify state transition
    if match["status"] != "in-progress":
        print_error(f"Expected status 'in-progress', got '{match['status']}'")
        return False
    
    if match["team1_first_innings_score"] != 165:
        print_error(f"Expected team1 score 165, got {match['team1_first_innings_score']}")
        return False
    
    if match["team2_first_innings_score"] is not None:
        print_error("Expected team2 score to be null")
        return False
    
    print_success("First innings score recorded (Status: in-progress)")
    print_info(f"SHARKS 1st Innings: {match['team1_first_innings_score']} runs")
    
    return True


# ============================================================
# TEST 4: SECOND INNINGS SCORE (Stage 3B)
# ============================================================

def test_second_innings_score(match_id):
    """Test updating second innings score (in-progress → in-progress)"""
    print_test(4, "Updating second innings score (Stage 3B - in-progress → in-progress)")
    
    payload = {
        "batting_team": "Thadaladi",
        "score": 152
    }
    
    response = requests.put(
        f"{BASE_URL}/matches/{match_id}/second-innings-score",
        json=payload,
        headers=HEADERS
    )
    
    if response.status_code != 200:
        print_error(f"Expected 200, got {response.status_code}")
        print_json(response.json())
        return False
    
    data = response.json()
    match = data["data"]
    
    # Verify state remains in-progress
    if match["status"] != "in-progress":
        print_error(f"Expected status 'in-progress', got '{match['status']}'")
        return False
    
    if match["team2_first_innings_score"] != 152:
        print_error(f"Expected team2 score 152, got {match['team2_first_innings_score']}")
        return False
    
    if match["team1_first_innings_score"] != 165:
        print_error("Team1 score was overwritten!")
        return False
    
    print_success("Second innings score recorded (Status: in-progress)")
    print_info(f"Thadaladi 1st Innings: {match['team2_first_innings_score']} runs")
    
    return True


# ============================================================
# TEST 5: FINISH MATCH (Stage 4)
# ============================================================

def test_finish_match(match_id):
    """Test finishing match (in-progress → completed)"""
    print_test(5, "Finishing match (Stage 4 - in-progress → completed)")
    
    now = datetime.now(timezone.utc)
    
    payload = {
        "winner": "SHARKS",
        "margin": 13,
        "margin_type": "runs",
        "match_end_time": now.isoformat()
    }
    
    response = requests.put(
        f"{BASE_URL}/matches/{match_id}/finish",
        json=payload,
        headers=HEADERS
    )
    
    if response.status_code != 200:
        print_error(f"Expected 200, got {response.status_code}")
        print_json(response.json())
        return False
    
    data = response.json()
    match = data["data"]
    
    # Verify final state
    if match["status"] != "completed":
        print_error(f"Expected status 'completed', got '{match['status']}'")
        return False
    
    # Check result object (nested structure)
    if not match.get("result"):
        print_error("Expected result object in response")
        return False
    
    result = match["result"]
    
    if result.get("winner") != "SHARKS":
        print_error(f"Expected winner 'SHARKS', got '{result.get('winner')}'")
        return False
    
    if result.get("margin") != 13:
        print_error(f"Expected margin 13, got {result.get('margin')}")
        return False
    
    # Support both snake_case and camelCase keys from API serialization
    margin_type_value = result.get("margin_type") or result.get("marginType")
    if margin_type_value != "runs":
        print_error(f"Expected margin_type 'runs', got '{margin_type_value}'")
        return False

    print_success("Match completed successfully (Status: completed)")
    print_info(f"Winner: {result.get('winner')} by {result.get('margin')} {margin_type_value}")
    
    return True


# ============================================================
# TEST 6: ERROR - INVALID STATUS TRANSITION
# ============================================================

def test_error_invalid_status_transition(match_id):
    """Test error when trying to start an already-live match"""
    print_test(6, "Testing error: Cannot start already-live match")
    
    payload = {
        "toss_winner": "SHARKS",
        "toss_choice": "bat",
        "match_score_url": "https://example.com/scorecard",
        "actual_start_time": datetime.now(timezone.utc).isoformat()
    }
    
    # Try to start a match that's already completed
    response = requests.put(
        f"{BASE_URL}/matches/{match_id}/start",
        json=payload,
        headers=HEADERS
    )
    
    # Should get 400 error
    if response.status_code == 400:
        resp_json = response.json()
        error_detail = resp_json.get("detail") or resp_json.get("message") or str(resp_json)
        if "scheduled" in str(error_detail).lower():
            print_success("Correctly prevented invalid status transition (400)")
            print_info(f"Error: {error_detail}")
            return True
    
    print_error(f"Expected 400 error, got {response.status_code}")
    return False


# ============================================================
# TEST 7: ERROR - INVALID TOSS WINNER
# ============================================================

def test_error_invalid_toss_winner():
    """Test error with invalid toss winner team"""
    print_test(7, "Testing error: Invalid toss winner team")
    
    # Create a match first with random round number
    random_round = random.randint(10000, 99999)
    payload = {
        "round": f"Error Test Round A {random_round}",
        "round_number": random_round,
        "match_number": 1,
        "team1": "SHARKS",
        "team2": "Thadaladi"
    }
    
    response = requests.post(f"{BASE_URL}/matches", json=payload, headers=HEADERS)
    if response.status_code != 201:
        print_error("Could not create test match")
        return False
    
    match_id = response.json()["data"]["id"]
    
    # Try to start with invalid team
    payload = {
        "toss_winner": "Invalid Team",
        "toss_choice": "bat",
        "match_score_url": "https://example.com/scorecard",
        "actual_start_time": datetime.now(timezone.utc).isoformat()
    }
    
    response = requests.put(
        f"{BASE_URL}/matches/{match_id}/start",
        json=payload,
        headers=HEADERS
    )
    
    if response.status_code in [400, 422]:
        print_success(f"Correctly rejected invalid team (Status: {response.status_code})")
        resp_json = response.json()
        error_detail = resp_json.get("detail") or resp_json.get("message") or str(resp_json)
        print_info(f"Error: {error_detail}")
        return True
    
    print_error(f"Expected 400/422 error, got {response.status_code}")
    return False


# ============================================================
# TEST 8: ERROR - INVALID MARGIN TYPE
# ============================================================

def test_error_invalid_margin_type():
    """Test error with invalid margin type"""
    print_test(8, "Testing error: Invalid margin type")
    
    # Create and complete a match with random round number
    random_round = random.randint(10000, 99999)
    payload = {
        "round": f"Error Test Round B {random_round}",
        "round_number": random_round,
        "match_number": 1,
        "team1": "SHARKS",
        "team2": "Thadaladi"
    }
    
    response = requests.post(f"{BASE_URL}/matches", json=payload, headers=HEADERS)
    match_id = response.json()["data"]["id"]
    
    # Start the match
    payload = {
        "toss_winner": "SHARKS",
        "toss_choice": "bat",
        "match_score_url": "https://example.com/scorecard",
        "actual_start_time": datetime.now(timezone.utc).isoformat()
    }
    requests.put(f"{BASE_URL}/matches/{match_id}/start", json=payload, headers=HEADERS)
    
    # Update scores
    requests.put(
        f"{BASE_URL}/matches/{match_id}/first-innings-score",
        json={"batting_team": "SHARKS", "score": 165},
        headers=HEADERS
    )
    requests.put(
        f"{BASE_URL}/matches/{match_id}/second-innings-score",
        json={"batting_team": "Thadaladi", "score": 152},
        headers=HEADERS
    )
    
    # Try to finish with invalid margin type
    payload = {
        "winner": "SHARKS",
        "margin": 13,
        "margin_type": "invalid_type",
        "match_end_time": datetime.now(timezone.utc).isoformat()
    }
    
    response = requests.put(
        f"{BASE_URL}/matches/{match_id}/finish",
        json=payload,
        headers=HEADERS
    )
    
    if response.status_code == 422:
        print_success("Correctly rejected invalid margin type (Status: 422)")
        resp_json = response.json()
        error_detail = resp_json.get("detail") or resp_json.get("message") or str(resp_json)
        print_info(f"Error: {error_detail}")
        return True
    
    print_error(f"Expected 422 error, got {response.status_code}")
    return False


# ============================================================
# TEST 9: GET COMPLETED MATCH
# ============================================================

def test_get_completed_match(match_id):
    """Test retrieving a completed match"""
    print_test(9, "Retrieving completed match details")
    
    response = requests.get(f"{BASE_URL}/matches/{match_id}", headers=HEADERS)
    
    if response.status_code != 200:
        print_error(f"Expected 200, got {response.status_code}")
        return False
    
    data = response.json()
    match = data["data"]
    
    # Verify status and scores
    if match["status"] != "completed":
        print_error(f"Expected status 'completed', got '{match['status']}'")
        return False
    
    if match["toss_winner"] != "SHARKS":
        print_error(f"Expected toss_winner 'SHARKS', got '{match['toss_winner']}'")
        return False
    
    if match["team1_first_innings_score"] != 165:
        print_error(f"Expected team1 score 165, got {match['team1_first_innings_score']}")
        return False
    
    if match["team2_first_innings_score"] != 152:
        print_error(f"Expected team2 score 152, got {match['team2_first_innings_score']}")
        return False
    
    # Check result object
    if not match.get("result"):
        print_error("Expected result object in response")
        return False
    
    result = match["result"]
    
    if result.get("winner") != "SHARKS":
        print_error(f"Expected winner 'SHARKS', got '{result.get('winner')}'")
        return False
    
    if result.get("margin") != 13:
        print_error(f"Expected margin 13, got {result.get('margin')}")
        return False
    
    print_success("Match details retrieved successfully")
    print_info(f"Status: {match['status']}")
    print_info(f"Scores: {match['team1']} {match['team1_first_innings_score']} vs {match['team2']} {match['team2_first_innings_score']}")
    # Support both snake_case and camelCase keys from API serialization
    margin_type_value = result.get("margin_type") or result.get("marginType")
    print_info(f"Result: {result.get('winner')} won by {result.get('margin')} {margin_type_value}")
    
    return True


# ============================================================
# TEST 10: LIST MATCHES WITH COMPLETED STATUS
# ============================================================

def test_list_matches(match_id):
    """Test listing all matches includes completed match"""
    print_test(10, "Listing all matches (verify completed match in list)")
    
    response = requests.get(f"{BASE_URL}/matches", headers=HEADERS)
    
    if response.status_code != 200:
        print_error(f"Expected 200, got {response.status_code}")
        return False
    
    data = response.json()
    matches = data["data"]
    
    # Find our test match
    test_match = next((m for m in matches if m["id"] == match_id), None)
    
    if not test_match:
        print_error("Test match not found in list")
        return False
    
    if test_match["status"] != "completed":
        print_error(f"Expected status 'completed', got '{test_match['status']}'")
        return False
    
    print_success(f"Found completed match in list (Total matches: {len(matches)})")
    print_info(f"Match: {test_match['team1']} vs {test_match['team2']}")
    # Support both nested result object and legacy top-level winner key
    winner_value = (test_match.get('result') or {}).get('winner') or test_match.get('winner')
    print_info(f"Status: {test_match['status']} (Winner: {winner_value})")
    
    return True


# ============================================================
# MAIN TEST RUNNER
# ============================================================

def main():
    """Run all tests"""
    print_header("4-STAGE MATCH WORKFLOW TEST SUITE")
    print_info("Testing complete match lifecycle from creation to completion\n")
    
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # Test 1: Create Match
    match_id = test_create_match()
    if match_id:
        results["passed"] += 1
        results["tests"].append(("Create Match (Stage 1)", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("Create Match (Stage 1)", "FAILED"))
        return print_results(results)
    
    # Test 2: Start Match
    if test_start_match(match_id):
        results["passed"] += 1
        results["tests"].append(("Start Match (Stage 2)", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("Start Match (Stage 2)", "FAILED"))
        return print_results(results)
    
    # Test 3: First Innings Score
    if test_first_innings_score(match_id):
        results["passed"] += 1
        results["tests"].append(("First Innings Score (Stage 3A)", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("First Innings Score (Stage 3A)", "FAILED"))
        return print_results(results)
    
    # Test 4: Second Innings Score
    if test_second_innings_score(match_id):
        results["passed"] += 1
        results["tests"].append(("Second Innings Score (Stage 3B)", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("Second Innings Score (Stage 3B)", "FAILED"))
        return print_results(results)
    
    # Test 5: Finish Match
    if test_finish_match(match_id):
        results["passed"] += 1
        results["tests"].append(("Finish Match (Stage 4)", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("Finish Match (Stage 4)", "FAILED"))
        return print_results(results)
    
    # Test 6: Error - Invalid Status Transition
    if test_error_invalid_status_transition(match_id):
        results["passed"] += 1
        results["tests"].append(("Error: Invalid Status Transition", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("Error: Invalid Status Transition", "FAILED"))
    
    # Test 7: Error - Invalid Toss Winner
    if test_error_invalid_toss_winner():
        results["passed"] += 1
        results["tests"].append(("Error: Invalid Toss Winner", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("Error: Invalid Toss Winner", "FAILED"))
    
    # Test 8: Error - Invalid Margin Type
    if test_error_invalid_margin_type():
        results["passed"] += 1
        results["tests"].append(("Error: Invalid Margin Type", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("Error: Invalid Margin Type", "FAILED"))
    
    # Test 9: Get Completed Match
    if test_get_completed_match(match_id):
        results["passed"] += 1
        results["tests"].append(("Get Completed Match", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("Get Completed Match", "FAILED"))
    
    # Test 10: List Matches
    if test_list_matches(match_id):
        results["passed"] += 1
        results["tests"].append(("List Matches", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("List Matches", "FAILED"))
    
    print_results(results)


def print_results(results):
    """Print test results summary"""
    print_header("TEST RESULTS SUMMARY")
    
    total = results["passed"] + results["failed"]
    
    print(f"\n{BOLD}Test Execution Results:{RESET}\n")
    for test_name, status in results["tests"]:
        status_color = GREEN if status == "PASSED" else RED
        status_symbol = "✅" if status == "PASSED" else "❌"
        print(f"  {status_symbol} {test_name:<45} {status_color}{status}{RESET}")
    
    print(f"\n{BOLD}Summary:{RESET}")
    print(f"  Total Tests: {total}")
    print(f"  {GREEN}Passed: {results['passed']}{RESET}")
    print(f"  {RED}Failed: {results['failed']}{RESET}")
    
    if results["failed"] == 0:
        print(f"\n{GREEN}{BOLD}🎉 ALL TESTS PASSED! 🎉{RESET}")
        print(f"{GREEN}4-Stage Match Workflow is fully functional!{RESET}\n")
    else:
        print(f"\n{RED}{BOLD}⚠️  SOME TESTS FAILED{RESET}")
        print(f"{RED}Please review the errors above{RESET}\n")


if __name__ == "__main__":
    main()
