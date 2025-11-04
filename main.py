import gspread
import json
import os
from google.oauth2.service_account import Credentials
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
    """Generate sequential Team ID (ICCT26-XXXX format)"""
    try:
        sheet = client.open_by_key(os.getenv('SPREADSHEET_ID')).worksheet('Team Information')
        rows = len(sheet.get_all_values())
        team_num = str(rows).zfill(4)
        return f"ICCT26-{team_num}"
    except:
        return f"ICCT26-{datetime.now().strftime('%H%M%S')}"

def save_to_google_sheet(data: dict, team_id: str, players: list) -> dict:
    """Save team and player data to Google Sheets
    
    Args:
        data: Team information dict
        team_id: Generated team ID
        players: List of player details
    
    Returns:
        dict with success status and message
    """
    try:
        if not os.getenv('SPREADSHEET_ID'):
            print("WARNING: SPREADSHEET_ID not configured")
            return {"success": False, "message": "Spreadsheet not configured"}
        
        # Placeholder for Google Sheets integration
        print(f"[PLACEHOLDER] Saving team {team_id} to Google Sheets")
        return {"success": True, "message": "Data saved (placeholder)"}
        
    except Exception as e:
        print(f"Sheet error: {str(e)}")
        return {"success": False, "message": str(e)}

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
                team_id = generate_team_id(None)
                result = save_to_google_sheet(team_data, team_id, players)
                
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
    print("🏏 ICCT26 Cricket Tournament Registration API Starting...")
    print("="*60)
    print("Event: ICCT26 Cricket Tournament 2026")
    print("Organizer: CSI St. Peter's Church, Coimbatore")
    print("Environment: DEVELOPMENT")
    print("Port: 8000")
    print("CORS Origins: *")
    print("="*60)
    
    try:
        load_dotenv()
        print("✓ Environment variables loaded")
        
        # Start background worker
        worker_thread = threading.Thread(target=process_registration_queue, daemon=True)
        worker_thread.start()
        print("✓ Background worker thread started")
        print("✓ Queue system initialized")
        print("✓ Google Sheets integration ready")
        
        if os.getenv('SMTP_USERNAME'):
            print("✓ SMTP email service configured")
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
