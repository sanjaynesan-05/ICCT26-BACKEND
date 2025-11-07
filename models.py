from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base

class Team(Base):
    """Team table matching PostgreSQL schema"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(20), unique=True, nullable=False, index=True)
    team_name = Column(String(100), nullable=False)
    church_name = Column(String(200), nullable=False)
    captain_name = Column(String(100), nullable=False)
    captain_phone = Column(String(15), nullable=False)
    captain_email = Column(String(255), nullable=False)
    captain_whatsapp = Column(String(10))
    vice_captain_name = Column(String(100), nullable=False)
    vice_captain_phone = Column(String(15), nullable=False)
    vice_captain_email = Column(String(255), nullable=False)
    vice_captain_whatsapp = Column(String(10))
    payment_receipt = Column(String(50))
    pastor_letter = Column(Text)
    registration_date = Column(TIMESTAMP, nullable=False, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship to players
    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")


class Player(Base):
    """Player table matching PostgreSQL schema"""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String(25), unique=True, nullable=False, index=True)
    team_id = Column(String(20), ForeignKey("teams.team_id"), nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    jersey_number = Column(String(3), nullable=False)
    aadhar_file = Column(Text)
    subscription_file = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship to team
    team = relationship("Team", back_populates="players")
