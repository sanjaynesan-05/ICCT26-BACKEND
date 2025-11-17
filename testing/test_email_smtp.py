"""
Test SMTP Email Service
Verifies that email sending is working correctly
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services import EmailService
from app.config import settings
from app.schemas import PlayerDetails

def test_email_configuration():
    """Test SMTP configuration"""
    print("\n" + "="*70)
    print("📧 SMTP EMAIL SERVICE TEST")
    print("="*70)
    
    print("\n📋 Configuration Check:")
    print(f"   SMTP Server:    {settings.SMTP_SERVER}")
    print(f"   SMTP Port:      {settings.SMTP_PORT}")
    print(f"   SMTP Username:  {settings.SMTP_USERNAME}")
    print(f"   SMTP Password:  {'*' * len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 'NOT SET'}")
    print(f"   From Email:     {settings.SMTP_FROM_EMAIL}")
    print(f"   From Name:      {settings.SMTP_FROM_NAME}")
    print(f"   SMTP Enabled:   {'✅ YES' if settings.SMTP_ENABLED else '❌ NO'}")
    
    if not settings.SMTP_ENABLED:
        print("\n❌ SMTP is NOT enabled!")
        print("   Please check your .env.local file and ensure:")
        print("   1. SMTP_USERNAME is set")
        print("   2. SMTP_PASSWORD is set")
        return False
    
    return True


def test_email_sending():
    """Test sending an actual email"""
    print("\n" + "="*70)
    print("📤 Sending Test Email...")
    print("="*70)
    
    # Create sample players for email template
    sample_players = [
        PlayerDetails(name="John Doe", age=25, phone="+919876543210", role="Batsman"),
        PlayerDetails(name="Jane Smith", age=23, phone="+919876543211", role="Bowler"),
        PlayerDetails(name="Mike Johnson", age=28, phone="+919876543212", role="All-Rounder"),
        PlayerDetails(name="Sarah Williams", age=22, phone="+919876543213", role="Wicket Keeper"),
        PlayerDetails(name="Tom Brown", age=26, phone="+919876543214", role="Batsman"),
        PlayerDetails(name="Emily Davis", age=24, phone="+919876543215", role="Bowler"),
        PlayerDetails(name="David Wilson", age=27, phone="+919876543216", role="All-Rounder"),
        PlayerDetails(name="Lisa Anderson", age=25, phone="+919876543217", role="Batsman"),
        PlayerDetails(name="Robert Taylor", age=29, phone="+919876543218", role="Bowler"),
        PlayerDetails(name="Jennifer Martin", age=23, phone="+919876543219", role="All-Rounder"),
        PlayerDetails(name="Michael Lee", age=26, phone="+919876543220", role="Batsman"),
    ]
    
    # Create email content
    print("\n📝 Creating email content...")
    html_content = EmailService.create_confirmation_email(
        team_name="Test Warriors",
        captain_name="Test Captain",
        church_name="Test CSI Church",
        team_id="ICCT26-TEST-20251117",
        players=sample_players
    )
    print("   ✅ Email template created")
    
    # Send email to captain's email (from .env.local)
    test_email = settings.SMTP_USERNAME  # Send test email to yourself
    subject = f"🏏 Test Email - {settings.TOURNAMENT_NAME}"
    
    print(f"\n📧 Sending email to: {test_email}")
    print("   Please wait...")
    
    result = EmailService.send_email(
        to_email=test_email,
        subject=subject,
        html_content=html_content
    )
    
    print("\n" + "="*70)
    if result['success']:
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print("="*70)
        print(f"\n📬 Check your inbox: {test_email}")
        print("   If you don't see the email:")
        print("   1. Check your spam/junk folder")
        print("   2. Wait 1-2 minutes for delivery")
        print("   3. Verify Gmail app password is correct")
        print("\n📧 Email Details:")
        print(f"   To:      {test_email}")
        print(f"   Subject: {subject}")
        print(f"   From:    {settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>")
        return True
    else:
        print("❌ EMAIL FAILED TO SEND")
        print("="*70)
        print(f"\n❗ Error: {result['message']}")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify Gmail App Password is correct:")
        print("      - Go to: https://myaccount.google.com/apppasswords")
        print("      - Generate new App Password if needed")
        print("      - Update SMTP_PASSWORD in .env.local")
        print("   2. Check your Gmail account settings:")
        print("      - 2-Factor Authentication must be enabled")
        print("      - Less secure app access may need to be enabled")
        print("   3. Verify SMTP_USERNAME matches your Gmail address")
        print("   4. Check firewall/antivirus blocking port 587")
        return False


def main():
    """Run email service tests"""
    print("\n🧪 ICCT26 Email Service Test Suite")
    print("   Testing SMTP configuration and email sending...")
    
    # Test 1: Configuration
    if not test_email_configuration():
        print("\n❌ Configuration test failed. Cannot proceed with email test.")
        return
    
    print("\n✅ Configuration test passed!")
    
    # Test 2: Send actual email
    success = test_email_sending()
    
    # Final summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    if success:
        print("✅ All tests passed!")
        print("✅ SMTP email service is working correctly")
        print("✅ Emails will be sent after team registration")
        print("\n💡 When teams register:")
        print("   1. Captain receives confirmation email immediately")
        print("   2. Email includes team ID and player roster")
        print("   3. Email includes tournament details and next steps")
    else:
        print("❌ Email test failed")
        print("❌ Please fix SMTP configuration before deployment")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
