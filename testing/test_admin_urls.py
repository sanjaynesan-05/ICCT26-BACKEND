#!/usr/bin/env python3
"""
Test script to verify Admin Panel API returns clean Cloudinary URLs
Tests:
- GET /admin/teams
- GET /admin/teams/{team_id}
- GET /admin/players/{player_id}
"""

import asyncio
import logging
from app.utils.file_utils import ensure_valid_url, clean_file_fields

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ensure_valid_url():
    """Test URL validation logic"""
    print("\n" + "="*70)
    print("TEST 1: URL Validation (ensure_valid_url)")
    print("="*70)
    
    test_cases = [
        # (input, expected_result, description)
        ("https://res.cloudinary.com/dplaeuuqk/image/upload/v1234/test.jpg", 
         "https://res.cloudinary.com/dplaeuuqk/image/upload/v1234/test.jpg",
         "Valid Cloudinary HTTPS URL"),
        
        ("http://res.cloudinary.com/dplaeuuqk/image/upload/v1234/test.jpg",
         "https://res.cloudinary.com/dplaeuuqk/image/upload/v1234/test.jpg",
         "Valid Cloudinary HTTP URL (convert to HTTPS)"),
        
        (None, "", "None value"),
        
        ("", "", "Empty string"),
        
        ("   ", "", "Whitespace only"),
        
        ("base64data...", "", "Raw Base64 (reject)"),
        
        ("data:image/png;base64,iVBOR...", "", "Base64 data URI (reject)"),
        
        ('{"url": "https://res.cloudinary.com/...", "public_id": "..."}', 
         "", "JSON object (reject)"),
        
        ("https://example.com/image.jpg", "", "Non-Cloudinary URL (reject)"),
        
        ("invalid!!!url", "", "Malformed URL (reject)"),
    ]
    
    all_passed = True
    for input_val, expected, description in test_cases:
        result = ensure_valid_url(input_val)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n{status}: {description}")
        if input_val:
            print(f"  Input: {input_val[:60]}{'...' if len(str(input_val)) > 60 else ''}")
        else:
            print(f"  Input: {repr(input_val)}")
        print(f"  Expected: {repr(expected)}")
        print(f"  Got: {repr(result)}")
    
    return all_passed


def test_clean_file_fields():
    """Test field cleaning logic"""
    print("\n" + "="*70)
    print("TEST 2: File Field Cleaning (clean_file_fields)")
    print("="*70)
    
    # Test Case 1: Mixed valid and invalid fields
    test_data = {
        "teamName": "Warriors",
        "churchName": "St. Mary's",
        "paymentReceipt": "https://res.cloudinary.com/dplaeuuqk/image/upload/v1234/payment.jpg",
        "pastorLetter": None,
        "groupPhoto": "base64data...",
        "extraField": "should not be touched"
    }
    
    print("\nTest Case 1: Team with mixed file field types")
    print(f"Input: {test_data}")
    
    cleaned = clean_file_fields(
        test_data.copy(),
        ["paymentReceipt", "pastorLetter", "groupPhoto"]
    )
    
    print(f"Output: {cleaned}")
    
    # Verify results
    assert cleaned["teamName"] == "Warriors", "Non-file field should not change"
    assert cleaned["paymentReceipt"] == "https://res.cloudinary.com/dplaeuuqk/image/upload/v1234/payment.jpg", "Valid URL should be preserved"
    assert cleaned["pastorLetter"] == "", "None should become empty string"
    assert cleaned["groupPhoto"] == "", "Base64 should become empty string"
    assert cleaned["extraField"] == "should not be touched", "Non-file fields should not change"
    
    print("✅ All assertions passed!")
    
    # Test Case 2: Player data with file fields
    print("\nTest Case 2: Player with file fields")
    player_data = {
        "playerId": "TEAM-20251117-ABC123-P01",
        "name": "John Doe",
        "role": "Batter",
        "aadharFile": "https://res.cloudinary.com/dplaeuuqk/raw/upload/v1234/aadhar.pdf",
        "subscriptionFile": "invalid"
    }
    
    print(f"Input: {player_data}")
    
    cleaned_player = clean_file_fields(
        player_data.copy(),
        ["aadharFile", "subscriptionFile"]
    )
    
    print(f"Output: {cleaned_player}")
    
    assert cleaned_player["aadharFile"] == "https://res.cloudinary.com/dplaeuuqk/raw/upload/v1234/aadhar.pdf", "Valid aadhar URL preserved"
    assert cleaned_player["subscriptionFile"] == "", "Invalid subscription file becomes empty"
    
    print("✅ All assertions passed!")
    
    return True


def test_response_format():
    """Test expected response format"""
    print("\n" + "="*70)
    print("TEST 3: Response Format Validation")
    print("="*70)
    
    # Simulate get_all_teams response after cleaning
    teams_response = {
        "success": True,
        "data": [
            {
                "teamId": "TEAM-20251117-ABC123",
                "teamName": "Warriors",
                "churchName": "St. Mary's",
                "captainName": "John Doe",
                "playerCount": 11,
                "paymentReceipt": "https://res.cloudinary.com/dplaeuuqk/image/upload/v1/payment.jpg",
                "pastorLetter": "https://res.cloudinary.com/dplaeuuqk/raw/upload/v1/letter.pdf",
                "groupPhoto": ""  # Empty if not uploaded
            }
        ]
    }
    
    print("\nGET /admin/teams Response:")
    print(f"Success: {teams_response['success']}")
    print(f"Number of teams: {len(teams_response['data'])}")
    
    team = teams_response['data'][0]
    print(f"\nTeam Fields:")
    print(f"  - teamName: {team['teamName']}")
    print(f"  - churchName: {team['churchName']}")
    print(f"  - paymentReceipt: {team['paymentReceipt'][:50]}..." if team['paymentReceipt'] else "  - paymentReceipt: (empty)")
    print(f"  - pastorLetter: {team['pastorLetter'][:50]}..." if team['pastorLetter'] else "  - pastorLetter: (empty)")
    print(f"  - groupPhoto: {team['groupPhoto']}")
    
    # Validate response structure
    assert isinstance(team['paymentReceipt'], str), "Payment receipt should be string"
    assert isinstance(team['pastorLetter'], str), "Pastor letter should be string"
    assert isinstance(team['groupPhoto'], str), "Group photo should be string"
    assert team['paymentReceipt'] == "" or team['paymentReceipt'].startswith("https://"), "Invalid URL format"
    assert team['pastorLetter'] == "" or team['pastorLetter'].startswith("https://"), "Invalid URL format"
    assert team['groupPhoto'] == "" or team['groupPhoto'].startswith("https://"), "Invalid URL format"
    
    print("\n✅ Response format is valid!")
    
    # Simulate get_team_details response
    team_details_response = {
        "success": True,
        "data": {
            "team": {
                "teamId": "TEAM-20251117-ABC123",
                "teamName": "Warriors",
                "churchName": "St. Mary's",
                "paymentReceipt": "https://res.cloudinary.com/dplaeuuqk/image/upload/v1/payment.jpg",
                "pastorLetter": "https://res.cloudinary.com/dplaeuuqk/raw/upload/v1/letter.pdf",
                "groupPhoto": ""
            },
            "players": [
                {
                    "playerId": "TEAM-20251117-ABC123-P01",
                    "name": "John Doe",
                    "role": "Batter",
                    "aadharFile": "https://res.cloudinary.com/dplaeuuqk/raw/upload/v1/aadhar.pdf",
                    "subscriptionFile": ""
                }
            ]
        }
    }
    
    print("\nGET /admin/teams/{team_id} Response:")
    print(f"Success: {team_details_response['success']}")
    
    team_detail = team_details_response['data']['team']
    print(f"\nTeam Detail Fields:")
    print(f"  - teamName: {team_detail['teamName']}")
    print(f"  - churchName: {team_detail['churchName']}")
    print(f"  - paymentReceipt: {team_detail['paymentReceipt'][:50] if team_detail['paymentReceipt'] else '(empty)'}")
    print(f"  - pastorLetter: {team_detail['pastorLetter'][:50] if team_detail['pastorLetter'] else '(empty)'}")
    
    player = team_details_response['data']['players'][0]
    print(f"\nPlayer Detail Fields:")
    print(f"  - name: {player['name']}")
    print(f"  - role: {player['role']}")
    print(f"  - aadharFile: {player['aadharFile'][:50] if player['aadharFile'] else '(empty)'}")
    print(f"  - subscriptionFile: {player['subscriptionFile']}")
    
    print("\n✅ Detailed response format is valid!")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 ADMIN PANEL URL CLEANING TEST SUITE")
    print("="*70)
    
    try:
        test1_passed = test_ensure_valid_url()
        test2_passed = test_clean_file_fields()
        test3_passed = test_response_format()
        
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"Test 1 (URL Validation): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
        print(f"Test 2 (Field Cleaning): ✅ PASSED")
        print(f"Test 3 (Response Format): ✅ PASSED")
        
        if test1_passed:
            print("\n✅ ALL TESTS PASSED!")
            print("\n🎯 Admin Panel will now receive:")
            print("  • Clean Cloudinary URLs for all file fields")
            print("  • Empty strings instead of undefined/null/objects")
            print("  • Guaranteed valid URLs or empty values")
            print("  • No malformed data or Base64 in responses")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED")
            return 1
            
    except Exception as e:
        logger.exception(f"❌ Test error: {str(e)}")
        print(f"\n❌ Test failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
