from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL connection URL
DATABASE_URL = "postgresql://postgres:icctpg@localhost:5432/icct26_db"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()
