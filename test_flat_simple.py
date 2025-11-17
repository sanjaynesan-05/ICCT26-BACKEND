"""
SIMPLE TEST - Check endpoint accepts multipart data
"""
import requests

print("\n🧪 Testing /api/register/team/flat endpoint structure...")

# Test with minimal data
form_data = {
    "team_name": "Test Team",
    "church_name": "Test Church",
    "captain_name": "Test Captain",
    "captain_phone": "1234567890",
    "captain_email": "test@test.com",
    "captain_whatsapp": "1234567890",
    "captain_aadhar_no": "123456789012",
    "captain_gender": "Male",
    "vice_name": "Test Vice",
    "vice_phone": "1234567891",
    "vice_email": "vice@test.com",
    "vice_whatsapp": "1234567891",
    "vice_aadhar_no": "123456789013",
    "vice_gender": "Female",
}

# Empty file placeholders
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
        "http://localhost:8000/api/register/team/flat",
        data=form_data,
        files=files,
        timeout=10
    )
    
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Response: {response.json()}")
    
except requests.exceptions.Timeout:
    print("❌ Request timed out - Cloudinary upload might be slow")
except Exception as e:
    print(f"❌ Error: {e}")
