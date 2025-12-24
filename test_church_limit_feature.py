#!/usr/bin/env python3
"""
Test the Church Team Limit Feature (Max 2 Teams)
This script tests the enforcement of a maximum of 2 teams per church
"""

import httpx
import asyncio
import json
import tempfile
import os
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# Test colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_test(title):
    """Print test title"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}TEST: {title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}")


def print_success(msg):
    """Print success message"""
    print(f"{GREEN}[OK] {msg}{RESET}")


def print_error(msg):
    """Print error message"""
    print(f"{RED}[FAIL] {msg}{RESET}")


def print_info(msg):
    """Print info message"""
    print(f"{BLUE}[i] {msg}{RESET}")


def print_response(response):
    """Print response details"""
    print(f"{YELLOW}Status: {response.status_code}{RESET}")
    try:
        print(f"{YELLOW}Body: {json.dumps(response.json(), indent=2)}{RESET}")
    except:
        print(f"{YELLOW}Body: {response.text}{RESET}")


async def test_health():
    """Test 1: Check if server is running"""
    print_test("Server Health Check")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success("Server is running and healthy")
            print_response(response)
            return True
        else:
            print_error("Server health check failed")
            print_response(response)
            return False


async def test_church_availability():
    """Test 2: Check current church availability"""
    print_test("Church Availability API")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/churches/availability")
            if response.status_code == 200:
                print_success("Church availability endpoint is working")
                data = response.json()
                print(f"{YELLOW}Total churches: {data['summary']['total_churches']}{RESET}")
                print(f"{YELLOW}Locked churches: {data['summary']['locked_churches']}{RESET}")
                print(f"{YELLOW}Available churches: {data['summary']['available_churches']}{RESET}")
                return True
            else:
                print_error("Church availability endpoint failed")
                print_response(response)
                return False
        except Exception as e:
            print_error(f"Church availability endpoint error: {e}")
            return False


async def test_single_church_multi_teams():
    """Test 3: Try to register 3 teams for the same church"""
    print_test("Church Team Limit Enforcement (Register Teams for Same Church)")
    
    church_name = "Test Church"
    print_info(f"Testing with church: {church_name}")
    
    # Create temporary files for upload
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy files
        pastor_file = os.path.join(tmpdir, "pastor_letter.pdf")
        receipt_file = os.path.join(tmpdir, "payment_receipt.pdf")
        photo_file = os.path.join(tmpdir, "group_photo.jpg")
        
        with open(pastor_file, "wb") as f:
            f.write(b"DUMMY PDF CONTENT FOR PASTOR LETTER" * 100)
        with open(receipt_file, "wb") as f:
            f.write(b"DUMMY PDF CONTENT FOR PAYMENT" * 100)
        with open(photo_file, "wb") as f:
            f.write(b"DUMMY JPEG DATA" * 100)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Team 1 - Should succeed
            print_info("\nRegistering Team 1 for the church...")
            
            form_data = {
                "team_name": "Team Alpha",
                "church_name": church_name,
                "captain_name": "Captain One",
                "captain_phone": "9876543210",
                "captain_email": "captain1@test.com",
                "captain_whatsapp": "9876543210",
                "vice_name": "Vice Captain One",
                "vice_phone": "9876543211",
                "vice_email": "vice1@test.com",
                "vice_whatsapp": "9876543211",
            }
            
            # Add 11 players
            for i in range(11):
                form_data[f"player_{i}_name"] = f"Player {i+1}"
                form_data[f"player_{i}_role"] = "Batsman"
            
            # Add file uploads
            files = {
                "pastor_letter": ("pastor_letter.pdf", open(pastor_file, "rb"), "application/pdf"),
                "payment_receipt": ("payment_receipt.pdf", open(receipt_file, "rb"), "application/pdf"),
                "group_photo": ("group_photo.jpg", open(photo_file, "rb"), "image/jpeg"),
            }
            
            response = await client.post(
                f"{BASE_URL}/api/register/team",
                data=form_data,
                files=files
            )
            
            # Close files
            for file_info in files.values():
                file_info[1].close()
            
            if response.status_code == 200:
                print_success("Team 1 registered successfully (1/2)")
                try:
                    print_info(f"Response: {response.json().get('message', 'Team registered')}")
                except:
                    print_info(f"Response: Team registered successfully")
            else:
                print_error(f"Team 1 registration failed with status {response.status_code}")
                print_response(response)
                return False
            
            # Team 2 - Should succeed
            print_info("\nRegistering Team 2 for the same church...")
            
            form_data = {
                "team_name": "Team Beta",
                "church_name": church_name,
                "captain_name": "Captain Two",
                "captain_phone": "9876543212",
                "captain_email": "captain2@test.com",
                "captain_whatsapp": "9876543212",
                "vice_name": "Vice Captain Two",
                "vice_phone": "9876543213",
                "vice_email": "vice2@test.com",
                "vice_whatsapp": "9876543213",
            }
            
            # Add 11 players
            for i in range(11):
                form_data[f"player_{i}_name"] = f"Player {i+1}"
                form_data[f"player_{i}_role"] = "Batsman"
            
            # Create new file handles
            files = {
                "pastor_letter": ("pastor_letter.pdf", open(pastor_file, "rb"), "application/pdf"),
                "payment_receipt": ("payment_receipt.pdf", open(receipt_file, "rb"), "application/pdf"),
                "group_photo": ("group_photo.jpg", open(photo_file, "rb"), "image/jpeg"),
            }
            
            response = await client.post(
                f"{BASE_URL}/api/register/team",
                data=form_data,
                files=files
            )
            
            # Close files
            for file_info in files.values():
                file_info[1].close()
            
            if response.status_code == 200:
                print_success("Team 2 registered successfully (2/2)")
                try:
                    print_info(f"Response: {response.json().get('message', 'Team registered')}")
                except:
                    print_info(f"Response: Team registered successfully")
            else:
                print_error(f"Team 2 registration failed with status {response.status_code}")
                print_response(response)
                return False
            
            # Team 3 - Should FAIL with 400
            print_info("\nAttempting to register Team 3 (should be rejected)...")
            
            form_data = {
                "team_name": "Team Gamma",
                "church_name": church_name,
                "captain_name": "Captain Three",
                "captain_phone": "9876543214",
                "captain_email": "captain3@test.com",
                "captain_whatsapp": "9876543214",
                "vice_name": "Vice Captain Three",
                "vice_phone": "9876543215",
                "vice_email": "vice3@test.com",
                "vice_whatsapp": "9876543215",
            }
            
            # Add 11 players
            for i in range(11):
                form_data[f"player_{i}_name"] = f"Player {i+1}"
                form_data[f"player_{i}_role"] = "Batsman"
            
            # Create new file handles
            files = {
                "pastor_letter": ("pastor_letter.pdf", open(pastor_file, "rb"), "application/pdf"),
                "payment_receipt": ("payment_receipt.pdf", open(receipt_file, "rb"), "application/pdf"),
                "group_photo": ("group_photo.jpg", open(photo_file, "rb"), "image/jpeg"),
            }
            
            response = await client.post(
                f"{BASE_URL}/api/register/team",
                data=form_data,
                files=files
            )
            
            # Close files
            for file_info in files.values():
                file_info[1].close()
            
            if response.status_code == 400:
                print_success("Team 3 CORRECTLY REJECTED with 400 Bad Request")
                try:
                    error_msg = response.json().get('detail', '')
                except:
                    error_msg = response.text
                print_info(f"Error message: {error_msg}")
                
                # Verify it mentions church limit
                if "Maximum 2 teams" in str(error_msg) or "church" in str(error_msg).lower():
                    print_success("Error message correctly mentions church team limit")
                    return True
                else:
                    print_error("Error message doesn't mention church limit")
                    print_error(f"Got: {error_msg}")
                    return False
            else:
                print_error(f"Team 3 should have been rejected but got status {response.status_code}")
                print_response(response)
                return False


async def test_church_availability_after_registration():
    """Test 4: Check church availability after registrations"""
    print_test("Church Availability After Registrations")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/churches/availability")
            if response.status_code == 200:
                print_success("Church availability endpoint is working")
                data = response.json()
                
                # Find our test church
                test_churches = [c for c in data['churches'] if 'Test Church' in c['church_name']]
                
                if test_churches:
                    for church in test_churches:
                        print_info(f"\nChurch: {church['church_name']}")
                        print_info(f"  Teams: {church['team_count']}/2")
                        print_info(f"  Locked: {church['locked']}")
                        
                        if church['team_count'] >= 2 and church['locked']:
                            print_success("Church correctly locked (2 teams registered)")
                        elif church['team_count'] == 2:
                            print_success("Church has 2 teams registered")
                else:
                    print_info("No test churches found yet (this is normal for first run)")
                
                return True
            else:
                print_error("Church availability endpoint failed")
                print_response(response)
                return False
        except Exception as e:
            print_error(f"Church availability endpoint error: {e}")
            return False


async def main():
    """Run all tests"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}CHURCH TEAM LIMIT FEATURE TEST SUITE{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    results = {
        "Health Check": await test_health(),
        "Church Availability (Initial)": await test_church_availability(),
        "Team Limit Enforcement": await test_single_church_multi_teams(),
        "Church Availability (After)": await test_church_availability_after_registration(),
    }
    
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}TEST SUMMARY{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n{BOLD}Total: {passed}/{total} tests passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}{BOLD}*** ALL TESTS PASSED! Feature is working correctly. ***{RESET}\n")
    else:
        print(f"{RED}{BOLD}*** Some tests failed. Please review the output above.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
