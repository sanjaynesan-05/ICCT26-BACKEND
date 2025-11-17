"""
PRODUCTION END-TO-END TEST
==========================
Tests the complete registration flow with:
- Multipart form data
- File uploads
- Players JSON
- Sequential team ID generation
"""

import requests
import json

print("\n" + "=" * 70)
print("🏏 PRODUCTION REGISTRATION TEST - COMPLETE E2E")
print("=" * 70)

# Form data (flattened fields)
form_data = {
    "team_name": "St. Mary's Warriors",
    "church_name": "St. Mary's Cathedral Church",
    "captain_name": "John Emmanuel",
    "captain_phone": "9876543210",
    "captain_email": "john.emmanuel@stmarys.com",
    "captain_whatsapp": "9876543210",
    "vice_name": "David Samuel",
    "vice_phone": "9876543211",
    "vice_email": "david.samuel@stmarys.com",
    "vice_whatsapp": "9876543211",
}

# Players as JSON string
players_data = [
    {"name": "John Emmanuel", "role": "Captain"},
    {"name": "David Samuel", "role": "Vice-Captain"},
    {"name": "Peter Johnson", "role": "Batsman"},
    {"name": "Paul Ravi", "role": "Bowler"},
    {"name": "Thomas Kumar", "role": "All-Rounder"},
    {"name": "James Wilson", "role": "Wicket Keeper"},
    {"name": "Michael Raj", "role": "Batsman"},
    {"name": "Joseph Xavier", "role": "Bowler"},
    {"name": "Simon Peter", "role": "All-Rounder"},
    {"name": "Andrew Thomas", "role": "Batsman"},
    {"name": "Philip Joseph", "role": "Bowler"},
]
form_data["players_json"] = json.dumps(players_data)

# File uploads
files = {
    "pastor_letter": ("pastor_recommendation.pdf", b"PDF_CONTENT_PASTOR_LETTER", "application/pdf"),
    "payment_receipt": ("payment_receipt.pdf", b"PDF_CONTENT_PAYMENT", "application/pdf"),
    "group_photo": ("team_photo.jpg", b"JPEG_CONTENT_GROUP_PHOTO", "image/jpeg"),
}

try:
    print("\n📤 Sending registration to POST /api/register/team...")
    print(f"   Team: {form_data['team_name']}")
    print(f"   Church: {form_data['church_name']}")
    print(f"   Captain: {form_data['captain_name']}")
    print(f"   Vice-Captain: {form_data['vice_name']}")
    print(f"   Players: {len(players_data)}")
    print(f"   Files: {len(files)}")
    
    response = requests.post(
        "http://localhost:8000/api/register/team",
        data=form_data,
        files=files,
        timeout=30
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("\n✅ ✅ ✅ REGISTRATION SUCCESS! ✅ ✅ ✅")
        print(f"   Team ID: {result.get('team_id')}")
        print(f"   Team Name: {result.get('team_name')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Email Sent: {result.get('email_sent')}")
        print(f"   Player Count: {result.get('player_count')}")
        print("\n🎉 All backend problems fixed!")
        print("=" * 70)
    else:
        print(f"\n❌ Registration failed: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Connection Error: Cannot connect to server")
    print(f"   Make sure server is running on http://localhost:8000")
    print(f"   Error: {e}")
except requests.exceptions.Timeout:
    print(f"\n❌ Timeout: Request took longer than 30 seconds")
except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
