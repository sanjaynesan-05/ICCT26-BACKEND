#!/usr/bin/env python3
"""
Test script for ICCT26 Backend with Google Sheets Integration
Tests team registration, queue processing, and Google Sheets synchronization
"""

import requests
import json
import time
import base64
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
TEAM_NAME = f"Test Team {datetime.now().strftime('%H%M%S')}"

# Minimal valid base64 image (1x1 pixel PNG)
MINIMAL_IMAGE_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text, end="\n"):
    """Print info message"""
    print(f"ℹ️  {text}", end=end)


def test_api_health():
    """Test if API is running"""
    print_header("Testing API Health")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print_success("API is running and responding")
            return True
        else:
            print_error(f"API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {API_URL}")
        print_info("Make sure the server is running: uvicorn main:app --reload")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False


def test_queue_status():
    """Test queue status endpoint"""
    print_header("Checking Queue Status")
    try:
        response = requests.get(f"{API_URL}/queue/status")
        if response.status_code == 200:
            data = response.json()
            print_success("Queue status retrieved:")
            print(f"  Queue Size: {data.get('queue_size', 'N/A')}")
            print(f"  Worker Active: {data.get('worker_active', 'N/A')}")
            print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
            return True
        else:
            print_error(f"Failed to get queue status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error checking queue: {str(e)}")
        return False


def create_test_team_data(num_players=11):
    """Create test team registration data"""
    players = []
    roles = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
    
    for i in range(1, num_players + 1):
        player = {
            "name": f"Player {i}",
            "age": 20 + i,
            "phone": f"911{i:08d}",
            "role": roles[(i - 1) % len(roles)],
            "aadharFile": MINIMAL_IMAGE_BASE64,
            "subscriptionFile": MINIMAL_IMAGE_BASE64
        }
        players.append(player)
    
    team_data = {
        "churchName": "CSI St. Peter's Church",
        "teamName": TEAM_NAME,
        "pastorLetter": MINIMAL_IMAGE_BASE64,
        "captain": {
            "name": "Captain Test",
            "phone": "9876543210",
            "whatsapp": "9876543210",
            "email": "captain@test.com"
        },
        "viceCaptain": {
            "name": "Vice Captain Test",
            "phone": "9123456789",
            "whatsapp": "9123456789",
            "email": "vice@test.com"
        },
        "players": players,
        "paymentReceipt": MINIMAL_IMAGE_BASE64
    }
    
    return team_data


def test_team_registration():
    """Test team registration"""
    print_header("Testing Team Registration")
    
    team_data = create_test_team_data(num_players=11)
    
    print_info(f"Registering team: {TEAM_NAME}")
    print_info(f"Number of players: {len(team_data['players'])}")
    
    try:
        response = requests.post(
            f"{API_URL}/register/team",
            json=team_data,
            timeout=10
        )
        
        if response.status_code in [200, 202]:
            data = response.json()
            print_success("Team registration request accepted")
            print(f"  Status: {data.get('status', 'N/A')}")
            print(f"  Message: {data.get('message', 'N/A')}")
            
            if "data" in data:
                team_info = data["data"]
                print(f"  Team Name: {team_info.get('teamName', 'N/A')}")
                print(f"  Church: {team_info.get('churchName', 'N/A')}")
                print(f"  Players: {team_info.get('playerCount', 'N/A')}")
                print(f"  Queued At: {team_info.get('queuedAt', 'N/A')}")
            
            return True
        else:
            print_error(f"Registration failed with status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timeout - server took too long to respond")
        return False
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return False


def test_invalid_registration():
    """Test with invalid data"""
    print_header("Testing Validation")
    
    # Test with too few players
    invalid_data = create_test_team_data(num_players=5)
    
    print_info("Testing with only 5 players (minimum is 11)...")
    
    try:
        response = requests.post(
            f"{API_URL}/register/team",
            json=invalid_data,
            timeout=10
        )
        
        if response.status_code == 422:  # Validation error
            print_success("Validation correctly rejected invalid data")
            print(f"  Status Code: {response.status_code}")
            return True
        else:
            print_error(f"Expected validation error (422), got: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error during validation test: {str(e)}")
        return False


def test_swagger_ui():
    """Test Swagger UI availability"""
    print_header("Testing Documentation")
    try:
        response = requests.get(f"{API_URL}/docs")
        if response.status_code == 200:
            print_success("Swagger UI is available at /docs")
            print_info(f"  URL: {API_URL}/docs")
            return True
        else:
            print_error(f"Swagger UI returned status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error accessing Swagger UI: {str(e)}")
        return False


def wait_for_processing(seconds=5):
    """Wait for background processing"""
    print_header("Waiting for Background Processing")
    print_info(f"Waiting {seconds} seconds for queue worker to process...")
    
    for i in range(seconds):
        print_info(f"  [{i+1}/{seconds}] ", end="")
        time.sleep(1)
    
    print("\n✅ Background processing completed")


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("█" * 60)
    print("█  ICCT26 Backend Testing Suite - Google Sheets Integration")
    print("█" * 60)
    print(f"\nTest Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Endpoint: {API_URL}\n")
    
    results = {}
    
    # Test 1: API Health
    results["API Health"] = test_api_health()
    if not results["API Health"]:
        print_error("Cannot proceed - API is not running")
        return results
    
    # Test 2: Queue Status
    results["Queue Status"] = test_queue_status()
    
    # Test 3: Documentation
    results["Swagger UI"] = test_swagger_ui()
    
    # Test 4: Team Registration
    results["Team Registration"] = test_team_registration()
    
    # Test 5: Validation
    results["Validation"] = test_invalid_registration()
    
    # Wait for processing
    if results["Team Registration"]:
        wait_for_processing(seconds=3)
    
    # Print Summary
    print_header("Test Summary")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print_success("All tests passed! ✨")
    else:
        print_error(f"{total - passed} test(s) failed")
    
    print(f"\nTest Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Next steps
    print_header("Next Steps")
    print("📋 Manual Verification:")
    print("1. Open your Google Sheet")
    print("2. Check the 'Teams' sheet for your new team entry")
    print("3. Verify all 11 players appear in the 'Players' sheet")
    print("4. Check 'Files' sheet for document entries")
    print("5. Verify email confirmation was received")
    
    print("\n📖 For detailed testing guide, see: docs/TESTING_GUIDE.md")
    print("📚 For API documentation, open: http://localhost:8000/docs")
    
    return results


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n❌ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
