#!/usr/bin/env python
"""
Send Confirmation Email to sanjaynesan@karunya.edu.in
Tests email delivery with a proper team registration confirmation
"""

import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def send_confirmation_email():
    """Send confirmation email to the target address"""
    
    recipient_email = "sanjaynesan@karunya.edu.in"
    
    logger.info("="*70)
    logger.info("📧 SENDING CONFIRMATION EMAIL")
    logger.info("="*70)
    
    logger.info(f"\n📮 Recipient: {recipient_email}")
    logger.info(f"   From: {settings.SMTP_FROM_EMAIL}")
    logger.info(f"   Subject: ICCT26 Team Registration Confirmation")
    
    # Check SMTP config
    if not settings.SMTP_ENABLED:
        logger.error("\n❌ SMTP NOT CONFIGURED!")
        logger.error("   SMTP_USER and SMTP_PASS are not set")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "ICCT26 Cricket Tournament - Registration Confirmation"
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = recipient_email
        
        # Plain text version
        text = f"""
Dear Team Captain,

Welcome to ICCT26 Cricket Tournament!

Your team registration has been received successfully.

Registration Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Team ID:        ICCT-TEST-001
Team Name:      Test Team Karunya
Captain Name:   Sanjay Nesan
Captain Email:  sanjaynesan@karunya.edu.in
Registration:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status:         PENDING ADMIN APPROVAL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
✓ Your registration has been submitted
✓ Admin will review your documents
✓ You will receive an approval email once confirmed
✓ Team ID will be activated upon approval

Documents Submitted:
✓ Pastor Letter
✓ Payment Receipt
✓ Group Photo
✓ Player Details

If you have any questions, please contact us at:
📧 contact@icct26.com
📱 +91-XXXXX-XXXXX

Thank you for registering!

Best regards,
ICCT26 Tournament Team
"""
        
        # HTML version
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #1e40af; color: white; padding: 20px; text-align: center; }}
                    .content {{ background-color: #f5f5f5; padding: 20px; margin: 10px 0; }}
                    .details {{ background-color: white; border-left: 4px solid #1e40af; padding: 15px; margin: 10px 0; }}
                    .details p {{ margin: 8px 0; }}
                    .label {{ font-weight: bold; color: #1e40af; }}
                    .status {{ background-color: #fef3c7; border: 1px solid #f59e0b; padding: 10px; border-radius: 4px; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; }}
                    .checkmark {{ color: #10b981; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏏 ICCT26 Cricket Tournament</h1>
                        <p>Registration Confirmation</p>
                    </div>
                    
                    <div class="content">
                        <h2>Dear Team Captain,</h2>
                        <p>Welcome to <strong>ICCT26 Cricket Tournament!</strong></p>
                        <p>Your team registration has been received successfully. Thank you for submitting your application.</p>
                    </div>
                    
                    <div class="details">
                        <h3>📋 Registration Details</h3>
                        <p><span class="label">Team ID:</span> ICCT-TEST-001</p>
                        <p><span class="label">Team Name:</span> Test Team Karunya</p>
                        <p><span class="label">Captain Name:</span> Sanjay Nesan</p>
                        <p><span class="label">Captain Email:</span> sanjaynesan@karunya.edu.in</p>
                        <p><span class="label">Registration Time:</span> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div class="details">
                        <h3>✅ Documents Submitted</h3>
                        <p><span class="checkmark">✓</span> Pastor Letter</p>
                        <p><span class="checkmark">✓</span> Payment Receipt</p>
                        <p><span class="checkmark">✓</span> Group Photo</p>
                        <p><span class="checkmark">✓</span> Player Details</p>
                    </div>
                    
                    <div class="status">
                        <h3>📊 Current Status</h3>
                        <p><strong>Status:</strong> <span style="color: #f59e0b;">⏳ PENDING ADMIN APPROVAL</span></p>
                        <p>Admin will review your documents and notify you of approval/rejection.</p>
                    </div>
                    
                    <div class="details">
                        <h3>📌 Next Steps</h3>
                        <p><span class="checkmark">✓</span> Registration submitted</p>
                        <p><span class="checkmark">✓</span> Awaiting admin review</p>
                        <p>➜ You will receive approval email</p>
                        <p>➜ Team ID will be activated</p>
                    </div>
                    
                    <div class="content">
                        <p>If you have any questions or need assistance, please contact us:</p>
                        <p>📧 Email: contact@icct26.com<br>📱 Phone: +91-XXXXX-XXXXX</p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2025 ICCT26 Cricket Tournament. All rights reserved.</p>
                        <p>This is an automated message. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Attach both versions
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        logger.info(f"\n🔐 Connecting to SMTP server...")
        logger.info(f"   Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        logger.info("   ✅ Connected")
        
        logger.info("   → Starting TLS encryption...")
        server.starttls()
        logger.info("   ✅ TLS enabled")
        
        logger.info(f"   → Authenticating as {settings.SMTP_USER}...")
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        logger.info("   ✅ Authenticated")
        
        logger.info(f"\n📮 Sending email to {recipient_email}...")
        server.send_message(msg)
        logger.info("   ✅ Email sent successfully!")
        
        server.quit()
        logger.info("\n" + "="*70)
        logger.info("✅ CONFIRMATION EMAIL DELIVERED")
        logger.info("="*70)
        logger.info(f"\n✉️  Email successfully sent to: {recipient_email}")
        logger.info(f"📧 Subject: ICCT26 Cricket Tournament - Registration Confirmation")
        logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("\n✅ Check your inbox at karunya.edu.in for the confirmation email!")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"\n❌ AUTHENTICATION ERROR: {e}")
        logger.error("   Invalid SMTP credentials")
        return False
    
    except smtplib.SMTPException as e:
        logger.error(f"\n❌ SMTP ERROR: {e}")
        return False
    
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    try:
        success = send_confirmation_email()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
