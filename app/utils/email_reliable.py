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
import re
from html import escape, unescape
from typing import Dict, List, Optional

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


_HTML_MARKER = re.compile(r"<!doctype\s+html|<html[\s>]|<(?:p|div|table|body|br)[\s>/]", re.IGNORECASE)


def _looks_like_html(body: str) -> bool:
    """True for HTML bodies, including <html lang="..."> and <!DOCTYPE html>."""
    return bool(_HTML_MARKER.search(body or ""))


def _html_to_text(html: str) -> str:
    """Readable plain-text fallback for an HTML email."""
    text = re.sub(r"(?is)<(head|style|script)[^>]*>.*?</\1>", "", html)
    text = re.sub(r"(?is)<div[^>]*display:\s*none[^>]*>.*?</div>", "", text)  # hidden preheader
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|tr|h[1-6]|li|table)>", "\n", text)
    text = re.sub(r"(?i)</td>", "  ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text).replace("\xa0", " ")
    lines = [" ".join(line.split()) for line in text.splitlines()]
    out, blank = [], False
    for line in lines:
        if line:
            out.append(line)
            blank = False
        elif not blank and out:
            out.append("")
            blank = True
    return "\n".join(out).strip() + "\n"


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
            
            # Attach body. For HTML send multipart/alternative: plain-text fallback
            # first, HTML last (clients show the last part they can render).
            if _looks_like_html(body):
                msg.attach(MIMEText(_html_to_text(body), 'plain', 'utf-8'))
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
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


def _contact_rows(person: Dict[str, Optional[str]]) -> str:
    """Table rows for a captain / vice-captain block (WhatsApp only if given)."""
    rows = [
        ("Name", person.get("name")),
        ("Phone", person.get("phone")),
        ("Email", person.get("email")),
    ]
    if person.get("whatsapp"):
        rows.append(("WhatsApp", person.get("whatsapp")))
    return "".join(
        f'<tr><td style="padding:4px 12px 4px 0;color:#666;width:90px;">{label}</td>'
        f'<td style="padding:4px 0;"><strong>{escape(value or "-")}</strong></td></tr>'
        for label, value in rows
    )


def create_registration_email(
    team_name: str,
    team_id: str,
    church_name: str,
    captain: Dict[str, Optional[str]],
    vice_captain: Dict[str, Optional[str]],
    players: List[str],
) -> str:
    """
    HTML "registration received" email.

    Args:
        team_name: Team name
        team_id: Generated team ID (e.g. ICCT-001)
        church_name: Church name
        captain / vice_captain: dicts with name, phone, email, whatsapp (whatsapp may be None)
        players: player names in the order they were registered (player_0 first)

    Every user-supplied value is HTML-escaped.
    """
    player_rows = "".join(
        f'<tr style="background:{"#ffffff" if i % 2 else "#f4f6fa"};">'
        f'<td style="padding:6px 10px;border:1px solid #e3e3e3;text-align:center;">{i}</td>'
        f'<td style="padding:6px 10px;border:1px solid #e3e3e3;">{escape(name)}</td>'
        f'<td style="padding:6px 10px;border:1px solid #e3e3e3;color:#666;">{escape(team_id)}-P{i:02d}</td></tr>'
        for i, name in enumerate(players, start=1)
    )
    team_name_html = escape(team_name)
    team_id_html = escape(team_id)
    section = "background:#ffffff;padding:20px;margin:20px 0;border-left:4px solid #FFCC29;"

    return f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;line-height:1.6;color:#333;">
  <div style="max-width:600px;margin:0 auto;padding:20px;">
    <div style="background:#002B5C;background:linear-gradient(135deg,#FFCC29 0%,#002B5C 100%);color:#ffffff;padding:30px;text-align:center;">
      <h1 style="margin:0;">&#127951; Team Registration Received</h1>
      <p style="margin:8px 0 0;">ICCT Cricket Tournament</p>
    </div>

    <div style="background:#f9f9f9;padding:30px;border:1px solid #ddd;">
      <p>Dear <strong>{escape(captain.get("name") or "Captain")}</strong>,</p>
      <p>Your registration for <strong>{team_name_html}</strong> was received and is awaiting administrator review.</p>

      <div style="{section}">
        <h3 style="margin-top:0;">&#128203; Registration Details</h3>
        <table style="border-collapse:collapse;">
          <tr><td style="padding:4px 12px 4px 0;color:#666;width:90px;">Team ID</td><td><strong style="font-size:18px;">{team_id_html}</strong></td></tr>
          <tr><td style="padding:4px 12px 4px 0;color:#666;">Team</td><td><strong>{team_name_html}</strong></td></tr>
          <tr><td style="padding:4px 12px 4px 0;color:#666;">Church</td><td><strong>{escape(church_name)}</strong></td></tr>
          <tr><td style="padding:4px 12px 4px 0;color:#666;">Players</td><td><strong>{len(players)}</strong></td></tr>
          <tr><td style="padding:4px 12px 4px 0;color:#666;">Status</td><td><strong>Pending administrator review</strong></td></tr>
        </table>
      </div>

      <div style="{section}">
        <h3 style="margin-top:0;">&#129506; Captain</h3>
        <table style="border-collapse:collapse;">{_contact_rows(captain)}</table>
      </div>

      <div style="{section}">
        <h3 style="margin-top:0;">&#129309; Vice-Captain</h3>
        <table style="border-collapse:collapse;">{_contact_rows(vice_captain)}</table>
      </div>

      <div style="{section}">
        <h3 style="margin-top:0;">&#128101; Players (registration order)</h3>
        <table style="border-collapse:collapse;width:100%;font-size:14px;">
          <tr style="background:#002B5C;color:#ffffff;">
            <th style="padding:6px 10px;border:1px solid #002B5C;width:40px;">#</th>
            <th style="padding:6px 10px;border:1px solid #002B5C;text-align:left;">Player Name</th>
            <th style="padding:6px 10px;border:1px solid #002B5C;text-align:left;">Player ID</th>
          </tr>
          {player_rows}
        </table>
      </div>

      <div style="{section}">
        <h3 style="margin-top:0;">&#9989; Next Steps</h3>
        <ul>
          <li>Save your Team ID: <strong>{team_id_html}</strong></li>
          <li>Quote it in any correspondence about your registration</li>
          <li>Wait for the administrator's approval update</li>
        </ul>
        <p style="color:#666;font-size:13px;">If any detail above is wrong, contact the tournament organisers and quote your Team ID.</p>
      </div>
    </div>

    <div style="background:#333;color:#ffffff;padding:20px;text-align:center;font-size:12px;">
      <p style="margin:0;">This is an automated message. Please do not reply.</p>
    </div>
  </div>
</body>
</html>
"""
