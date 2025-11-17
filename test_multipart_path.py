"""
PRODUCTION TEST - Using a different path to avoid conflicts
"""
import requests

print("\n" + "=" * 70)
print("🏏 PRODUCTION TEST - /api/register/team/multipart")
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
    print("\n📤 Sending to /api/register/team/multipart...")
    response = requests.post(
        "http://localhost:8000/api/register/team/multipart",
        data=form_data,
        files=files,
        timeout=15
    )
    
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("\n✅ SUCCESS!")
        print(f"   Team ID: {result.get('team_id')}")
        print(f"   Team: {result.get('team_name')}")
        print(f"   Captain: {result.get('captain_name')}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.json())
    
except Exception as e:
    print(f"❌ Error: {e}")
