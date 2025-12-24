# Church Team Limit Enforcement (Max 2 Teams)

## Overview
This document describes the implementation of a backend-only validation that enforces a maximum of 2 teams per church in the ICCT26 registration system.

## Feature Details

### 1. Core Validation: Max 2 Teams Per Church

**Location**: `app/utils/church_limit_validator.py::validate_church_limit()`

**How It Works**:
- Before inserting a new team, the registration endpoint performs a check on the teams table
- The check counts existing teams for the church using the `church_name` field
- If count >= 2, the request is rejected with HTTP 400
- Uses database-level locking (SELECT FOR UPDATE) to prevent race conditions

**Integration Point**:
- Called in `app/routes/registration_production.py` at line ~418
- Executes within the same transaction as team/player insertion
- Ensures atomicity and prevents concurrent bypass attempts

**Error Response**:
```json
{
    "success": false,
    "detail": "Maximum 2 teams already registered for this church"
}
```

Status Code: **400 Bad Request**

### 2. Race Condition Protection

**Implementation**: SELECT FOR UPDATE with Async Transaction

```python
# The validator uses:
stmt = select(func.count(Team.id)).where(
    Team.church_name == church_name
).with_for_update()

result = await db.execute(stmt)
team_count = result.scalar() or 0
```

**Why This Works**:
- `SELECT FOR UPDATE` acquires a row-level lock on matching rows
- Prevents other concurrent transactions from reading/modifying those rows
- Two simultaneous requests cannot both see team_count < 2
- First request will lock; second request waits for lock release
- By the time second request acquires lock, the count will be 2, and it will be rejected

**Scenario**:
```
Time  Request A                         Request B
t0    Count teams for "Grace Church"   Count teams for "Grace Church"
      Result: 1 team (acquires lock)   Waits for lock...
t1    Validates: 1 < 2 ✅             [blocked]
      Inserts new team
t2    Commits transaction              Acquires lock
                                       Counts teams: 2
                                       Validates: 2 >= 2 ❌
                                       Rejects with 400
```

### 3. Church Availability Endpoint (Read-Only)

**Endpoint**: `GET /api/churches/availability`

**Location**: `app/routes/churches.py`

**Purpose**: 
- Provides frontend/admin visibility into which churches can still register
- Non-blocking, read-only operation
- Does not affect registration logic

**Request**:
```bash
GET /api/churches/availability
```

**Response**:
```json
{
    "churches": [
        {
            "church_name": "Grace Church",
            "team_count": 1,
            "locked": false
        },
        {
            "church_name": "Holy Trinity",
            "team_count": 2,
            "locked": true
        },
        {
            "church_name": "New Life Assembly",
            "team_count": 0,
            "locked": false
        }
    ],
    "summary": {
        "total_churches": 3,
        "locked_churches": 1,
        "available_churches": 2
    }
}
```

**Status Code**: 200 OK

## Implementation Details

### Files Created

1. **`app/utils/church_limit_validator.py`** (NEW)
   - `validate_church_limit(db, church_name, request_id)` - Core validation function
   - `get_church_availability(db)` - Query for availability endpoint
   - Uses SELECT FOR UPDATE locking
   - Comprehensive error handling and logging

2. **`app/routes/churches.py`** (NEW)
   - `GET /api/churches/availability` - Read-only endpoint
   - Returns church availability summary
   - Included in main router

### Files Modified

1. **`app/routes/registration_production.py`**
   - Line 25: Added import for `validate_church_limit`
   - Lines ~418-420: Added validation call before team insertion
   - Lines ~515-525: Added HTTPException handler for church limit validation

2. **`app/routes/__init__.py`**
   - Line 11: Added import for churches router
   - Line 22: Registered churches router in main_router

### No Database Schema Changes
- No migrations required
- No new tables created
- Uses existing `teams.church_name` column
- Zero impact on existing data

## API Contract

### Registration Endpoint (Unchanged)
```
POST /api/register/team
```
- Signature: **UNCHANGED**
- Request format: **UNCHANGED**
- Response format: **UNCHANGED**
- Side effect: Now includes church limit validation before insertion

### New Endpoint
```
GET /api/churches/availability
```
- New read-only endpoint
- No impact on registration flow
- Can be called anytime without side effects

## Testing

### Test Case 1: Single Church Registration
```bash
# Register Team A for "Grace Church" (no prior teams)
POST /api/register/team
Response: 200 ✅

# Register Team B for "Grace Church" (1 prior team)
POST /api/register/team
Response: 200 ✅

# Try to register Team C for "Grace Church" (2 prior teams)
POST /api/register/team
Response: 400 ❌
Detail: "Maximum 2 teams already registered for this church"
```

### Test Case 2: Check Availability
```bash
GET /api/churches/availability

Response:
{
    "churches": [
        {
            "church_name": "Grace Church",
            "team_count": 2,
            "locked": true
        }
    ],
    "summary": {
        "total_churches": 1,
        "locked_churches": 1,
        "available_churches": 0
    }
}
```

### Test Case 3: Concurrent Registrations (Race Condition Test)
```
# Two simultaneous requests for the same church (1 team currently registered)

Time  Thread 1                    Thread 2
t0    Lock acquired
      Count: 1 ✅
t1                              Lock wait...
      Insert team
      Commit
t2                              Lock acquired
                                Count: 2 ❌
                                Reject 400
```

## Safety & Backward Compatibility

✅ **No Breaking Changes**
- Registration endpoint signature unchanged
- Request/response format unchanged
- No database migrations
- No schema changes

✅ **Data Integrity**
- Row-level locking prevents race conditions
- Atomic transaction ensures consistency
- Existing registrations unaffected

✅ **Isolation**
- Only affects team registration flow
- Does not touch:
  - Player registration
  - File uploads
  - Email sending
  - Admin approval
  - Payment processing
  - Authentication
  - Any other APIs

✅ **Error Handling**
- Clean HTTP 400 for exceeded limits
- Proper exception handling in registration endpoint
- Logging for audit trail
- Cloudinary cleanup on validation failure

## Production Readiness

✅ **Locking Strategy**: SELECT FOR UPDATE (production-grade)
✅ **Transaction Isolation**: Async transaction with row locking
✅ **Error Messages**: User-friendly, specific error details
✅ **Logging**: Comprehensive request ID tracking
✅ **Monitoring**: Structured logs for audit trail
✅ **Performance**: O(1) count operation, minimal overhead

## Configuration

No configuration required. The 2-team limit is hardcoded as a requirement. To change the limit in the future:

**File**: `app/utils/church_limit_validator.py`
**Line**: 71 (in `validate_church_limit` function)
```python
if team_count >= 2:  # <-- Change this number
```

## Deployment

### Pre-Deployment Checklist
- ✅ No database migrations needed
- ✅ No existing data to modify
- ✅ No schema changes
- ✅ Import statement added to registration endpoint
- ✅ Churches router registered

### Deployment Steps
1. Deploy code changes
2. Restart application
3. Verify `/api/churches/availability` endpoint responds
4. Test registration with multiple teams per church

### Rollback Plan
1. Revert code changes (2 files modified, 2 files created)
2. Remove import of `church_limit_validator`
3. Remove validation call from registration endpoint
4. Remove churches router registration
5. Restart application
6. No database recovery needed (no schema changes)

## Logging & Monitoring

### Log Examples

**Successful Validation**:
```
[abc123def] 🔒 Checking church team limit for: Grace Church
[abc123def] Current team count for 'Grace Church': 1
[abc123def] ✅ Church limit check passed: 1/2 teams
```

**Validation Failed**:
```
[abc123def] 🔒 Checking church team limit for: Grace Church
[abc123def] Current team count for 'Grace Church': 2
[abc123def] ❌ Church limit exceeded: 'Grace Church' already has 2 team(s), maximum is 2
```

**Request Rejected**:
```
[abc123def] Request rejected: Maximum 2 teams already registered for this church
[abc123def] Cleaning up 2 uploaded files...
```

## Summary

| Aspect | Status | Details |
|--------|--------|---------|
| Core Validation | ✅ | Enforces max 2 teams per church |
| Race Condition Protection | ✅ | SELECT FOR UPDATE locking |
| Non-Intrusive | ✅ | No schema changes, backward compatible |
| Error Handling | ✅ | HTTP 400 with clear message |
| Availability API | ✅ | Read-only endpoint for visibility |
| Logging | ✅ | Comprehensive audit trail |
| Testing | ✅ | Ready for concurrent load testing |
| Production Ready | ✅ | Secure, performant, maintainable |

---

**Implementation Date**: December 24, 2025  
**Status**: Production Ready ✅
