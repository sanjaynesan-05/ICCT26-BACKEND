"""
SQLAlchemy ORM models for ICCT26 Cricket Tournament
Matches PostgreSQL schema on Neon database
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Team(Base):
    """Team model matching PostgreSQL schema exactly"""
    __tablename__ = "teams"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Team identification
    team_id = Column(String(50), unique=True, nullable=False, index=True)
    team_name = Column(String(100), nullable=False)
    church_name = Column(String(200), nullable=False)

    # Captain information
    captain_name = Column(String(100), nullable=False)
    captain_phone = Column(String(15), nullable=False)
    captain_email = Column(String(255), nullable=False)
    captain_whatsapp = Column(String(20), nullable=True)

    # Vice-Captain information
    vice_captain_name = Column(String(100), nullable=False)
    vice_captain_phone = Column(String(15), nullable=False)
    vice_captain_email = Column(String(255), nullable=False)
    vice_captain_whatsapp = Column(String(20), nullable=True)

    # File uploads (Base64 - Text for unlimited size)
    payment_receipt = Column(Text, nullable=True)
    pastor_letter = Column(Text, nullable=True)

    # Timestamps with server defaults
    registration_date = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    created_at = Column(DateTime, default=func.now(), server_default=func.now())

    # Relationship to players (One-to-Many with cascade delete)
    players = relationship(
        "Player",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Team(team_id={self.team_id}, team_name={self.team_name})>"


class Player(Base):
    """Player model matching PostgreSQL schema exactly"""
    __tablename__ = "players"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Player identification
    player_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign key to team (ON DELETE CASCADE)
    team_id = Column(
        String(50),
        ForeignKey("teams.team_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Player information
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String(15), nullable=False)
    role = Column(String(20), nullable=False)
    jersey_number = Column(String(3), nullable=False)

    # File uploads (Base64 - Text for unlimited size)
    aadhar_file = Column(Text, nullable=True)
    subscription_file = Column(Text, nullable=True)

    # Timestamps with server default
    created_at = Column(DateTime, default=func.now(), server_default=func.now())

    # Relationship to team (Many-to-One)
    team = relationship("Team", back_populates="players")

    def __repr__(self):
        return f"<Player(player_id={self.player_id}, name={self.name}, team_id={self.team_id})>"
