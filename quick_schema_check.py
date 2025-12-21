import asyncio
from database import async_engine
from sqlalchemy import text
from models import Team, Player

async def main():
    async with async_engine.connect() as conn:
        # Teams
        result = await conn.execute(text(
            "SELECT data_type FROM information_schema.columns WHERE table_name = 'teams' AND column_name = 'id'"
        ))
        db_type = result.scalar()
        orm_type = str(Team.id.type)
        
        print("\n" + "="*60)
        print("🔍 SCHEMA MIGRATION STATUS")
        print("="*60)
        print(f"\n📊 Teams Table:")
        print(f"   Database:  teams.id is {db_type}")
        print(f"   ORM Model: Team.id is {orm_type}")
        
        if db_type and 'uuid' in db_type.lower():
            print(f"   ✅ MIGRATED - Schema matches model")
        else:
            print(f"   ⚠️  NOT MIGRATED - Schema mismatch!")
        
        # Players
        result = await conn.execute(text(
            "SELECT data_type FROM information_schema.columns WHERE table_name = 'players' AND column_name = 'id'"
        ))
        db_type = result.scalar()
        orm_type = str(Player.id.type)
        
        print(f"\n📊 Players Table:")
        print(f"   Database:  players.id is {db_type}")
        print(f"   ORM Model: Player.id is {orm_type}")
        
        if db_type and 'integer' in db_type.lower():
            print(f"   ✅ MIGRATED - Schema matches model")
        else:
            print(f"   ⚠️  NOT MIGRATED - Schema mismatch!")
        
        print("\n" + "="*60)

asyncio.run(main())
