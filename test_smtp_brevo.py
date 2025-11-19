#!/usr/bin/env python3
"""
SMTP Connection & Email Send Test
==================================
Tests the SMTP configuration from .env.local and sends a test email.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

# Import email utilities
from app.utils.email_reliable import send_email_with_retry


async def test_smtp_connection():
    """Test SMTP connection and send a test email"""
    
    print("=" * 80)
    print("SMTP CONNECTION TEST")
    print("=" * 80)
    
    # Display loaded configuration (sanitized)
    smtp_server = os.getenv('SMTP_SERVER', os.getenv('SMTP_HOST', 'NOT_SET'))
    smtp_port = os.getenv('SMTP_PORT', 'NOT_SET')
    smtp_user = os.getenv('SMTP_USERNAME', os.getenv('SMTP_USER', 'NOT_SET'))
    smtp_from = os.getenv('SMTP_FROM_EMAIL', 'NOT_SET')
    
    print(f"\n📧 SMTP Configuration:")
    print(f"   Server: {smtp_server}")
    print(f"   Port: {smtp_port}")
    print(f"   Username: {smtp_user}")
    print(f"   From Email: {smtp_from}")
    print(f"   Environment: {os.getenv('ENVIRONMENT', 'NOT_SET')}")
    
    # Check if all required env vars are set
    required_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_FROM_EMAIL']
    alt_vars = ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASS', 'SMTP_FROM_EMAIL']
    
    has_config = all(os.getenv(var) for var in required_vars) or all(os.getenv(var) for var in alt_vars)
    
    if not has_config:
        print(f"\n❌ Missing required SMTP environment variables")
        print(f"   Need either: {', '.join(required_vars)}")
        print(f"   Or: {', '.join(alt_vars)}")
        return False
    
    print("\n✅ All required SMTP environment variables are set\n")
    
    try:
        # Test 1: Send a simple test email
        print("🔄 Test 1: Sending test email to admin...")
        test_email = "sanjaynesan007@gmail.com"
        
        html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2>🏏 ICCT26 SMTP Test Email</h2>
    <p>Hello,</p>
    <p>This is a test email from the <strong>ICCT26 Cricket Tournament Registration</strong> system.</p>
    <p><strong style="color: green;">✅ If you're seeing this, your SMTP configuration is working correctly!</strong></p>
    <hr>
    <h4>Test Details:</h4>
    <ul>
      <li><strong>SMTP Server:</strong> {smtp_server}</li>
      <li><strong>Port:</strong> {smtp_port}</li>
      <li><strong>Environment:</strong> {os.getenv('ENVIRONMENT', 'development')}</li>
      <li><strong>Test Status:</strong> ✅ Success</li>
    </ul>
    <hr>
    <p><em>ICCT26 Registration System</em></p>
  </body>
</html>
        """
        
        result = await send_email_with_retry(
            to_email=test_email,
            subject="[TEST] ICCT26 SMTP Configuration Test",
            body=html_body
        )
        
        if result:
            print(f"✅ Test email sent successfully to {test_email}\n")
        else:
            print(f"❌ Failed to send test email to {test_email}\n")
            return False
        
        # Test 2: Send email with registration confirmation format
        print("🔄 Test 2: Testing registration confirmation email format...")
        
        html_body2 = """
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px;">
    <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
      <h1 style="color: #2c3e50; text-align: center;">🏏 ICCT26 Cricket Tournament</h1>
      <h2 style="color: #27ae60; text-align: center;">Team Registration Successful!</h2>
      
      <p style="font-size: 16px;">Dear Team,</p>
      <p style="font-size: 16px;">Your team has been successfully registered for <strong>ICCT26 Cricket Tournament</strong>.</p>
      
      <div style="background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0;">
        <h3 style="color: #2c3e50;">📋 Team Details:</h3>
        <ul>
          <li><strong>Team Name:</strong> Test Team</li>
          <li><strong>Captain:</strong> Test Player</li>
          <li><strong>Registration ID:</strong> TEST-123456</li>
          <li><strong>Status:</strong> <span style="color: green; font-weight: bold;">✅ Confirmed</span></li>
        </ul>
      </div>
      
      <p style="text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px;">
        This is an automated test email from ICCT26 Registration System.
      </p>
    </div>
  </body>
</html>
        """
        
        result = await send_email_with_retry(
            to_email=test_email,
            subject="[TEST] ICCT26 Team Registration Confirmation",
            body=html_body2
        )
        
        if result:
            print("✅ Email formatting test sent successfully\n")
        else:
            print("❌ Failed to send formatted email\n")
            return False
        
        print("=" * 80)
        print("✅ ALL SMTP TESTS PASSED!")
        print("=" * 80)
        print("\n✅ SMTP Configuration is working correctly!")
        print(f"✅ Emails sent to: {test_email}")
        print("✅ Email formatting is functional")
        print("\nYour system is ready to send team registration emails.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ SMTP TEST FAILED")
        print(f"Error: {str(e)}")
        print(f"Type: {type(e).__name__}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return False


async def main():
    """Run the SMTP test"""
    try:
        success = await test_smtp_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
