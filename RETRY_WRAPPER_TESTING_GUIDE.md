# 🧪 Retry Wrapper Testing Guide

**Date:** November 12, 2025  
**Status:** ✅ Deployed (Commit c1e86ad)

## Overview

This guide helps you test the retry wrapper to ensure transient connection failures are handled gracefully.

## Prerequisites

- ✅ Code deployed to Render (auto-deploy in progress)
- ✅ Neon database accessible
- ✅ Frontend ready to send registration requests
- ✅ `curl` or API testing tool (Postman, Insomnia, etc.)

## Test Scenarios

### Test 1: Normal Registration (No Failures)

**Objective:** Verify retry wrapper doesn't interfere with normal operations

**Steps:**

1. Prepare payload:

```json
{
  "churchName": "Test Church",
  "teamName": "Test Team",
  "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "captain": {
    "name": "Captain One",
    "phone": "+919876543210",
    "whatsapp": "919876543210",
    "email": "captain@example.com"
  },
  "viceCaptain": {
    "name": "Vice Captain One",
    "phone": "+919876543211",
    "whatsapp": "919876543211",
    "email": "vicecaptain@example.com"
  },
  "paymentReceipt": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "players": [
    {
      "name": "Player 1",
      "age": 25,
      "phone": "+919876543220",
      "role": "batsman"
    },
    ... (11-15 players total)
  ]
}
```

2. Send request:

```bash
curl -X POST https://icct26-backend.onrender.com/api/register/team \
  -H "Content-Type: application/json" \
  -d @payload.json
```

3. Expected response:

```json
{
  "success": true,
  "message": "Team and players registered successfully",
  "team_id": "ICCT26-20251112120000",
  "player_count": 11
}
```

4. Check logs (Render dashboard):

```
INFO - 🔄 Executing register_team (attempt 1/3)
INFO - ✅ register_team succeeded after 0 retries
```

**Pass Criteria:**
- ✅ Status 201 Created
- ✅ Response includes team_id and player_count
- ✅ Logs show "after 0 retries" (first attempt succeeded)

---

### Test 2: Simulate Network Failure (Manual)

**Objective:** Verify retry decorator triggers on connection errors

**Prerequisites:**
- Access to Render deployment logs
- Ability to view database operations

**Steps:**

1. Send normal registration request (same as Test 1)

2. While request is processing, simulate connection loss:
   - Restart Neon database (if you have admin access)
   - Or trigger a connection pool issue

3. Observe behavior:

**Expected Logs (Scenario: Connection lost on first attempt):**

```
INFO - 🔄 Executing register_team (attempt 1/3)
WARNING - ⚠️ register_team failed with OperationalError (attempt 1/3): connection closed
INFO - ⏳ Retrying register_team in 2s... (1/3)
INFO - 🔄 Executing register_team (attempt 2/3)
INFO - ✅ register_team succeeded after 1 retries
```

**Expected Response:**
- ✅ Status 201 Created (after ~2s delay)
- ✅ Team and players successfully registered
- ✅ Only delayed slightly (by 2s retry wait)

**Pass Criteria:**
- ✅ Request succeeds despite connection failure
- ✅ Logs show retry attempt
- ✅ Data is persisted correctly

---

### Test 3: Multiple Connection Failures

**Objective:** Verify multiple retries work correctly

**Scenario:** Connection fails twice, succeeds on third attempt

**Expected Logs:**

```
INFO - 🔄 Executing register_team (attempt 1/3)
WARNING - ⚠️ register_team failed with OperationalError (attempt 1/3): connection closed
INFO - ⏳ Retrying register_team in 2s... (1/3)
INFO - 🔄 Executing register_team (attempt 2/3)
WARNING - ⚠️ register_team failed with TimeoutError (attempt 2/3): query timeout
INFO - ⏳ Retrying register_team in 4s... (2/3)
INFO - 🔄 Executing register_team (attempt 3/3)
INFO - ✅ register_team succeeded after 2 retries
```

**Expected Response:**
- ✅ Status 201 Created (after ~6s delay: 2s + 4s)
- ✅ Data persisted on third attempt

**Pass Criteria:**
- ✅ All three attempts shown in logs
- ✅ Exponential backoff visible (2s, then 4s)
- ✅ Success after retries

---

### Test 4: Permanent Failure (Max Retries Exceeded)

**Objective:** Verify graceful failure when retries exhausted

**Scenario:** Connection continuously fails (simulate Neon downtime)

**Expected Logs:**

```
INFO - 🔄 Executing register_team (attempt 1/3)
WARNING - ⚠️ register_team failed with OperationalError (attempt 1/3): connection closed
INFO - ⏳ Retrying register_team in 2s... (1/3)
INFO - 🔄 Executing register_team (attempt 2/3)
WARNING - ⚠️ register_team failed with OperationalError (attempt 2/3): connection closed
INFO - ⏳ Retrying register_team in 4s... (2/3)
INFO - 🔄 Executing register_team (attempt 3/3)
WARNING - ⚠️ register_team failed with OperationalError (attempt 3/3): connection closed
ERROR - ❌ register_team failed after 3 attempts. Last error: OperationalError: connection closed
```

**Expected Response:**
- ✅ Status 500 Internal Server Error
- ✅ Error message indicating database connection failed
- ✅ After ~14 seconds (2s + 4s + 8s delays attempted, but no long delay on final failure)

**Pass Criteria:**
- ✅ All 3 attempts shown
- ✅ Returns 500 error gracefully
- ✅ Doesn't hang indefinitely
- ✅ Error logged clearly

---

### Test 5: Validation Error (Non-Retryable)

**Objective:** Verify validation errors fail fast (not retried)

**Scenario:** Send invalid player count (only 10 players)

**Payload:**

```json
{
  "churchName": "Test Church",
  "teamName": "Test Team",
  ...
  "players": [
    { "name": "Player 1", ... },
    ... (only 10 players - INVALID)
  ]
}
```

**Expected Logs:**

```
INFO - 🔄 Executing register_team (attempt 1/3)
ERROR - ❌ register_team failed with non-retryable error HTTPException: Invalid player count
```

**Expected Response:**
- ✅ Status 422 Unprocessable Entity
- ✅ Message: "Invalid player count. Expected 11-15 players, got 10"
- ✅ Immediate failure (0 retries)

**Pass Criteria:**
- ✅ Only 1 attempt (no retries for validation)
- ✅ Fast failure
- ✅ Clear error message

---

## Performance Verification

### Response Times

**Scenario 1: No failure**
- Expected: < 500ms (normal processing)
- Actual: ?

```bash
time curl -X POST https://icct26-backend.onrender.com/api/register/team \
  -H "Content-Type: application/json" \
  -d @payload.json
```

**Scenario 2: 1 retry (failure → success)**
- Expected: 2-3 seconds (2s wait + 100-200ms processing)
- Actual: ?

**Scenario 3: 2 retries (2 failures → success)**
- Expected: 6-7 seconds (2s + 4s wait + processing)
- Actual: ?

**Scenario 4: 3 retries exhausted**
- Expected: 14-15 seconds max
- Actual: ?

---

## Log Monitoring

### Where to Check Logs

**Option 1: Render Dashboard**
- Go to: https://dashboard.render.com/
- Select: ICCT26-BACKEND service
- Click: Logs tab
- Filter: `register_team` or `retry`

**Option 2: Frontend Console**
- Open browser DevTools (F12)
- Check Network tab for API response times
- Check Console for CORS or JavaScript errors

**Option 3: Database Logs**
- Go to Neon console: https://console.neon.tech/
- Check query performance and connection issues

### What to Look For

✅ Success indicators:
```
INFO - 🔄 Executing register_team
INFO - ✅ register_team succeeded
```

⚠️ Retry indicators:
```
WARNING - ⚠️ register_team failed
INFO - ⏳ Retrying register_team in Xs
```

❌ Failure indicators:
```
ERROR - ❌ register_team failed after 3 attempts
```

---

## Metrics Collection

### Success Rate

```
Total registrations attempted: X
Successful (201): Y
Failed (500): Z

Success rate = Y / X × 100%
Expected: ≥ 99.5%
```

### Retry Frequency

```
Registrations with no retries: A
Registrations with 1 retry: B
Registrations with 2 retries: C
Registrations with 3 retries (failed): D

Total registrations = A + B + C + D
Retry rate = (B + C + D) / Total × 100%
Expected: < 5% (good network) to < 10% (poor network)
```

### Average Response Time

```
No retries average: ~200-500ms
1 retry average: ~2-3s
2 retries average: ~6-7s
3 retries (failed) average: ~14-15s
```

---

## Troubleshooting

### Issue: All requests failing immediately

**Possible causes:**
1. NullPool not configured
2. Neon database down
3. Invalid connection string

**Fix:**
- Check `database.py` has `poolclass=NullPool`
- Verify Neon status page
- Test connection manually

### Issue: No retry logs appearing

**Possible causes:**
1. Logging level too high
2. Decorator not applied
3. Errors being caught elsewhere

**Fix:**
- Check logging configuration
- Verify `@retry_db_operation` is present in route
- Ensure no try/except blocks above decorator

### Issue: Retrying too many times

**Possible causes:**
1. Legitimate timeout (requests genuinely slow)
2. Network issues
3. Database overloaded

**Fix:**
- Check database metrics
- Review Neon query performance
- Consider increasing timeout in `database.py`

---

## Test Checklist

- [ ] **Test 1 Passed:** Normal registration works
- [ ] **Test 2 Passed:** Single connection failure recovered
- [ ] **Test 3 Passed:** Multiple failures recovered
- [ ] **Test 4 Passed:** Max retries gracefully fail
- [ ] **Test 5 Passed:** Validation errors fail fast
- [ ] **Performance 1:** No-failure response < 500ms
- [ ] **Performance 2:** 1-retry response ~2-3s
- [ ] **Performance 3:** 2-retry response ~6-7s
- [ ] **Logs:** Retry messages visible in Render
- [ ] **Database:** Data correctly persisted after retries
- [ ] **CORS:** Frontend can communicate without errors
- [ ] **Error Handling:** 500 errors on permanent failures

---

## Success Criteria

✅ All tests pass  
✅ No data corruption  
✅ Consistent retry behavior  
✅ Proper logging for debugging  
✅ Performance acceptable (<15s max)  

**Overall Status:** 🚀 **Ready for production testing!**
