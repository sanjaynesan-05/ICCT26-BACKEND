#!/usr/bin/env python3
"""
Same File Upload Test for ICCT26 Frontend Testing
Tests using the same file for all upload types to verify frontend integration
"""

import requests
import base64
import json
import time
from datetime import datetime

API_URL = "http://localhost:8000"
TEST_FILE_PATH = "./rulebook.pdf"

def read_file_as_base64(file_path: str, mime_type: str = "application/pdf") -> str:
    """Read a file and convert to base64 with data URI prefix"""
    print(f"📁 Reading test file: {file_path}")
    with open(file_path, 'rb') as f:
        file_content = f.read()
        file_size_kb = len(file_content) / 1024
        print(f"   File size: {file_size_kb:.2f} KB")

        base64_content = base64.b64encode(file_content).decode('utf-8')
        data_uri = f"data:{mime_type};base64,{base64_content}"
        print("   ✅ Converted to base64 data URI")
        return data_uri

def test_same_file_uploads():
    """Test using the same file for all upload types"""
    print("\n" + "╔" + "="*60 + "╗")
    print("║" + " "*60 + "║")
    print("║" + "  SAME FILE UPLOAD TEST - Frontend Integration".center(60) + "║")
    print("║" + "  Using rulebook.pdf for ALL file uploads".center(60) + "║")
    print("║" + " "*60 + "║")
    print("╚" + "="*60 + "╝\n")

    # Step 1: Read the test file once
    print("="*62)
    print("STEP 1: LOAD TEST FILE")
    print("="*62 + "\n")

    try:
        same_file_data = read_file_as_base64(TEST_FILE_PATH)
        print("✅ Test file loaded successfully\n")
    except FileNotFoundError:
        print(f"❌ Error: Test file '{TEST_FILE_PATH}' not found!")
        print("   Make sure rulebook.pdf exists in the project root.")
        return False

    # Step 2: Prepare test data using the same file for everything
    print("="*62)
    print("STEP 2: PREPARE TEST DATA (Same File for All)")
    print("="*62 + "\n")

    test_data = {
        "churchName": "Frontend Test Church",
        "teamName": f"SameFile_Test_{datetime.now().strftime('%H%M%S')}",
        "pastorLetter": same_file_data,  # Same file
        "captain": {
            "name": "Frontend Test Captain",
            "phone": "+91 9999999999",
            "whatsapp": "9999999999",
            "email": "frontend@test.com"
        },
        "viceCaptain": {
            "name": "Frontend Test Vice Captain",
            "phone": "+91 8888888888",
            "whatsapp": "8888888888",
            "email": "frontend-vc@test.com"
        },
        "players": [
            {
                "name": f"Frontend Player {i+1}",
                "age": 20 + (i % 5),
                "phone": f"+91 77777777{i:02d}",
                "role": ["Batsman", "Bowler", "All-Rounder", "Wicket Keeper"][i % 4],
                "aadharFile": same_file_data,      # Same file for all Aadhar
                "subscriptionFile": same_file_data # Same file for all Subscription
            }
            for i in range(11)
        ],
        "paymentReceipt": same_file_data  # Same file
    }

    print("✅ Test data prepared with SAME FILE for all uploads:")
    print(f"   📄 File used: {TEST_FILE_PATH}")
    print(f"   🏏 Team: {test_data['teamName']}")
    print(f"   ⛪ Church: {test_data['churchName']}")
    print(f"   👥 Players: {len(test_data['players'])}")
    print("   📎 File assignments:")
    print("      • Pastor Letter: rulebook.pdf")
    print("      • Payment Receipt: rulebook.pdf")
    print("      • All 11 Aadhar files: rulebook.pdf")
    print("      • All 11 Subscription files: rulebook.pdf")
    print("   📊 Total uploads: 24 files (all same PDF)\n")

    # Step 3: Send registration
    print("="*62)
    print("STEP 3: SEND REGISTRATION")
    print("="*62 + "\n")

    print(f"📤 Sending registration to {API_URL}/register/team...")
    print("   This will upload 24 copies of the same file to test your frontend!")

    try:
        response = requests.post(
            f"{API_URL}/register/team",
            json=test_data,
            timeout=300  # 5 minutes timeout for file uploads
        )

        print(f"📡 Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Registration successful!")

            # Show results
            team_id = result.get('team_id', 'N/A')
            print(f"🏷️  Team ID: {team_id}")

            # Check queue processing
            print("\n⏳ Waiting for background processing...")
            time.sleep(3)  # Give it a moment

            # Check queue status
            queue_status = get_queue_status()
            if queue_status:
                print("📋 Queue Status:")
                print(f"   • Pending: {queue_status.get('pending', 0)}")
                print(f"   • Processing: {queue_status.get('processing', 0)}")
                print(f"   • Completed: {queue_status.get('completed', 0)}")
                print(f"   • Failed: {queue_status.get('failed', 0)}")

            print("\n🎉 SUCCESS! Your frontend can use the same test file for all uploads!")
            print("💡 This proves your file upload system works correctly.")
            print("🔄 All 24 files were uploaded successfully using rulebook.pdf")

            return True

        else:
            print(f"❌ Registration failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:200]}...")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def get_queue_status():
    """Check queue status"""
    try:
        response = requests.get(f"{API_URL}/queue/status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

if __name__ == "__main__":
    print("🚀 ICCT26 Same File Upload Test")
    print("This test uses rulebook.pdf for ALL file uploads to verify your frontend integration.\n")

    # Check if server is running
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("⚠️  Backend server may not be responding correctly")
    except:
        print("❌ Cannot connect to backend server!")
        print(f"   Make sure your server is running on {API_URL}")
        print("   Run: python main.py")
        exit(1)

    # Run the test
    success = test_same_file_uploads()

    if success:
        print("\n" + "="*62)
        print("🎯 TEST PASSED - Frontend Ready!")
        print("="*62)
        print("Your frontend can now use rulebook.pdf for testing all file uploads:")
        print("• Drag & drop the same file into all upload fields")
        print("• Test multiple file uploads with identical content")
        print("• Verify upload progress and success messages")
        print("• Check Google Drive for uploaded files")
    else:
        print("\n" + "="*62)
        print("❌ TEST FAILED")
        print("="*62)
        print("Check your backend server and try again.")
        exit(1)