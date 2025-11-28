from database import SessionLocal, sync_engine
from models import Match
from sqlalchemy import inspect

# Get the columns in the matches table
inspector = inspect(sync_engine)
columns = inspector.get_columns('matches')

print("Current columns in matches table:")
for col in columns:
    print(f"  - {col['name']}: {col['type']}")

print("\nRequired new columns:")
required_cols = [
    'toss_winner_id', 'toss_choice',
    'scheduled_start_time', 'actual_start_time', 'match_end_time',
    'team1_first_innings_score', 'team2_first_innings_score',
    'team1_second_innings_score', 'team2_second_innings_score'
]

existing_cols = [col['name'] for col in columns]
for col in required_cols:
    status = "✅ EXISTS" if col in existing_cols else "❌ MISSING"
    print(f"  {col}: {status}")
