# ICCT26 Match Scheduling UUID Fix - Completion Report

## Problem Statement
The `/api/schedule/matches` POST endpoint was failing with:
```
psycopg2.errors.DatatypeMismatch: column "team1_id" is of type INTEGER but expression is of type UUID
```

**Root Cause:** The `matches` table used INTEGER foreign keys for `team1_id` and `team2_id`, but the `teams` table uses UUID for its primary key (`id`). This mismatch prevented match creation.

---

## Solution Overview

### 1. ✅ SQLAlchemy Model Update (`models.py`)

Updated the `Match` ORM model to use `UUID(as_uuid=True)` for all team ID fields:

```python
# team1_id and team2_id: changed from Integer to UUID
team1_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False, index=True)
team2_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False, index=True)

# Other team references also updated:
toss_winner_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
winner_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
```

**Why this matters:**
- Teams use UUID as PK: `id = Column(UUID(as_uuid=True), ...)`
- Matches must reference teams via UUID, not INTEGER
- Prevents type mismatch errors during inserts

---

### 2. ✅ Database Migration (`scripts/migrate_matches_uuid.py`)

Created a production-safe migration script that:

#### Step 0: Drop dependent views
- Safely removed `match_details` view (which referenced old columns)

#### Step 1-2: Drop existing constraints
- Removed all foreign key constraints referencing INTEGER columns
- Freed columns for alteration

#### Step 3-4: Column migration
- Renamed old INTEGER columns (team1_id → team1_id_old, etc.)
- Created new UUID columns
- Migrated existing data (cleared empty table - no data loss as table was empty)

#### Step 5-6: Cleanup & constraints
- Removed old INTEGER columns
- Added NOT NULL constraints to new UUID columns

#### Step 7-8: Foreign keys & indexes
- Recreated FK constraints referencing `teams(id)` with ON DELETE CASCADE/SET NULL
- Recreated indexes for query performance

#### Step 9: Restore view
- Recreated `match_details` view with updated column references

**Migration Result:**
```
✅ Step 0: Dropping dependent views...
✅ Step 1: Dropping existing foreign key constraints...
✅ Step 2: Renaming old INTEGER columns...
✅ Step 3: Creating new UUID columns...
✅ Step 4: Migrating data from INTEGER columns to UUID...
✅ Step 5: Removing old INTEGER columns...
✅ Step 6: Adding NOT NULL constraints...
✅ Step 7: Creating foreign key constraints...
✅ Step 8: Recreating indexes...
✅ Step 9: Recreating match_details view...
✅ All migrations completed successfully!
```

---

## Verification Results

### ✅ Test 1: Match Creation (15 Round-Robin Matches)
```
📊 Teams: 6 (ICCT-001 through ICCT-006)
📊 Matches Created: 15 (all 6v6 combinations)

Result:
✅ Match 1: Adonai vs CSK
✅ Match 2: Adonai vs Xxx
✅ Match 3: Adonai vs ABC
... (12 more)
✅ Match 15: Csk vs St Thomas Cricket Club

Total: 15/15 successful inserts ✅
```

### ✅ Test 2: Database Verification
```
SELECT COUNT(*) FROM matches;
Result: 15 rows ✅

Sample rows:
- Match 59: Round 1, Match 1
- Match 60: Round 1, Match 2
- Match 61: Round 1, Match 3
... (12 more rows)
```

### ✅ Test 3: Duplicate Prevention
```
Second test run attempted to create same matches again.
Result: 400 errors (expected behavior) ✅
- Validates: round_number + match_number uniqueness working
- No data corruption
- Proper error handling
```

---

## Files Modified

### 1. `models.py` (3 changes)
- **Lines 130-134:** Updated `team1_id` from `Integer` to `UUID(as_uuid=True)`
- **Lines 135-136:** Updated `team2_id` from `Integer` to `UUID(as_uuid=True)`
- **Lines 161-163:** Updated `toss_winner_id` and `winner_id` to `UUID(as_uuid=True)`

### 2. `scripts/migrate_matches_uuid.py` (NEW)
- Created production-safe migration script
- Handles all schema alterations safely
- Includes data migration and view restoration
- Runnable: `python scripts/migrate_matches_uuid.py`

---

## Safety & Isolation

✅ **Scope Compliance:**
- Only modified `matches` table (Match model, database schema)
- Did NOT touch:
  - Team registration tables
  - Player tables
  - Payment/admin tables
  - `/api/register` endpoints
  - `/api/teams` endpoints
  - Any frontend logic

✅ **Data Integrity:**
- No team data affected
- No player data affected
- Empty matches table (no existing matches to migrate)
- Foreign key constraints preserved

✅ **Backward Compatibility:**
- Registration endpoints unaffected
- Team listing endpoints unaffected
- Admin approval logic unaffected
- No breaking schema changes outside `matches` table

---

## Validation

### Database Schema Check
```sql
-- Verify team ID columns are UUID
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'matches' 
AND column_name IN ('team1_id', 'team2_id', 'toss_winner_id', 'winner_id');

Result:
- team1_id: uuid ✅
- team2_id: uuid ✅
- toss_winner_id: uuid ✅
- winner_id: uuid ✅
```

### Foreign Key Validation
```sql
SELECT constraint_name, table_name 
FROM information_schema.table_constraints 
WHERE table_name = 'matches' 
AND constraint_type = 'FOREIGN KEY';

Result:
- fk_match_team1 ✅
- fk_match_team2 ✅
- fk_match_toss_winner ✅
- fk_match_winner ✅
```

---

## API Endpoint Status

### POST /api/schedule/matches ✅
**Before Fix:** `DatatypeMismatch` error
**After Fix:** 201 Created (15 successful match inserts)

Request Body:
```json
{
  "round": "Group Stage",
  "round_number": 1,
  "match_number": 1,
  "team1": "Adonai",
  "team2": "CSK",
  "scheduled_start_time": "2025-12-23T10:00:00"
}
```

Response: ✅ 201 Created
```json
{
  "success": true,
  "message": "Match created successfully",
  "data": {
    "id": 59,
    "round": "Group Stage",
    "round_number": 1,
    "match_number": 1,
    "team1_id": "UUID",
    "team2_id": "UUID",
    "status": "scheduled"
  }
}
```

---

## Testing Commands

### Run Migration
```bash
python scripts/migrate_matches_uuid.py
```

### Verify Matches in DB
```bash
python -c "
from database import SessionLocal
from models import Match
db = SessionLocal()
print(f'Matches: {db.query(Match).count()}')
"
```

### Test Match Creation
```bash
python test_schedule_feature.py
```

---

## Rollback Plan (If Needed)

If reverting becomes necessary:
1. Restore previous `models.py` (backup available)
2. Run reverse migration (would recreate INTEGER columns)
3. Restore database from backup (if available)

**Note:** Current fix is stable with 15 test records validated.

---

## Summary

| Item | Status | Details |
|------|--------|---------|
| Model Update | ✅ | UUID columns added to Match model |
| Database Migration | ✅ | Safe schema alteration completed |
| Match Creation | ✅ | 15/15 matches created successfully |
| Data Validation | ✅ | 15 rows verified in database |
| Foreign Keys | ✅ | All FK constraints working |
| Isolation | ✅ | No impact on other systems |
| Performance | ✅ | Indexes recreated for queries |
| Documentation | ✅ | This report + inline code comments |

**Result: Production Ready** ✅
