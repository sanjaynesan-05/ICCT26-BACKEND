"""
Direct SMTP Test - Minimal Dependencies
========================================
Tests SMTP connection directly without app dependencies
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv('.env.local')

def test_smtp_direct():
    """Test SMTP connection directly"""
    
    print("=" * 80)
    print("DIRECT SMTP CONNECTION TEST")
    print("=" * 80)
    
    # Get config
    smtp_host = os.getenv('SMTP_SERVER', os.getenv('SMTP_HOST', 'smtp-relay.brevo.com'))
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USERNAME', os.getenv('SMTP_USER', ''))
    smtp_pass = os.getenv('SMTP_PASSWORD', os.getenv('SMTP_PASS', ''))
    from_email = os.getenv('SMTP_FROM_EMAIL', '')
    from_name = os.getenv('SMTP_FROM_NAME', 'ICCT26')
    
    print(f"\n📧 Configuration:")
    print(f"   Host: {smtp_host}")
    print(f"   Port: {smtp_port}")
    print(f"   User: {smtp_user}")
    print(f"   From: {from_email}")
    print(f"   From Name: {from_name}")
    
    if not all([smtp_user, smtp_pass, from_email]):
        print("\n❌ Missing SMTP credentials")
        return False
    
    try:
        print("\n🔄 Step 1: Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        print("✅ Connected successfully\n")
        
        print("🔄 Step 2: Starting TLS...")
        server.starttls()
        print("✅ TLS started\n")
        
        print("🔄 Step 3: Logging in...")
        server.login(smtp_user, smtp_pass)
        print("✅ Login successful\n")
        
        print("🔄 Step 4: Creating test email...")
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = "sanjaynesan007@gmail.com"
        msg['Subject'] = "[DIRECT TEST] ICCT26 SMTP Test"
        
        html = """
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2 style="color: #27ae60;">✅ SMTP Test Successful!</h2>
    <p>This email was sent directly using Python's smtplib.</p>
    <p>Your Brevo SMTP configuration is working correctly!</p>
    <hr>
    <p><small>ICCT26 Registration System - Direct SMTP Test</small></p>
  </body>
</html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        print("✅ Email created\n")
        
        print("🔄 Step 5: Sending email...")
        server.send_message(msg)
        print("✅ Email sent successfully!\n")
        
        print("🔄 Step 6: Closing connection...")
        server.quit()
        print("✅ Connection closed\n")
        
        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nCheck your inbox at sanjaynesan007@gmail.com")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ Authentication failed: {e}")
        print("   Check your SMTP username and password")
        return False
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP error: {e}")
        return False
    except TimeoutError as e:
        print(f"\n❌ Connection timeout: {e}")
        print("   This could be a firewall or network issue")
        print("   Try:")
        print("   1. Check if port 587 is open")
        print("   2. Try from a different network")
        print("   3. Check antivirus/firewall settings")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = test_smtp_direct()
    sys.exit(0 if success else 1)
