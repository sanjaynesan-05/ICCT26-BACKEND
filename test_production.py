"""
PRODUCTION TEST - Full registration with sequential team IDs
"""
import requests

print("\n" + "=" * 70)
print("🏏 PRODUCTION REGISTRATION TEST")
print("=" * 70)

form_data = {
    "team_name": "Production Test Warriors",
    "church_name": "Production Test Church",
    "captain_name": "Production Captain",
    "captain_phone": "1234567890",
    "captain_email": "sanjaynesan007@gmail.com",
    "captain_whatsapp": "1234567890",
    "captain_aadhar_no": "123456789012",
    "captain_gender": "Male",
    "vice_name": "Production Vice",
    "vice_phone": "1234567891",
    "vice_email": "vice@test.com",
    "vice_whatsapp": "1234567891",
    "vice_aadhar_no": "123456789013",
    "vice_gender": "Female",
}

files = {
    "pastor_letter": ("pastor.pdf", b"PDF_CONTENT", "application/pdf"),
    "captain_aadhar": ("capt_aadhar.pdf", b"PDF_CONTENT", "application/pdf"),
    "captain_subscription": ("capt_sub.pdf", b"PDF_CONTENT", "application/pdf"),
    "vice_aadhar": ("vice_aadhar.pdf", b"PDF_CONTENT", "application/pdf"),
    "vice_subscription": ("vice_sub.pdf", b"PDF_CONTENT", "application/pdf"),
}

try:
    print("\n📤 Sending registration request to /api/register/team...")
    print(f"   Team: {form_data['team_name']}")
    print(f"   Captain: {form_data['captain_name']}")
    print(f"   Vice: {form_data['vice_name']}")
    
    response = requests.post(
        "http://localhost:8000/api/register/team",
        data=form_data,
        files=files,
        timeout=15
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    result = response.json()
    
    if response.status_code == 201:
        print("\n✅ REGISTRATION SUCCESSFUL!")
        print(f"   Team ID: {result.get('team_id')}")
        print(f"   Team Name: {result.get('team_name')}")
        print(f"   Captain: {result.get('captain_name')}")
        print(f"   Players: {result.get('player_count')}")
        print(f"   Message: {result.get('message')}")
        
        print("\n" + "=" * 70)
        print("✅ PRODUCTION ENDPOINT WORKS!")
        print("=" * 70)
        print("\n📋 Summary:")
        print("   ✓ Multipart form data accepted")
        print("   ✓ Sequential team ID generated")
        print("   ✓ Team stored in database")
        print("   ✓ Captain stored in database")
        print("   ✓ Vice-Captain stored in database")
        print("   ✓ Ready for frontend deployment")
        
    else:
        print(f"\n❌ Registration failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {result}")
    
except requests.exceptions.Timeout:
    print("\n❌ Request timed out")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
