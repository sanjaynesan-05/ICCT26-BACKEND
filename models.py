"""
SQLAlchemy ORM models for ICCT26 Cricket Tournament
Matches PostgreSQL schema on Neon database
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, UniqueConstraint, Index, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Team(Base):
    """Team model matching PostgreSQL schema exactly"""
    __tablename__ = "teams"
    
    __table_args__ = (
        # Unique constraint to prevent duplicate submissions
        UniqueConstraint('team_name', 'captain_phone', name='uq_team_name_captain_phone'),
        Index('idx_team_captain', 'team_name', 'captain_phone'),
    )

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
    group_photo = Column(Text, nullable=True)  # Team group photo (Base64)
    payment_screenshot = Column(Text, nullable=True)  # Payment proof screenshot (Cloudinary URL)

    # Payment & Registration Status
    status = Column(String(50), nullable=False, default="PENDING_PAYMENT", index=True)  # Registration status state machine
    payment_date = Column(DateTime, nullable=True, index=True)  # When payment screenshot was uploaded
    approval_date = Column(DateTime, nullable=True)  # When admin approved registration
    rejection_date = Column(DateTime, nullable=True)  # When admin rejected registration
    rejection_reason = Column(Text, nullable=True)  # Reason for rejection if rejected
    approved_by = Column(String(100), nullable=True)  # Admin who approved
    rejected_by = Column(String(100), nullable=True)  # Admin who rejected

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
    role = Column(String(20), nullable=True)  # Optional player role

    # File uploads (Base64 - Text for unlimited size)
    aadhar_file = Column(Text, nullable=True)
    subscription_file = Column(Text, nullable=True)

    # Timestamps with server default
    created_at = Column(DateTime, default=func.now(), server_default=func.now())

    # Relationship to team (Many-to-One)
    team = relationship("Team", back_populates="players")

    def __repr__(self):
        return f"<Player(player_id={self.player_id}, name={self.name}, team_id={self.team_id})>"


class Match(Base):
    """Match model for cricket tournament schedule and results"""
    __tablename__ = "matches"
    
    __table_args__ = (
        # Ensure unique match per round
        UniqueConstraint('round_number', 'match_number', name='uq_match_round_number'),
        # Indexes for common queries
        Index('idx_match_status', 'status'),
        Index('idx_match_round', 'round_number'),
        Index('idx_match_team1', 'team1_id'),
        Index('idx_match_team2', 'team2_id'),
    )

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Match identification
    round = Column(String(50), nullable=False)  # e.g., "Round 1", "Semi-Final"
    round_number = Column(Integer, nullable=False)  # Numeric round (1, 2, 3...)
    match_number = Column(Integer, nullable=False)  # Match number within round
    
    # Teams
    team1_id = Column(Integer, ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False, index=True)
    team2_id = Column(Integer, ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Match status
    status = Column(String(20), nullable=False, default="scheduled", index=True)  # 'scheduled', 'live', 'completed'
    
    # Toss details
    toss_winner_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)  # Team that won the toss
    toss_choice = Column(String(10), nullable=True)  # 'bat' or 'bowl'
    
    # Match timing
    scheduled_start_time = Column(DateTime, nullable=True)  # When match is scheduled to start
    actual_start_time = Column(DateTime, nullable=True)  # When match actually started
    match_end_time = Column(DateTime, nullable=True)  # When match ended
    
    # Innings scores - Separate runs and wickets for each team
    # First innings (batting first team)
    team1_first_innings_runs = Column(Integer, nullable=True)  # Team 1 runs in first innings
    team1_first_innings_wickets = Column(Integer, nullable=True)  # Team 1 wickets lost in first innings
    team2_first_innings_runs = Column(Integer, nullable=True)  # Team 2 runs in first innings
    team2_first_innings_wickets = Column(Integer, nullable=True)  # Team 2 wickets lost in first innings
    
    # Legacy fields (deprecated - for backward compatibility)
    team1_first_innings_score = Column(Integer, nullable=True)  # DEPRECATED: Use team1_first_innings_runs
    team2_first_innings_score = Column(Integer, nullable=True)  # DEPRECATED: Use team2_first_innings_runs
    team1_second_innings_score = Column(Integer, nullable=True)  # DEPRECATED
    team2_second_innings_score = Column(Integer, nullable=True)  # DEPRECATED
    
    # Result fields (NULL until match is completed)
    winner_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    margin = Column(Integer, nullable=True)  # Numeric margin value
    margin_type = Column(String(20), nullable=True)  # 'runs' or 'wickets'
    won_by_batting_first = Column(Boolean, nullable=True)  # true if batting first team won
    
    # Match score URL
    match_score_url = Column(String(500), nullable=True)  # URL to external match score/scorecard
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    team1 = relationship("Team", foreign_keys=[team1_id], viewonly=True, lazy="selectin")
    team2 = relationship("Team", foreign_keys=[team2_id], viewonly=True, lazy="selectin")
    winner = relationship("Team", foreign_keys=[winner_id], viewonly=True, lazy="selectin")
    toss_winner = relationship("Team", foreign_keys=[toss_winner_id], viewonly=True, lazy="selectin")

    def __repr__(self):
        return f"<Match(id={self.id}, round={self.round}, team1={self.team1_id}, team2={self.team2_id}, status={self.status})>"
