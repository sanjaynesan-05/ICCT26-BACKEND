"""
Test SMTP Connection and Email Sending
Tests actual connectivity to Gmail SMTP server
"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_smtp_connection():
    """Test SMTP server connection"""
    logger.info("="*60)
    logger.info("🧪 TESTING SMTP CONNECTION")
    logger.info("="*60)
    
    try:
        logger.info("\n📧 Connecting to SMTP server...")
        logger.info(f"   Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        logger.info(f"   User: {settings.SMTP_USER}")
        
        # Create SMTP connection
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        logger.info("✅ TCP connection established")
        
        # Start TLS
        logger.info("🔒 Starting TLS encryption...")
        server.starttls()
        logger.info("✅ TLS encryption active")
        
        # Login
        logger.info("🔐 Authenticating with Gmail...")
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        logger.info("✅ Authentication successful")
        
        # Test: Send a test email
        logger.info("\n📮 Sending test email...")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🧪 ICCT26 Backend SMTP Test"
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = settings.SMTP_USER  # Send to self for testing
        
        # Email body
        text = "This is a test email from the ICCT26 backend.\n\nIf you received this, SMTP is working correctly! ✅"
        html = """\
        <html>
          <body>
            <h2>🧪 ICCT26 Backend SMTP Test</h2>
            <p>This is a test email from the ICCT26 backend.</p>
            <p><strong>If you received this, SMTP is working correctly! ✅</strong></p>
            <hr>
            <p><em>Sent at: """ + __import__('datetime').datetime.now().isoformat() + """</em></p>
          </body>
        </html>
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send the email
        server.sendmail(
            settings.SMTP_FROM_EMAIL,
            settings.SMTP_USER,
            msg.as_string()
        )
        logger.info(f"✅ Test email sent successfully to {settings.SMTP_USER}")
        
        # Quit
        server.quit()
        logger.info("✅ Connection closed properly")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 SMTP CONNECTION TEST: PASSED")
        logger.info("="*60)
        logger.info("\n✅ Configuration Status:")
        logger.info(f"   - Host: {settings.SMTP_HOST}")
        logger.info(f"   - Port: {settings.SMTP_PORT}")
        logger.info(f"   - User: {settings.SMTP_USER}")
        logger.info(f"   - From Email: {settings.SMTP_FROM_EMAIL}")
        logger.info(f"   - From Name: {settings.SMTP_FROM_NAME}")
        logger.info(f"   - TLS Enabled: Yes")
        logger.info(f"   - Status: ✅ WORKING")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"\n❌ AUTHENTICATION FAILED")
        logger.error(f"   Error: {e}")
        logger.error(f"\n   Check:")
        logger.error(f"   - Email: {settings.SMTP_USER}")
        logger.error(f"   - Password: Verify Gmail App Password is correct")
        logger.error(f"   - 2FA: Must be enabled for App Password to work")
        return False
        
    except smtplib.SMTPException as e:
        logger.error(f"\n❌ SMTP ERROR")
        logger.error(f"   Error: {e}")
        logger.error(f"   Check SMTP settings in .env.local")
        return False
        
    except Exception as e:
        logger.error(f"\n❌ CONNECTION ERROR")
        logger.error(f"   Error: {e}")
        logger.error(f"   Check:")
        logger.error(f"   - Internet connection")
        logger.error(f"   - Firewall/Proxy settings")
        logger.error(f"   - Gmail SMTP host: {settings.SMTP_HOST}")
        return False


if __name__ == "__main__":
    try:
        success = test_smtp_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Test interrupted by user")
        sys.exit(1)
