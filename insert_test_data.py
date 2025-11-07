"""
Insert test data into ICCT26 database for admin endpoint testing
"""

from database import SessionLocal
from models import Team, Player
from datetime import datetime

def insert_test_data():
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("📊 Inserting Test Data into Database")
        print("=" * 60)
        
        # Check if data already exists
        existing_team = db.query(Team).filter(Team.team_id == "ICCT26-0001").first()
        if existing_team:
            print("✅ Test data already exists, skipping insertion")
            return
        
        # Create test team
        team = Team(
            team_id="ICCT26-0001",
            team_name="CSI Eagles",
            church_name="CSI St. Peter's Church",
            captain_name="John Wilson",
            captain_phone="9876543210",
            captain_email="john@example.com",
            captain_whatsapp="9876543210",
            vice_captain_name="Sarah Johnson",
            vice_captain_phone="9876543211",
            vice_captain_email="sarah@example.com",
            vice_captain_whatsapp="9876543211",
            payment_receipt="RECEIPT-001",
            pastor_letter="Letter approved",
            registration_date=datetime.now()
        )
        db.add(team)
        db.flush()
        
        print(f"✅ Created team: {team.team_name} (ID: {team.team_id})")
        
        # Create test players
        players_data = [
            ("ICCT26-0001-P001", "Rohit Sharma", 28, "9876543212", "batsman@example.com", "Batsman", "1"),
            ("ICCT26-0001-P002", "Virat Kohli", 35, "9876543213", "virat@example.com", "Batsman", "18"),
            ("ICCT26-0001-P003", "Jasprit Bumrah", 30, "9876543214", "bumrah@example.com", "Bowler", "93"),
            ("ICCT26-0001-P004", "KL Rahul", 31, "9876543215", "rahul@example.com", "All-Rounder", "1"),
            ("ICCT26-0001-P005", "Hardik Pandya", 30, "9876543216", "hardik@example.com", "All-Rounder", "33"),
            ("ICCT26-0001-P006", "MS Dhoni", 43, "9876543217", "dhoni@example.com", "Wicket Keeper", "7"),
            ("ICCT26-0001-P007", "Ravindra Jadeja", 35, "9876543218", "jadeja@example.com", "All-Rounder", "8"),
            ("ICCT26-0001-P008", "Mohammed Shami", 33, "9876543219", "shami@example.com", "Bowler", "25"),
            ("ICCT26-0001-P009", "Rishabh Pant", 26, "9876543220", "pant@example.com", "Wicket Keeper", "17"),
            ("ICCT26-0001-P010", "Suryakumar Yadav", 33, "9876543221", "surya@example.com", "Batsman", "63"),
            ("ICCT26-0001-P011", "Shubman Gill", 24, "9876543222", "gill@example.com", "Batsman", "77"),
        ]
        
        for player_id, name, age, phone, email, role, jersey in players_data:
            player = Player(
                player_id=player_id,
                team_id=team.team_id,
                name=name,
                age=age,
                phone=phone,
                email=email,
                role=role,
                jersey_number=jersey
            )
            db.add(player)
            print(f"   ✅ Added player: {name} ({role})")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ Test data inserted successfully!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error inserting test data: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    insert_test_data()
