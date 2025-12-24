# ICCT26 Backend - Frontend Integration Prompt

**Last Updated:** December 24, 2025  
**Backend Version:** 1.0.0 (Production Ready)

---

## Executive Summary

The backend has implemented a **Church Team Limit Feature** that enforces a maximum of 2 teams per church. This document provides comprehensive integration guidance for the frontend.

**Status:** ✅ Backend implementation complete. 57/57 tests passing. Production-ready.

---

## 1. KEY CHANGES - Church Team Limit Feature

### What Changed
- Backend now enforces a **maximum of 2 teams per church**
- Validation happens atomically at database level using row-level locking
- Prevents concurrent requests from bypassing the limit
- **NO database schema changes** required on frontend
- **NO API contract breaking changes**

### User Impact
When a user tries to register a 3rd team for any church:
- HTTP 400 Bad Request response
- Error message: "Maximum 2 teams already registered for this church"
- Previously uploaded files are automatically cleaned up
- User can retry with a different church name

---

## 2. NEW API ENDPOINT

### GET /api/churches/availability

**Purpose:** Check church capacity before registration

**Request:**
```
GET http://localhost:8000/api/churches/availability
```

**Response (200 OK):**
```json
{
  "churches": [
    {
      "church_name": "Grace Church",
      "team_count": 2,
      "locked": true
    },
    {
      "church_name": "New Life Assembly",
      "team_count": 1,
      "locked": false
    }
  ],
  "summary": {
    "total_churches": 5,
    "locked_churches": 1,
    "available_churches": 4
  }
}
```

**Status Codes:**
- `200 OK` - Successfully retrieved church availability
- `500 Internal Server Error` - Database error

**Frontend Use Cases:**
1. Display locked/available status on church selection dropdown
2. Show "This church is at capacity (2/2)" warning
3. Disable church selection when locked (optional)
4. Show real-time capacity updates

---

## 3. REGISTRATION ENDPOINT - Updated

### POST /api/register/team

**Endpoint:** `http://localhost:8000/api/register/team`

**Method:** POST  
**Content-Type:** multipart/form-data  
**Headers:** Optional: `Idempotency-Key: <unique-uuid>`

---

### 3.1 Form Fields (No Changes from Before)

#### Team Information
```
team_name         (string, required) - Team name (3-50 chars)
church_name       (string, required) - Church name (3-100 chars)
```

#### Captain Details
```
captain_name      (string, required) - Captain full name
captain_phone     (string, required) - 10-digit phone number
captain_email     (string, required) - Valid email address
captain_whatsapp  (string, optional) - 10-digit WhatsApp number
```

#### Vice-Captain Details
```
vice_name         (string, required) - Vice-captain full name  
vice_phone        (string, required) - 10-digit phone number
vice_email        (string, required) - Valid email address
vice_whatsapp     (string, optional) - 10-digit WhatsApp number
```

#### Player Information (11 Players Required)
```
player_0_name     (string, required) - Player name
player_0_role     (string, required) - Role (Batsman, Bowler, All-rounder)
player_0_aadhar_file    (file, optional) - Aadhar/ID document
player_0_subscription_file (file, optional) - Subscription document

... repeat for player_1 through player_10 ...
```

#### File Uploads (3 Required)
```
pastor_letter     (file, required) - Pastor approval letter (PDF)
payment_receipt   (file, required) - Payment receipt (PDF)
group_photo       (file, required) - Team group photo (JPG/PNG)
```

---

### 3.2 Form Submission Example

```javascript
const formData = new FormData();

// Team info
formData.append('team_name', 'Team Alpha');
formData.append('church_name', 'Grace Church');

// Captain info
formData.append('captain_name', 'John Doe');
formData.append('captain_phone', '9876543210');
formData.append('captain_email', 'john@example.com');
formData.append('captain_whatsapp', '9876543210');

// Vice-captain info
formData.append('vice_name', 'Jane Smith');
formData.append('vice_phone', '9876543211');
formData.append('vice_email', 'jane@example.com');
formData.append('vice_whatsapp', '9876543211');

// Players (example for 2 players)
formData.append('player_0_name', 'Player One');
formData.append('player_0_role', 'Batsman');

formData.append('player_1_name', 'Player Two');
formData.append('player_1_role', 'Bowler');

// ... add remaining 9 players ...

// Files
formData.append('pastor_letter', pastorFile);      // File object
formData.append('payment_receipt', receiptFile);   // File object
formData.append('group_photo', photoFile);         // File object

// Submit
const response = await fetch('/api/register/team', {
  method: 'POST',
  body: formData,
  headers: {
    'Idempotency-Key': crypto.randomUUID()  // Optional but recommended
  }
});
```

---

### 3.3 Response on Success (200 OK)

```json
{
  "success": true,
  "message": "Team registered successfully",
  "team_id": "ICCT-008",
  "team_name": "Team Alpha",
  "church_name": "Grace Church",
  "player_count": 11,
  "registration_status": "pending",
  "captain_email": "john@example.com"
}
```

---

### 3.4 Response on Church Limit Exceeded (400 Bad Request)

**NEW BEHAVIOR - This is what you need to handle:**

```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Maximum 2 teams already registered for this church",
  "details": {
    "field": null
  }
}
```

**Frontend Action Required:**
```javascript
if (response.status === 400) {
  const error = await response.json();
  
  if (error.message.includes('Maximum 2 teams')) {
    // Show church capacity error
    showErrorModal(
      'Church at Capacity',
      `${churchName} has reached its team limit of 2. Please select a different church.`
    );
    // Clear previously uploaded files (they are auto-cleaned by backend)
    clearFormData();
  }
}
```

---

### 3.5 Other Error Responses (Unchanged)

```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Pastor letter (file) is required",
  "details": { "field": null }
}
```

```json
{
  "success": false,
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred during registration",
  "details": { "exception_type": "..." }
}
```

---

## 4. VALIDATION RULES - Reference

### Phone Numbers
- Format: 10-digit Indian phone number
- Valid: 9876543210
- Invalid: 987654321, 98765432101, abc1234567

### Email
- Must be valid email format
- Example: john@example.com

### Team Name
- Length: 3-50 characters
- Example: "Alpha Team", "Team Warriors"

### Church Name
- Length: 3-100 characters
- Only alphanumeric, spaces, hyphens
- Example: "Grace Church", "New-Life Assembly"

### Player Role
- Valid values: "Batsman", "Bowler", "All-rounder"
- Case-sensitive

### Files
- **pastor_letter**: PDF only, max 5MB
- **payment_receipt**: PDF only, max 5MB
- **group_photo**: JPG/PNG only, max 10MB
- **player_aadhar_file**: Optional, max 5MB
- **player_subscription_file**: Optional, max 5MB

---

## 5. FRONTEND IMPLEMENTATION CHECKLIST

### Pre-Registration
- [ ] Fetch `/api/churches/availability` on church selection dropdown load
- [ ] Disable/warn when church has `locked: true`
- [ ] Display "2/2 teams" badge for locked churches
- [ ] Real-time update of church capacity (optional, can refresh on demand)

### During Registration
- [ ] Keep current form validation intact
- [ ] Validate phone numbers before submission
- [ ] Validate email format before submission
- [ ] Ensure all 11 players have name and role
- [ ] Check all 3 files are uploaded

### After Registration
- [ ] Handle 400 error for "Maximum 2 teams" message
- [ ] Show user-friendly error: "This church has reached its team limit"
- [ ] Clear form on error (backend auto-cleans uploaded files)
- [ ] Refresh church availability list after successful registration

### Error Handling
- [ ] Display specific error messages from backend
- [ ] Retry logic for network errors
- [ ] Idempotency-Key header for safety (recommended)

---

## 6. INTEGRATION SUMMARY

### What the Frontend Needs to Do

1. **Add Church Availability Check**
   - Call `GET /api/churches/availability` on page load or church dropdown open
   - Display locked status visually (badge, icon, or grayed out)

2. **Update Error Handling**
   - Catch 400 errors specifically for church limit
   - Show user-friendly message about church capacity
   - Don't re-submit if church is at capacity

3. **User Experience**
   - Let users select different church if first choice is locked
   - Show capacity (1/2, 2/2) on church selection
   - Provide clear feedback when limit is hit

### What the Frontend Does NOT Need to Change

- ✅ Form fields (no new fields, no removed fields)
- ✅ File upload requirements
- ✅ Player information structure
- ✅ API endpoint path
- ✅ HTTP method
- ✅ Idempotency mechanism (optional but still works)

---

## 7. TESTING CHECKLIST

### Manual Testing
- [ ] Can register 2 teams for a church successfully
- [ ] 3rd team registration shows "Maximum 2 teams" error
- [ ] Different churches can each have 2 teams
- [ ] Church availability endpoint shows correct counts
- [ ] Locked churches display correctly in UI

### Browser Console
```javascript
// Test church availability endpoint
fetch('/api/churches/availability')
  .then(r => r.json())
  .then(data => console.log(data))

// Expected output
{
  churches: [{church_name, team_count, locked}, ...],
  summary: {total_churches, locked_churches, available_churches}
}
```

### Edge Cases
- [ ] What if all churches are locked? (Show message)
- [ ] What if user goes back and tries to register same church again? (Show error)
- [ ] What if user refreshes after registration started? (Idempotency key helps)

---

## 8. API ENDPOINTS REFERENCE

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/health` | GET | Server health check | ✅ Unchanged |
| `/api/register/team` | POST | Register new team | ✅ Updated (church limit added) |
| `/api/churches/availability` | GET | Church capacity status | ✅ NEW |
| `/api/admin/*` | * | Admin endpoints | ✅ Unchanged |
| `/api/schedule/*` | * | Match scheduling | ✅ Fixed (UUID issue resolved) |

---

## 9. BACKEND SYSTEM DETAILS (For Reference)

### Church Limit Enforcement
- **Database Level:** Row-level locking with `SELECT FOR UPDATE`
- **Transaction:** Atomic validation within registration transaction
- **Concurrency:** Safe for simultaneous requests
- **Cleanup:** Failed registrations auto-delete uploaded files

### Files Uploaded
- Uploaded to Cloudinary
- Auto-deleted on validation failure
- Retrieved via URLs in response

---

## 10. SUPPORT & DEBUGGING

### Common Issues & Solutions

**Issue:** "Maximum 2 teams" error even for first team
- **Cause:** Duplicate church name from previous registrations
- **Solution:** Check church availability endpoint for exact church name used

**Issue:** Church availability shows wrong counts
- **Cause:** Page cache or stale data
- **Solution:** Hard refresh or clear browser cache

**Issue:** Files seem uploaded but registration fails
- **Cause:** Validation error in player info
- **Solution:** Check all 11 players have name and role

### Debug Endpoints

```javascript
// Check church availability
fetch('/api/churches/availability').then(r => r.json())

// Check server health
fetch('/health').then(r => r.json())

// Check API response before submitting
// Enable network tab in DevTools to see full request/response
```

---

## 11. DEPLOYMENT NOTES

- Backend is **production-ready** on localhost:8000
- All 57 tests passing
- No database migrations needed
- Backward compatible with existing registrations
- Can be deployed without frontend changes (graceful degradation)

---

## 12. NEXT STEPS

1. ✅ **Backend:** Implementation complete
2. 📋 **Frontend:** Update church selection with availability check
3. 📋 **Frontend:** Add church limit error handling (400 error case)
4. 📋 **Frontend:** Display locked/available status
5. 🧪 **Testing:** Test full registration flow with church limit
6. 🚀 **Deployment:** Deploy together with confidence

---

## Questions?

Refer to this prompt file for all integration details. The backend is ready and waiting for frontend integration.

**Current Backend Status:** ✅ Ready for frontend integration
