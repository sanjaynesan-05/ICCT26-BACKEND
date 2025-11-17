"""
Test the FIXED multipart endpoint at /api/register/team/multipart
"""
import requests

print("\n" + "=" * 70)
print("🏏 TESTING /api/register/team/multipart (FIXED)")
print("=" * 70)

form_data = {
    "team_name": "Fixed Test Warriors",
    "church_name": "Fixed Test Church",
    "captain_name": "Fixed Captain",
    "captain_phone": "1111111111",
    "captain_email": "fixed@test.com",
    "captain_whatsapp": "1111111111",
    "captain_aadhar_no": "111111111111",
    "captain_gender": "Male",
    "vice_name": "Fixed Vice",
    "vice_phone": "2222222222",
    "vice_email": "fixed.vice@test.com",
    "vice_whatsapp": "2222222222",
    "vice_aadhar_no": "222222222222",
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
        print(f"   Vice-Captain: {result.get('vice_captain_name')}")
    else:
        print(f"\n❌ Failed: {response.status_code}")
        print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
