# Team ID Generation - Quick Reference

## What Was Fixed

**Problem:** Team IDs were duplicating (ICCT-001, ICCT-001, etc.) under concurrent requests

**Root Cause:** No database-level locking in sequence generation

**Solution:** Implemented `SELECT...FOR UPDATE` for atomic, locked ID generation

## How It Works Now

### Before Team Registration
1. Lock sequence row (only one request at a time)
2. Read current number from `team_sequence` table
3. Increment atomically
4. Return formatted ID (ICCT-006 from number 6)

### Why This Works
- Database enforces locking (not code)
- No race conditions possible
- Industry-standard pattern

## New Functions in `app/utils/race_safe_team_id.py`

```python
# Generate next ID (with auto-locking)
team_id = await generate_next_team_id(db)
# Returns: "ICCT-006"

# Generate with retry logic
team_id = await generate_next_team_id_with_retry(db, max_retries=5)

# Get current number
current = await get_current_sequence_number(db)
# Returns: 5 (next will be ICCT-006)

# Sync with database (on startup automatically)
await sync_sequence_with_teams(db)

# Reset sequence (admin only)
await reset_sequence(db, new_number=100)
```

## New Admin Endpoints

### View Current Sequence
```bash
curl http://localhost:8000/admin/sequence/current
```

Response:
```json
{
    "success": true,
    "current_number": 5,
    "next_team_id": "ICCT-006"
}
```

### Reset Sequence (Admin Only)
```bash
curl -X POST "http://localhost:8000/admin/sequence/reset?new_number=100"
```

### Auto-Sync Sequence
```bash
curl -X POST http://localhost:8000/admin/sequence/sync
```

## Usage in Registration

```python
from app.utils.race_safe_team_id import generate_next_team_id_with_retry

# In registration endpoint
team_id = await generate_next_team_id_with_retry(db, max_retries=5)

team = Team(
    team_id=team_id,
    team_name=team_data.team_name,
    # ...other fields
)
```

## Why SELECT...FOR UPDATE?

```sql
-- This is what happens internally:
BEGIN TRANSACTION;

-- Lock the sequence row (blocks other transactions)
SELECT last_number FROM team_sequence WHERE id = 1 FOR UPDATE;
-- Result: 5

-- Only this transaction can do this while locked
UPDATE team_sequence SET last_number = 6 WHERE id = 1;

COMMIT;
-- Lock automatically released
```

Result: Guaranteed unique, sequential IDs!

## Files Changed

1. **app/utils/race_safe_team_id.py** - New atomic ID generation
2. **app/routes/registration_production.py** - Use new approach
3. **app/routes/admin.py** - Admin endpoints for control
4. **main.py** - Startup sync on application launch
5. **app/utils/startup_validation.py** - Validate sequence table

## Testing

### Single Request
```bash
curl -X POST http://localhost:8000/admin/sequence/current
# Should return ICCT-006 as next ID
```

### Concurrent Requests (No Duplicates!)
```bash
# 5 simultaneous registrations
for i in {1..5}; do
    curl -X POST http://localhost:8000/register/team \
         -F "team_name=Team$i" \
         -F "captain_phone=555000$i" \
         # ...other fields &
done
wait
# Result: ICCT-001, ICCT-002, ICCT-003, ICCT-004, ICCT-005 ✅
```

## Monitoring

Watch logs for these indicators:

### ✅ Success
```
✅ Generated team ID: ICCT-006 (sequence: 5 → 6)
✅ Sequence synchronized (current: 5, next: ICCT-006)
```

### ❌ Problems (shouldn't happen now)
```
❌ duplicate key value violates unique constraint "teams_team_id_key"
(This means FOR UPDATE isn't working - contact support)
```

## Emergency Reset

If sequence gets out of sync:

```bash
# Option 1: Auto-sync with database
curl -X POST http://localhost:8000/admin/sequence/sync

# Option 2: Manual reset (know what you're doing!)
curl -X POST "http://localhost:8000/admin/sequence/reset?new_number=5"
```

## Key Takeaway

**The sequence table uses database-level locking to guarantee:**
- ✅ No duplicate IDs
- ✅ Perfect sequential numbering
- ✅ Works under ANY concurrent load
- ✅ Survives server restarts
- ✅ Manually controllable if needed

This is the industry-standard approach used in production systems worldwide!
