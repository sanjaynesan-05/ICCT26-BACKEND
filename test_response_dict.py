from models import Match
from database import SessionLocal

db = SessionLocal()
match = db.query(Match).filter(Match.id == 16).first()

print('ORM __dict__ keys:')
orm_dict = match.__dict__.copy()
orm_dict.pop('_sa_instance_state', None)
print(sorted(orm_dict.keys()))
print()
print('Has team1_second_innings_score:', 'team1_second_innings_score' in orm_dict)
print('Has team2_second_innings_score:', 'team2_second_innings_score' in orm_dict)
print()
print('team1_second_innings_score value:', orm_dict.get('team1_second_innings_score'))
print('team2_second_innings_score value:', orm_dict.get('team2_second_innings_score'))

