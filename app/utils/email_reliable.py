"""
Reliable Email Service - ICCT26
================================
Email sending with retry logic and exponential backoff.

Features:
- 2 retries with backoff (1s → 2s)
- Never crashes registration endpoint
- Returns success/failure status
- Detailed logging
"""

import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Thread pool for async email sending
executor = ThreadPoolExecutor(max_workers=2)


class EmailSendError(Exception):
    """Custom exception for email sending failures"""
    pass


async def send_email_with_retry(
    to_email: str,
    subject: str,
    body: str,
    max_retries: int = 2,
    initial_delay: float = 1.0
) -> bool:
    """
    Send email with retry logic and exponential backoff.
    
    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body (HTML or plain text)
        max_retries: Maximum retry attempts (default 2)
        initial_delay: Initial retry delay in seconds (default 1.0s)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            logger.info(f"📧 Sending email (attempt {retry_count + 1}/{max_retries + 1}): {to_email}")
            
            # Send in thread pool to avoid blocking
            await _send_sync_in_executor(to_email, subject, body)
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            retry_count += 1
            last_error = str(e)
            
            if retry_count <= max_retries:
                delay = initial_delay * (2 ** (retry_count - 1))
                logger.warning(
                    f"⚠️ Email send failed (attempt {retry_count}/{max_retries + 1}): {last_error}"
                    f" - Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"❌ Email send failed after {max_retries + 1} attempts: {last_error}"
                )
    
    return False


async def _send_sync_in_executor(to_email: str, subject: str, body: str) -> None:
    """
    Execute synchronous email sending in thread pool.
    
    Args:
        to_email: Recipient
        subject: Subject line
        body: Email body
    
    Raises:
        EmailSendError: If sending fails
    """
    def _send():
        """Sync email send function"""
        try:
            if not settings.SMTP_ENABLED:
                logger.warning("⚠️ SMTP not configured - email not sent")
                raise EmailSendError("SMTP not configured")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach body
            if '<html>' in body.lower() or '<p>' in body.lower():
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send via SMTP
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error: {str(e)}")
            raise EmailSendError(f"SMTP error: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Email send error: {str(e)}")
            raise EmailSendError(f"Email error: {str(e)}")
    
    # Run in thread pool
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _send)


def create_registration_email(
    team_name: str,
    team_id: str,
    captain_name: str,
    church_name: str,
    player_count: int
) -> str:
    """
    Create HTML email template for registration confirmation.
    
    Args:
        team_name: Team name
        team_id: Generated team ID
        captain_name: Captain name
        church_name: Church name
        player_count: Number of players
    
    Returns:
        str: HTML email body
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #FFCC29 0%, #002B5C 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .section {{ background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #FFCC29; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏏 Team Registration Confirmed!</h1>
                <p>Welcome to ICCT26 Cricket Tournament</p>
            </div>
            
            <div class="content">
                <p>Dear <strong>{captain_name}</strong>,</p>
                <p>Congratulations! Your team <strong>{team_name}</strong> has been successfully registered.</p>
                
                <div class="section">
                    <h3>📋 Registration Details</h3>
                    <p><strong>Team ID:</strong> {team_id}</p>
                    <p><strong>Team Name:</strong> {team_name}</p>
                    <p><strong>Church:</strong> {church_name}</p>
                    <p><strong>Players:</strong> {player_count}</p>
                </div>
                
                <div class="section">
                    <h3>✅ Next Steps</h3>
                    <ul>
                        <li>Save your Team ID: <strong>{team_id}</strong></li>
                        <li>Check email for match schedule updates</li>
                        <li>Review tournament rules</li>
                        <li>Arrive 30 minutes before match time</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated confirmation. Please do not reply.</p>
                <p>&copy; 2025-2026 ICCT26 Tournament. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
