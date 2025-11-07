"""
Initialize PostgreSQL database tables for ICCT26 Backend
Run this to create the teams and players tables in your database
"""

from sqlalchemy import text
from database import Base, engine
from models import Team, Player

def init_database():
    """Create all tables in the database"""
    print("=" * 60)
    print("🔧 Initializing ICCT26 Database Tables")
    print("=" * 60)
    
    try:
        # Test connection first
        print("\n📡 Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Create all tables
        print("\n📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        # Show created tables
        print("\n📋 Created Tables:")
        print("   • teams")
        print("   • players")
        
        print("\n" + "=" * 60)
        print("✅ Database initialization complete!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {str(e)}")
        print("\n📝 Troubleshooting:")
        print("   1. Check DATABASE_URL in .env file")
        print("   2. Ensure PostgreSQL is running")
        print("   3. Verify database credentials")
        print(f"\n   Error details: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = init_database()
    exit(0 if success else 1)
