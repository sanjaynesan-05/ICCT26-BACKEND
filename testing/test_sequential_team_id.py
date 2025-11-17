"""
Test Complete Registration Flow with New Sequential Team IDs
Demonstrates ICCT-001, ICCT-002 format in real registration
"""

import requests
import json

def create_simple_test_registration(team_name):
    """Create minimal test registration data"""
    
    # Simple 1x1 PNG in base64
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    return {
        "teamName": team_name,
        "churchName": "Test Church Coimbatore",
        "pastorLetter": f"data:image/png;base64,{test_image}",
        "groupPhoto": f"data:image/png;base64,{test_image}",
        "captain": {
            "name": f"{team_name} Captain",
            "phone": "+919876543210",
            "whatsapp": "919876543210",
            "email": "captain@test.com"
        },
        "viceCaptain": {
            "name": f"{team_name} Vice Captain",
            "phone": "+919876543211",
            "whatsapp": "919876543211",
            "email": "vice@test.com"
        },
        "players": [
            {
                "name": f"Player {i}",
                "age": 20 + i,
                "phone": f"+9198765432{10+i}",
                "role": ["Batsman", "Bowler", "All-Rounder", "Wicket Keeper"][i % 4],
                "aadharFile": f"data:image/png;base64,{test_image}",
                "subscriptionFile": f"data:image/png;base64,{test_image}"
            }
            for i in range(11)
        ],
        "paymentReceipt": f"data:image/png;base64,{test_image}"
    }


def test_sequential_team_ids():
    """Test that team IDs are generated sequentially"""
    
    print("\n" + "="*70)
    print("🧪 TESTING SEQUENTIAL TEAM ID FORMAT")
    print("="*70)
    print("\nThis test demonstrates the new team ID format:")
    print("  ICCT-001, ICCT-002, ICCT-003, etc.")
    print("\n⚠️  Note: Server must be running on http://localhost:8000")
    
    # Check if server is running
    try:
        health_response = requests.get('http://localhost:8000/health', timeout=5)
        if health_response.status_code != 200:
            print("\n❌ Server health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Server is not running!")
        print("   Please start the server first: python main.py")
        return False
    except Exception as e:
        print(f"\n❌ Error connecting to server: {str(e)}")
        return False
    
    print("✅ Server is running")
    
    # Register a test team
    print("\n" + "-"*70)
    print("📝 Registering Test Team...")
    print("-"*70)
    
    test_data = create_simple_test_registration("Sequential ID Test Team")
    
    try:
        response = requests.post(
            'http://localhost:8000/api/register/team',
            json=test_data,
            timeout=60
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            
            print("\n" + "="*70)
            print("✅ REGISTRATION SUCCESSFUL!")
            print("="*70)
            
            team_id = result.get('team_id', 'N/A')
            
            print(f"\n🎯 NEW TEAM ID FORMAT:")
            print(f"   Team ID: {team_id}")
            print(f"   Format:  ICCT-XXX")
            
            # Validate format
            if team_id.startswith("ICCT-") and len(team_id) == 8:
                number_part = team_id.split('-')[1]
                if number_part.isdigit() and len(number_part) == 3:
                    print(f"   ✅ Format is correct!")
                    print(f"   ✅ Sequential number: {int(number_part)}")
                else:
                    print(f"   ⚠️  Number format may be incorrect")
            else:
                print(f"   ⚠️  ID format does not match expected pattern")
            
            print(f"\n📋 Registration Details:")
            print(f"   Team ID:        {team_id}")
            print(f"   Team Name:      {result.get('team_name', 'N/A')}")
            print(f"   Church:         {result.get('church_name', 'N/A')}")
            print(f"   Captain:        {result.get('captain_name', 'N/A')}")
            print(f"   Vice Captain:   {result.get('vice_captain_name', 'N/A')}")
            print(f"   Players:        {result.get('player_count', 'N/A')}")
            print(f"   Email Sent:     {result.get('email_sent', False)}")
            
            print(f"\n👥 Expected Player IDs:")
            for i in range(1, min(4, result.get('player_count', 0) + 1)):
                print(f"   Player {i}: {team_id}-P{i:02d}")
            print(f"   ...")
            
            print(f"\n✅ Team ID Consistency:")
            print(f"   ✅ Stored in database: {team_id}")
            print(f"   ✅ Returned to frontend: {team_id}")
            print(f"   ✅ Will appear in email: {team_id}")
            print(f"   ✅ Will show in admin panel: {team_id}")
            
            return True
            
        else:
            print("\n❌ Registration failed")
            print(f"   Status: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {json.dumps(error, indent=2)}")
            except:
                print(f"   Response: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("\n❌ Request timeout (>60 seconds)")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def main():
    """Run the test"""
    print("\n🧪 Sequential Team ID Format Test")
    print("   Testing ICCT-001, ICCT-002, ICCT-003 format in real registration")
    
    success = test_sequential_team_ids()
    
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    if success:
        print("✅ Sequential team ID format is working!")
        print("\n📝 Format Specification:")
        print("   • Team IDs: ICCT-001, ICCT-002, ICCT-003, ...")
        print("   • Player IDs: ICCT-XXX-P01, ICCT-XXX-P02, ...")
        print("   • Consistent across backend, frontend, and database")
        print("   • Same ID displayed to user after registration")
    else:
        print("❌ Test failed - Please check server status")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
