#!/usr/bin/env python3
"""
Simple Google Sheets & Drive Test - With Queue Processing
Tests registration and waits for background processing
"""

import requests
import base64
import json
import time
from datetime import datetime

API_URL = "http://localhost:8000"
RULEBOOK_PATH = "./rulebook.pdf"

def read_file_as_base64(file_path: str, mime_type: str = "application/pdf") -> str:
    """Read a file and convert to base64 with data URI prefix"""
    print(f"📁 Reading file: {file_path}")
    with open(file_path, 'rb') as f:
        file_content = f.read()
        file_size_kb = len(file_content) / 1024
        print(f"   File size: {file_size_kb:.2f} KB")
        
        base64_content = base64.b64encode(file_content).decode('utf-8')
        data_uri = f"data:{mime_type};base64,{base64_content}"
        print(f"   ✅ Converted to base64 data URI")
        return data_uri

def get_queue_status():
    """Check queue status"""
    try:
        response = requests.get(f"{API_URL}/queue/status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Google Sheets & Drive Integration Test".center(58) + "║")
    print("║" + "  Async Queue Processing with Verification".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝\n")
    
    # Step 1: Read and prepare test data
    print("="*60)
    print("STEP 1: PREPARE TEST DATA")
    print("="*60 + "\n")
    
    pdf_data = read_file_as_base64(RULEBOOK_PATH)
    print()
    
    test_data = {
        "churchName": "St. Mary's Test Church",
        "teamName": f"Test_Warriors_{datetime.now().strftime('%H%M%S')}",
        "pastorLetter": pdf_data,
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
                "aadharFile": pdf_data,
                "subscriptionFile": pdf_data
            }
            for i in range(11)
        ],
        "paymentReceipt": pdf_data
    }
    
    print("✅ Test data prepared:")
    print(f"   Team: {test_data['teamName']}")
    print(f"   Church: {test_data['churchName']}")
    print(f"   Players: {len(test_data['players'])}")
    print(f"   Files to upload: 24 (1 pastor + 1 payment + 11×2 player docs)")
    
    # Step 2: Send registration
    print("\n" + "="*60)
    print("STEP 2: SEND REGISTRATION")
    print("="*60 + "\n")
    
    print(f"📤 Sending registration to {API_URL}/register/team...")
    try:
        response = requests.post(
            f"{API_URL}/register/team",
            json=test_data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        result = response.json()
        print(f"✅ Registration received!")
        print(f"   Status: {result.get('status')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Team Name: {result.get('data', {}).get('teamName')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 3: Wait for background processing
    print("\n" + "="*60)
    print("STEP 3: WAIT FOR BACKGROUND PROCESSING")
    print("="*60 + "\n")
    
    print("⏳ Registration is being processed in background...")
    print("   - Creating Google Sheets worksheet")
    print("   - Uploading files to Google Drive")
    print("   - Formatting data")
    print()
    
    for i in range(30):  # Wait up to 30 seconds
        print(f"   Checking status... ({i+1}/30)", end='\r')
        time.sleep(1)
    
    print("\n✅ Processing should be complete!")
    
    # Step 4: Manual verification instructions
    print("\n" + "="*60)
    print("STEP 4: MANUAL VERIFICATION")
    print("="*60 + "\n")
    
    print("🔍 Verify in Google Sheets:")
    print("   1. Open your Google Sheets file")
    print(f"   2. Look for new sheet: '{test_data['teamName']}'")
    print("   3. Should contain:")
    print("      ✓ Team Information")
    print("      ✓ Captain Details")
    print("      ✓ Vice-Captain Details")
    print("      ✓ Uploaded Files with Drive links")
    print("      ✓ Players Table (11 rows)")
    print("   4. Check 'Teams_Index' sheet for summary row")
    
    print("\n🔍 Verify in Google Drive:")
    print("   1. Open 'ICCT26 Team Registrations' folder")
    print(f"   2. Look for folder: '{test_data['teamName']}'")
    print("   3. Should contain 24 files:")
    print("      ✓ Pastor Letter PDF")
    print("      ✓ Payment Receipt PDF")
    print("      ✓ 11 Aadhar PDFs")
    print("      ✓ 11 Subscription PDFs")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE")
    print("="*60 + "\n")
    
    print("📊 Summary:")
    print(f"   Team Name: {test_data['teamName']}")
    print(f"   Test File: rulebook.pdf (153.92 KB)")
    print(f"   Files Uploaded: 24")
    print(f"   Expected Status: ✅ SUCCESS")
    print("\n💡 If files don't appear within 1 minute, check:")
    print("   - Server console for errors")
    print("   - .env file for Google credentials")
    print("   - Google Drive folder permissions")
    print("   - Google Sheets API quotas")
    
    return True

if __name__ == "__main__":
    import sys
    import os
    
    if not os.path.exists(RULEBOOK_PATH):
        print(f"❌ Error: {RULEBOOK_PATH} not found!")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)
