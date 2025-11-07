from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Team

app = FastAPI(title="ICCT26 Backend")

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "ICCT26 Backend connected to PostgreSQL successfully"}

@app.post("/register/team")
def register_team(name: str, captain: str, db: Session = Depends(get_db)):
    team = Team(name=name, captain=captain)
    db.add(team)
    db.commit()
    db.refresh(team)
    return {"id": team.id, "name": team.name, "captain": team.captain}
