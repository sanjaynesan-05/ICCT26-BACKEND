#!/usr/bin/env python3
"""
Simple test to verify the registration endpoint and background processing
"""
import requests
import base64
import time
import json

# Read test file
print("📁 Reading test file...")
with open('rulebook.pdf', 'rb') as f:
    content = f.read()
    base64_data = base64.b64encode(content).decode('utf-8')
    file_data = f'data:application/pdf;base64,{base64_data}'

print(f"✅ File size: {len(content) / 1024:.2f} KB")

# Create test data with 11 players
timestamp = str(int(time.time()) % 10000)
test_data = {
    'churchName': 'Test Church',
    'teamName': f'QA_Test_{timestamp}',
    'pastorLetter': file_data,
    'captain': {
        'name': 'Test Captain',
        'phone': '+919876543210',
        'whatsapp': '9876543210',
        'email': 'captain@test.com'
    },
    'viceCaptain': {
        'name': 'Test Vice Captain', 
        'phone': '+919876543211',
        'whatsapp': '9876543211',
        'email': 'vice@test.com'
    },
    'players': [
        {
            'name': f'Player {i+1}',
            'age': 20 + i,
            'phone': f'+9198765432{i:02d}',
            'role': ['Batsman', 'Bowler', 'All-Rounder', 'Wicket Keeper'][i % 4],
            'aadharFile': file_data,
            'subscriptionFile': file_data
        }
        for i in range(11)
    ],
    'paymentReceipt': file_data
}

print(f"\n📝 Test data prepared:")
print(f"   Team: {test_data['teamName']}")
print(f"   Church: {test_data['churchName']}")
print(f"   Players: {len(test_data['players'])}")
print(f"   Files: {len([p for p in test_data['players']]) * 2 + 2}")

print(f"\n📤 Sending registration to http://localhost:8000/register/team...")
try:
    start_time = time.time()
    response = requests.post(
        'http://localhost:8000/register/team',
        json=test_data,
        timeout=30
    )
    elapsed = time.time() - start_time
    
    print(f"✅ Response received in {elapsed:.2f} seconds")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ REGISTRATION SUCCESSFUL!")
        print(f"   Team Name: {result['data']['teamName']}")
        print(f"   Captain: {result['data']['captainName']}")
        print(f"   Status: {result['status']}")
        print(f"   Queued At: {result['data']['queuedAt']}")
        
        print(f"\n⏳ Waiting for background processing (5 seconds)...")
        time.sleep(5)
        
        print(f"\n✅ Test complete!")
        print(f"   Check Google Sheets for: ICCT26-0XX_{test_data['teamName']}")
        print(f"   Check Google Drive for folder: ICCT26-0XX_{test_data['teamName']}")
        print(f"   Check email for confirmation")
    else:
        print(f"❌ Error: {response.text}")
        
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection Error: {e}")
    print(f"   Make sure the server is running: python main.py")
except Exception as e:
    print(f"❌ Error: {e}")
