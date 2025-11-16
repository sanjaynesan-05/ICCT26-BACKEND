# Player Fields Removal Migration

**Date**: November 17, 2025  
**Migration**: Remove `age`, `phone`, and `jersey_number` from Player model

---

## Changes Made

### 1. ✅ SQLAlchemy Model (models.py)
**Status**: Already correct - no changes needed

The Player model already had these fields removed:
```python
class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String(50), unique=True, nullable=False, index=True)
    team_id = Column(String(50), ForeignKey("teams.team_id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    aadhar_file = Column(Text, nullable=True)
    subscription_file = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # ✅ NO age, phone, jersey_number columns
```

---

### 2. ✅ Pydantic Schemas (app/schemas_team.py)

**BEFORE**:
```python
class PlayerInfo(BaseModel):
    name: str
    age: int = Field(..., ge=15, le=65)  # ❌ REMOVED
    phone: str = Field(..., min_length=7, max_length=15)  # ❌ REMOVED
    role: str
    jersey_number: Optional[str] = Field(None, min_length=1, max_length=3)  # ❌ REMOVED
    aadharFile: Optional[str]
    subscriptionFile: Optional[str]
    
    @field_validator('phone')  # ❌ REMOVED
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # validation logic
```

**AFTER**:
```python
class PlayerInfo(BaseModel):
    name: str
    role: str
    aadharFile: Optional[str]
    subscriptionFile: Optional[str]
    
    # ✅ Only 4 fields remain
```

---

### 3. ✅ Registration Route (app/routes/registration.py)

**BEFORE**:
```python
# Player creation with removed fields
jersey_num = player_data.jersey_number if player_data.jersey_number else str(idx)

player = Player(
    player_id=player_id,
    team_id=team_id,
    name=player_data.name,
    age=player_data.age,  # ❌ REMOVED
    phone=player_data.phone,  # ❌ REMOVED
    role=player_data.role,
    jersey_number=jersey_num,  # ❌ REMOVED
    aadhar_file=player_data.aadharFile,
    subscription_file=player_data.subscriptionFile
)

# Jersey number verification logging
logger.info(f"Jersey: {p.jersey_number}")  # ❌ REMOVED
```

**AFTER**:
```python
# Simplified player creation
player = Player(
    player_id=player_id,
    team_id=team_id,
    name=player_data.name,
    role=player_data.role,
    aadhar_file=player_data.aadharFile,
    subscription_file=player_data.subscriptionFile
)

# ✅ No jersey_number logic or logging
```

**Error Handling Updated**:
```python
# BEFORE
if "jersey_number" in error_msg:
    detail_msg = "Jersey number is required or invalid..."

# AFTER - removed jersey_number check
if "not null" in error_msg:
    detail_msg = "A required field is missing or null"
```

---

### 4. ✅ Team Route (app/routes/team.py)

**Player Creation - BEFORE**:
```python
player = Player(
    player_id=player_id,
    team_id=team_id,
    name=p.name,
    age=p.age,  # ❌ REMOVED
    phone=p.phone,  # ❌ REMOVED
    role=p.role,
    aadhar_file=aadhar_ref,
    subscription_file=sub_ref,
)
```

**Player Creation - AFTER**:
```python
player = Player(
    player_id=player_id,
    team_id=team_id,
    name=p.name,
    role=p.role,
    aadhar_file=aadhar_ref,
    subscription_file=sub_ref,
    created_at=datetime.utcnow(),
)
```

**Player Serialization - BEFORE**:
```python
"players": [
    {
        "player_id": p.player_id,
        "name": p.name,
        "age": p.age,  # ❌ REMOVED
        "phone": p.phone,  # ❌ REMOVED
        "role": p.role,
        "aadhar_file": p.aadhar_file,
        "subscription_file": p.subscription_file
    } for p in players
]
```

**Player Serialization - AFTER**:
```python
"players": [
    {
        "player_id": p.player_id,
        "name": p.name,
        "role": p.role,
        "aadhar_file": p.aadhar_file,
        "subscription_file": p.subscription_file
    } for p in players
]
```

---

### 5. ✅ Database Migration Scripts Created

**SQL Migration** (`scripts/remove_player_fields.sql`):
```sql
-- Remove age column
ALTER TABLE players DROP COLUMN IF EXISTS age;

-- Remove phone column
ALTER TABLE players DROP COLUMN IF EXISTS phone;

-- Remove jersey_number column
ALTER TABLE players DROP COLUMN IF EXISTS jersey_number;
```

**Python Migration Script** (`scripts/remove_player_fields_migration.py`):
```bash
python scripts/remove_player_fields_migration.py
```

Features:
- ✅ Checks if columns exist before dropping
- ✅ Drops all three columns safely
- ✅ Verifies final table structure
- ✅ Provides detailed logging

---

## How to Apply Database Migration

### Option 1: Using Python Script (Recommended)
```bash
cd "d:\ICCT26 BACKEND"
python scripts/remove_player_fields_migration.py
```

### Option 2: Using SQL Directly
```bash
psql -h <neon-host> -U <username> -d <database> -f scripts/remove_player_fields.sql
```

### Option 3: Using Neon Console
1. Go to https://console.neon.tech
2. Select your database
3. Open SQL Editor
4. Run:
```sql
ALTER TABLE players DROP COLUMN IF EXISTS age;
ALTER TABLE players DROP COLUMN IF EXISTS phone;
ALTER TABLE players DROP COLUMN IF EXISTS jersey_number;
```

---

## Testing After Migration

### 1. Start Backend
```bash
python main.py
```

### 2. Test Player Registration
```bash
curl -X POST "http://localhost:8000/api/register/team" \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "Test Church",
    "teamName": "Test Team",
    "captain": {
      "name": "Captain",
      "phone": "+919876543210",
      "whatsapp": "9876543210",
      "email": "captain@test.com"
    },
    "viceCaptain": {
      "name": "Vice Captain",
      "phone": "+919876543211",
      "whatsapp": "9876543211",
      "email": "vice@test.com"
    },
    "players": [
      {
        "name": "Player 1",
        "role": "Batsman",
        "aadharFile": "data:application/pdf;base64,JVBERi0x...",
        "subscriptionFile": "data:application/pdf;base64,JVBERi0x..."
      }
    ]
  }'
```

**Expected**: 201 Created with no errors about missing fields

### 3. Test Get Team Details
```bash
curl "http://localhost:8000/api/teams/TEAM-ID-HERE"
```

**Expected**: Player objects without age, phone, jersey_number fields

---

## Files Modified

| File | Changes |
|------|---------|
| `app/schemas_team.py` | Removed age, phone, jersey_number from PlayerInfo |
| `app/routes/registration.py` | Removed fields from Player creation & error handling |
| `app/routes/team.py` | Removed fields from Player creation & serialization |
| `models.py` | ✅ Already correct - no changes |

## Files Created

| File | Purpose |
|------|---------|
| `scripts/remove_player_fields.sql` | SQL migration script |
| `scripts/remove_player_fields_migration.py` | Python migration script |

---

## Expected API Request Format (NEW)

### Player Object (Simplified)
```json
{
  "name": "Player Name",
  "role": "Batsman",
  "aadharFile": "data:application/pdf;base64,...",
  "subscriptionFile": "data:application/pdf;base64,..."
}
```

**Required Fields**: `name`, `role`  
**Optional Fields**: `aadharFile`, `subscriptionFile`

---

## Expected API Response Format (NEW)

### Player in Response
```json
{
  "player_id": "ICCT26-20251116103045-P01",
  "name": "Player Name",
  "role": "Batsman",
  "aadhar_file": "data:application/pdf;base64,...",
  "subscription_file": "data:application/pdf;base64,..."
}
```

**No longer includes**: `age`, `phone`, `jerseyNumber`

---

## Verification Checklist

- [x] Player model has no age, phone, jersey_number columns
- [x] PlayerInfo schema has no age, phone, jersey_number fields
- [x] Registration route doesn't reference removed fields
- [x] Team route doesn't reference removed fields
- [x] Error handling doesn't reference jersey_number
- [x] Player serialization doesn't include removed fields
- [x] Migration scripts created (SQL + Python)
- [ ] Database migration executed
- [ ] Backend tested successfully
- [ ] API requests work without errors

---

## Next Steps

1. **Run Database Migration**:
   ```bash
   python scripts/remove_player_fields_migration.py
   ```

2. **Restart Backend**:
   ```bash
   python main.py
   ```

3. **Test Registration**:
   - POST `/api/register/team` with simplified player objects
   - Verify no errors about missing fields

4. **Update Frontend**:
   - Remove age, phone, jersey_number from registration form
   - Update player interfaces/types
   - Remove validation for these fields

---

**Migration Status**: ✅ Backend code updated, database migration ready to execute

**Last Updated**: November 17, 2025
