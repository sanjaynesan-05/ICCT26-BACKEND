#!/usr/bin/env python3
"""
Frontend File Upload Helper for ICCT26
Generates test data for frontend testing with same file for all uploads
"""

import base64
import json
from datetime import datetime

def create_frontend_test_data():
    """Create test data that frontend can use for testing"""

    # Read the test file
    with open('./rulebook.pdf', 'rb') as f:
        file_content = f.read()
        base64_content = base64.b64encode(file_content).decode('utf-8')
        same_file_data = f"data:application/pdf;base64,{base64_content}"

    # Create test data
    test_data = {
        "churchName": "Frontend Test Church",
        "teamName": f"Frontend_Test_{datetime.now().strftime('%H%M%S')}",
        "pastorLetter": same_file_data,
        "captain": {
            "name": "Test Captain",
            "phone": "+91 9999999999",
            "whatsapp": "9999999999",
            "email": "captain@test.com"
        },
        "viceCaptain": {
            "name": "Test Vice Captain",
            "phone": "+91 8888888888",
            "whatsapp": "8888888888",
            "email": "vicecaptain@test.com"
        },
        "players": [
            {
                "name": f"Player {i+1}",
                "age": 20 + (i % 5),
                "phone": f"+91 77777777{i:02d}",
                "role": ["Batsman", "Bowler", "All-Rounder", "Wicket Keeper"][i % 4],
                "aadharFile": same_file_data,
                "subscriptionFile": same_file_data
            }
            for i in range(11)
        ],
        "paymentReceipt": same_file_data
    }

    return test_data

def save_test_data_to_file():
    """Save test data to JSON file for frontend use"""
    test_data = create_frontend_test_data()

    with open('frontend_test_data.json', 'w') as f:
        json.dump(test_data, f, indent=2)

    print("✅ Frontend test data saved to: frontend_test_data.json")
    print("\n📋 File Upload Summary:")
    print("   • 1 Pastor Letter file")
    print("   • 1 Payment Receipt file")
    print("   • 11 Aadhar Card files")
    print("   • 11 Subscription Card files")
    print("   📊 Total: 24 files (all using rulebook.pdf)")

    print("\n🎯 Frontend Testing Instructions:")
    print("   1. Load frontend_test_data.json in your frontend")
    print("   2. Use rulebook.pdf for ALL file upload fields")
    print("   3. Submit the registration")
    print("   4. Verify all 24 files upload successfully")
    print("   5. Check Google Drive for uploaded files")

if __name__ == "__main__":
    print("🛠️  ICCT26 Frontend Test Data Generator")
    print("Generating test data with same file for all uploads...\n")

    try:
        save_test_data_to_file()
    except FileNotFoundError:
        print("❌ Error: rulebook.pdf not found!")
        print("   Make sure rulebook.pdf exists in the project root.")
    except Exception as e:
        print(f"❌ Error: {e}")