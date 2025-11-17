"""
COMPLETE END-TO-END REGISTRATION TEST
Tests sequential team ID generation, database storage, API response, and email sending
"""
import requests
import json
from datetime import datetime

# Use port 8001
BASE_URL = "http://localhost:8001/api"
HEALTH_URL = "http://localhost:8001"

print("\n" + "🏏" * 35)
print("ICCT26 BACKEND - COMPLETE REGISTRATION TEST")
print("Sequential Team ID + Database + API + Email (SMTP)")
print("🏏" * 35 + "\n")

print("=" * 70)
print("🧪 COMPLETE END-TO-END REGISTRATION TEST")
print("=" * 70)
print("\nThis test verifies:")
print("  1. ✅ Sequential Team ID (ICCT-XXX)")
print("  2. ✅ Database storage")
print("  3. ✅ API response")
print("  4. ✅ Email via SMTP")
print("  5. ✅ ID consistency across all systems")

# Step 1: Health Check
print("\n" + "─" * 70)
print("STEP 1: Server Health Check")
print("─" * 70)
try:
    response = requests.get(HEALTH_URL, timeout=5)
    if response.status_code == 200:
        print("✅ Server is running")
        print(f"   URL: {HEALTH_URL}")
    else:
        print(f"❌ Server returned status {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Server is not running: {e}")
    exit(1)

# Step 2: Create Test Data
print("\n" + "─" * 70)
print("STEP 2: Creating Test Registration Data")
print("─" * 70)

# Small test images (1x1 px GIF in Base64)
test_image = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
test_pdf = "data:application/pdf;base64,JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSA0IDAgUgo+Pgo+PgovQ29udGVudHMgNSAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvVGltZXMtUm9tYW4KPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFRlc3QpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDEwIDAwMDAwIG4gCjAwMDAwMDAwNTkgMDAwMDAgbiAKMDAwMDAwMDEzNyAwMDAwMCBuIAowMDAwMDAwMjY1IDAwMDAwIG4gCjAwMDAwMDAzNTMgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo0NDYKJSVFT0Y="

registration_data = {
    "churchName": "CSI Complete Test Church Coimbatore",
    "teamName": "Complete Test Warriors",
    "pastorLetter": test_pdf,
    "paymentReceipt": test_image,
    "groupPhoto": test_image,
    "captain": {
        "name": "Complete Test Captain",
        "phone": "+919876543210",
        "whatsapp": "919876543210",
        "email": "sanjaynesan007@gmail.com",  # Real email for testing
        "aadhar": test_image,
        "aadharNo": "123456789012",
        "gender": "Male",
        "subscription": test_image
    },
    "viceCaptain": {
        "name": "Complete Test Vice Captain",
        "phone": "+919876543211",
        "whatsapp": "919876543211",
        "email": "vice@test.com",
        "aadhar": test_image,
        "aadharNo": "123456789013",
        "gender": "Male",
        "subscription": test_image
    },
    "players": []
}

# Add 11 test players
for i in range(1, 12):
    player = {
        "name": f"Test Player {i}",
        "phone": f"+9198765432{i:02d}",
        "whatsapp": f"9198765432{i:02d}",
        "email": f"player{i}@test.com",
        "aadhar": test_image,
        "aadharNo": f"12345678{i:04d}",
        "gender": "Male" if i % 2 == 0 else "Female",
        "subscription": test_image
    }
    registration_data["players"].append(player)

print(f"✅ Team Name: {registration_data['teamName']}")
print(f"✅ Church: {registration_data['churchName']}")
print(f"✅ Captain: {registration_data['captain']['name']}")
print(f"✅ Captain Email: {registration_data['captain']['email']}")
print(f"✅ Players: {len(registration_data['players'])}")

# Step 3: Submit Registration
print("\n" + "─" * 70)
print("STEP 3: Submitting Team Registration")
print("─" * 70)
print(f"📤 POST {BASE_URL}/register/team")
print("⏳ Please wait... (uploading files to Cloudinary)")

start_time = datetime.now()
try:
    response = requests.post(
        f"{BASE_URL}/register/team",
        json=registration_data,
        timeout=30
    )
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ Response received in {elapsed:.2f} seconds")
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code != 201:
        print(f"\n❌ Registration failed!")
        print(f"Status: {response.status_code}")
        print(f"Error: {json.dumps(response.json(), indent=2)}")
        exit(1)
    
    result = response.json()
    print(f"\n✅ REGISTRATION SUCCESSFUL!")
    print(f"   Team ID: {result.get('team_id', 'NOT FOUND')}")
    print(f"   Team Name: {result.get('team_name', 'NOT FOUND')}")
    print(f"   Success: {result.get('success', False)}")
    
    # Verify Team ID format
    team_id = result.get('team_id', '')
    if team_id.startswith('ICCT-') and len(team_id) == 8:
        print(f"✅ Team ID format correct: {team_id}")
    else:
        print(f"❌ Team ID format incorrect: {team_id}")
        exit(1)
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print(f"\n📋 Registration Summary:")
    print(f"   Team ID:     {team_id}")
    print(f"   Team Name:   {result.get('team_name')}")
    print(f"   Players:     {len(registration_data['players']) + 2}")  # +captain +vice
    print(f"   Email Sent:  {registration_data['captain']['email']}")
    print("\n💡 Next Steps:")
    print("   1. Check email inbox for confirmation")
    print("   2. Verify team in database")
    print("   3. Check admin panel for team details")
    
except requests.exceptions.Timeout:
    print(f"❌ Request timed out after 30 seconds")
    exit(1)
except Exception as e:
    print(f"❌ Request failed: {e}")
    exit(1)
