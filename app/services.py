"""
Business logic and service functions
Handles email, database operations, and registration logic
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.schemas import PlayerDetails, TeamRegistration

logger = logging.getLogger(__name__)


# ============================================================
# Email Service
# ============================================================

class EmailService:
    """Email service for sending registration confirmations"""
    
    @staticmethod
    def create_confirmation_email(
        team_name: str,
        captain_name: str,
        church_name: str,
        team_id: str,
        players: List[PlayerDetails]
    ) -> str:
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
                    <p>Welcome to {settings.TOURNAMENT_NAME}</p>
                </div>
                
                <div class="content">
                    <p>Dear <strong>{captain_name}</strong>,</p>
                    <p>Congratulations! Your team <strong>{team_name}</strong> has been successfully registered for 
                    the {settings.TOURNAMENT_NAME}.</p>
                    
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
                        <p><strong>Event:</strong> {settings.TOURNAMENT_NAME}</p>
                        <p><strong>Dates:</strong> {settings.TOURNAMENT_DATES}</p>
                        <p><strong>Venue:</strong> {settings.TOURNAMENT_VENUE}</p>
                        <p><strong>Location:</strong> {settings.TOURNAMENT_LOCATION}</p>
                        <p><strong>Format:</strong> {settings.TOURNAMENT_FORMAT}</p>
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
                    <p>&copy; 2025-2026 {settings.TOURNAMENT_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> Dict[str, Any]:
        """Send email using SMTP"""
        
        try:
            if not settings.SMTP_ENABLED:
                logger.warning(f"SMTP not configured. Email not sent to {to_email}")
                return {"success": False, "message": "SMTP not configured"}
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return {"success": True, "message": "Email sent successfully"}
            
        except Exception as e:
            logger.error(f"Email error: {str(e)}")
            return {"success": False, "message": str(e)}


# ============================================================
# Database Service
# ============================================================

class DatabaseService:
    """Database service for registration and queries"""
    
    @staticmethod
    async def save_registration_to_db(
        session: AsyncSession,
        registration: TeamRegistration,
        team_id: str
    ) -> int:
        """Save team registration to database"""
        
        try:
            # Import models
            from models import Team, Player
            
            # Create team record with all information
            team_db = Team(
                team_id=team_id,
                team_name=registration.teamName,
                church_name=registration.churchName,
                captain_name=registration.captain.name,
                captain_phone=registration.captain.phone,
                captain_email=registration.captain.email,
                captain_whatsapp=registration.captain.whatsapp,
                vice_captain_name=registration.viceCaptain.name,
                vice_captain_phone=registration.viceCaptain.phone,
                vice_captain_email=registration.viceCaptain.email,
                vice_captain_whatsapp=registration.viceCaptain.whatsapp,
                payment_receipt=registration.paymentReceipt,
                pastor_letter=registration.pastorLetter
            )
            session.add(team_db)
            await session.flush()
            
            # Create player records
            for idx, player in enumerate(registration.players, 1):
                player_id = f"{team_id}-P{idx:02d}"  # e.g., ICCT26-0001-P01
                player_db = Player(
                    player_id=player_id,
                    team_id=team_id,
                    name=player.name,
                    age=player.age,
                    phone=player.phone,
                    email=player.email if hasattr(player, 'email') else f"{player.name.lower().replace(' ', '')}@example.com",
                    role=player.role,
                    jersey_number=str(idx),  # Default jersey number
                    aadhar_file=player.aadharFile,
                    subscription_file=player.subscriptionFile
                )
                session.add(player_db)
            
            await session.commit()
            logger.info(f"Registration saved to database with Team ID: {team_id}")
            return team_db.id
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to save registration: {str(e)}")
            raise

    @staticmethod
    def get_all_teams(db: Session) -> List[Dict[str, Any]]:
        """Get all registered teams"""
        
        try:
            query = text("""
                SELECT t.id, t.team_id, t.team_name, t.church_name, 
                       t.payment_receipt, t.created_at,
                       t.captain_name, t.captain_phone, t.captain_email,
                       t.vice_captain_name, t.vice_captain_phone, t.vice_captain_email,
                       COUNT(p.id) as player_count
                FROM teams t
                LEFT JOIN players p ON p.team_id = t.team_id
                GROUP BY t.id
                ORDER BY t.created_at DESC
            """)
            
            result = db.execute(query).fetchall()
            teams = []
            
            for row in result:
                teams.append({
                    "teamId": row.team_id,
                    "teamName": row.team_name,
                    "churchName": row.church_name,
                    "captainName": row.captain_name,
                    "captainPhone": row.captain_phone,
                    "captainEmail": row.captain_email,
                    "viceCaptainName": row.vice_captain_name,
                    "viceCaptainPhone": row.vice_captain_phone,
                    "viceCaptainEmail": row.vice_captain_email,
                    "playerCount": row.player_count,
                    "registrationDate": str(row.created_at) if row.created_at else None,
                    "paymentReceipt": row.payment_receipt
                })
            
            return teams
            
        except Exception as e:
            logger.error(f"Error fetching teams: {str(e)}")
            raise

    @staticmethod
    def get_team_details(db: Session, team_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific team"""
        
        try:
            team_query = text("""
                SELECT id, team_id, team_name, church_name, payment_receipt, created_at,
                       captain_name, captain_phone, captain_email,
                       vice_captain_name, vice_captain_phone, vice_captain_email
                FROM teams
                WHERE team_id = :team_id
            """)
            
            team_result = db.execute(team_query, {"team_id": team_id}).fetchone()
            
            if not team_result:
                return None
            
            # Get players for this team
            players_query = text("""
                SELECT id, player_id, name, age, phone, email, role, jersey_number
                FROM players
                WHERE team_id = :team_id
                ORDER BY id
            """)
            
            players_result = db.execute(
                players_query,
                {"team_id": team_id}
            ).fetchall()
            
            return {
                "team": {
                    "teamId": team_result.team_id,
                    "teamName": team_result.team_name,
                    "churchName": team_result.church_name,
                    "captain": {
                        "name": team_result.captain_name,
                        "phone": team_result.captain_phone,
                        "email": team_result.captain_email
                    } if team_result.captain_name else None,
                    "viceCaptain": {
                        "name": team_result.vice_captain_name,
                        "phone": team_result.vice_captain_phone,
                        "email": team_result.vice_captain_email
                    } if team_result.vice_captain_name else None,
                    "paymentReceipt": team_result.payment_receipt,
                    "registrationDate": str(team_result.created_at) if team_result.created_at else None
                },
                "players": [
                    {
                        "playerId": p.player_id,
                        "name": p.name,
                        "age": p.age,
                        "phone": p.phone,
                        "email": p.email,
                        "role": p.role,
                        "jerseyNumber": p.jersey_number
                    } for p in players_result
                ]
            }
            
        except Exception as e:
            logger.error(f"Error fetching team details: {str(e)}")
            raise

    @staticmethod
    def get_player_details(db: Session, player_id: int) -> Dict[str, Any]:
        """Fetch details of a specific player"""
        
        try:
            player_query = text("""
                SELECT p.id, p.player_id, p.name, p.age, p.phone, p.email, p.role, p.jersey_number,
                       p.aadhar_file, p.subscription_file,
                       t.team_id, t.team_name, t.church_name
                FROM players p
                LEFT JOIN teams t ON t.team_id = p.team_id
                WHERE p.id = :player_id
            """)
            
            player_result = db.execute(player_query, {"player_id": player_id}).fetchone()
            
            if not player_result:
                return None
            
            return {
                "playerId": player_result.player_id,
                "name": player_result.name,
                "age": player_result.age,
                "phone": player_result.phone,
                "email": player_result.email,
                "role": player_result.role,
                "jerseyNumber": player_result.jersey_number,
                "aadharFile": player_result.aadhar_file,
                "subscriptionFile": player_result.subscription_file,
                "team": {
                    "teamId": player_result.team_id,
                    "teamName": player_result.team_name,
                    "churchName": player_result.church_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching player details: {str(e)}")
            raise

    @staticmethod
    def create_tables(db: Session) -> bool:
        """Create database tables if they don't exist"""
        
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS team_registrations (
                    id SERIAL PRIMARY KEY,
                    team_id VARCHAR(50) UNIQUE NOT NULL,
                    church_name VARCHAR(200) NOT NULL,
                    team_name VARCHAR(100) NOT NULL,
                    pastor_letter TEXT,
                    payment_receipt TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS captains (
                    id SERIAL PRIMARY KEY,
                    registration_id INTEGER REFERENCES team_registrations(id),
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    whatsapp VARCHAR(20) NOT NULL,
                    email VARCHAR(255) NOT NULL
                )
            """))
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS vice_captains (
                    id SERIAL PRIMARY KEY,
                    registration_id INTEGER REFERENCES team_registrations(id),
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    whatsapp VARCHAR(20) NOT NULL,
                    email VARCHAR(255) NOT NULL
                )
            """))
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    registration_id INTEGER REFERENCES team_registrations(id),
                    name VARCHAR(100) NOT NULL,
                    age INTEGER NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    aadhar_file TEXT,
                    subscription_file TEXT
                )
            """))
            db.commit()
            logger.info("Database tables created successfully")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating tables: {str(e)}")
            raise
