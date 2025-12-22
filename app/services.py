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
    
    @staticmethod
    def create_admin_approval_email(
        team_name: str,
        captain_name: str,
        team_id: str,
        church_name: str = "",
        vice_captain_name: str = "",
        vice_captain_phone: str = "",
        vice_captain_email: str = "",
        captain_phone: str = "",
        captain_email: str = "",
        players: List[Dict[str, Any]] = None
    ) -> str:
        """Create HTML email template for admin approval confirmation"""
        
        # Build players table HTML
        players_html = ""
        if players:
            for idx, player in enumerate(players, 1):
                player_id = player.get('playerId', 'N/A')
                player_name = player.get('name', 'N/A')
                players_html += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: center;">{idx}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #eee;"><strong>{player_id}</strong></td>
                    <td style="padding: 12px; border-bottom: 1px solid #eee;">{player_name}</td>
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
                .team-id {{
                    background: #f0f0f0;
                    padding: 15px;
                    border: 2px solid #FFCC29;
                    border-radius: 5px;
                    font-size: 18px;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0;
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
                a {{
                    color: #FFCC29;
                }}
                ul {{
                    padding-left: 20px;
                }}
                li {{
                    margin: 10px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                th {{
                    background: #002B5C;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                .info-row {{
                    display: flex;
                    padding: 10px 0;
                    border-bottom: 1px solid #eee;
                }}
                .info-label {{
                    font-weight: bold;
                    width: 180px;
                    color: #666;
                }}
                .info-value {{
                    flex: 1;
                    color: #333;
                }}
                .phone-link {{
                    color: #002B5C;
                    text-decoration: none;
                    font-weight: 600;
                    border-bottom: 2px solid #FFCC29;
                    padding-bottom: 2px;
                }}
                .phone-link:hover {{
                    color: #FFCC29;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Registration Approved!</h1>
                    <p>Your Team is Ready to Play</p>
                </div>
                
                <div class="content">
                    <p>Dear <strong>{captain_name}</strong>,</p>
                    <p>Great news! Your team <strong>{team_name}</strong> has been <strong>approved and confirmed</strong> for the ICCT26 Cricket Tournament. Your registration is now complete!</p>
                    
                    <div class="section">
                        <h3>🏆 Your Team ID</h3>
                        <p>Please save and remember your Team ID for all tournament communications:</p>
                        <div class="team-id">{team_id}</div>
                        <p style="text-align: center; color: #666; font-size: 12px;">Use this ID for check-in and reference</p>
                    </div>
                    
                    <div class="section">
                        <h3>📋 Team Information</h3>
                        <div class="info-row">
                            <div class="info-label">🏏 Team Name:</div>
                            <div class="info-value"><strong>{team_name}</strong></div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">⛪ Church Name:</div>
                            <div class="info-value">{church_name if church_name else 'N/A'}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">🎖️ Team ID:</div>
                            <div class="info-value"><strong>{team_id}</strong></div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>👤 Captain Details</h3>
                        <div class="info-row">
                            <div class="info-label">Name:</div>
                            <div class="info-value"><strong>{captain_name}</strong></div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Phone:</div>
                            <div class="info-value">{captain_phone if captain_phone else 'N/A'}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Email:</div>
                            <div class="info-value">{captain_email if captain_email else 'N/A'}</div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>👤 Vice Captain Details</h3>
                        <div class="info-row">
                            <div class="info-label">Name:</div>
                            <div class="info-value"><strong>{vice_captain_name if vice_captain_name else 'N/A'}</strong></div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Phone:</div>
                            <div class="info-value">{vice_captain_phone if vice_captain_phone else 'N/A'}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">Email:</div>
                            <div class="info-value">{vice_captain_email if vice_captain_email else 'N/A'}</div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>👥 Team Players ({len(players) if players else 0} Players)</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th style="text-align: center;">#</th>
                                    <th>ICCT Player ID</th>
                                    <th>Player Name</th>
                                </tr>
                            </thead>
                            <tbody>
                                {players_html if players_html else '<tr><td colspan="3" style="padding: 12px; text-align: center; color: #666;">No players registered</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="section">
                        <h3>❓ Important Reminders</h3>
                        <ul>
                            <li>Keep your Team ID ({team_id}) safe and handy</li>
                            <li>Check website(<strong>icct26.netlify.app</strong>) regularly for match updates</li>
                            <li>Bring valid IDs for all players at check-in (<strong>AADHAAR CARDS, SUBSCRIPTION CARDS, PASTOR LETTER</strong>)</li>
                            <li>Follow tournament rules and regulations</li>
                        </ul>
                    </div>
                    
                    <div class="section">
                        <h3>📞 Contact Us</h3>
                        
                        <p><strong>Website:</strong> <a href="https://icct26.netlify.app" target="_blank">icct26.netlify.app</a></p>
                        
                        <p><strong>Tournament Coordinators:</strong></p>
                        <p>Mr. Sam Richard (Head Co-Ordinator) - <a href="tel:+919543656533" class="phone-link">+91 9543656533</a></p>
                        <p>Mr. Jebarsan (Co-Ordinator) - <a href="tel:+917806965812" class="phone-link">+91 7806965812</a></p>
                        <p>Mr. Jerald (Co-Ordinator) - <a href="tel:+917871541469" class="phone-link">+91 7871541469</a></p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated confirmation email. Please do not reply to this email.</p>
                    <p>&copy; 2025 ICCT26 Cricket Tournament. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    @staticmethod
    async def send_email_async_if_available(to_email: str, subject: str, body: str) -> bool:
        """
        Send email asynchronously using thread pool executor.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body (plain text or HTML)
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def _send_sync():
            """Synchronous email sending in thread pool"""
            try:
                if not settings.SMTP_ENABLED:
                    logger.warning(f"SMTP not configured. Email not sent to {to_email}")
                    return False
                
                # Create email message
                msg = MIMEMultipart('alternative')
                msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
                msg['To'] = to_email
                msg['Subject'] = subject
                
                # Attach body as HTML or plain text
                if '<html>' in body.lower() or '<p>' in body.lower():
                    msg.attach(MIMEText(body, 'html'))
                else:
                    msg.attach(MIMEText(body, 'plain'))
                
                # Send email
                with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                    server.send_message(msg)
                
                logger.info(f"✅ Email sent successfully to {to_email}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Email error: {str(e)}")
                return False
        
        try:
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=2)
            result = await loop.run_in_executor(executor, _send_sync)
            return result
        except Exception as e:
            logger.error(f"❌ Async email failed: {e}")
            return False


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
        """Save team registration to database with retry logic for Neon timeouts"""
        
        try:
            # Import models and retry utilities
            from models import Team, Player
            from app.db_utils import safe_commit
            
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
                pastor_letter=registration.pastorLetter,
                group_photo=registration.groupPhoto
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
                    role=player.role,
                    aadhar_file=player.aadharFile,
                    subscription_file=player.subscriptionFile
                )
                session.add(player_db)
            
            # 🔥 Use retry logic for commit (handles Neon timeouts)
            await safe_commit(session, max_retries=3)
            logger.info(f"✅ Registration saved to database with Team ID: {team_id}")
            return team_db.id
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Failed to save registration: {str(e)}")
            raise

    @staticmethod
    async def get_all_teams(db: AsyncSession) -> List[Dict[str, Any]]:
        """Get all registered teams"""
        
        logger.info("Fetching all teams...")
        try:
            query = text("""
                SELECT t.id, t.team_id, t.team_name, t.church_name, 
                       t.payment_receipt, t.pastor_letter, t.group_photo, t.created_at,
                       t.captain_name, t.captain_phone, t.captain_email,
                       t.vice_captain_name, t.vice_captain_phone, t.vice_captain_email,
                       t.registration_status,
                       COUNT(p.id) as player_count
                FROM teams t
                LEFT JOIN players p ON p.team_id = t.team_id
                GROUP BY t.id
                ORDER BY t.created_at DESC
            """)
            
            result = await db.execute(query)
            data = result.mappings().all()
            teams = []
            
            for row in data:
                teams.append({
                    "teamId": row["team_id"],
                    "teamName": row["team_name"],
                    "churchName": row["church_name"],
                    "captainName": row["captain_name"],
                    "captainPhone": row["captain_phone"],
                    "captainEmail": row["captain_email"],
                    "viceCaptainName": row["vice_captain_name"],
                    "viceCaptainPhone": row["vice_captain_phone"],
                    "viceCaptainEmail": row["vice_captain_email"],
                    "playerCount": row["player_count"],
                    "registrationDate": str(row["created_at"]) if row["created_at"] else None,
                    "registrationStatus": row.get("registration_status", "pending"),
                    "paymentReceipt": row["payment_receipt"],
                    "pastorLetter": row["pastor_letter"],
                    "groupPhoto": row["group_photo"]
                })
            
            logger.info(f"Found {len(teams)} teams")
            return teams
            
        except Exception as e:
            logger.error(f"Error fetching teams: {str(e)}")
            raise

    @staticmethod
    async def get_team_by_team_id(db: AsyncSession, team_id: str):
        """
        Get Team ORM object by team_id (e.g., 'ICCT-001')
        
        Args:
            db: AsyncSession database session
            team_id: Team identifier (ICCT-001 format)
            
        Returns:
            Team ORM object or None if not found
        """
        from models import Team
        from sqlalchemy import select
        
        logger.info(f"Fetching Team ORM object for team_id: {team_id}")
        try:
            query = select(Team).where(Team.team_id == team_id)
            result = await db.execute(query)
            team = result.scalar_one_or_none()
            
            if team:
                logger.info(f"✅ Found team: {team.team_name} ({team_id})")
            else:
                logger.warning(f"❌ Team not found: {team_id}")
            
            return team
            
        except Exception as e:
            logger.error(f"Error fetching team by team_id: {str(e)}")
            raise

    @staticmethod
    async def confirm_team_registration(
        db: AsyncSession, 
        team_id: str,
        new_cloudinary_urls: dict = None
    ) -> bool:
        """
        Confirm a team's registration and update Cloudinary URLs
        
        Args:
            db: AsyncSession database session
            team_id: Team identifier (ICCT-001 format)
            new_cloudinary_urls: Dictionary of updated Cloudinary URLs
                {
                    "payment_receipt": "https://...",
                    "pastor_letter": "https://...",
                    "group_photo": "https://..."
                }
            
        Returns:
            True if successful, False if team not found
        """
        from models import Team
        
        logger.info(f"Confirming team registration for: {team_id}")
        try:
            team = await DatabaseService.get_team_by_team_id(db, team_id)
            
            if not team:
                logger.warning(f"❌ Cannot confirm - team not found: {team_id}")
                return False
            
            # Check if already confirmed
            if team.registration_status == "confirmed":
                logger.info(f"ℹ️ Team {team_id} is already confirmed")
                return True
            
            # Update Cloudinary URLs if provided
            if new_cloudinary_urls:
                if "payment_receipt" in new_cloudinary_urls:
                    team.payment_receipt = new_cloudinary_urls["payment_receipt"]
                if "pastor_letter" in new_cloudinary_urls:
                    team.pastor_letter = new_cloudinary_urls["pastor_letter"]
                if "group_photo" in new_cloudinary_urls:
                    team.group_photo = new_cloudinary_urls["group_photo"]
                logger.info(f"Updated Cloudinary URLs: {list(new_cloudinary_urls.keys())}")
            
            # Update status to confirmed
            team.registration_status = "confirmed"
            db.add(team)
            await db.commit()
            
            logger.info(f"✅ Team {team_id} confirmed successfully")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error confirming team registration: {str(e)}")
            raise

    @staticmethod
    async def get_team_details(db: AsyncSession, team_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific team"""
        
        logger.info(f"Fetching team details for team_id: {team_id}")
        try:
            team_query = text("""
                SELECT id, team_id, team_name, church_name, payment_receipt, pastor_letter, group_photo, created_at,
                       captain_name, captain_phone, captain_email,
                       vice_captain_name, vice_captain_phone, vice_captain_email,
                       registration_status
                FROM teams
                WHERE team_id = :team_id
            """)
            
            result = await db.execute(team_query, {"team_id": team_id})
            team_data = result.mappings().first()
            
            if not team_data:
                logger.warning(f"Team not found: {team_id}")
                return None
            
            # Get players for this team
            players_query = text("""
                SELECT id, player_id, name, role,
                       aadhar_file, subscription_file
                FROM players
                WHERE team_id = :team_id
                ORDER BY id
            """)
            
            result = await db.execute(players_query, {"team_id": team_id})
            players_data = result.mappings().all()
            
            logger.info(f"Found team with {len(players_data)} players")
            return {
                "team": {
                    "teamId": team_data["team_id"],
                    "teamName": team_data["team_name"],
                    "churchName": team_data["church_name"],
                    "captain": {
                        "name": team_data["captain_name"],
                        "phone": team_data["captain_phone"],
                        "email": team_data["captain_email"]
                    } if team_data["captain_name"] else None,
                    "viceCaptain": {
                        "name": team_data["vice_captain_name"],
                        "phone": team_data["vice_captain_phone"],
                        "email": team_data["vice_captain_email"]
                    } if team_data["vice_captain_name"] else None,
                    "paymentReceipt": team_data["payment_receipt"],
                    "pastorLetter": team_data["pastor_letter"],
                    "groupPhoto": team_data["group_photo"],
                    "registrationDate": str(team_data["created_at"]) if team_data["created_at"] else None,
                    "registrationStatus": team_data.get("registration_status", "pending")
                },
                "players": [
                    {
                        "playerId": p["player_id"],
                        "name": p["name"],
                        "role": p["role"],
                        "aadharFile": p["aadhar_file"],
                        "subscriptionFile": p["subscription_file"]
                    } for p in players_data
                ]
            }
            
        except Exception as e:
            logger.error(f"Error fetching team details: {str(e)}")
            raise

    @staticmethod
    async def update_team_registration_status(
        db: AsyncSession, 
        team_id: str, 
        status: str
    ) -> bool:
        """
        Update the registration status of a team.
        
        Args:
            db: Database session
            team_id: Team identifier
            status: New status ('pending', 'confirmed', 'rejected')
            
        Returns:
            True if team was found and updated, False otherwise
        """
        logger.info(f"Updating registration status for team {team_id} to {status}")
        try:
            update_query = text("""
                UPDATE teams 
                SET registration_status = :status
                WHERE team_id = :team_id
            """)
            
            result = await db.execute(
                update_query, 
                {"team_id": team_id, "status": status}
            )
            await db.commit()
            
            rows_updated = result.rowcount
            if rows_updated > 0:
                logger.info(f"✅ Successfully updated team {team_id} to status: {status}")
                return True
            else:
                logger.warning(f"❌ Team not found: {team_id}")
                return False
                
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating team registration status: {str(e)}")
            raise

    @staticmethod
    async def get_player_details(db: AsyncSession, player_id: int) -> Dict[str, Any]:
        """Fetch details of a specific player"""
        
        logger.info(f"Fetching player details for player_id: {player_id}")
        try:
            player_query = text("""
                SELECT p.id, p.player_id, p.name, p.role,
                       p.aadhar_file, p.subscription_file,
                       t.team_id, t.team_name, t.church_name
                FROM players p
                LEFT JOIN teams t ON t.team_id = p.team_id
                WHERE p.id = :player_id
            """)
            
            result = await db.execute(player_query, {"player_id": player_id})
            player_data = result.mappings().first()
            
            if not player_data:
                logger.warning(f"Player not found: {player_id}")
                return None
            
            logger.info(f"Found player: {player_data['name']}")
            return {
                "playerId": player_data["player_id"],
                "name": player_data["name"],
                "role": player_data["role"],
                "aadharFile": player_data["aadhar_file"],
                "subscriptionFile": player_data["subscription_file"],
                "team": {
                    "teamId": player_data["team_id"],
                    "teamName": player_data["team_name"],
                    "churchName": player_data["church_name"]
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
