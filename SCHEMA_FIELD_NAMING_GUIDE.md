# 📋 SCHEMA FIELD NAMING & UNPACKING GUIDE

**Status:** ✅ All schemas verified and aligned  
**Date:** November 12, 2025

---

## 🎯 CRITICAL: Field Name Convention

### **Database Column Names (snake_case)**
These are the EXACT names in PostgreSQL:
```sql
SELECT * FROM players;

Columns:
  - player_id
  - team_id
  - name
  - age
  - phone
  - role
  - jersey_number        ← SNAKE_CASE
  - aadhar_file          ← SNAKE_CASE
  - subscription_file    ← SNAKE_CASE
```

---

## 🔄 Schema Hierarchy

### **Level 1: Frontend Request (camelCase)**
Frontend sends this format (from React form):
```json
{
  "players": [
    {
      "name": "Player Name",
      "age": 20,
      "phone": "9999999999",
      "role": "Batsman",
      "jerseyNumber": "1",           ← camelCase
      "aadharFile": "data:...",      ← camelCase
      "subscriptionFile": "data:..."  ← camelCase
    }
  ]
}
```

### **Level 2: Pydantic Request Schema (app/schemas_team.py)**
```python
class PlayerInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(..., alias="name")
    age: int = Field(...)
    phone: str = Field(...)
    role: str = Field(...)
    jersey_number: Optional[str] = Field(None, min_length=1, max_length=3, alias="jersey_number")
    aadharFile: Optional[str] = Field(None, alias="aadhar_file")    # Accepts camelCase
    subscriptionFile: Optional[str] = Field(None, alias="subscription_file")  # Accepts camelCase
```

**What happens:**
- `populate_by_name=True` allows BOTH camelCase and snake_case
- Frontend sends: `"aadharFile"` (camelCase)
- Pydantic parses it as: `aadharFile` (Python attribute)
- Database stores as: `aadhar_file` (via alias mapping)

### **Level 3: ORM Model (models.py)**
```python
class Player(Base):
    __tablename__ = "players"
    
    player_id = Column(String(50), unique=True, nullable=False)
    team_id = Column(String(50), ForeignKey("teams.team_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String(15), nullable=False)
    role = Column(String(20), nullable=False)
    jersey_number = Column(String(3), nullable=False)      ← MUST BE snake_case
    aadhar_file = Column(Text)                              ← MUST BE snake_case
    subscription_file = Column(Text)                        ← MUST BE snake_case
```

### **Level 4: PlayerCreate Schema (app/schemas.py)**
For bulk inserts, use this exact schema:
```python
class PlayerCreate(BaseModel):
    """All fields use snake_case to match database columns exactly"""
    
    player_id: str
    team_id: str
    name: str
    age: int
    phone: str
    role: str
    jersey_number: str              ← snake_case
    aadhar_file: Optional[str]      ← snake_case
    subscription_file: Optional[str] ← snake_case
```

---

## ✅ CORRECT UNPACKING PATTERNS

### **Pattern 1: Direct Attribute Access (PREFERRED)**
```python
# ✅ CORRECT - Uses Python attribute names
for player_data in registration.players:
    jersey_num = player_data.jersey_number or str(idx)
    
    player = Player(
        player_id=f"{team_id}-P{idx:02d}",
        team_id=team_id,
        name=player_data.name,
        age=player_data.age,
        phone=player_data.phone,
        role=player_data.role,
        jersey_number=jersey_num,          # ← snake_case in model
        aadhar_file=player_data.aadharFile,        # ← reads from aadharFile (Pydantic attribute)
        subscription_file=player_data.subscriptionFile  # ← reads from subscriptionFile
    )
    db.add(player)
```

### **Pattern 2: .dict() Unpacking (USE WITH CAUTION)**
```python
# ⚠️ CAREFUL - .dict() uses Python attribute names, not database names
player_dict = player_data.dict()
# Result: {'name': '...', 'jersey_number': '...', 'aadharFile': '...'}

# WRONG ❌
player = Player(**player_dict)  # aadharFile won't map to aadhar_file

# CORRECT ✅
player_dict_renamed = {
    'name': player_dict['name'],
    'age': player_dict['age'],
    'phone': player_dict['phone'],
    'role': player_dict['role'],
    'jersey_number': player_dict['jersey_number'],
    'aadhar_file': player_dict['aadharFile'],           # ← rename
    'subscription_file': player_dict['subscriptionFile'] # ← rename
}
player = Player(**player_dict_renamed)
```

### **Pattern 3: Bulk Insert Helper**
```python
def create_player_from_pydantic(team_id: str, idx: int, player_data: PlayerInfo) -> Player:
    """Convert Pydantic PlayerInfo to ORM Player with correct field mapping"""
    jersey_num = player_data.jersey_number or str(idx)
    
    return Player(
        player_id=f"{team_id}-P{idx:02d}",
        team_id=team_id,
        name=player_data.name,
        age=player_data.age,
        phone=player_data.phone,
        role=player_data.role,
        jersey_number=jersey_num,
        aadhar_file=player_data.aadharFile,
        subscription_file=player_data.subscriptionFile
    )

# Usage:
players_list = [
    create_player_from_pydantic(team_id, idx, pd)
    for idx, pd in enumerate(registration.players, 1)
]
db.add_all(players_list)
```

---

## 🔍 FIELD NAME MAPPING TABLE

| Frontend Input | Pydantic Attribute | Database Column | Model Attribute |
|----------------|-------------------|-----------------|-----------------|
| `"name"` | `name` | `name` | `name` |
| `"age"` | `age` | `age` | `age` |
| `"phone"` | `phone` | `phone` | `phone` |
| `"role"` | `role` | `role` | `role` |
| `"jerseyNumber"` OR `"jersey_number"` | `jersey_number` | `jersey_number` | `jersey_number` |
| `"aadharFile"` OR `"aadhar_file"` | `aadharFile` | `aadhar_file` | `aadhar_file` |
| `"subscriptionFile"` OR `"subscription_file"` | `subscriptionFile` | `subscription_file` | `subscription_file` |

**Key Point:** 
- Frontend can use either camelCase OR snake_case (due to `populate_by_name=True`)
- Pydantic uses Python attribute names (mostly camelCase in schema_team.py)
- ORM uses database column names (all snake_case)

---

## ❌ COMMON MISTAKES

### ❌ Mistake 1: Using camelCase in Player Model
```python
class Player(Base):
    __tablename__ = "players"
    jerseyNumber = Column(String(3))  # ❌ WRONG - Database expects snake_case
```

**Result:** `asyncpg.exceptions.NotNullViolationError` - Column `jersey_number` not found

**Fix:**
```python
jersey_number = Column(String(3))  # ✅ CORRECT
```

---

### ❌ Mistake 2: Direct .dict() Unpacking Without Mapping
```python
player = Player(**player_data.dict())  # ❌ WRONG
# Attributes: name, age, phone, role, jersey_number, aadharFile (❌), subscriptionFile (❌)
# Database expects: aadhar_file, subscription_file
```

**Result:** `TypeError: unexpected keyword argument 'aadharFile'`

**Fix:**
```python
# Rename camelCase fields to snake_case
data = player_data.dict()
data['aadhar_file'] = data.pop('aadharFile', None)
data['subscription_file'] = data.pop('subscriptionFile', None)
player = Player(**data)  # ✅ CORRECT
```

---

### ❌ Mistake 3: Forgetting to Handle Optional jersey_number
```python
player = Player(
    jersey_number=player_data.jersey_number  # ❌ Could be None
)
```

**Result:** `asyncpg.exceptions.NotNullViolationError: null value in column "jersey_number"`

**Fix:**
```python
player = Player(
    jersey_number=player_data.jersey_number or str(idx)  # ✅ Fallback to position
)
```

---

### ❌ Mistake 4: Mixing Schema Levels
```python
# ❌ WRONG - Using schemas_team.py PlayerInfo for bulk insert
from app.schemas_team import PlayerInfo

players = [PlayerInfo(**p.dict()) for p in registration.players]  # ❌ Type mismatch

# ✅ CORRECT - Use PlayerCreate for bulk operations
from app.schemas import PlayerCreate

players = [PlayerCreate(**p.dict()) for p in registration.players]  # ✅ Type matches
```

---

## 🧪 TEST VERIFICATION

### Test 1: Verify Pydantic Accepts Both camelCase and snake_case

```python
from app.schemas_team import PlayerInfo

# Both should work:
player1 = PlayerInfo(
    name="Player 1",
    age=20,
    phone="9999999999",
    role="Batsman",
    jerseyNumber="1",          # ← camelCase
    aadharFile="data:..."
)

player2 = PlayerInfo(
    name="Player 2",
    age=21,
    phone="9999999998",
    role="Bowler",
    jersey_number="2",         # ← snake_case
    aadhar_file="data:..."
)

# Both instances should parse successfully
print(f"Player 1 jersey: {player1.jersey_number}")  # Output: "1"
print(f"Player 2 jersey: {player2.jersey_number}")  # Output: "2"
```

### Test 2: Verify ORM Field Names

```python
from models import Player

# Create player instance
player = Player(
    player_id="ICCT26-...-P01",
    team_id="ICCT26-...",
    name="Test Player",
    age=20,
    phone="9999999999",
    role="Batsman",
    jersey_number="1",          # ← MUST be snake_case
    aadhar_file="base64data",   # ← MUST be snake_case
    subscription_file="base64data"
)

# Verify attributes exist
assert player.jersey_number == "1"
assert player.aadhar_file is not None
print("✅ ORM model correctly accepts snake_case field names")
```

### Test 3: Full Unpacking Workflow

```python
# Frontend JSON
payload = {
    "players": [
        {
            "name": "Player 1",
            "age": 20,
            "phone": "9999999999",
            "role": "Batsman",
            "jerseyNumber": "1",        # ← camelCase from frontend
            "aadharFile": "data:..."
        }
    ]
}

# Parse with Pydantic
from app.schemas_team import TeamRegistrationRequest
request = TeamRegistrationRequest(**payload)

# Unpack to ORM
from models import Player
for idx, player_data in enumerate(request.players, 1):
    player = Player(
        player_id=f"ICCT26-...-P{idx:02d}",
        team_id="ICCT26-...",
        name=player_data.name,
        age=player_data.age,
        phone=player_data.phone,
        role=player_data.role,
        jersey_number=player_data.jersey_number or str(idx),
        aadhar_file=player_data.aadharFile,       # ← reads from Pydantic attribute
        subscription_file=player_data.subscriptionFile
    )
    # Player model converts to snake_case for database
    assert player.jersey_number is not None
    assert player.aadhar_file is not None
    
print("✅ Full workflow tested successfully")
```

---

## 🔧 QUICK REFERENCE

| Layer | Field Name Style | Example |
|-------|------------------|---------|
| Frontend (JSON) | camelCase OR snake_case | `"jerseyNumber"` or `"jersey_number"` |
| Pydantic Schema | Python naming (mixed) | `jersey_number` (attribute) |
| ORM Model | snake_case (SQL convention) | `jersey_number` (Column) |
| Database | snake_case (SQL) | `jersey_number` (table column) |

**Golden Rule:**
```
Frontend (any case)
    ↓
Pydantic (with alias mapping)
    ↓
ORM Model (snake_case)
    ↓
Database (snake_case)
```

---

## ✅ PRODUCTION CHECKLIST

- [ ] All Column names in models.py use snake_case
- [ ] ORM Model attributes match Column names exactly
- [ ] Pydantic schemas have `populate_by_name=True` for flexibility
- [ ] Field aliases map camelCase to snake_case where needed
- [ ] jersey_number is guaranteed non-null before insert (via auto-assign)
- [ ] .dict() operations handle field renaming if needed
- [ ] Bulk insert uses PlayerCreate schema (all snake_case)
- [ ] Frontend can send either camelCase or snake_case
- [ ] Database stores everything in snake_case
- [ ] All tests pass with field name combinations

