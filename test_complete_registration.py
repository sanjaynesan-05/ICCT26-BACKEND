"""
Complete End-to-End Registration Test
Tests the entire registration flow with file uploads
"""
import asyncio
import httpx
import os
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = f"{BASE_URL}/api/register/team"

def create_test_image():
    """Create a simple test image file"""
    from PIL import Image
    import io
    
    # Create a 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def create_test_pdf():
    """Create a simple test PDF file"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    import io
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Test Document")
    c.save()
    buffer.seek(0)
    return buffer

async def test_registration():
    """Test complete registration flow"""
    
    print("=" * 80)
    print("🧪 TESTING COMPLETE REGISTRATION FLOW")
    print("=" * 80)
    
    # Generate unique team name with timestamp
    import time
    timestamp = int(time.time())
    unique_team_name = f"Test Thunder FC {timestamp}"
    unique_phone_captain = f"98765{timestamp % 100000:05d}"
    unique_phone_vice = f"98766{timestamp % 100000:05d}"
    
    # Create test files
    print("\n📁 Creating test files...")
    pastor_letter = create_test_pdf()
    payment_receipt = create_test_image()
    group_photo = create_test_image()
    player_1_aadhar = create_test_pdf()
    player_1_sub = create_test_pdf()
    player_2_aadhar = create_test_pdf()
    player_2_sub = create_test_pdf()
    
    print("✅ Test files created")
    
    # Prepare form data
    form_data = {
        # Team information
        "team_name": unique_team_name,
        "church_name": "Saint Johns Cathedral",
        
        # Captain information
        "captain_name": "John Smith",
        "captain_phone": unique_phone_captain,
        "captain_email": f"john{timestamp}@example.com",
        "captain_whatsapp": unique_phone_captain,
        
        # Vice-captain information
        "vice_name": "Mike Johnson",
        "vice_phone": unique_phone_vice,
        "vice_email": f"mike{timestamp}@example.com",
        "vice_whatsapp": unique_phone_vice,
        
        # Player 1
        "player_0_name": "Player One",
        "player_0_role": "Batsman",
        
        # Player 2
        "player_1_name": "Player Two",
        "player_1_role": "Bowler",
    }
    
    # Prepare files
    files = {
        "pastor_letter": ("pastor_letter.pdf", pastor_letter, "application/pdf"),
        "payment_receipt": ("receipt.png", payment_receipt, "image/png"),
        "group_photo": ("group.png", group_photo, "image/png"),
        "player_0_aadhar_file": ("aadhar_1.pdf", player_1_aadhar, "application/pdf"),
        "player_0_subscription_file": ("sub_1.pdf", player_1_sub, "application/pdf"),
        "player_1_aadhar_file": ("aadhar_2.pdf", player_2_aadhar, "application/pdf"),
        "player_1_subscription_file": ("sub_2.pdf", player_2_sub, "application/pdf"),
    }
    
    print("\n📤 Sending registration request...")
    print(f"Endpoint: {REGISTER_ENDPOINT}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                REGISTER_ENDPOINT,
                data=form_data,
                files=files,
                headers={
                    "Idempotency-Key": f"test-registration-{int(asyncio.get_event_loop().time())}"
                }
            )
            
            print(f"\n📥 Response Status: {response.status_code}")
            print(f"Response Body:")
            
            try:
                response_json = response.json()
                import json
                print(json.dumps(response_json, indent=2))
            except:
                print(response.text)
            
            if response.status_code == 201:
                print("\n✅ SUCCESS! Registration completed successfully")
                result = response.json()
                print(f"\n📋 Registration Details:")
                print(f"   Team ID: {result.get('team_id')}")
                print(f"   Team Name: {result.get('team_name')}")
                print(f"   Player Count: {result.get('player_count')}")
                return result
            else:
                print(f"\n❌ FAILED! Status: {response.status_code}")
                return None
                
        except httpx.ConnectError as e:
            print(f"\n❌ CONNECTION ERROR: Cannot connect to server at {BASE_URL}")
            print(f"   Make sure the server is running: python -m uvicorn main:app --host 0.0.0.0 --port 8000")
            print(f"   Error details: {e}")
            return None
        except Exception as e:
            print(f"\n❌ ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

async def verify_cloudinary_structure(team_id: str):
    """Verify Cloudinary folder structure"""
    print("\n" + "=" * 80)
    print("🔍 VERIFYING CLOUDINARY FOLDER STRUCTURE")
    print("=" * 80)
    
    print(f"\nExpected structure for Team ID: {team_id}")
    print(f"├── players/")
    print(f"│   └── {team_id}/")
    print(f"│       ├── {team_id}-P01/")
    print(f"│       │   ├── aadhar_file")
    print(f"│       │   └── subscription_file")
    print(f"│       └── {team_id}-P02/")
    print(f"│           ├── aadhar_file")
    print(f"│           └── subscription_file")
    
    print("\n⚠️  Manual verification required:")
    print("   1. Log into Cloudinary dashboard")
    print("   2. Check Media Library")
    print("   3. Verify folder structure matches above")

if __name__ == "__main__":
    print("\n🚀 Starting end-to-end test...\n")
    
    # Check if required packages are installed
    try:
        import PIL
        import reportlab
    except ImportError as e:
        print("❌ Missing required packages. Installing...")
        os.system("pip install pillow reportlab httpx")
        print("\n✅ Packages installed. Please run the script again.")
        exit(0)
    
    # Run test
    result = asyncio.run(test_registration())
    
    if result and result.get('team_id'):
        asyncio.run(verify_cloudinary_structure(result['team_id']))
    
    print("\n" + "=" * 80)
    print("✅ Test completed")
    print("=" * 80)
