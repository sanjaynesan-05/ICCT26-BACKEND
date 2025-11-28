import json
from models import Match
from database import SessionLocal
from app.routes.schedule import match_to_response

db = SessionLocal()
match = db.query(Match).filter(Match.id == 16).first()

response_dict = match_to_response(match, db)

print("Dictionary keys:")
for key in sorted(response_dict.keys()):
    print(f"  {key}")

print("\nHas team1_second_innings_score?", 'team1_second_innings_score' in response_dict)
print("Has team2_second_innings_score?", 'team2_second_innings_score' in response_dict)

print("\nJSON dump:")
print(json.dumps(response_dict, indent=2, default=str))
