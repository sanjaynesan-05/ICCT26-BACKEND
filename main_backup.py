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

# Pydantic models for registration
class PlayerDetails(BaseModel):
    """Player information model matching form card fields"""
    name: str = Field(..., description="Player full name (required)")
    age: int = Field(..., description="Player age (required; min=15, max=60)", ge=15, le=60)
    phone: str = Field(..., description="Player phone number (required)")
    role: str = Field(..., description="Player role (required; options: Batsman, Bowler, All-Rounder, Wicket Keeper)")
    aadharFile: Optional[str] = Field(None, description="Aadhar Card file (base64 or file URL; required)")
    subscriptionFile: Optional[str] = Field(None, description="Subscription Card file (base64 or file URL; required)")

class CaptainInfo(BaseModel):
    """Captain information model"""
    name: str = Field(..., description="Captain full name (required)")
    phone: str = Field(..., description="Captain phone number (required)")
    whatsapp: str = Field(..., description="Captain WhatsApp number (required; max 10 digits)")
    email: str = Field(..., description="Captain email address (required)")

class ViceCaptainInfo(BaseModel):
    """Vice-captain information model"""
    name: str = Field(..., description="Vice-captain full name (required)")
    phone: str = Field(..., description="Vice-captain phone number (required)")
    whatsapp: str = Field(..., description="Vice-captain WhatsApp number (required; max 10 digits)")
    email: str = Field(..., description="Vice-captain email address (required)")

class TeamRegistration(BaseModel):
    """Complete team registration model matching the form structure (Steps 1-5)"""
    # Step 1: Church & Team Name
    churchName: str = Field(..., description="Church name (required; select from available churches)")
    teamName: str = Field(..., description="Team name (required; unique)")
    
    # Pastor/Church Letter
    pastorLetter: Optional[str] = Field(None, description="Church/Pastor letter file (base64 or URL; required)")
    
    # Steps 2-3: Captain & Vice-Captain Details
    captain: CaptainInfo = Field(..., description="Captain information (required)")
    viceCaptain: ViceCaptainInfo = Field(..., description="Vice-captain information (required)")
    
    # Step 4: Players
    players: List[PlayerDetails] = Field(
        ..., 
        description="List of 11-15 players (required; minimum 11, maximum 15)",
        min_items=11,
        max_items=15
    )
    
    # Step 5: Payment
    paymentReceipt: Optional[str] = Field(None, description="Payment receipt file (base64 or URL; required for final submission)")

def create_email_template_team(data: dict, team_id: str, players: list) -> str:
    """Create HTML email template for team registration with new form structure"""
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
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
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
            <h2>Dear {data.get('captain', {}).get('name', 'Team Captain')},</h2>
            <p>Congratulations! Your team <strong>{data.get('teamName', 'N/A')}</strong> has been successfully registered for the ICCT26 Cricket Tournament 2026.</p>
            
            <div class="details">
                <h3 style="color: #002B5C; margin-top: 0;">🏏 Team Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Team ID:</span>
                    <span class="detail-value"><strong>{team_id}</strong></span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Team Name:</span>
                    <span class="detail-value">{data.get('teamName', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Church:</span>
                    <span class="detail-value">{data.get('churchName', 'N/A')}</span>
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
                <h3 style="color: #002B5C; margin-top: 0;">� Registration Checklist</h3>
                <div class="detail-row">
                    <span class="detail-label">✅ Church Letter:</span>
                    <span class="detail-value">Uploaded</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">✅ Player Documents:</span>
                    <span class="detail-value">All Aadhar & Subscription Cards Uploaded</span>
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">✅ Payment Receipt:</span>
                    <span class="detail-value">Submitted</span>
                </div>
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
            
            <h3>🎯 What's Next?</h3>
            <ul>
                <li>Keep your Team ID safe: <strong>{team_id}</strong></li>
                <li>Check your email for match schedule updates</li>
                <li>Review tournament rules on our website</li>
                <li>Prepare your team for exciting matches</li>
                <li>Arrive 30 minutes before match time</li>
            </ul>
            
            <p><strong>Important:</strong> Please save this email for your records. Your Team ID <strong>{team_id}</strong> is required for tournament participation.</p>
            
            <p>If you have any questions or concerns, feel free to reach out to our support team.</p>
            
            <p>Best of luck to {data.get('teamName', 'your team')}! Play well and have fun! 🏏</p>
            
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
            
            <h3>� What's Next?</h3>
            <ul>
                <li>Keep your Team ID safe: <strong>{team_id}</strong></li>
                <li>Check your email for match schedule updates</li>
                <li>Review tournament rules on our website</li>
                <li>Prepare your team for exciting matches</li>
                <li>Arrive 30 minutes before match time</li>
            </ul>
            
            <p><strong>Important:</strong> Please save this email for your records. Your Team ID <strong>{team_id}</strong> is required for tournament participation.</p>
            
            <p>If you have any questions or concerns, feel free to reach out to our support team.</p>
            
            <p>Best of luck to {data['teamName']}! Play well and have fun! 🏏</p>
            
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

def send_confirmation_email(to_email: str, subject: str, html_content: str, captain_name: str) -> dict:
    """Send confirmation email using SMTP"""
    try:
        # Check if SMTP is configured
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print("⚠️  SMTP credentials not configured. Email not sent.")
            return {
                "success": False,
                "message": "SMTP not configured"
            }
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server and send email
        print(f"📧 Sending confirmation email to {to_email}...")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {captain_name} ({to_email})")
        return {
            "success": True,
            "message": f"Email sent to {to_email}"
        }
    
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}"
        }

def get_google_credentials():
    """Load Google credentials from environment variables or file"""
    try:
        # Check if environment variables are set
        if os.getenv('GOOGLE_PROJECT_ID'):
            # Use environment variables (recommended for production)
            private_key = os.getenv('GOOGLE_PRIVATE_KEY', '')
            
            # Handle newline characters in private key
            if '\\n' in private_key:
                private_key = private_key.replace('\\n', '\n')
            
            creds_info = {
                "type": os.getenv('GOOGLE_CREDENTIALS_TYPE', 'service_account'),
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": private_key,
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": os.getenv('GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                "token_uri": os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
                "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN', 'googleapis.com')
            }
            
            env_name = os.getenv('ENVIRONMENT', 'production')
            print(f"✓ Using environment variables for credentials ({env_name})")
            
        elif os.path.exists('credentials.json'):
            # Fallback to local JSON file (for local development only)
            with open('credentials.json', 'r') as f:
                creds_info = json.load(f)
            print("⚠️  Using local credentials.json file (development only)")
            print("⚠️  For production, use environment variables!")
        
        else:
            raise FileNotFoundError(
                "No credentials found! Please either:\n"
                "1. Set environment variables (recommended for production)\n"
                "2. Place credentials.json file in the project root (development only)"
            )
        
        # Define required scopes for Google Sheets and Drive
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Create credentials and authorize client
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        return client
    
    except FileNotFoundError as e:
        print(f"❌ Credentials Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        traceback.print_exc()
        return None

def save_to_google_sheet(data: dict, team_id: str, players: list) -> dict:
    """
    Save team registration data to Google Sheets
    """
    try:
        client = get_google_credentials()
        if not client:
            return {"error": "Failed to authenticate with Google Sheets"}
        
        # Get Spreadsheet ID from environment
        spreadsheet_id = os.getenv('SPREADSHEET_ID', '1NXwX5RkuPMPxOonmD7cJDjCK5sxhUnvytwj7O3FMyuQ')
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        # Get or create worksheets
        try:
            team_sheet = spreadsheet.get_worksheet(0)  # First sheet for teams
            print(f"Opened team information worksheet: {team_sheet.title}")
        except Exception as e:
            print(f"Error opening team worksheet: {e}")
            return {"error": "Failed to open team worksheet"}
        
        try:
            player_sheet = spreadsheet.get_worksheet(1)  # Second sheet for players
            print(f"Opened player details worksheet: {player_sheet.title}")
        except:
            # Create second sheet if it doesn't exist
            try:
                player_sheet = spreadsheet.add_worksheet("Player Details", 1000, 10)
                print(f"Created player details worksheet")
            except Exception as e:
                print(f"Error creating player worksheet: {e}")
                return {"error": "Failed to create player worksheet"}
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create headers for team sheet if empty
        try:
            headers = team_sheet.row_values(1)
            if not headers or len(headers) == 0:
                team_sheet.append_row([
                    "Team ID", "Team Name", "Church Name", "Captain Name", "Captain Phone", 
                    "Captain Email", "Vice-Captain Name", "Vice-Captain Phone", 
                    "Vice-Captain Email", "Payment Receipt", "Player Count", "Timestamp"
                ])
                print("Created headers for team information sheet")
        except Exception as e:
            print(f"Error checking team headers: {e}")
        
        # Create headers for player sheet if empty
        try:
            headers = player_sheet.row_values(1)
            if not headers or len(headers) == 0:
                player_sheet.append_row([
                    "Team ID", "Team Name", "Player Name", "Phone", "Email", 
                    "Role", "Jersey Number", "Timestamp"
                ])
                print("Created headers for player details sheet")
        except Exception as e:
            print(f"Error checking player headers: {e}")
        
        # Check for duplicate registration (based on team_name + payment_receipt)
        try:
            all_records = team_sheet.get_all_records()
            for record in all_records:
                existing_team = str(record.get('Team Name', '')).strip()
                existing_receipt = str(record.get('Payment Receipt', '')).strip()
                
                if (existing_team == data['teamName'].strip() and 
                    existing_receipt == data['paymentReceipt'].strip()):
                    return {
                        "error": "Duplicate registration",
                        "message": f"Team '{data['teamName']}' with payment receipt '{data['paymentReceipt']}' already exists"
                    }
        except Exception as e:
            print(f"Error checking duplicates: {e}")
        
        # Append team information row
        team_row_data = [
            team_id,
            data['teamName'],
            data['churchName'],
            data['captainName'],
            data['captainPhone'],
            data['captainEmail'],
            data['viceCaptainName'],
            data['viceCaptainPhone'],
            data['viceCaptainEmail'],
            data['paymentReceipt'],
            len(players),
            timestamp
        ]
        
        team_sheet.append_row(team_row_data)
        print(f"Successfully saved team information: {data['teamName']} ({team_id})")
        
        # Append player details rows
        for player in players:
            player_row_data = [
                team_id,
                data['teamName'],
                player['name'],
                player['phone'],
                player['email'],
                player['role'],
                player['jerseyNumber'],
                timestamp
            ]
            player_sheet.append_row(player_row_data)
        print(f"Successfully saved {len(players)} player records for team {team_id}")
        
        # Send confirmation email after successful registration
        email_result = {"success": False, "message": "Email not sent"}
        try:
            html_content = create_email_template_team(data, team_id, players)
            subject = f"🏏 ICCT26 Team Registration Confirmed - {data['teamName']}"
            
            email_result = send_confirmation_email(
                to_email=data['captainEmail'],
                subject=subject,
                html_content=html_content,
                captain_name=data['captainName']
            )
        except Exception as email_error:
            print(f"⚠️  Email sending failed but registration successful: {email_error}")
        
        return {
            "success": True,
            "message": "Team registration saved successfully",
            "team_id": team_id,
            "email_sent": email_result.get('success', False),
            "data": {
                **data,
                "team_id": team_id,
                "player_count": len(players),
                "timestamp": timestamp
            }
        }
    
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")
        traceback.print_exc()
        return {"error": f"Failed to save registration: {str(e)}"}

def generate_team_id(client) -> str:
    """Generate next sequential team ID (ICCT26-XXXX format)"""
    try:
        spreadsheet_id = os.getenv('SPREADSHEET_ID', '1NXwX5RkuPMPxOonmD7cJDjCK5sxhUnvytwj7O3FMyuQ')
        spreadsheet = client.open_by_key(spreadsheet_id)
        team_sheet = spreadsheet.get_worksheet(0)
        
        # Get all records and find the highest number
        all_records = team_sheet.get_all_records()
        max_number = 0
        
        for record in all_records:
            team_id = str(record.get('Team ID', '')).strip()
            if team_id.startswith('ICCT26-'):
                try:
                    number = int(team_id.replace('ICCT26-', ''))
                    max_number = max(max_number, number)
                except:
                    pass
        
        next_number = max_number + 1
        return f"ICCT26-{next_number:04d}"
    except Exception as e:
        print(f"Error generating team ID: {e}")
        return "ICCT26-0001"

def process_registration_queue():
    """Background worker to process team registrations from queue"""
    print("Started team registration queue processor")
    while True:
        try:
            # Get registration from queue (blocking call)
            registration_data, players, result_callback = registration_queue.get()
            
            print(f"Processing team registration from queue: {registration_data.get('teamName')}")
            
            # Generate unique team ID
            client = get_google_credentials()
            if client:
                team_id = generate_team_id(client)
            else:
                team_id = "ICCT26-0000"
            
            # Save to Google Sheets
            result = save_to_google_sheet(registration_data, team_id, players)
            
            # Call callback with result if provided
            if result_callback:
                result_callback(result)
            
            # Mark task as done
            registration_queue.task_done()
            
        except Exception as e:
            print(f"Error in queue processor: {e}")
            traceback.print_exc()
            registration_queue.task_done()

# Start background worker thread
worker_thread = threading.Thread(target=process_registration_queue, daemon=True)
worker_thread.start()

# Create FastAPI app
app = FastAPI(
    title="ICCT26 Cricket Tournament Registration API",
    description="Asynchronous API for handling cricket team registrations with Google Sheets integration",
    version="1.0.0"
)

# Configure CORS based on environment
allowed_origins_env = os.getenv('ALLOWED_ORIGINS', '*')
if allowed_origins_env == '*':
    allowed_origins = ["*"]
else:
    # Split comma-separated origins
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(',')]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/register/team")
async def register_team(registration: TeamRegistration, background_tasks: BackgroundTasks):
    """
    Register a cricket team with all player details
    """
    try:
        print(f"Received team registration request: {registration.teamName}")
        
        # Validate player count
        if len(registration.players) < 11 or len(registration.players) > 15:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid player count",
                    "message": "Team must have between 11-15 players"
                }
            )
        
        # Convert to dict
        team_data = {
            "churchName": registration.churchName,
            "teamName": registration.teamName,
            "pastorLetter": registration.pastorLetter,
            "captainName": registration.captainName,
            "captainPhone": registration.captainPhone,
            "captainWhatsapp": registration.captainWhatsapp,
            "captainEmail": registration.captainEmail,
            "viceCaptainName": registration.viceCaptainName,
            "viceCaptainPhone": registration.viceCaptainPhone,
            "viceCaptainWhatsapp": registration.viceCaptainWhatsapp,
            "viceCaptainEmail": registration.viceCaptainEmail,
            "paymentReceipt": registration.paymentReceipt
        }
        
        players = [player.dict() for player in registration.players]
        
        def callback(result):
            pass  # Callback for queue processing
        
        # Add to queue for processing
        registration_queue.put((team_data, players, callback))
        
        # Return immediate response - registration is queued
        return {
            "success": True,
            "message": "Team registration queued successfully",
            "status": "processing",
            "data": {
                "teamName": registration.teamName,
                "churchName": registration.churchName,
                "captainName": registration.captainName,
                "playerCount": len(players),
                "queuedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in team registration endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )

@app.get("/queue/status")
async def get_queue_status():
    """Get current queue status"""
    return {
        "queue_size": registration_queue.qsize(),
        "worker_active": worker_thread.is_alive(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/")
async def home():
    """Home endpoint with API information"""
    return {
        "message": "ICCT26 Cricket Tournament Registration API - Asynchronous Team Registration System",
        "version": "1.0.0",
        "event": "ICCT26 Cricket Tournament 2026",
        "organizer": "CSI St. Peter's Church, Coimbatore",
        "features": [
            "Asynchronous queue-based processing",
            "Google Sheets integration",
            "Automated email confirmations",
            "Duplicate detection",
            "Team and player management"
        ],
        "endpoints": {
            "/": "GET - API documentation",
            "/register/team": "POST - Team registration endpoint",
            "/queue/status": "GET - Queue status monitoring",
            "/docs": "GET - Swagger UI documentation",
            "/redoc": "GET - ReDoc documentation"
        },
        "team_registration": {
            "method": "POST",
            "endpoint": "/register/team",
        "team_registration": {
            "method": "POST",
            "endpoint": "/register/team",
            "fields": {
                "churchName": "Church name (required)",
                "teamName": "Team name (required, unique)",
                "pastorLetter": "Pastor letter (optional)",
                "captainName": "Captain name (required)",
                "captainPhone": "Captain phone (required)",
                "captainWhatsapp": "Captain WhatsApp (required)",
                "captainEmail": "Captain email (required)",
                "viceCaptainName": "Vice-captain name (required)",
                "viceCaptainPhone": "Vice-captain phone (required)",
                "viceCaptainWhatsapp": "Vice-captain WhatsApp (required)",
                "viceCaptainEmail": "Vice-captain email (required)",
                "paymentReceipt": "Payment receipt number (required)",
                "players": "List of 11-15 players (required)"
            },
            "example": {
                "churchName": "CSI St. Peter's Church",
                "teamName": "Thunder Strikers",
                "captainName": "John Doe",
                "captainPhone": "+919876543210",
                "captainWhatsapp": "919876543210",
                "captainEmail": "john.doe@example.com",
                "viceCaptainName": "Jane Smith",
                "viceCaptainPhone": "+919123456789",
                "viceCaptainWhatsapp": "919123456789",
                "viceCaptainEmail": "jane.smith@example.com",
                "paymentReceipt": "TXN123456789",
                "players": [
                    {
                        "name": "John Doe",
                        "phone": "+919876543210",
                        "email": "john.doe@example.com",
                        "role": "Captain",
                        "jerseyNumber": "1"
                    }
                ]
            }
        },
        "notes": [
            "All registrations are processed asynchronously",
            "Queue system ensures no data loss",
            "Duplicate registrations are automatically detected (team_name + payment_receipt)",
            "Timestamps are automatically added",
            "Team IDs are auto-generated in ICCT26-XXXX format",
            "Make sure service account has edit access to Google Sheets"
        ]
    }
    }

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    environment = os.getenv('ENVIRONMENT', 'development')
    
    print("=" * 60)
    print("🏏 ICCT26 Cricket Tournament Registration API Starting...")
    print("=" * 60)
    print(f"Event: ICCT26 Cricket Tournament 2026")
    print(f"Organizer: CSI St. Peter's Church, Coimbatore")
    print(f"Environment: {environment.upper()}")
    print(f"Port: {os.getenv('PORT', '8000')}")
    print(f"CORS Origins: {os.getenv('ALLOWED_ORIGINS', '*')}")
    print("=" * 60)
    print("✓ Environment variables loaded")
    print("✓ Background worker thread started")
    print("✓ Queue system initialized")
    print("✓ Google Sheets integration ready")
    
    # Test credentials on startup
    client = get_google_credentials()
    if client:
        print("✓ Google Cloud credentials validated successfully")
    else:
        print("❌ WARNING: Failed to validate Google credentials!")
        print("   Please check your environment variables or credentials.json")
    
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print("Waiting for queue to finish processing...")
    registration_queue.join()
    print("ICCT26 Cricket Tournament Registration API shutting down...")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting ICCT26 Cricket Tournament Registration API on port {port}...")
    print(f"Access API documentation at: http://localhost:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
