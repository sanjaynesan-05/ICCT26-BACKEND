#!/usr/bin/env python
"""
SMTP Test Against Deployed Backend
Tests whether the Render deployment can send emails
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_smtp_against_deployed_backend():
    """Test SMTP functionality"""
    
    logger.info("="*70)
    logger.info("🧪 TESTING SMTP EMAIL FUNCTIONALITY")
    logger.info("="*70)
    
    # Import settings
    from config.settings import settings
    
    logger.info(f"\n📋 Configuration Check:")
    logger.info(f"   SMTP_HOST: {settings.SMTP_HOST}")
    logger.info(f"   SMTP_PORT: {settings.SMTP_PORT}")
    logger.info(f"   SMTP_USER: {settings.SMTP_USER if settings.SMTP_USER else '❌ NOT SET'}")
    logger.info(f"   SMTP_ENABLED: {settings.SMTP_ENABLED}")
    
    if not settings.SMTP_ENABLED:
        logger.error("\n❌ SMTP IS NOT CONFIGURED!")
        logger.error("   SMTP_USER and SMTP_PASS are not set")
        logger.error("   Email sending will NOT work")
        return False
    
    logger.info("\n📧 Testing SMTP Connection...")
    
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        # Step 1: Connect
        logger.info(f"   → Connecting to {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        logger.info("   ✅ Connected")
        
        # Step 2: Start TLS
        logger.info("   → Starting TLS encryption")
        server.starttls()
        logger.info("   ✅ TLS enabled")
        
        # Step 3: Authenticate
        logger.info(f"   → Authenticating as {settings.SMTP_USER}")
        try:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            logger.info("   ✅ Authentication successful")
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"   ❌ Authentication FAILED: {e}")
            logger.error("   → Reason: Invalid credentials or Gmail app password")
            logger.error("   → This could be a Gmail security issue")
            server.quit()
            return False
        
        # Step 4: Send test email
        logger.info(f"\n   → Sending test email to {settings.SMTP_USER}")
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = settings.SMTP_USER
        msg['Subject'] = '[TEST] ICCT26 SMTP Verification'
        
        body = """
        This is a test email from ICCT26 backend.
        
        If you received this, SMTP is working correctly!
        
        ✅ Email sending is functional
        ✅ Notifications will be delivered
        
        Test Time: """ + str(__import__('datetime').datetime.now())
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server.send_message(msg)
            logger.info("   ✅ Email sent successfully")
            server.quit()
            logger.info("\n" + "="*70)
            logger.info("✅ SMTP TEST PASSED - EMAIL SENDING IS WORKING")
            logger.info("="*70)
            return True
        except smtplib.SMTPException as e:
            logger.error(f"   ❌ Failed to send email: {e}")
            server.quit()
            return False
            
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"\n❌ AUTHENTICATION ERROR: {e}")
        logger.error("   Possible causes:")
        logger.error("   1. Invalid Gmail password/app-password")
        logger.error("   2. Less secure app access disabled")
        logger.error("   3. Gmail account locked")
        return False
    
    except smtplib.SMTPException as e:
        logger.error(f"\n❌ SMTP ERROR: {e}")
        logger.error("   Network or server issue")
        return False
    
    except Exception as e:
        logger.error(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_email_service():
    """Test the email service wrapper"""
    logger.info("\n" + "="*70)
    logger.info("🧪 TESTING EMAIL SERVICE")
    logger.info("="*70)
    
    try:
        from app.utils.email_reliable import send_email_with_retry
        from config.settings import settings
        
        logger.info("\n📧 Attempting to send email via EmailService...")
        
        success = await send_email_with_retry(
            to_email=settings.SMTP_USER,
            subject="[SERVICE TEST] ICCT26 Backend",
            html_content="""
            <html>
                <body>
                    <h2>ICCT26 Email Service Test</h2>
                    <p>This email was sent via the email service wrapper.</p>
                    <p>✅ If received, the email service is working!</p>
                </body>
            </html>
            """
        )
        
        if success:
            logger.info("✅ Email service test PASSED")
            return True
        else:
            logger.error("❌ Email service test FAILED")
            return False
            
    except Exception as e:
        logger.error(f"❌ Email service error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Run all SMTP tests"""
    
    # Test 1: Direct SMTP
    smtp_result = await test_smtp_against_deployed_backend()
    
    # Test 2: Email Service
    service_result = await test_email_service()
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("📊 TEST SUMMARY")
    logger.info("="*70)
    logger.info(f"Direct SMTP Test: {'✅ PASSED' if smtp_result else '❌ FAILED'}")
    logger.info(f"Email Service Test: {'✅ PASSED' if service_result else '❌ FAILED'}")
    
    if smtp_result:
        logger.info("\n✅ SMTP IS WORKING!")
        logger.info("   → Email notifications will be sent")
        logger.info("   → Team approvals will include email confirmation")
    else:
        logger.info("\n❌ SMTP IS NOT WORKING")
        logger.info("   → Email notifications WILL NOT be sent")
        logger.info("   → Consider using alternative notification methods")
    
    logger.info("="*70)
    
    return smtp_result


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
