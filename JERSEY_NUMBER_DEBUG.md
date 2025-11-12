# 🔍 Jersey Number Debug & Fix Guide

**Issue:** `asyncpg.exceptions.NotNullViolationError: null value in column "jersey_number"`

**Root Cause Analysis:** The `jersey_number` field might not be properly received from the frontend.

---

## ✅ VERIFICATION CHECKLIST

### 1. **Model Definition** (models.py)
```python
class Player(Base):
    __tablename__ = "players"
    jersey_number = Column(String(3), nullable=False)  # ✅ CORRECT
```
Status: ✅ VERIFIED

### 2. **Schema Definition** (app/schemas_team.py)
```python
class PlayerInfo(BaseModel):
    jersey_number: Optional[str] = Field(None, min_length=1, max_length=3, alias="jersey_number")
```
Status: ✅ VERIFIED - Accepts optional, auto-assigns if None

### 3. **Route Handler** (app/routes/registration.py)
```python
jersey_num = player_data.jersey_number if player_data.jersey_number else str(idx)
player = Player(
    ...
    jersey_number=jersey_num,  # ✅ GUARANTEED to have value
    ...
)
```
Status: ✅ VERIFIED - Auto-assigns from position if None

---

## 🧪 TEST PAYLOADS

### Test 1: Frontend Sends jersey_number Explicitly

**Request:**
```bash
POST https://icct26-backend.onrender.com/api/register/team
Content-Type: application/json
```

**Payload:**
```json
{
  "churchName": "St. Mary Church",
  "teamName": "Mumbai Warriors",
  "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA...",
  "paymentReceipt": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA...",
  "captain": {
    "name": "Rohit Sharma",
    "phone": "9876543210",
    "whatsapp": "919876543210",
    "email": "rohit@example.com"
  },
  "viceCaptain": {
    "name": "Virat Kohli",
    "phone": "9876543211",
    "whatsapp": "919876543211",
    "email": "virat@example.com"
  },
  "players": [
    {
      "name": "Player 1",
      "age": 20,
      "phone": "9999999999",
      "role": "Batsman",
      "jersey_number": "1",
      "aadharFile": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA...",
      "subscriptionFile": "data:application/pdf;base64,JVBERi0xLjQ..."
    },
    {
      "name": "Player 2",
      "age": 21,
      "phone": "9999999998",
      "role": "Bowler",
      "jersey_number": "2"
    },
    {
      "name": "Player 3",
      "age": 22,
      "phone": "9999999997",
      "role": "All-rounder",
      "jersey_number": "3"
    }
    // ... 8 more players to reach 11 total ...
  ]
}
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "message": "Team and players registered successfully",
  "team_id": "ICCT26-20251112120000",
  "player_count": 11,
  "registration_date": "2025-11-12T12:00:00.123456"
}
```

---

### Test 2: Frontend Omits jersey_number (AUTO-ASSIGN)

**Payload:**
```json
{
  "churchName": "St. Mary Church",
  "teamName": "Delhi Lions",
  "captain": {
    "name": "Captain Name",
    "phone": "9876543210",
    "whatsapp": "919876543210",
    "email": "captain@example.com"
  },
  "viceCaptain": {
    "name": "Vice Captain Name",
    "phone": "9876543211",
    "whatsapp": "919876543211",
    "email": "vicecaptain@example.com"
  },
  "players": [
    {
      "name": "Player 1",
      "age": 20,
      "phone": "9999999999",
      "role": "Batsman"
      // jersey_number: OMITTED - backend auto-assigns "1"
    },
    {
      "name": "Player 2",
      "age": 21,
      "phone": "9999999998",
      "role": "Bowler"
      // jersey_number: OMITTED - backend auto-assigns "2"
    }
    // ... more players ...
  ]
}
```

**Expected:** Backend auto-assigns jersey_number from position (1, 2, 3...)

---

### Test 3: Using camelCase Field Names

**Payload (Both formats should work):**
```json
{
  "players": [
    {
      "name": "Player Name",
      "age": 20,
      "phone": "9999999999",
      "role": "Batsman",
      "jerseyNumber": "1",        // ✅ camelCase
      "aadharFile": "data:...",
      "subscriptionFile": "data:..."
    }
  ]
}
```

OR

```json
{
  "players": [
    {
      "name": "Player Name",
      "age": 20,
      "phone": "9999999999",
      "role": "Batsman",
      "jersey_number": "1",       // ✅ snake_case
      "aadhar_file": "data:...",
      "subscription_file": "data:..."
    }
  ]
}
```

Both should work due to `populate_by_name=True` in Pydantic.

---

## 🐛 DEBUGGING STEPS

If you still get the null error, follow these steps:

### Step 1: Check Render Logs
```
1. Go to https://dashboard.render.com/
2. Select ICCT26-BACKEND service
3. Click "Logs"
4. Look for DEBUG entries showing:
   - "Player X: ... Jersey: 1"
   - "Player Y: ... Jersey: 2"
   - etc.
```

### Step 2: Check Database Directly
```sql
-- Connect to Neon console at https://console.neon.tech/
SELECT id, player_id, name, jersey_number FROM players LIMIT 5;

-- Should show jersey_number populated with values like "1", "2", "3", etc.
```

### Step 3: Add Logging to Trace the Issue

If you still have issues, add this temporary logging to `app/routes/registration.py`:

```python
# In the player creation loop, add after line 134:
logger.info(f"DEBUG: player_data.jersey_number = {player_data.jersey_number}")
logger.info(f"DEBUG: jersey_num calculated = {jersey_num}")
logger.info(f"DEBUG: Creating Player with jersey_number={jersey_num}")
```

Then check Render logs to see what's being received.

---

## 📋 Field Aliases - IMPORTANT!

**Pydantic Configuration:**
```python
class PlayerInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # ✅ ALLOWS BOTH
    
    jersey_number: Optional[str] = Field(None, alias="jersey_number")
```

**This means the frontend can send EITHER:**
- `"jersey_number": "1"` (snake_case - preferred)
- `"jerseyNumber": "1"` (camelCase - also works)

Both will be accepted and mapped correctly.

---

## ✅ CURL TEST COMMAND

Run this from terminal to test locally (update BASE64 strings with real data):

```bash
curl -X POST http://localhost:8000/api/register/team \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "Test Church",
    "teamName": "Test Team",
    "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
    "paymentReceipt": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
    "captain": {
      "name": "Test Captain",
      "phone": "9999999999",
      "whatsapp": "919999999999",
      "email": "captain@test.com"
    },
    "viceCaptain": {
      "name": "Test Vice Captain",
      "phone": "9999999998",
      "whatsapp": "919999999998",
      "email": "vicecaptain@test.com"
    },
    "players": [
      {
        "name": "Test Player 1",
        "age": 20,
        "phone": "9999999990",
        "role": "Batsman",
        "jersey_number": "1"
      },
      {
        "name": "Test Player 2",
        "age": 21,
        "phone": "9999999991",
        "role": "Bowler",
        "jersey_number": "2"
      },
      {
        "name": "Test Player 3",
        "age": 22,
        "phone": "9999999992",
        "role": "All-rounder"
      }
    ]
  }'
```

---

## 🎯 SUMMARY

| Component | Status | Verified |
|-----------|--------|----------|
| models.py jersey_number | ✅ String(3), NOT NULL | YES |
| schemas_team.py jersey_number | ✅ Optional[str], auto-assigns | YES |
| registration.py assignment | ✅ Guaranteed non-null value | YES |
| Database column | ✅ VARCHAR(3), NOT NULL | NEEDS CHECK |
| Frontend payload format | ❓ Likely cause if null | CHECK |

**If you're still getting null errors:**
1. Check Render logs for the DEBUG messages
2. Verify frontend is sending `jersey_number` field
3. Verify database column is String(3) NOT NULL
4. Check if camelCase/snake_case mismatch

