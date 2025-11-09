from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# PostgreSQL connection URL - Use Render database
# Read DATABASE_URL directly and convert for psycopg2
raw_db_url = os.environ.get(
    'DATABASE_URL',
    "postgresql://icctadmin:FhfKgVwHX7P7hmObQJFQvN0YBZxYUly7@dpg-d45imk49c44c73c4j4v0-a/icct26_db"
)

# Convert to psycopg2 compatible format
DATABASE_URL = raw_db_url
if raw_db_url.startswith('postgresql+asyncpg://'):
    DATABASE_URL = raw_db_url.replace('postgresql+asyncpg://', 'postgresql://')
elif raw_db_url.startswith('postgres://'):
    DATABASE_URL = raw_db_url.replace('postgres://', 'postgresql://')

print(f"Sync DATABASE_URL configured: {DATABASE_URL[:50]}...")

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
