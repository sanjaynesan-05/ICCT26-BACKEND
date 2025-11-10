from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base

class Team(Base):
    """Team table matching PostgreSQL schema"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    # Increase team_id length to avoid truncation for generated IDs
    team_id = Column(String(50), unique=True, nullable=False, index=True)
    team_name = Column(String(200), nullable=False)
    church_name = Column(String(200), nullable=False)

    captain_name = Column(String(150), nullable=False)
    captain_phone = Column(String(20), nullable=False)
    captain_email = Column(String(255), nullable=False)
    captain_whatsapp = Column(String(20), nullable=True)

    vice_captain_name = Column(String(150), nullable=False)
    vice_captain_phone = Column(String(20), nullable=False)
    vice_captain_email = Column(String(255), nullable=False)
    vice_captain_whatsapp = Column(String(20), nullable=True)

    # Use Text for file/storage references (base64 or URLs)
    payment_receipt = Column(Text, nullable=True)
    pastor_letter = Column(Text, nullable=True)

    registration_date = Column(TIMESTAMP, nullable=False, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship to players
    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")


class Player(Base):
    """Player table matching PostgreSQL schema"""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String(50), unique=True, nullable=False, index=True)
    # team_id references Team.team_id (string) — lengths should match
    team_id = Column(String(50), ForeignKey("teams.team_id"), nullable=False)

    name = Column(String(150), nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String(20), nullable=False)
    role = Column(String(50), nullable=False)

    # store file refs or short base64 snippets as Text
    aadhar_file = Column(Text, nullable=True)
    subscription_file = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship to team
    team = relationship("Team", back_populates="players")
