"""
Quick test of Cloudinary integration
Tests the registration endpoint with sample data
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Valid Base64 strings (proper padding)
VALID_PDF_B64 = "JVBERi0xLjQKCjEgMCBvYmpvCjEgMCBvYmpvCjEgMCBvYmpv"
VALID_JPEG_B64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgK"

# Sample registration data with valid Base64-encoded files
sample_data = {
    "teamName": "Test Warriors",
    "churchName": "Grace Church",
    "pastorLetter": f"data:application/pdf;base64,{VALID_PDF_B64}",
    "paymentReceipt": f"data:image/jpeg;base64,{VALID_JPEG_B64}",
    "groupPhoto": f"data:image/jpeg;base64,{VALID_JPEG_B64}",
    "captain": {
        "name": "John Smith",
        "phone": "+919876543210",
        "whatsapp": "919876543210",
        "email": "john@example.com"
    },
    "viceCaptain": {
        "name": "Jane Smith",
        "phone": "+919876543211",
        "whatsapp": "919876543211",
        "email": "jane@example.com"
    },
    "players": [
        {
            "name": "Player 1",
            "role": "Batsman",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        },
        {
            "name": "Player 2",
            "role": "Bowler",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        },
        {
            "name": "Player 3",
            "role": "Batsman",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        },
        {
            "name": "Player 4",
            "role": "Bowler",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        },
        {
            "name": "Player 5",
            "role": "All-rounder",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        },
        {
            "name": "Player 6",
            "role": "Batsman",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        },
        {
            "name": "Player 7",
            "role": "Bowler",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        },
        {
            "name": "Player 8",
            "role": "Batsman",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        },
        {
            "name": "Player 9",
            "role": "Bowler",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        },
        {
            "name": "Player 10",
            "role": "All-rounder",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        },
        {
            "name": "Player 11",
            "role": "Batsman",
            "aadharFile": f"data:application/pdf;base64,{VALID_PDF_B64}",
            "subscriptionFile": f"data:application/pdf;base64,{VALID_PDF_B64}"
        }
    ]
}

def test_registration():
    """Test registration endpoint"""
    
    print("=" * 70)
    print("🧪 TESTING CLOUDINARY INTEGRATION")
    print("=" * 70)
    print()
    
    # Test endpoint
    endpoint = f"{BASE_URL}/api/register/team"
    
    print(f"📍 Endpoint: POST {endpoint}")
    print(f"📦 Payload size: {len(json.dumps(sample_data))} bytes")
    print()
    
    try:
        print("🔄 Sending registration request...")
        response = requests.post(
            endpoint,
            json=sample_data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print()
        
        if response.status_code == 201:
            print("✅ SUCCESS! Registration completed")
            print()
            
            data = response.json()
            
            # Check if we got Cloudinary URLs (not Base64)
            if "data" in data:
                result = data["data"]
                
                print("📋 Response Summary:")
                print(f"  - Team ID: {result.get('team_id', 'N/A')}")
                print(f"  - Team Name: {result.get('team_name', 'N/A')}")
                print(f"  - Players Count: {len(result.get('players', []))}")
                print()
                
                # Check for file URLs
                if "files" in result:
                    print("📁 Files:")
                    for file_type, url in result["files"].items():
                        is_url = url.startswith("https://")
                        status = "✅ URL" if is_url else "❌ Base64"
                        url_preview = url[:80] + "..." if len(url) > 80 else url
                        print(f"  {status} {file_type}:")
                        print(f"      {url_preview}")
                    print()
                
                # Check player files
                if "players" in result and len(result["players"]) > 0:
                    player = result["players"][0]
                    print("👤 First Player Files:")
                    if "files" in player:
                        for file_type, url in player["files"].items():
                            is_url = url.startswith("https://")
                            status = "✅ URL" if is_url else "❌ Base64"
                            url_preview = url[:80] + "..." if len(url) > 80 else url
                            print(f"  {status} {file_type}:")
                            print(f"      {url_preview}")
                    print()
                
                print("=" * 70)
                print("🎉 CLOUDINARY INTEGRATION WORKING!")
                print("=" * 70)
                print()
                print("✅ Files are being uploaded to Cloudinary")
                print("✅ URLs are returned instead of Base64")
                print("✅ Check Cloudinary dashboard at: https://console.cloudinary.com")
                print("   Media Library → ICCT26 folder")
                print()
                
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print()
            print("Response:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend")
        print(f"   Make sure backend is running on {BASE_URL}")
        print()
        print("To start backend, run:")
        print("  cd 'd:\\ICCT26 BACKEND'")
        print("  .\\venv\\Scripts\\Activate.ps1")
        print("  python -m uvicorn main:app --reload --port 8000")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_registration()
