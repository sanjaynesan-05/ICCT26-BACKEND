"""
Simple test to check if we can query the Neon database
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment
load_dotenv('.env.local')
load_dotenv()

# Get database URL
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Convert for psycopg2
if DATABASE_URL.startswith('postgresql+asyncpg://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    DATABASE_URL = DATABASE_URL.replace('?ssl=require', '?sslmode=require')

print(f"Testing connection to: {DATABASE_URL[:80]}...")

try:
    # Create engine
    engine = create_engine(
        DATABASE_URL,
        connect_args={"sslmode": "require"},
        echo=True
    )
    
    # Create session
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Query teams
    print("\n" + "="*70)
    print("Querying teams table...")
    print("="*70)
    
    result = db.execute(text("SELECT * FROM teams"))
    teams = result.fetchall()
    
    print(f"\n✅ Found {len(teams)} teams in database")
    
    for team in teams:
        print(f"   - {team}")
    
    db.close()
    print("\n✅ Database query successful!")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
