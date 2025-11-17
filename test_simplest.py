"""
TEST SIMPLEST ENDPOINT - Just form parsing, no DB, no Cloudinary
"""
import requests

print("\n🧪 Testing SIMPLEST endpoint /api/register/team/test...")

form_data = {
    "team_name": "Simple Test Team",
    "church_name": "Simple Test Church",
    "captain_name": "Simple Captain",
    "captain_phone": "1234567890",
    "captain_email": "sanjaynesan007@gmail.com",
    "captain_whatsapp": "1234567890",
    "captain_aadhar_no": "123456789012",
    "captain_gender": "Male",
    "vice_name": "Simple Vice",
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
    print("📤 Sending request...")
    response = requests.post(
        "http://localhost:8000/api/register/team/test",
        data=form_data,
        files=files,
        timeout=10
    )
    
    print(f"📊 Status: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print("\n✅ FORM PARSING WORKS!")
        print(f"   Team: {result['data']['team']}")
        print(f"   Church: {result['data']['church']}")
        print(f"   Captain: {result['data']['captain']} ({result['data']['captain_email']})")
        print(f"   Vice: {result['data']['vice']} ({result['data']['vice_email']})")
        print(f"   Files received: {len(result['data']['files'])} files")
        
        print("\n" + "=" * 70)
        print("✅ MULTIPART/FORM-DATA PARSING WORKS!")
        print("=" * 70)
        print("\n📝 This confirms:")
        print("   ✓ FastAPI accepts multipart/form-data correctly")
        print("   ✓ Form fields parse correctly")
        print("   ✓ Files are received")
        print("   ✓ No 422 validation errors")
        
    else:
        print(f"\n❌ Failed: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
