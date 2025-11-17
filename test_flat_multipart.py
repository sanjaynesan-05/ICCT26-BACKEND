"""
TEST FLAT MULTIPART REGISTRATION ENDPOINT
==========================================
Tests the new /api/register/team/flat endpoint with flattened form fields.
"""

import requests
from io import BytesIO

BASE_URL = "http://localhost:8000"

print("\n" + "=" * 70)
print("🧪 TESTING FLAT MULTIPART REGISTRATION")
print("=" * 70)

# Create dummy files
def create_dummy_pdf():
    """Create a minimal valid PDF"""
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (Test Document) Tj ET
endstream endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000056 00000 n 
0000000115 00000 n 
0000000214 00000 n 
trailer<</Size 5/Root 1 0 R>>
startxref
306
%%EOF"""
    return BytesIO(pdf_content)

def create_dummy_image():
    """Create a minimal valid image (1x1 GIF)"""
    gif_content = bytes.fromhex('474946383961010001008000000000ffffff21f90401000000002c00000000010001000002024401003b')
    return BytesIO(gif_content)

# Prepare form data
form_data = {
    # Team info
    "team_name": "Flat Test Warriors",
    "church_name": "CSI Flat Test Church Coimbatore",
    
    # Captain info
    "captain_name": "Flat Captain Test",
    "captain_phone": "+919876543210",
    "captain_email": "sanjaynesan007@gmail.com",
    "captain_whatsapp": "919876543210",
    "captain_aadhar_no": "123456789012",
    "captain_gender": "Male",
    
    # Vice-captain info
    "vice_name": "Flat Vice Captain Test",
    "vice_phone": "+919876543211",
    "vice_email": "vice@test.com",
    "vice_whatsapp": "919876543211",
    "vice_aadhar_no": "123456789013",
    "vice_gender": "Female",
}

# Prepare files
files = {
    "pastor_letter": ("pastor.pdf", create_dummy_pdf(), "application/pdf"),
    "payment_receipt": ("receipt.jpg", create_dummy_image(), "image/jpeg"),
    "group_photo": ("group.jpg", create_dummy_image(), "image/jpeg"),
    "captain_aadhar": ("capt_aadhar.pdf", create_dummy_pdf(), "application/pdf"),
    "captain_subscription": ("capt_sub.pdf", create_dummy_pdf(), "application/pdf"),
    "vice_aadhar": ("vice_aadhar.pdf", create_dummy_pdf(), "application/pdf"),
    "vice_subscription": ("vice_sub.pdf", create_dummy_pdf(), "application/pdf"),
}

print("\n📤 Sending request to /api/register/team/flat...")
print(f"   Team: {form_data['team_name']}")
print(f"   Captain: {form_data['captain_name']} ({form_data['captain_email']})")
print(f"   Vice: {form_data['vice_name']} ({form_data['vice_email']})")
print(f"   Files: {len(files)} files attached")

try:
    response = requests.post(
        f"{BASE_URL}/api/register/team/flat",
        data=form_data,
        files=files,
        timeout=30
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("\n✅ REGISTRATION SUCCESSFUL!")
        print(f"   Team ID: {result.get('team_id')}")
        print(f"   Team Name: {result.get('team_name')}")
        print(f"   Captain: {result.get('captain_name')}")
        print(f"   Players: {result.get('player_count')}")
        print(f"\n   Pastor Letter URL: {result.get('pastor_letter_url', 'N/A')[:60]}...")
        print(f"   Payment Receipt URL: {result.get('payment_receipt_url', 'N/A')[:60]}...")
        print(f"   Group Photo URL: {result.get('group_photo_url', 'N/A')[:60]}...")
        
        print("\n" + "=" * 70)
        print("✅ TEST PASSED - FLAT MULTIPART ENDPOINT WORKS!")
        print("=" * 70)
        print("\n💡 Frontend Integration:")
        print("   Use FormData() with flattened field names:")
        print("   formData.append('team_name', 'My Team')")
        print("   formData.append('captain_name', 'John Doe')")
        print("   formData.append('captain_aadhar', fileObject)")
        print("   POST to: /api/register/team/flat")
        
    else:
        print(f"\n❌ REGISTRATION FAILED")
        print(f"   Status: {response.status_code}")
        try:
            error = response.json()
            print(f"   Error: {error}")
        except:
            print(f"   Error: {response.text}")
    
except requests.exceptions.Timeout:
    print("\n❌ Request timed out after 30 seconds")
except Exception as e:
    print(f"\n❌ Request failed: {e}")

print("\n" + "=" * 70)
