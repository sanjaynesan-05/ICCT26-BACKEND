"""
ICCT26 Cricket Tournament Registration API
Clean implementation with SMTP email and database schema
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
import os
import json
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uvicorn

# NEW: Import synchronous database and models
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, engine, Base
from models import Team, Player

# Database imports (keep for old endpoints)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker as async_sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, select, func
from sqlalchemy.dialects.postgresql import JSONB

# Load environment variables
load_dotenv()

# ============================================================
# Async Database Configuration (For old async endpoints)
# ============================================================
DATABASE_URL_ASYNC = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:password@localhost/icct26_db')
if 'postgresql://icctadmin' in DATABASE_URL_ASYNC:
    DATABASE_URL_ASYNC = DATABASE_URL_ASYNC.replace('postgresql://', 'postgresql+asyncpg://')

async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
AsyncBase = declarative_base()

# Define async database models (for old endpoints only)
class TeamRegistrationDB(AsyncBase):
    __tablename__ = "team_registrations"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(50), unique=True, index=True)
    church_name = Column(String(200))
    team_name = Column(String(100))
    pastor_letter = Column(Text, nullable=True)
    payment_receipt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CaptainDB(AsyncBase):
    __tablename__ = "captains"
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    phone = Column(String(15))
    whatsapp = Column(String(10))
    email = Column(String(255))

class ViceCaptainDB(AsyncBase):
    __tablename__ = "vice_captains"
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    phone = Column(String(15))
    whatsapp = Column(String(10))
    email = Column(String(255))

class PlayerDB(AsyncBase):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    age = Column(Integer)
    phone = Column(String(15))
    role = Column(String(20))
    aadhar_file = Column(Text, nullable=True)
    subscription_file = Column(Text, nullable=True)

# ============================================================
# SMTP Configuration
# ============================================================
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', SMTP_USERNAME)
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'ICCT26 Cricket Tournament')

# ============================================================
# Pydantic Models (Request/Response Schemas)
# ============================================================

class PlayerDetails(BaseModel):
    """Player information schema"""
    name: str = Field(..., description="Player full name", min_length=1, max_length=100)
    age: int = Field(..., description="Player age", ge=15, le=60)
    phone: str = Field(..., description="Player phone number", min_length=10, max_length=15)
    role: str = Field(..., description="Player role (Batsman/Bowler/All-Rounder/Wicket Keeper)")
    aadharFile: Optional[str] = Field(None, description="Aadhar file (base64)")
    subscriptionFile: Optional[str] = Field(None, description="Subscription file (base64)")

    @validator('role')
    def validate_role(cls, v):
        valid_roles = ['Batsman', 'Bowler', 'All-Rounder', 'Wicket Keeper']
        if v not in valid_roles:
            raise ValueError(f'Role must be one of {valid_roles}')
        return v


class CaptainInfo(BaseModel):
    """Captain information schema"""
    name: str = Field(..., description="Captain full name", min_length=1, max_length=100)
    phone: str = Field(..., description="Captain phone number", min_length=10, max_length=15)
    whatsapp: str = Field(..., description="Captain WhatsApp number", min_length=10, max_length=10)
    email: EmailStr = Field(..., description="Captain email address")


class ViceCaptainInfo(BaseModel):
    """Vice-Captain information schema"""
    name: str = Field(..., description="Vice-Captain full name", min_length=1, max_length=100)
    phone: str = Field(..., description="Vice-Captain phone number", min_length=10, max_length=15)
    whatsapp: str = Field(..., description="Vice-Captain WhatsApp number", min_length=10, max_length=10)
    email: EmailStr = Field(..., description="Vice-Captain email address")


class TeamRegistration(BaseModel):
    """Team registration schema"""
    churchName: str = Field(..., description="Church name", min_length=1, max_length=200)
    teamName: str = Field(..., description="Team name (unique)", min_length=1, max_length=100)
    pastorLetter: Optional[str] = Field(None, description="Pastor letter (base64)")
    
    captain: CaptainInfo = Field(..., description="Captain details")
    viceCaptain: ViceCaptainInfo = Field(..., description="Vice-Captain details")
    
    players: List[PlayerDetails] = Field(
        ..., 
        description="Player list (11-15 players)",
        min_items=11,
        max_items=15
    )
    
    paymentReceipt: Optional[str] = Field(None, description="Payment receipt (base64)")

    @validator('players')
    def validate_player_count(cls, v):
        if len(v) < 11 or len(v) > 15:
            raise ValueError('Team must have 11-15 players')
        return v


# ============================================================
# Database Functions
# ============================================================

async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(AsyncBase.metadata.create_all)

async def get_db_async():
    """Get async database session for old endpoints"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def save_registration_to_db(session: AsyncSession, registration: TeamRegistration, team_id: str):
    """Save team registration to database"""
    # Create team registration record
    team_db = TeamRegistrationDB(
        team_id=team_id,
        church_name=registration.churchName,
        team_name=registration.teamName,
        pastor_letter=registration.pastorLetter,
        payment_receipt=registration.paymentReceipt
    )
    session.add(team_db)
    await session.flush()  # Get the ID

    # Create captain record
    captain_db = CaptainDB(
        registration_id=team_db.id,
        name=registration.captain.name,
        phone=registration.captain.phone,
        whatsapp=registration.captain.whatsapp,
        email=registration.captain.email
    )
    session.add(captain_db)

    # Create vice-captain record
    vice_captain_db = ViceCaptainDB(
        registration_id=team_db.id,
        name=registration.viceCaptain.name,
        phone=registration.viceCaptain.phone,
        whatsapp=registration.viceCaptain.whatsapp,
        email=registration.viceCaptain.email
    )
    session.add(vice_captain_db)

    # Create player records
    for player in registration.players:
        player_db = PlayerDB(
            registration_id=team_db.id,
            name=player.name,
            age=player.age,
            phone=player.phone,
            role=player.role,
            aadhar_file=player.aadharFile,
            subscription_file=player.subscriptionFile
        )
        session.add(player_db)

    await session.commit()
    return team_db.id


# ============================================================
# SMTP Email Functions
# ============================================================

def create_confirmation_email(team_name: str, captain_name: str, church_name: str, 
                             team_id: str, players: List[PlayerDetails]) -> str:
    """Create HTML email template for registration confirmation"""
    
    players_html = ""
    for idx, player in enumerate(players, 1):
        players_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{idx}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{player.name}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{player.age}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{player.role}</td>
        </tr>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #FFCC29 0%, #002B5C 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
                border-radius: 0 0 5px 5px;
            }}
            .section {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #FFCC29;
                border-radius: 3px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            th {{
                background: #002B5C;
                color: white;
                padding: 10px;
                text-align: left;
            }}
            .footer {{
                background: #333;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 0 0 5px 5px;
                font-size: 12px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏏 Team Registration Confirmed!</h1>
                <p>Welcome to ICCT26 Cricket Tournament 2026</p>
            </div>
            
            <div class="content">
                <p>Dear <strong>{captain_name}</strong>,</p>
                <p>Congratulations! Your team <strong>{team_name}</strong> has been successfully registered for 
                the ICCT26 Cricket Tournament 2026.</p>
                
                <div class="section">
                    <h3>📋 Registration Details</h3>
                    <p><strong>Team ID:</strong> {team_id}</p>
                    <p><strong>Team Name:</strong> {team_name}</p>
                    <p><strong>Church:</strong> {church_name}</p>
                    <p><strong>Registration Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="section">
                    <h3>👥 Team Roster</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Name</th>
                                <th>Age</th>
                                <th>Role</th>
                            </tr>
                        </thead>
                        <tbody>
                            {players_html}
                        </tbody>
                    </table>
                </div>
                
                <div class="section">
                    <h3>📅 Tournament Information</h3>
                    <p><strong>Event:</strong> ICCT26 Cricket Tournament 2026</p>
                    <p><strong>Dates:</strong> January 24-26, 2026</p>
                    <p><strong>Venue:</strong> CSI St. Peter's Church Cricket Ground</p>
                    <p><strong>Location:</strong> Coimbatore, Tamil Nadu</p>
                    <p><strong>Format:</strong> Red Tennis Ball Cricket</p>
                </div>
                
                <div class="section">
                    <h3>✅ Next Steps</h3>
                    <ul>
                        <li>Save your Team ID: <strong>{team_id}</strong></li>
                        <li>Check your email for match schedule updates</li>
                        <li>Review tournament rules on our website</li>
                        <li>Prepare your team for exciting matches</li>
                        <li>Arrive 30 minutes before match time</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated confirmation email. Please do not reply to this email.</p>
                <p>&copy; 2026 ICCT26 Cricket Tournament. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content


def send_email(to_email: str, subject: str, html_content: str) -> dict:
    """Send email using SMTP"""
    try:
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print(f"⚠️  SMTP not configured. Email not sent to {to_email}")
            return {"success": False, "message": "SMTP not configured"}
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {to_email}")
        return {"success": True, "message": "Email sent successfully"}
        
    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        return {"success": False, "message": str(e)}


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="ICCT26 Cricket Tournament Registration API",
    description="Team registration system with email notifications",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://icct26.netlify.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Database initialization
@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
        print("✅ Database tables initialized")
    except Exception as e:
        print(f"[WARNING] Database initialization failed: {e}")
        print("   Make sure PostgreSQL is running and DATABASE_URL is correct")
        print("   Run: python scripts/setup_database.py for setup instructions")

# ============================================================
# API Endpoints
# ============================================================

@app.get("/")
async def read_root():
    """Home endpoint"""
    return {
        "message": "ICCT26 Cricket Tournament Registration API",
        "version": "1.0.0",
        "status": "active",
        "db": "PostgreSQL Connected"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ICCT26 Registration API",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
def api_status(db: Session = Depends(get_db)):
    """API status endpoint with database check"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "operational",
        "api_version": "1.0.0",
        "database": db_status,
        "email_service": "configured",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/teams")
async def get_teams(db: AsyncSession = Depends(get_db_async)):
    """Get all registered teams"""
    try:
        result = await db.execute(select(TeamRegistrationDB))
        teams = result.scalars().all()
        
        return {
            "success": True,
            "count": len(teams),
            "teams": [
                {
                    "team_id": team.team_id,
                    "team_name": team.team_name,
                    "church_name": team.church_name,
                    "created_at": team.created_at.isoformat() if team.created_at else None
                }
                for team in teams
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/queue/status")
async def queue_status():
    """Queue status endpoint (placeholder for future implementation)"""
    return {
        "status": "active",
        "pending_registrations": 0,
        "processed_registrations": 0,
        "message": "Queue system ready"
    }


# ============================================================
# Admin Panel Endpoints (Using Synchronous DB)
# ============================================================

@app.get("/admin/teams")
def admin_get_teams(db: Session = Depends(get_db)):
    """
    Get all registered teams with player count.
    
    Returns a list of all teams with essential information:
    - Team ID, Name, Church Name
    - Captain and Vice-Captain details
    - Player count
    - Registration date
    - Payment receipt status
    """
    try:
        # Query team registrations with captain info
        registrations = db.query(TeamRegistrationDB).all()
        result = []
        
        for reg in registrations:
            # Get captain
            captain = db.query(CaptainDB).filter(CaptainDB.registration_id == reg.id).first()
            # Get vice captain
            vice_captain = db.query(ViceCaptainDB).filter(ViceCaptainDB.registration_id == reg.id).first()
            # Get player count
            player_count = db.query(PlayerDB).filter(PlayerDB.registration_id == reg.id).count()
            
            result.append({
                "teamId": reg.team_id,
                "teamName": reg.team_name,
                "churchName": reg.church_name,
                "captainName": captain.name if captain else None,
                "captainPhone": captain.phone if captain else None,
                "captainEmail": captain.email if captain else None,
                "viceCaptainName": vice_captain.name if vice_captain else None,
                "viceCaptainPhone": vice_captain.phone if vice_captain else None,
                "viceCaptainEmail": vice_captain.email if vice_captain else None,
                "playerCount": player_count,
                "registrationDate": str(reg.created_at) if reg.created_at else None,
                "paymentReceipt": reg.payment_receipt
            })
        
        return {"success": True, "teams": result}
    
    except Exception as e:
        print(f"❌ Error fetching teams: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/teams/{team_id}")
def admin_get_team_details(team_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific team and its player roster.
    
    Parameters:
    - team_id: The unique team identifier (string, e.g., 'ICCT26-0001')
    
    Returns:
    - Team information (ID, Name, Church, Captain, Vice-Captain, etc.)
    - Complete player roster with all details
    """
    try:
        team = db.query(TeamRegistrationDB).filter(TeamRegistrationDB.team_id == team_id).first()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Get captain
        captain = db.query(CaptainDB).filter(CaptainDB.registration_id == team.id).first()
        # Get vice captain
        vice_captain = db.query(ViceCaptainDB).filter(ViceCaptainDB.registration_id == team.id).first()
        # Get players
        players = db.query(PlayerDB).filter(PlayerDB.registration_id == team.id).all()
        
        return {
            "team": {
                "teamId": team.team_id,
                "teamName": team.team_name,
                "churchName": team.church_name,
                "captain": {
                    "name": captain.name if captain else None,
                    "phone": captain.phone if captain else None,
                    "email": captain.email if captain else None
                } if captain else None,
                "viceCaptain": {
                    "name": vice_captain.name if vice_captain else None,
                    "phone": vice_captain.phone if vice_captain else None,
                    "email": vice_captain.email if vice_captain else None
                } if vice_captain else None,
                "paymentReceipt": team.payment_receipt,
                "registrationDate": str(team.created_at) if team.created_at else None
            },
            "players": [
                {
                    "playerId": p.id,
                    "name": p.name,
                    "age": p.age,
                    "phone": p.phone,
                    "role": p.role
                } for p in players
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching team details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/players/{player_id}")
def admin_get_player_details(player_id: int, db: Session = Depends(get_db)):
    """
    Fetch details of a specific player with team context.
    
    Parameters:
    - player_id: The unique player identifier (integer ID)
    
    Returns:
    - Player information (ID, Name, Age, Phone, Role, etc.)
    - Team information (Team ID, Name, Church)
    """
    try:
        player = db.query(PlayerDB).filter(PlayerDB.id == player_id).first()
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Get team info
        team = db.query(TeamRegistrationDB).filter(TeamRegistrationDB.id == player.registration_id).first()
        
        return {
            "playerId": player.id,
            "name": player.name,
            "age": player.age,
            "phone": player.phone,
            "role": player.role,
            "aadharFile": player.aadhar_file,
            "subscriptionFile": player.subscription_file,
            "team": {
                "teamId": team.team_id if team else None,
                "teamName": team.team_name if team else None,
                "churchName": team.church_name if team else None
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching player details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/register/team")
async def register_team(registration: TeamRegistration, db: AsyncSession = Depends(get_db_async)):
    """Register a team for the tournament"""
    try:
        # Validate input
        if len(registration.players) < 11 or len(registration.players) > 15:
            raise HTTPException(
                status_code=422,
                detail="Team must have 11-15 players"
            )

        # Generate team ID
        team_id = f"ICCT26-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        print(f"\n{'='*60}")
        print(f"📝 New Registration: {registration.teamName}")
        print(f"   Team ID: {team_id}")
        print(f"   Church: {registration.churchName}")
        print(f"   Captain: {registration.captain.name}")
        print(f"   Players: {len(registration.players)}")
        print(f"{'='*60}")

        # Save to database
        db_id = await save_registration_to_db(db, registration, team_id)
        print(f"✅ Saved to database with ID: {db_id}")

        # Send confirmation email to captain
        captain_email = registration.captain.email
        email_subject = f"ICCT26 Registration Confirmed - {team_id}"
        email_html = create_confirmation_email(
            team_name=registration.teamName,
            captain_name=registration.captain.name,
            church_name=registration.churchName,
            team_id=team_id,
            players=registration.players
        )

        email_result = send_email(captain_email, email_subject, email_html)

        return {
            "success": True,
            "message": "Team registration successful",
            "data": {
                "team_id": team_id,
                "team_name": registration.teamName,
                "captain_name": registration.captain.name,
                "players_count": len(registration.players),
                "registered_at": datetime.now().isoformat(),
                "email_sent": email_result.get("success", False),
                "database_saved": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n{'='*60}")
    print(f"[STARTING] ICCT26 Cricket Tournament Registration API")
    print(f"   Starting on port {port}...")
    print(f"{'='*60}\n")
    
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
