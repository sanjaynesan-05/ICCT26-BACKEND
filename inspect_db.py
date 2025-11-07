#!/usr/bin/env python3
"""
Database Inspection Script for ICCT26 Backend
Shows all data stored in the database tables
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:password@localhost/icct26_db')

# Database models (same as in main.py)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

Base = declarative_base()

class TeamRegistrationDB(Base):
    __tablename__ = "team_registrations"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(50), unique=True, index=True)
    church_name = Column(String(200))
    team_name = Column(String(100))
    pastor_letter = Column(Text, nullable=True)
    payment_receipt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CaptainDB(Base):
    __tablename__ = "captains"
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    phone = Column(String(15))
    whatsapp = Column(String(10))
    email = Column(String(255))

class ViceCaptainDB(Base):
    __tablename__ = "vice_captains"
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    phone = Column(String(15))
    whatsapp = Column(String(10))
    email = Column(String(255))

class PlayerDB(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    age = Column(Integer)
    phone = Column(String(15))
    role = Column(String(20))
    aadhar_file = Column(Text, nullable=True)
    subscription_file = Column(Text, nullable=True)

async def inspect_database():
    """Inspect all data in the database"""
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with AsyncSession(engine) as session:
        print("🔍 ICCT26 Database Inspection")
        print("=" * 50)

        # 1. Team Registrations
        print("\n📋 TEAM REGISTRATIONS:")
        print("-" * 30)
        result = await session.execute(select(TeamRegistrationDB))
        teams = result.scalars().all()

        if not teams:
            print("No teams registered yet.")
        else:
            for team in teams:
                print(f"ID: {team.id}")
                print(f"Team ID: {team.team_id}")
                print(f"Team Name: {team.team_name}")
                print(f"Church: {team.church_name}")
                print(f"Created: {team.created_at}")
                print("-" * 20)

        # 2. Captains
        print("\n👑 CAPTAINS:")
        print("-" * 30)
        result = await session.execute(select(CaptainDB))
        captains = result.scalars().all()

        if not captains:
            print("No captains registered yet.")
        else:
            for captain in captains:
                print(f"ID: {captain.id}")
                print(f"Registration ID: {captain.registration_id}")
                print(f"Name: {captain.name}")
                print(f"Phone: {captain.phone}")
                print(f"WhatsApp: {captain.whatsapp}")
                print(f"Email: {captain.email}")
                print("-" * 20)

        # 3. Vice Captains
        print("\n👨‍💼 VICE CAPTAINS:")
        print("-" * 30)
        result = await session.execute(select(ViceCaptainDB))
        vice_captains = result.scalars().all()

        if not vice_captains:
            print("No vice captains registered yet.")
        else:
            for vc in vice_captains:
                print(f"ID: {vc.id}")
                print(f"Registration ID: {vc.registration_id}")
                print(f"Name: {vc.name}")
                print(f"Phone: {vc.phone}")
                print(f"WhatsApp: {vc.whatsapp}")
                print(f"Email: {vc.email}")
                print("-" * 20)

        # 4. Players
        print("\n🏏 PLAYERS:")
        print("-" * 30)
        result = await session.execute(select(PlayerDB))
        players = result.scalars().all()

        if not players:
            print("No players registered yet.")
        else:
            for player in players:
                print(f"ID: {player.id}")
                print(f"Registration ID: {player.registration_id}")
                print(f"Name: {player.name}")
                print(f"Age: {player.age}")
                print(f"Phone: {player.phone}")
                print(f"Role: {player.role}")
                print(f"Aadhar File: {'Yes' if player.aadhar_file else 'No'}")
                print(f"Subscription File: {'Yes' if player.subscription_file else 'No'}")
                print("-" * 20)

        # Summary
        print("\n📊 SUMMARY:")
        print("-" * 30)
        print(f"Total Teams: {len(teams)}")
        print(f"Total Captains: {len(captains)}")
        print(f"Total Vice Captains: {len(vice_captains)}")
        print(f"Total Players: {len(players)}")

        await session.close()

if __name__ == "__main__":
    asyncio.run(inspect_database())