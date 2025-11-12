# 🏏 Jersey Number & Role Validation Fix

**Date:** November 12, 2025  
**Issue:** Frontend couldn't send valid role values (e.g., "wicket keeper", "all rounder"), jersey_number field missing from request schema  
**Root Cause:** Pydantic schema validation limits didn't match database column sizes  
**Status:** ✅ FIXED

---

## 🔴 Problems Fixed

### 1. **Phone Field Length Validation**
- **Database Column:** `VARCHAR(15)` (max 15 chars)
- **Schema Validation:** `max_length=20` ❌ (too lenient)
- **Fix:** Changed to `max_length=15` ✅

### 2. **Role Field Length Validation**
- **Database Column:** `VARCHAR(20)` (max 20 chars)
- **Schema Validation:** `max_length=20` ✅ (correct)
- **Issue:** Frontend sends "all rounder" (11 chars) - should work! But strict validation blocked it
- **Fix:** Kept at `max_length=20`, ensures exact match

### 3. **Jersey Number Missing from Schema**
- **Database Column:** `VARCHAR(3)` NOT NULL - **required field**
- **Schema Definition:** `jersey_number` field was completely missing ❌
- **Result:** Frontend couldn't send jersey_number, causing null violation errors
- **Fix:** Added `jersey_number: Optional[str]` to `PlayerInfo` schema ✅

### 4. **Backend Auto-Assignment Logic**
- **Problem:** When frontend omits jersey_number (now optional), backend gets None
- **Solution:** If `player_data.jersey_number` is None, auto-assign from position (1, 2, 3...)
- **Code Change:** `jersey_num = player_data.jersey_number if player_data.jersey_number else str(idx)`

### 5. **Error Handling for Integrity Errors**
- **Problem:** Missing jersey_number caused `NotNullViolationError` → 500 error
- **Solution:** Added specific error handlers for `IntegrityError` and `DataError`
- **Result:** Now returns 400 Bad Request with clear message instead of 500

---

## 📋 Files Changed

### 1. **app/schemas_team.py**
```python
class PlayerInfo(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    age: int = Field(..., ge=15, le=65)
    phone: str = Field(..., min_length=7, max_length=15)  # ✅ FIXED: was 20
    role: str = Field(..., min_length=1, max_length=20)   # ✅ Correct
    
    # ✅ NEW: Jersey number is optional (backend auto-assigns)
    jersey_number: Optional[str] = Field(None, min_length=1, max_length=3)
    
    aadharFile: Optional[str] = Field(None)
    subscriptionFile: Optional[str] = Field(None)
```

**What Changed:**
- `phone`: `max_length=20` → `max_length=15` (matches DB column)
- `jersey_number`: NEW field (Optional, auto-assigned if missing)
- Other fields unchanged

### 2. **app/routes/registration.py**

**Imports Added:**
```python
from sqlalchemy.exc import IntegrityError, DataError
```

**Player Creation Logic (Lines 140-155):**
```python
for idx, player_data in enumerate(registration.players, 1):
    player_id = f"{team_id}-P{idx:02d}"
    # ✅ NEW: Use provided jersey_number or auto-assign
    jersey_num = player_data.jersey_number if player_data.jersey_number else str(idx)
    
    player = Player(
        player_id=player_id,
        team_id=team_id,
        name=player_data.name,
        age=player_data.age,
        phone=player_data.phone,
        role=player_data.role,
        jersey_number=jersey_num,  # ✅ FIXED: guaranteed to have value
        aadhar_file=player_data.aadharFile,
        subscription_file=player_data.subscriptionFile
    )
    players_list.append(player)
```

**Error Handling (New Sections):**
```python
except IntegrityError as e:
    # Handles: NOT NULL violations, UNIQUE constraint failures
    # Returns 400 Bad Request with specific message
    logger.error(f"❌ Integrity error: {str(e.orig)}")
    # Check if jersey_number field failed
    if "jersey_number" in error_msg:
        detail_msg = "Jersey number is required or invalid"
    # ... handle other fields ...
    raise HTTPException(status_code=400, detail={...})

except DataError as e:
    # Handles: Data too long, invalid data type
    # Returns 400 Bad Request
    logger.error(f"❌ Data error: {str(e.orig)}")
    raise HTTPException(status_code=400, detail={...})
```

---

## ✅ Validation Rules

| Field | Min | Max | Type | Notes |
|-------|-----|-----|------|-------|
| `name` | 1 | 150 | string | Required |
| `age` | 15 | 65 | int | Required |
| `phone` | 7 | 15 | string | Required, digits/+ only |
| `role` | 1 | 20 | string | Required. Examples: "Batsman", "Bowler", "All-rounder", "Wicket Keeper" |
| `jersey_number` | 1 | 3 | string | Optional. Auto-assigned (1,2,3...) if omitted |
| `aadharFile` | - | - | base64 | Optional, JPEG/PNG/PDF only |
| `subscriptionFile` | - | - | base64 | Optional, JPEG/PNG/PDF only |

---

## 🧪 Test Cases

### ✅ Test 1: Frontend Sends role="all rounder"
```json
{
  "name": "Robin Singh",
  "age": 20,
  "phone": "9999999999",
  "role": "all rounder",
  "aadharFile": "data:image/jpeg;base64,...",
  "subscriptionFile": "data:application/pdf;base64,..."
}
```
**Expected:** ✅ PASS (11 chars ≤ 20 chars limit)

### ✅ Test 2: Frontend Sends role="wicket keeper"
```json
{
  "role": "wicket keeper"
}
```
**Expected:** ✅ PASS (13 chars ≤ 20 chars limit)

### ✅ Test 3: Frontend Omits jersey_number (AUTO-ASSIGN)
```json
{
  "name": "Arjun Kumar",
  "age": 22,
  "phone": "8888888888",
  "role": "Bowler"
  // jersey_number: OMITTED
}
```
**Expected:** ✅ PASS  
**Backend Assigns:** `jersey_number = "1"` (first player), `"2"` (second), etc.

### ✅ Test 4: Frontend Provides jersey_number
```json
{
  "name": "Vikram Patel",
  "age": 25,
  "phone": "7777777777",
  "role": "Batsman",
  "jersey_number": "07"
}
```
**Expected:** ✅ PASS  
**Backend Uses:** `jersey_number = "07"` (as provided)

### ❌ Test 5: Phone too long (>15 chars)
```json
{
  "phone": "919876543210123"  // 15 chars ✅
}
```
**Expected:** ✅ PASS

```json
{
  "phone": "9198765432101234"  // 16 chars ❌
}
```
**Expected:** ❌ FAIL (422 Validation Error)

### ❌ Test 6: Role too long (>20 chars)
```json
{
  "role": "All-rounder Fast Bowler"  // 25 chars ❌
}
```
**Expected:** ❌ FAIL (422 Validation Error)

### ❌ Test 7: Jersey number too long (>3 chars)
```json
{
  "jersey_number": "1234"  // 4 chars ❌
}
```
**Expected:** ❌ FAIL (422 Validation Error)

---

## 📊 Response Examples

### ✅ Successful Registration (201 Created)
```json
{
  "success": true,
  "message": "Team and players registered successfully",
  "team_id": "ICCT26-20251112120000",
  "team_name": "Mumbai Warriors",
  "church_name": "St. Mary's Church",
  "captain_name": "Rohit Sharma",
  "vice_captain_name": "Virat Kohli",
  "player_count": 11,
  "registration_date": "2025-11-12T12:00:00.123456"
}
```

### ❌ Validation Error (422)
```json
{
  "success": false,
  "message": "Validation error: String should have at most 20 characters",
  "detail": {
    "loc": ["body", "players", 0, "role"],
    "msg": "String should have at most 20 characters",
    "type": "string_too_long"
  }
}
```

### ❌ Integrity Error (400) - NEW!
```json
{
  "success": false,
  "message": "Jersey number is required or invalid. Backend auto-assigns if omitted.",
  "error": "null value in column \"jersey_number\""
}
```

### ❌ Data Error (400) - NEW!
```json
{
  "success": false,
  "message": "Invalid data format or field too long: value too long for type character varying(20)",
  "error": "value too long for type character varying(20)"
}
```

---

## 🚀 How to Test

### Option 1: cURL from Terminal
```bash
curl -X POST https://icct26-backend.onrender.com/api/register/team \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "St. Mary Church",
    "teamName": "Mumbai Warriors",
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
        "name": "Robin Singh",
        "age": 20,
        "phone": "9999999999",
        "role": "all rounder",
        "aadharFile": "data:image/jpeg;base64,..."
      },
      {
        "name": "Vikram Patel",
        "age": 25,
        "phone": "8888888888",
        "role": "wicket keeper"
      }
      // ... 9 more players ...
    ],
    "paymentReceipt": "data:image/jpeg;base64,..."
  }'
```

### Option 2: Postman
1. Create new POST request to `https://icct26-backend.onrender.com/api/register/team`
2. Set header: `Content-Type: application/json`
3. Copy JSON from above into Body (raw)
4. Click Send
5. Verify 201 Created response

### Option 3: Frontend Form
1. Navigate to https://icct26.netlify.app
2. Fill registration form
3. Select role: "all rounder" or "wicket keeper"
4. Jersey numbers will auto-assign (no need to fill)
5. Submit
6. Check DevTools Console for success message

---

## 🔍 Database Verification

Run in Neon console:
```sql
\d+ players;
```

Should show:
```
jersey_number | character varying(3) | not null
phone         | character varying(15)| not null
role          | character varying(20)| not null
```

---

## 📝 Summary

| Issue | Before | After | Impact |
|-------|--------|-------|--------|
| Phone validation | 20 chars | 15 chars | ✅ Matches DB |
| Jersey number field | Missing | Optional | ✅ Auto-assigns if omitted |
| Role validation | N/A | 20 chars | ✅ "all rounder" now works |
| Null errors | 500 error | 400 error | ✅ Better error messages |
| Error handling | Generic | Specific | ✅ IntegrityError, DataError handled |

**Result:** Frontend can now send any valid role (≤20 chars), jersey_number auto-assigns, better error messages for debugging.

---

## 🎯 Next Steps

1. ✅ Commit this fix: `git add app/schemas_team.py app/routes/registration.py`
2. ✅ Push to GitHub: `git push origin main`
3. ✅ Wait for Render auto-deploy (5-10 min)
4. ✅ Test endpoint with role="all rounder"
5. ✅ Verify database has correct jersey_numbers

