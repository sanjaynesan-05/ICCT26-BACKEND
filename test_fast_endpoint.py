"""
TEST FAST ENDPOINT - No Cloudinary (instant response)
"""
import requests

print("\n🧪 Testing FAST endpoint /api/register/team/flat/nocloud...")

form_data = {
    "team_name": "Fast Test Team",
    "church_name": "Fast Test Church",
    "captain_name": "Fast Captain",
    "captain_phone": "1234567890",
    "captain_email": "sanjaynesan007@gmail.com",
    "captain_whatsapp": "1234567890",
    "captain_aadhar_no": "123456789012",
    "captain_gender": "Male",
    "vice_name": "Fast Vice",
    "vice_phone": "1234567891",
    "vice_email": "vice@test.com",
    "vice_whatsapp": "1234567891",
    "vice_aadhar_no": "123456789013",
    "vice_gender": "Female",
}

files = {
    "pastor_letter": ("test.pdf", b"test", "application/pdf"),
    "captain_aadhar": ("test.pdf", b"test", "application/pdf"),
    "captain_subscription": ("test.pdf", b"test", "application/pdf"),
    "vice_aadhar": ("test.pdf", b"test", "application/pdf"),
    "vice_subscription": ("test.pdf", b"test", "application/pdf"),
}

try:
    response = requests.post(
        "http://localhost:8000/api/register/team/flat/nocloud",
        data=form_data,
        files=files,
        timeout=5
    )
    
    print(f"📊 Status: {response.status_code}")
    result = response.json()
    
    if response.status_code == 201:
        print("\n✅ REGISTRATION SUCCESSFUL!")
        print(f"   Team ID: {result.get('team_id')}")
        print(f"   Team Name: {result.get('team_name')}")
        print(f"   Captain: {result.get('captain_name')}")
        print(f"   Players: {result.get('player_count')}")
        print(f"\n   Note: {result.get('note')}")
        
        print("\n" + "=" * 70)
        print("✅ FLAT MULTIPART ENDPOINT WORKS!")
        print("=" * 70)
        print("\n💡 Frontend can now use:")
        print("   POST /api/register/team/flat")
        print("   Content-Type: multipart/form-data")
        print("   With flattened field names (no nested objects)")
        
    else:
        print(f"\n❌ Failed: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
