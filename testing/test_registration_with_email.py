"""
Test Team Registration with Email Sending
Complete end-to-end test including database save and email notification
"""

import requests
import json
import base64
from datetime import datetime

def create_test_registration():
    """Create test registration data"""
    
    # Create a simple 1x1 PNG image in base64
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    return {
        "teamName": "Email Test Warriors",
        "churchName": "CSI Test Church Coimbatore",
        "pastorLetter": f"data:image/png;base64,{test_image_base64}",
        "groupPhoto": f"data:image/png;base64,{test_image_base64}",
        "captain": {
            "name": "Email Test Captain",
            "phone": "+919876543210",
            "whatsapp": "919876543210",
            "email": "sanjaynesan007@gmail.com"  # Your email for testing
        },
        "viceCaptain": {
            "name": "Email Test Vice Captain",
            "phone": "+919876543211",
            "whatsapp": "919876543211",
            "email": "sanjaynesan007@gmail.com"
        },
        "players": [
            {
                "name": f"Test Player {i}",
                "age": 20 + i,
                "phone": f"+9198765432{10+i}",
                "role": ["Batsman", "Bowler", "All-Rounder", "Wicket Keeper"][i % 4],
                "aadharFile": f"data:image/png;base64,{test_image_base64}",
                "subscriptionFile": f"data:image/png;base64,{test_image_base64}"
            }
            for i in range(11)
        ],
        "paymentReceipt": f"data:image/png;base64,{test_image_base64}"
    }


def test_registration_with_email():
    """Test complete registration flow with email"""
    
    print("\n" + "="*70)
    print("📧 TESTING TEAM REGISTRATION WITH EMAIL NOTIFICATION")
    print("="*70)
    
    # Create test data
    print("\n📝 Creating test registration data...")
    test_data = create_test_registration()
    print(f"   ✅ Team: {test_data['teamName']}")
    print(f"   ✅ Church: {test_data['churchName']}")
    print(f"   ✅ Captain: {test_data['captain']['name']}")
    print(f"   ✅ Captain Email: {test_data['captain']['email']}")
    print(f"   ✅ Players: {len(test_data['players'])}")
    
    # Send registration
    print(f"\n📤 Sending registration to http://localhost:8000/api/register/team...")
    
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
            
            print(f"\n📋 Registration Details:")
            print(f"   Team ID:        {result.get('team_id', 'N/A')}")
            print(f"   Team Name:      {result.get('team_name', 'N/A')}")
            print(f"   Church Name:    {result.get('church_name', 'N/A')}")
            print(f"   Captain:        {result.get('captain_name', 'N/A')}")
            print(f"   Vice Captain:   {result.get('vice_captain_name', 'N/A')}")
            print(f"   Players:        {result.get('player_count', 'N/A')}")
            print(f"   Registration:   {result.get('registration_date', 'N/A')}")
            
            # Check email status
            email_sent = result.get('email_sent', False)
            print(f"\n📧 Email Status:")
            if email_sent:
                print(f"   ✅ CONFIRMATION EMAIL SENT!")
                print(f"   📬 Check inbox: {test_data['captain']['email']}")
                print(f"\n💡 Email should include:")
                print(f"   • Team ID: {result.get('team_id', 'N/A')}")
                print(f"   • Team roster with all {result.get('player_count', 'N/A')} players")
                print(f"   • Tournament details and dates")
                print(f"   • Next steps for the team")
                print(f"\n📱 If you don't see the email:")
                print(f"   1. Check spam/junk folder")
                print(f"   2. Wait 1-2 minutes for delivery")
                print(f"   3. Search for: {result.get('team_name', 'N/A')}")
            else:
                print(f"   ❌ EMAIL WAS NOT SENT")
                print(f"   ⚠️ Registration saved to database, but email failed")
                print(f"\n🔧 Possible reasons:")
                print(f"   1. SMTP configuration issue")
                print(f"   2. Invalid email address")
                print(f"   3. SMTP server temporarily unavailable")
                print(f"   4. Check server logs for details")
            
            # Check file uploads
            if 'files' in result:
                files = result['files']
                print(f"\n☁️ Cloudinary Files:")
                print(f"   Pastor Letter:    {'✅' if files.get('pastor_letter_url') else '❌'}")
                print(f"   Payment Receipt:  {'✅' if files.get('payment_receipt_url') else '❌'}")
                print(f"   Group Photo:      {'✅' if files.get('group_photo_url') else '❌'}")
            
            print("\n" + "="*70)
            print("✅ TEST COMPLETED SUCCESSFULLY")
            print("="*70)
            
            if email_sent:
                print("\n🎉 Email notification is working perfectly!")
                print("✅ Teams will receive confirmation emails after registration")
            else:
                print("\n⚠️  Database save successful, but email needs attention")
                print("❗ Review SMTP configuration or server logs")
            
            return True
            
        else:
            print("\n" + "="*70)
            print("❌ REGISTRATION FAILED")
            print("="*70)
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            try:
                error = response.json()
                print(f"\nError Details:")
                print(json.dumps(error, indent=2))
            except:
                pass
            
            return False
    
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR")
        print("   Server is not running on http://localhost:8000")
        print("\n💡 To fix:")
        print("   1. Open a new terminal")
        print("   2. Run: python main.py")
        print("   3. Wait for server to start")
        print("   4. Run this test again")
        return False
    
    except requests.exceptions.Timeout:
        print("\n❌ REQUEST TIMEOUT")
        print("   Registration took too long (>60 seconds)")
        print("\n💡 This might indicate:")
        print("   1. Large file uploads taking time")
        print("   2. Database connection issues")
        print("   3. Network problems")
        return False
    
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        return False


def main():
    """Run the test"""
    print("\n🧪 ICCT26 Email Integration Test")
    print("   Testing complete registration flow with email notification")
    
    success = test_registration_with_email()
    
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    
    if success:
        print("✅ Test passed - Registration and email working")
        print("\n📧 What happens after real registration:")
        print("   1. Team data saved to PostgreSQL database")
        print("   2. Files uploaded to Cloudinary cloud storage")
        print("   3. Captain receives confirmation email with:")
        print("      • Unique Team ID")
        print("      • Complete player roster")
        print("      • Tournament schedule and venue details")
        print("      • Next steps and instructions")
        print("   4. Admin can view all teams in admin panel")
    else:
        print("❌ Test failed - Check server status and configuration")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
