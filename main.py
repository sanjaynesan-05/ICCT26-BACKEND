"""
ICCT26 Cricket Tournament Registration API
Clean implementation with SMTP email and database schema
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
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

# Database imports
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB

# Load environment variables
load_dotenv()

# ============================================================
# Database Configuration
# ============================================================
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:password@localhost/icct26_db')

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

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
# Database Models
# ============================================================

class TeamRegistrationDB(Base):
    __tablename__ = "team_registrations"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(50), unique=True, index=True)
    church_name = Column(String(200))
    team_name = Column(String(100))
    pastor_letter = Column(Text, nullable=True)
    payment_receipt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CaptainDB(Base):
    __tablename__ = "captains"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    phone = Column(String(15))
    whatsapp = Column(String(10))
    email = Column(String(255))

class ViceCaptainDB(Base):
    __tablename__ = "vice_captains"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    phone = Column(String(15))
    whatsapp = Column(String(10))
    email = Column(String(255))

class PlayerDB(Base):
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
# Database Schema Models
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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Get database session"""
    async with async_session() as session:
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
        print(f"⚠️  Database initialization failed: {e}")
        print("💡 Make sure PostgreSQL is running and DATABASE_URL is correct")
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
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ICCT26 Registration API",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/register/team")
async def register_team(registration: TeamRegistration, db: AsyncSession = Depends(get_db)):
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
    print(f"🚀 ICCT26 Cricket Tournament Registration API")
    print(f"   Starting on port {port}...")
    print(f"{'='*60}\n")
    
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
