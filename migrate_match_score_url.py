"""
Database migration script to add match_score_url column to matches table
"""

from sqlalchemy import text
from database import sync_engine

def migrate_add_match_score_url():
    """Add match_score_url column to matches table"""
    with sync_engine.begin() as connection:
        # Check if column exists
        result = connection.execute(
            text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='matches' AND column_name='match_score_url'
            );
            """)
        )
        
        column_exists = result.scalar()
        
        if column_exists:
            print("✓ Column 'match_score_url' already exists in matches table")
            return
        
        # Add the column
        print("Adding 'match_score_url' column to matches table...")
        connection.execute(
            text("""
            ALTER TABLE matches
            ADD COLUMN match_score_url VARCHAR(500) NULL;
            """)
        )
        print("✓ Successfully added 'match_score_url' column")
        
        # Create index on match_score_url for faster queries
        print("Creating index on match_score_url...")
        try:
            connection.execute(
                text("""
                CREATE INDEX idx_match_score_url ON matches(match_score_url);
                """)
            )
            print("✓ Successfully created index on match_score_url")
        except Exception as e:
            print(f"⚠ Index creation skipped (may already exist): {str(e)}")

if __name__ == "__main__":
    try:
        migrate_add_match_score_url()
        print("\n✅ Migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise
