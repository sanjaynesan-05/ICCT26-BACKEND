import gspread
import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import base64
import traceback
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from datetime import datetime
import asyncio
from typing import Optional, List
import queue
import threading
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', SMTP_USERNAME)
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'ICCT26 Cricket Tournament')

# Thread-safe queue for handling registrations
registration_queue = queue.Queue()

# ============================================================
# Pydantic Models - Updated to match form structure
# ============================================================

class PlayerDetails(BaseModel):
    """Player information model matching PlayerFormCard fields from registration form"""
    name: str = Field(..., description="Player full name (required)")
    age: int = Field(..., description="Player age (required; min=15, max=60)", ge=15, le=60)
    phone: str = Field(..., description="Player phone number (required)")
    role: str = Field(
        ..., 
        description="Player role (required; options: Batsman, Bowler, All-Rounder, Wicket Keeper)"
    )
    aadharFile: Optional[str] = Field(None, description="Aadhar Card file (base64 or file URL; required)")
    subscriptionFile: Optional[str] = Field(None, description="Subscription Card file (base64 or file URL; required)")

class CaptainInfo(BaseModel):
    """Captain information model (Steps 2-3 form fields)"""
    name: str = Field(..., description="Captain full name (required)")
    phone: str = Field(..., description="Captain phone number (required)")
    whatsapp: str = Field(..., description="Captain WhatsApp number (required; max 10 digits)")
    email: str = Field(..., description="Captain email address (required)")

class ViceCaptainInfo(BaseModel):
    """Vice-captain information model (Steps 2-3 form fields)"""
    name: str = Field(..., description="Vice-captain full name (required)")
    phone: str = Field(..., description="Vice-captain phone number (required)")
    whatsapp: str = Field(..., description="Vice-captain WhatsApp number (required; max 10 digits)")
    email: str = Field(..., description="Vice-captain email address (required)")

class TeamRegistration(BaseModel):
    """Complete team registration model matching the registration form structure (Steps 1-5)
    
    Step 1: Church & Team Selection
    Step 2: Captain Details
    Step 3: Vice-Captain Details
    Step 4: Player List (Review)
    Step 5: Payment
    """
    # Step 1: Church & Team Name
    churchName: str = Field(..., description="Church name (required; select from available churches)")
    teamName: str = Field(..., description="Team name (required; unique identifier)")
    pastorLetter: Optional[str] = Field(None, description="Church/Pastor letter file (base64 or URL; required)")
    
    # Steps 2-3: Captain & Vice-Captain Details
    captain: CaptainInfo = Field(..., description="Captain information (required)")
    viceCaptain: ViceCaptainInfo = Field(..., description="Vice-captain information (required)")
    
    # Step 4: Players (11-15 players with individual cards)
    players: List[PlayerDetails] = Field(
        ..., 
        description="List of 11-15 players (required; minimum 11, maximum 15)",
        min_items=11,
        max_items=15
    )
    
    # Step 5: Payment
    paymentReceipt: Optional[str] = Field(None, description="Payment receipt file (base64 or URL; required)")

# ============================================================
# Email Template
# ============================================================

def create_email_template_team(data: dict, team_id: str, players: list) -> str:
    """Create HTML email template for team registration confirmation"""
    players_html = ""
    for idx, player in enumerate(players, 1):
        players_html += f"""
        <div style="padding: 12px 0; border-bottom: 1px solid #eee;">
            <span style="font-weight: bold; color: #002B5C; display: inline-block; width: 30px;">{idx}.</span>
            <span style="color: #333; font-weight: 500;">{player.get('name', 'N/A')}</span>
            <span style="color: #666; font-size: 12px; margin-left: 10px;">
                Age: {player.get('age', 'N/A')} | Role: {player.get('role', 'N/A')}
            </span>
        </div>
        """
    
    captain_name = data.get('captain', {}).get('name', 'Team Captain')
    team_name = data.get('teamName', 'N/A')
    church_name = data.get('churchName', 'N/A')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #FFCC29 0%, #002B5C 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
            }}
            .details {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #FFCC29;
                border-radius: 5px;
            }}
            .detail-row {{
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }}
            .detail-label {{
                font-weight: bold;
                color: #002B5C;
                display: inline-block;
                width: 180px;
            }}
            .detail-value {{
                color: #333;
            }}
            .footer {{
                background: #333;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 0 0 10px 10px;
                font-size: 12px;
            }}
            .success-icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="success-icon">🏏</div>
            <h1>Team Registration Confirmed!</h1>
            <p>Welcome to ICCT26 Cricket Tournament 2026</p>
        </div>
        
        <div class="content">
            <h2>Dear {captain_name},</h2>
            <p>Congratulations! Your team <strong>{team_name}</strong> has been successfully registered for the ICCT26 Cricket Tournament 2026.</p>
            
            <div class="details">
                <h3 style="color: #002B5C; margin-top: 0;">🏏 Team Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Team ID:</span>
                    <span class="detail-value"><strong>{team_id}</strong></span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Team Name:</span>
                    <span class="detail-value">{team_name}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Church:</span>
                    <span class="detail-value">{church_name}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Captain:</span>
                    <span class="detail-value">{data.get('captain', {}).get('name', 'N/A')} ({data.get('captain', {}).get('phone', 'N/A')})</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Vice-Captain:</span>
                    <span class="detail-value">{data.get('viceCaptain', {}).get('name', 'N/A')} ({data.get('viceCaptain', {}).get('phone', 'N/A')})</span>
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">Total Players:</span>
                    <span class="detail-value">{len(players)}</span>
                </div>
            </div>
            
            <div class="details">
                <h3 style="color: #002B5C; margin-top: 0;">👥 Team Roster</h3>
                {players_html}
            </div>
            
            <div class="details">
                <h3 style="color: #002B5C; margin-top: 0;">📋 Registration Checklist</h3>
                <div class="detail-row">
                    <span class="detail-label">✓ Church Letter:</span>
                    <span class="detail-value">Uploaded</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">✓ Player Documents:</span>
                    <span class="detail-value">All Aadhar &amp; Subscription Cards Uploaded</span>
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">✓ Payment Receipt:</span>
                    <span class="detail-value">Submitted</span>
                </div>
            </div>
            
            <div class="details">
                <h3 style="color: #002B5C; margin-top: 0;">📅 Tournament Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Event:</span>
                    <span class="detail-value">ICCT26 Cricket Tournament 2026</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Dates:</span>
                    <span class="detail-value">January 24-26, 2026</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Venue:</span>
                    <span class="detail-value">CSI St. Peter's Church Cricket Ground</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location:</span>
                    <span class="detail-value">Coimbatore, Tamil Nadu</span>
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">Format:</span>
                    <span class="detail-value">Red Tennis Ball Cricket</span>
                </div>
            </div>
            
            <h3>Next Steps</h3>
            <ul>
                <li>Keep your Team ID safe: <strong>{team_id}</strong></li>
                <li>Check your email for match schedule updates</li>
                <li>Review tournament rules on our website</li>
                <li>Prepare your team for exciting matches</li>
                <li>Arrive 30 minutes before match time</li>
            </ul>
            
            <p><strong>Important:</strong> Please save this email for your records. Your Team ID <strong>{team_id}</strong> is required for tournament participation.</p>
            
            <p>If you have any questions or concerns, feel free to reach out to our support team.</p>
            
            <p>Best of luck to {team_name}! Play well and have fun! 🏏</p>
            
            <p>Best regards,<br>
            <strong>ICCT26 Cricket Tournament Team</strong><br>
            CSI St. Peter's Church, Coimbatore</p>
        </div>
        
        <div class="footer">
            <p>This is an automated confirmation email. Please do not reply to this email.</p>
            <p>&copy; 2026 ICCT26 Cricket Tournament. All rights reserved.</p>
        </div>
    </body>
    </html>
    """

def send_confirmation_email(to_email: str, subject: str, html_content: str) -> dict:
    """Send confirmation email using SMTP"""
    try:
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print("WARNING: SMTP credentials not configured. Email not sent.")
            return {"success": False, "message": "SMTP not configured"}
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return {"success": True, "message": "Email sent successfully"}
        
    except Exception as e:
        print(f"Email error: {str(e)}")
        return {"success": False, "message": str(e)}

# ============================================================
# Placeholder functions for future implementation
# ============================================================

def generate_team_id(client) -> str:
    """Generate sequential Team ID (ICCT26-0XX format)"""
    try:
        # Get the next sequential number from Teams_Index sheet
        sheet = client.open_by_key(os.getenv('SPREADSHEET_ID')).worksheet('Teams_Index')
        rows = sheet.get_all_values()
        # Skip header row, so team count is len(rows) - 1
        team_count = len(rows) - 1
        team_num = str(team_count + 1).zfill(3)  # 3 digits for 0XX format
        return f"ICCT26-{team_num}"
    except Exception as e:
        print(f"Warning: Could not generate sequential team ID: {e}")
        # Fallback to timestamp-based ID
        return f"ICCT26-{datetime.now().strftime('%H%M%S')}"

# ============================================================
# Google Drive File Upload Functions
# ============================================================

def upload_file_to_drive(file_data: str, file_name: str, folder_id: str, creds) -> dict:
    """Upload a base64 encoded file to Google Drive
    
    Args:
        file_data: Base64 encoded file data (with or without data URI prefix)
        file_name: Name for the file in Drive
        folder_id: Google Drive folder ID where file will be stored
        creds: Google credentials object
        
    Returns:
        dict with success status, file_id, and web_view_link
    """
    try:
        # Build Drive service
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Parse base64 data
        if ',' in file_data:
            # Remove data URI prefix (e.g., "data:image/png;base64,")
            header, encoded = file_data.split(',', 1)
            file_bytes = base64.b64decode(encoded)
            
            # Extract mime type from header
            if 'data:' in header and ';base64' in header:
                mime_type = header.split('data:')[1].split(';')[0]
            else:
                mime_type = 'application/octet-stream'
        else:
            # Plain base64 without prefix
            file_bytes = base64.b64decode(file_data)
            mime_type = 'application/octet-stream'
        
        # Create file metadata
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        # Create media upload
        media = MediaIoBaseUpload(
            io.BytesIO(file_bytes),
            mimetype=mime_type,
            resumable=True
        )
        
        # Upload file
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink'
        ).execute()
        
        print(f"✅ Uploaded file '{file_name}' to Google Drive (ID: {file.get('id')})")
        
        return {
            "success": True,
            "file_id": file.get('id'),
            "web_view_link": file.get('webViewLink'),
            "web_content_link": file.get('webContentLink')
        }
        
    except Exception as e:
        print(f"❌ Failed to upload file '{file_name}': {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def upload_team_files_to_drive(data: dict, team_id: str, players: list, creds) -> dict:
    """Upload all team files (pastor letter, payment receipt, player documents) to Google Drive
    
    Args:
        data: Team registration data
        team_id: Team ID for organizing files
        players: List of player details with files
        creds: Google credentials object
        
    Returns:
        dict with upload results and file links
    """
    try:
        folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        if not folder_id:
            print("WARNING: GOOGLE_DRIVE_FOLDER_ID not configured")
            return {"success": False, "message": "Drive folder not configured"}
        
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Create team folder
        team_folder_metadata = {
            'name': f"{team_id}_{data.get('teamName', 'Unknown')}",
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder_id]
        }
        team_folder = drive_service.files().create(
            body=team_folder_metadata,
            fields='id'
        ).execute()
        team_folder_id = team_folder.get('id')
        print(f"✅ Created team folder: {team_folder_id}")
        
        results = {
            "team_folder_id": team_folder_id,
            "uploads": []
        }
        
        # Upload pastor letter
        if data.get('pastorLetter'):
            result = upload_file_to_drive(
                data['pastorLetter'],
                f"{team_id}_Pastor_Letter.pdf",
                team_folder_id,
                creds
            )
            results["uploads"].append({"type": "pastor_letter", **result})
        
        # Upload payment receipt
        if data.get('paymentReceipt'):
            result = upload_file_to_drive(
                data['paymentReceipt'],
                f"{team_id}_Payment_Receipt.pdf",
                team_folder_id,
                creds
            )
            results["uploads"].append({"type": "payment_receipt", **result})
        
        # Upload player documents
        for i, player in enumerate(players, 1):
            player_name = player.get('name', f'Player{i}').replace(' ', '_')
            
            # Upload Aadhar card
            if player.get('aadharFile'):
                result = upload_file_to_drive(
                    player['aadharFile'],
                    f"{team_id}_Player{i}_{player_name}_Aadhar.pdf",
                    team_folder_id,
                    creds
                )
                results["uploads"].append({"type": "aadhar", "player": player_name, **result})
            
            # Upload Subscription card
            if player.get('subscriptionFile'):
                result = upload_file_to_drive(
                    player['subscriptionFile'],
                    f"{team_id}_Player{i}_{player_name}_Subscription.pdf",
                    team_folder_id,
                    creds
                )
                results["uploads"].append({"type": "subscription", "player": player_name, **result})
        
        successful_uploads = sum(1 for upload in results["uploads"] if upload.get("success", False))
        total_uploads = len(results["uploads"])
        
        print(f"✅ Uploaded {successful_uploads}/{total_uploads} files to Google Drive")
        
        return {
            "success": True,
            "message": f"Uploaded {successful_uploads}/{total_uploads} files",
            **results
        }
        
    except Exception as e:
        error_msg = f"Drive upload error: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "message": error_msg}

def save_to_google_sheet(data: dict, players: list) -> dict:
    """Save team and player data to Google Sheets - Creates one worksheet per team

    Args:
        data: Team information dict
        players: List of player details

    Returns:
        dict with success status, message, and team_id
    """
    try:
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not spreadsheet_id:
            print("WARNING: SPREADSHEET_ID not configured")
            return {"success": False, "message": "Spreadsheet not configured"}
        
        # Load Google Sheets credentials
        creds_info = {
            "type": os.getenv('GOOGLE_CREDENTIALS_TYPE', 'service_account'),
            "project_id": os.getenv('GOOGLE_PROJECT_ID'),
            "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
            "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
            "client_id": os.getenv('GOOGLE_CLIENT_ID'),
            "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
            "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
            "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
            "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
            "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN', 'googleapis.com')
        }
        
        # Authenticate with Google Sheets and Drive
        creds = Credentials.from_service_account_info(
            creds_info,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ]
        )
        
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        # Generate team ID using the client
        team_id = generate_team_id(client)
        
        # Upload files to Google Drive first to get links
        drive_result = upload_team_files_to_drive(data, team_id, players, creds)
        
        # Create a new worksheet for this team
        sheet_name = f"{team_id}_{data.get('teamName', 'Team')}"[:100]  # Limit to 100 chars
        
        # Check if sheet already exists, if yes add a suffix
        try:
            team_sheet = spreadsheet.worksheet(sheet_name)
            # Sheet exists, add timestamp suffix
            sheet_name = f"{sheet_name}_{datetime.now().strftime('%H%M%S')}"
        except:
            pass
        
        # Create new worksheet for this team (rows: 50, columns: 10)
        team_sheet = spreadsheet.add_worksheet(title=sheet_name, rows=50, cols=10)
        
        print(f"✅ Created worksheet '{sheet_name}' for team {team_id}")
        
        # ============================================================
        # TEAM INFORMATION SECTION
        # ============================================================
        
        captain = data.get('captain', {})
        vice_captain = data.get('viceCaptain', {})
        
        # Row 1: Title
        team_sheet.update('A1', [[f"TEAM REGISTRATION: {team_id}"]])
        team_sheet.format('A1', {
            "textFormat": {"bold": True, "fontSize": 14},
            "horizontalAlignment": "CENTER"
        })
        team_sheet.merge_cells('A1:F1')
        
        # Row 3: Team Details Header
        team_sheet.update('A3', [["TEAM INFORMATION"]])
        team_sheet.format('A3', {"textFormat": {"bold": True, "fontSize": 12}})
        team_sheet.merge_cells('A3:F3')
        
        # Rows 4-10: Team Details
        team_info = [
            ["Team ID:", team_id],
            ["Team Name:", data.get('teamName', 'N/A')],
            ["Church Name:", data.get('churchName', 'N/A')],
            ["Registration Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["Status:", "Registered"],
            ["Total Players:", len(players)],
            ["", ""]  # Empty row
        ]
        team_sheet.update('A4', team_info)
        team_sheet.format('A4:A9', {"textFormat": {"bold": True}})
        
        # ============================================================
        # CAPTAIN & VICE-CAPTAIN SECTION
        # ============================================================
        
        # Row 11: Captain Header
        team_sheet.update('A11', [["CAPTAIN DETAILS"]])
        team_sheet.format('A11', {"textFormat": {"bold": True, "fontSize": 12}})
        team_sheet.merge_cells('A11:F11')
        
        # Rows 12-15: Captain Info
        captain_info = [
            ["Name:", captain.get('name', 'N/A')],
            ["Phone:", captain.get('phone', 'N/A')],
            ["WhatsApp:", captain.get('whatsapp', 'N/A')],
            ["Email:", captain.get('email', 'N/A')]
        ]
        team_sheet.update('A12', captain_info)
        team_sheet.format('A12:A15', {"textFormat": {"bold": True}})
        
        # Row 17: Vice-Captain Header
        team_sheet.update('A17', [["VICE-CAPTAIN DETAILS"]])
        team_sheet.format('A17', {"textFormat": {"bold": True, "fontSize": 12}})
        team_sheet.merge_cells('A17:F17')
        
        # Rows 18-21: Vice-Captain Info
        vice_captain_info = [
            ["Name:", vice_captain.get('name', 'N/A')],
            ["Phone:", vice_captain.get('phone', 'N/A')],
            ["WhatsApp:", vice_captain.get('whatsapp', 'N/A')],
            ["Email:", vice_captain.get('email', 'N/A')]
        ]
        team_sheet.update('A18', vice_captain_info)
        team_sheet.format('A18:A21', {"textFormat": {"bold": True}})
        
        # ============================================================
        # UPLOADED FILES SECTION
        # ============================================================
        
        # Row 23: Files Header
        team_sheet.update('A23', [["UPLOADED FILES"]])
        team_sheet.format('A23', {"textFormat": {"bold": True, "fontSize": 12}})
        team_sheet.merge_cells('A23:F23')
        
        # Rows 24+: File Links
        file_links = []
        if drive_result.get('success'):
            uploads = drive_result.get('uploads', [])
            
            # Pastor Letter
            pastor_letter = next((u for u in uploads if u.get('type') == 'pastor_letter'), None)
            if pastor_letter and pastor_letter.get('success'):
                file_links.append(["Pastor Letter:", pastor_letter.get('web_view_link', 'N/A')])
            else:
                file_links.append(["Pastor Letter:", "Not uploaded"])
            
            # Payment Receipt
            payment_receipt = next((u for u in uploads if u.get('type') == 'payment_receipt'), None)
            if payment_receipt and payment_receipt.get('success'):
                file_links.append(["Payment Receipt:", payment_receipt.get('web_view_link', 'N/A')])
            else:
                file_links.append(["Payment Receipt:", "Not uploaded"])
        else:
            file_links.append(["Files:", "Upload failed - " + drive_result.get('message', 'Unknown error')])
        
        team_sheet.update('A24', file_links)
        team_sheet.format('A24:A25', {"textFormat": {"bold": True}})
        
        # ============================================================
        # PLAYERS SECTION
        # ============================================================
        
        # Row 27: Players Header
        team_sheet.update('A27', [["PLAYERS LIST"]])
        team_sheet.format('A27', {"textFormat": {"bold": True, "fontSize": 12}})
        team_sheet.merge_cells('A27:F27')
        
        # Row 28: Column Headers
        player_headers = [["#", "Name", "Age", "Phone", "Role", "Aadhar Link", "Subscription Link"]]
        team_sheet.update('A28', player_headers)
        team_sheet.format('A28:G28', {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
        })
        
        # Rows 29+: Player Data
        player_data = []
        uploads = drive_result.get('uploads', []) if drive_result.get('success') else []
        
        for i, player in enumerate(players, 1):
            player_name = player.get('name', 'N/A')
            
            # Find Aadhar and Subscription links for this player
            aadhar_link = "Not uploaded"
            subscription_link = "Not uploaded"
            
            for upload in uploads:
                if upload.get('type') == 'aadhar' and upload.get('player', '').replace('_', ' ') == player_name.replace(' ', '_'):
                    if upload.get('success'):
                        aadhar_link = upload.get('web_view_link', 'Error')
                    break
            
            for upload in uploads:
                if upload.get('type') == 'subscription' and upload.get('player', '').replace('_', ' ') == player_name.replace(' ', '_'):
                    if upload.get('success'):
                        subscription_link = upload.get('web_view_link', 'Error')
                    break
            
            player_data.append([
                i,
                player_name,
                player.get('age', 'N/A'),
                player.get('phone', 'N/A'),
                player.get('role', 'N/A'),
                aadhar_link,
                subscription_link
            ])
        
        team_sheet.update('A29', player_data)
        
        # Auto-resize columns
        team_sheet.columns_auto_resize(0, 6)
        
        print(f"✅ Saved complete team data to worksheet '{sheet_name}'")
        
        # ============================================================
        # UPDATE MASTER INDEX SHEET
        # ============================================================
        
        # Get or create master index sheet
        try:
            index_sheet = spreadsheet.worksheet('Teams_Index')
        except:
            index_sheet = spreadsheet.add_worksheet('Teams_Index', 1000, 10)
            # Add headers
            index_sheet.update('A1', [[
                'Team ID', 'Team Name', 'Church Name', 'Captain Name', 
                'Vice-Captain Name', 'Player Count', 'Status', 'Registration Date', 'Sheet Link'
            ]])
            index_sheet.format('A1:I1', {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9}
            })
        
        # Add entry to index
        sheet_link = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={team_sheet.id}"
        index_row = [
            team_id,
            data.get('teamName', 'N/A'),
            data.get('churchName', 'N/A'),
            captain.get('name', 'N/A'),
            vice_captain.get('name', 'N/A'),
            len(players),
            'Registered',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            sheet_link
        ]
        index_sheet.append_row(index_row)
        
        print(f"✅ Updated Teams_Index with link to '{sheet_name}'")
        
        return {
            "success": True,
            "message": f"Team {team_id} saved to dedicated worksheet '{sheet_name}'",
            "team_id": team_id,
            "players_count": len(players),
            "sheet_name": sheet_name,
            "sheet_link": sheet_link,
            "drive_upload": drive_result
        }
        
    except Exception as e:
        error_msg = f"Sheet error: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "message": error_msg}

# ============================================================
# Background Queue Processing
# ============================================================

def process_registration_queue():
    """Process registrations from queue in background thread"""
    print("Started team registration queue processor")
    while True:
        try:
            if not registration_queue.empty():
                item = registration_queue.get(timeout=1)
                team_data, players, callback = item
                result = save_to_google_sheet(team_data, players)
                team_id = result.get('team_id', 'Unknown')
                
                if result.get('success'):
                    html_content = create_email_template_team(team_data, team_id, players)
                    captain_email = team_data.get('captain', {}).get('email', '')
                    if captain_email:
                        send_confirmation_email(captain_email, f"ICCT26 Registration Confirmed - {team_id}", html_content)
                
                if callback:
                    callback(result)
        except:
            pass

# ============================================================
# FastAPI Application Setup
# ============================================================

app = FastAPI(
    title="ICCT26 Cricket Tournament Registration API",
    description="Team registration system with Google Sheets integration",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Home endpoint with API information"""
    return {
        "message": "ICCT26 Cricket Tournament Registration API - Asynchronous Team Registration System",
        "version": "2.0.0",
        "event": "ICCT26 Cricket Tournament 2026",
        "organizer": "CSI St. Peter's Church, Coimbatore",
        "features": [
            "Asynchronous queue-based processing",
            "Google Sheets integration",
            "Automated email confirmations",
            "Duplicate detection",
            "File upload support (Pastor Letter, Aadhar, Subscription Cards, Payment Receipt)"
        ]
    }

@app.post("/register/team")
async def register_team(registration: TeamRegistration):
    """Register a cricket team with 11-15 players
    
    Expected request body matches the TeamRegistration Pydantic model:
    - Church name, team name, pastor letter
    - Captain and vice-captain details
    - 11-15 players with individual information
    - Payment receipt
    """
    try:
        if len(registration.players) < 11 or len(registration.players) > 15:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Invalid player count",
                    "message": "Team must have between 11-15 players"
                }
            )
        
        team_data = registration.dict()
        players = [p.dict() for p in registration.players]
        
        # Queue the registration
        registration_queue.put((team_data, players, None))
        
        return {
            "success": True,
            "message": "Team registration queued successfully",
            "status": "processing",
            "data": {
                "teamName": registration.teamName,
                "churchName": registration.churchName,
                "captainName": registration.captain.name,
                "playerCount": len(registration.players),
                "queuedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for Render monitoring (supports GET and HEAD)"""
    return {
        "status": "healthy",
        "service": "ICCT26 Cricket Tournament Registration API",
        "version": "2.0.0",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/queue/status")
async def queue_status():
    """Get current queue status"""
    return {
        "queue_size": registration_queue.qsize(),
        "worker_active": True,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ============================================================
# Startup and Shutdown Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize background worker thread on startup"""
    print("\n" + "="*60)
    print("ICCT26 Cricket Tournament Registration API Starting...")
    print("="*60)
    print("Event: ICCT26 Cricket Tournament 2026")
    print("Organizer: CSI St. Peter's Church, Coimbatore")
    print("Environment: DEVELOPMENT")
    # Read port from environment to reflect Render-assigned dynamic port in logs
    port = os.environ.get('PORT', '8000')
    print(f"Port: {port}")
    print("CORS Origins: *")
    print("="*60)
    
    try:
        load_dotenv()
        print("[OK] Environment variables loaded")
        
        # Start background worker
        worker_thread = threading.Thread(target=process_registration_queue, daemon=True)
        worker_thread.start()
        print("[OK] Background worker thread started")
        print("[OK] Queue system initialized")
        print("[OK] Google Sheets integration ready")
        
        if os.getenv('SMTP_USERNAME'):
            print("[OK] SMTP email service configured")
        else:
            print("⚠ SMTP not configured (emails disabled)")
        
    except Exception as e:
        print(f"⚠ Startup warning: {str(e)}")
    
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown"""
    print("\nICCT26 Cricket Tournament Registration API shutting down...")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))  # Use Render-assigned port if available
    uvicorn.run("main:app", host="0.0.0.0", port=port)
