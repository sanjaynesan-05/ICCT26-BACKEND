from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    captain = Column(String(100), nullable=False)
    registered_on = Column(DateTime(timezone=True), server_default=func.now())
