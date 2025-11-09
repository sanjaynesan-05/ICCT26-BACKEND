from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection URL - Use Render database
# Convert async URL to sync URL if needed
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    "postgresql://icctadmin:FhfKgVwHX7P7hmObQJFQvN0YBZxYUly7@dpg-d45imk49c44c73c4j4v0-a/icct26_db"
)

# Replace asyncpg with psycopg2 for synchronous operations
# Only convert if it contains asyncpg
if DATABASE_URL and 'postgresql+asyncpg://' in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
elif DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # Handle postgres:// URLs (common on some platforms)
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

print(f"Using DATABASE_URL: {DATABASE_URL[:50]}...")  # Debug log (first 50 chars)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
