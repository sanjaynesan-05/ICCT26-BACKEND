#!/usr/bin/env python3
"""
Google Sheets and Google Drive Integration Test
Tests file uploads and data storage using rulebook.pdf
"""

import requests
import base64
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
RULEBOOK_PATH = "./rulebook.pdf"

# Test data
TEST_TEAM_DATA = {
    "churchName": "St. Mary's Test Church",
    "teamName": f"Test_Warriors_{datetime.now().strftime('%H%M%S')}",
    "pastorLetter": None,  # Will be filled with base64 PDF
    "captain": {
        "name": "Test Captain",
        "phone": "+91 9876543210",
        "whatsapp": "9876543210",
        "email": "captain@test.com"
    },
    "viceCaptain": {
        "name": "Test Vice Captain",
        "phone": "+91 9876543211",
        "whatsapp": "9876543211",
        "email": "vicecaptain@test.com"
    },
    "players": [
        {
            "name": f"Player {i}",
            "age": 20 + i,
            "phone": f"+91 987654321{i:02d}",
            "role": ["Batsman", "Bowler", "All-Rounder", "Wicket Keeper"][i % 4],
            "aadharFile": None,  # Will be filled with base64 PDF
            "subscriptionFile": None  # Will be filled with base64 PDF
        }
        for i in range(11)  # 11 players
    ],
    "paymentReceipt": None  # Will be filled with base64 PDF
}


def read_file_as_base64(file_path: str, mime_type: str = "application/pdf") -> str:
    """Read a file and convert to base64 with data URI prefix"""
    print(f"📁 Reading file: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_size_kb = len(file_content) / 1024
            print(f"   File size: {file_size_kb:.2f} KB")
            
            base64_content = base64.b64encode(file_content).decode('utf-8')
            data_uri = f"data:{mime_type};base64,{base64_content}"
            print(f"   ✅ Converted to base64 data URI")
            return data_uri
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        raise


def prepare_test_data():
    """Prepare test data with file uploads"""
    print("\n" + "="*60)
    print("PREPARING TEST DATA")
    print("="*60)
    
    # Read rulebook.pdf and use it for all file fields
    print("\n📋 Using rulebook.pdf for test files...")
    pdf_data_uri = read_file_as_base64(RULEBOOK_PATH)
    
    # Assign PDF to all file fields
    TEST_TEAM_DATA["pastorLetter"] = pdf_data_uri
    TEST_TEAM_DATA["paymentReceipt"] = pdf_data_uri
    
    for player in TEST_TEAM_DATA["players"]:
        player["aadharFile"] = pdf_data_uri
        player["subscriptionFile"] = pdf_data_uri
    
    print(f"\n✅ Test data prepared with files:")
    print(f"   - Pastor Letter: rulebook.pdf ✓")
    print(f"   - Payment Receipt: rulebook.pdf ✓")
    print(f"   - {len(TEST_TEAM_DATA['players'])} players × 2 files each = {len(TEST_TEAM_DATA['players']) * 2} files ✓")
    print(f"   - Total files to upload: {len(TEST_TEAM_DATA['players']) * 2 + 2} files")
    
    return TEST_TEAM_DATA


def test_registration():
    """Test team registration endpoint"""
    print("\n" + "="*60)
    print("TESTING REGISTRATION ENDPOINT")
    print("="*60)
    
    print(f"\n📤 Sending registration request to {API_URL}/register/team")
    print(f"   Team: {TEST_TEAM_DATA['teamName']}")
    print(f"   Church: {TEST_TEAM_DATA['churchName']}")
    print(f"   Players: {len(TEST_TEAM_DATA['players'])}")
    print(f"   Files: 13 total (1 pastor + 1 payment + 11 players × 1 aadhar + 11 × 1 subscription)")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_URL}/register/team",
            json=TEST_TEAM_DATA,
            timeout=120  # 2 minutes timeout for file uploads
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ Response received in {elapsed_time:.2f} seconds")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            return True, result, elapsed_time
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            try:
                return False, response.json(), elapsed_time
            except:
                return False, {"error": response.text}, elapsed_time
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Cannot connect to {API_URL}")
        print(f"   Make sure the server is running: python main.py")
        return False, None, 0
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Request took longer than 120 seconds")
        return False, None, 0
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, None, 0


def display_results(success: bool, result: dict, elapsed_time: float):
    """Display and verify test results"""
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    
    if not success:
        print("\n❌ REGISTRATION FAILED")
        return False
    
    print("\n✅ REGISTRATION SUCCESSFUL!\n")
    
    # Debug: Print raw response
    print("📝 Raw Response:")
    print(json.dumps(result, indent=2)[:500] + "..." if len(json.dumps(result, indent=2)) > 500 else json.dumps(result, indent=2))
    print()
    
    # Basic info
    print("📊 Registration Response:")
    print(f"   Team ID: {result.get('team_id', 'N/A')}")
    print(f"   Players Count: {result.get('players_count', 'N/A')}")
    print(f"   Sheet Name: {result.get('sheet_name', 'N/A')}")
    print(f"   Processing Time: {elapsed_time:.2f} seconds")
    
    # Google Sheets info
    print(f"\n📄 Google Sheets:")
    print(f"   Sheet Link: {result.get('sheet_link', 'N/A')}")
    
    # Google Drive uploads
    drive_result = result.get('drive_upload', {})
    if drive_result.get('success'):
        print(f"\n📁 Google Drive Upload:")
        print(f"   Status: ✅ SUCCESS")
        print(f"   Team Folder ID: {drive_result.get('team_folder_id', 'N/A')}")
        print(f"   Message: {drive_result.get('message', 'N/A')}")
        
        # Analyze uploads
        uploads = drive_result.get('uploads', [])
        print(f"\n📤 File Uploads ({len(uploads)} total):")
        
        # Summary by type
        upload_types = {}
        for upload in uploads:
            upload_type = upload.get('type', 'unknown')
            success = upload.get('success', False)
            
            if upload_type not in upload_types:
                upload_types[upload_type] = {'success': 0, 'failed': 0}
            
            if success:
                upload_types[upload_type]['success'] += 1
            else:
                upload_types[upload_type]['failed'] += 1
        
        for file_type, counts in upload_types.items():
            total = counts['success'] + counts['failed']
            status = "✅" if counts['failed'] == 0 else "⚠️"
            print(f"   {status} {file_type.replace('_', ' ').title()}: {counts['success']}/{total}")
        
        # Show detailed file uploads
        print(f"\n📋 Uploaded Files Details:")
        for upload in uploads:
            if upload.get('success'):
                file_type = upload.get('type', 'unknown')
                player = upload.get('player', '')
                file_id = upload.get('file_id', 'N/A')[:20] + "..."
                
                if player:
                    print(f"   ✅ {file_type.title()} - {player}: {file_id}")
                else:
                    print(f"   ✅ {file_type.title()}: {file_id}")
            else:
                print(f"   ❌ Error: {upload.get('error', 'Unknown error')}")
        
        return True
    else:
        print(f"\n📁 Google Drive Upload:")
        print(f"   Status: ❌ FAILED")
        print(f"   Message: {drive_result.get('message', 'N/A')}")
        print(f"   Error Details: {drive_result}")
        return False


def print_verification_steps():
    """Print steps to manually verify in Google Sheets and Drive"""
    print("\n" + "="*60)
    print("MANUAL VERIFICATION STEPS")
    print("="*60)
    
    print("\n📄 Verify Google Sheets:")
    print("   1. Open your Google Sheets file")
    print("   2. Look for new sheet tab: 'ICCT26-0XX_Test_Warriors_HHMMSS'")
    print("   3. Check that sheet contains:")
    print("      - Team information section")
    print("      - Captain & Vice-Captain details")
    print("      - Uploaded files section with Drive links")
    print("      - Players table with all 11 players")
    print("      - File links for each player (Aadhar + Subscription)")
    print("   4. Check 'Teams_Index' sheet for new entry")
    
    print("\n📁 Verify Google Drive:")
    print("   1. Open your Google Drive folder: 'ICCT26 Team Registrations'")
    print("   2. Look for new folder: 'ICCT26-0XX_Test_Warriors_HHMMSS'")
    print("   3. Inside folder, verify files:")
    print("      - ICCT26-0XX_Pastor_Letter.pdf ✓")
    print("      - ICCT26-0XX_Payment_Receipt.pdf ✓")
    print("      - ICCT26-0XX_Player1_Player_1_Aadhar.pdf ✓")
    print("      - ICCT26-0XX_Player1_Player_1_Subscription.pdf ✓")
    print("      - ... (for all 11 players)")
    
    print("\n✅ If all checks pass, both Google Sheets and Drive integration is working!")


def main():
    """Main test function"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Google Sheets & Drive Integration Test".center(58) + "║")
    print("║" + "  Using rulebook.pdf for file uploads".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Step 1: Prepare test data
    try:
        test_data = prepare_test_data()
    except Exception as e:
        print(f"\n❌ Failed to prepare test data: {e}")
        return False
    
    # Step 2: Send registration request
    success, result, elapsed_time = test_registration()
    
    # Step 3: Display results
    if success:
        verification_ok = display_results(success, result, elapsed_time)
        print_verification_steps()
        return verification_ok
    else:
        print("\n❌ TEST FAILED - Could not complete registration")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure server is running: python main.py")
        print("   2. Check server console for errors")
        print("   3. Verify .env file has all required credentials")
        print("   4. Check internet connection")
        return False


if __name__ == "__main__":
    import sys
    
    print("\n🚀 Starting test...")
    print(f"   Server URL: {API_URL}")
    print(f"   Test File: {RULEBOOK_PATH}")
    
    # Check if file exists
    import os
    if not os.path.exists(RULEBOOK_PATH):
        print(f"\n❌ Error: {RULEBOOK_PATH} not found!")
        print("   Please make sure rulebook.pdf is in the current directory")
        sys.exit(1)
    
    success = main()
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED - Check errors above")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)
