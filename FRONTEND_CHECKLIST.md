# ✅ Frontend Checklist - Registration Changes

## 📋 Overview

The backend now supports **dynamic player field extraction** and **player file uploads**. Your frontend needs to ensure it sends the correct field names and files in the FormData.

---

## 🎯 What to Check in Frontend

### 1. **Form Field Names** (CRITICAL)

**Check that your FormData includes these exact field names:**

#### Team Fields:
```javascript
formData.append("team_name", teamName)
formData.append("church_name", churchName)
```

#### Captain Fields:
```javascript
formData.append("captain_name", captainName)
formData.append("captain_phone", captainPhone)
formData.append("captain_email", captainEmail)
formData.append("captain_whatsapp", captainWhatsapp)
```

#### Vice-Captain Fields:
```javascript
formData.append("vice_name", viceName)
formData.append("vice_phone", vicePhone)
formData.append("vice_email", viceEmail)
formData.append("vice_whatsapp", viceWhatsapp)
```

#### Team Files:
```javascript
formData.append("pastor_letter", pastorLetterFile)
formData.append("payment_receipt", paymentReceiptFile)  // Optional
formData.append("group_photo", groupPhotoFile)  // Optional
```

✅ **Verify:** Field names match exactly (case-sensitive, underscores not hyphens)

---

### 2. **Player Dynamic Fields** (MOST IMPORTANT)

**Your frontend must send players as INDIVIDUAL FORM FIELDS, not JSON:**

#### ❌ WRONG (Old way - JSON):
```javascript
// DON'T do this anymore
formData.append("players_json", JSON.stringify([
  { name: "Robin", role: "Batsman" },
  { name: "Anand", role: "Bowler" }
]))
```

#### ✅ RIGHT (New way - Dynamic fields):
```javascript
// For each player, append individual fields with index:
for (let i = 0; i < players.length; i++) {
  const player = players[i]
  
  // Player name and role
  formData.append(`player_${i}_name`, player.name)
  formData.append(`player_${i}_role`, player.role)
  
  // Player files (if present)
  if (player.aadharFile) {
    formData.append(`player_${i}_aadhar_file`, player.aadharFile)
  }
  if (player.subscriptionFile) {
    formData.append(`player_${i}_subscription_file`, player.subscriptionFile)
  }
}
```

**Result should look like:**
```
player_0_name: "Robin Kumar"
player_0_role: "Batsman"
player_0_aadhar_file: [File object]
player_0_subscription_file: [File object]

player_1_name: "Anand Raj"
player_1_role: "Bowler"
player_1_aadhar_file: [File object]
player_1_subscription_file: [File object]

player_2_name: "Jerald"
player_2_role: "All-Rounder"
player_2_aadhar_file: [File object]
player_2_subscription_file: [File object]
```

✅ **Verify:** Players sent as `player_0_*`, `player_1_*`, etc. (NOT as JSON)

---

### 3. **Player Files** (CRITICAL)

**Check that player files are being appended:**

#### 🔍 Debug Step 1: Check if files are collected
```typescript
// In your player form component
console.log("Player files state:", {
  player1_aadhar: player1.aadharFile?.name,
  player1_subscription: player1.subscriptionFile?.name,
  player2_aadhar: player2.aadharFile?.name,
  player2_subscription: player2.subscriptionFile?.name
})
```

Expected output:
```
Player files state: {
  player1_aadhar: "robin_aadhar.jpg",
  player1_subscription: "robin_subscription.pdf",
  player2_aadhar: "anand_aadhar.jpg",
  player2_subscription: "anand_subscription.pdf"
}
```

#### 🔍 Debug Step 2: Check FormData before sending
```typescript
// Before calling fetch
console.log("FormData contents:")
for (let [key, value] of formData.entries()) {
  if (value instanceof File) {
    console.log(`✅ ${key}: File(name: ${value.name}, size: ${value.size} bytes)`)
  } else {
    console.log(`📝 ${key}: ${value}`)
  }
}
```

Expected output includes:
```
✅ player_0_aadhar_file: File(name: robin_aadhar.jpg, size: 245678 bytes)
✅ player_0_subscription_file: File(name: robin_sub.pdf, size: 123456 bytes)
✅ player_1_aadhar_file: File(name: anand_aadhar.jpg, size: 234567 bytes)
✅ player_1_subscription_file: File(name: anand_sub.pdf, size: 145678 bytes)
```

If you see **MISSING**, that's the problem! ❌

✅ **Verify:** All player files appear in FormData console logs

---

### 4. **File Type & Size Validation**

**Check that files meet requirements:**

#### File Type Validation:
```typescript
const validAadharTypes = ['image/jpeg', 'image/png']
const validSubscriptionTypes = ['image/jpeg', 'image/png', 'application/pdf']

// Check aadhar file type
if (!validAadharTypes.includes(aadharFile.type)) {
  console.error("❌ Aadhar must be JPG or PNG")
  return
}

// Check subscription file type
if (!validSubscriptionTypes.includes(subscriptionFile.type)) {
  console.error("❌ Subscription must be JPG, PNG, or PDF")
  return
}
```

#### File Size Validation:
```typescript
const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB

if (aadharFile.size > MAX_FILE_SIZE) {
  console.error("❌ Aadhar file too large (max 5MB)")
  return
}

if (subscriptionFile.size > MAX_FILE_SIZE) {
  console.error("❌ Subscription file too large (max 5MB)")
  return
}
```

✅ **Verify:** Files are valid type and within size limits

---

### 5. **API Endpoint Check**

**Verify the endpoint URL:**

```typescript
// ✅ CORRECT
const response = await fetch("https://icct26-backend.onrender.com/api/register/team", {
  method: "POST",
  body: formData
})

// ❌ WRONG (missing /api prefix)
const response = await fetch("https://icct26-backend.onrender.com/register/team", {
  method: "POST",
  body: formData
})
```

✅ **Verify:** URL is `/api/register/team` (has `/api` prefix)

---

### 6. **Idempotency Header**

**Check that Idempotency-Key header is sent:**

```typescript
const response = await fetch("https://icct26-backend.onrender.com/api/register/team", {
  method: "POST",
  headers: {
    "Idempotency-Key": `registration-${Date.now()}-${Math.random()}`
  },
  body: formData
})
```

✅ **Verify:** Idempotency-Key header is unique per request

---

### 7. **Response Handling**

**Check that you're reading the new response format:**

```typescript
const response = await fetch(...)
const data = await response.json()

// ✅ NEW FORMAT (after backend fix)
if (response.ok) {
  const teamId = data.team_id  // ✅ Has team_id
  const playerCount = data.player_count  // ✅ Has player_count (NEW)
  // Note: NO email_sent field anymore
  
  console.log(`✅ Team registered: ${teamId} with ${playerCount} players`)
}

// ❌ OLD FORMAT (should not expect this anymore)
// const emailSent = data.email_sent  // ← No longer present
```

✅ **Verify:** Response handling updated for new format

---

### 8. **Error Handling**

**Check error responses are handled:**

```typescript
if (!response.ok) {
  const error = await response.json()
  
  // Validation error
  if (response.status === 400) {
    console.error(`Validation Error: ${error.details?.field}`)
    console.error(`Message: ${error.message}`)
  }
  
  // Duplicate submission
  if (response.status === 409) {
    console.error(`Duplicate submission (idempotency)`)
    console.error(`Team ID: ${error.team_id}`)
  }
  
  // Server error
  if (response.status === 500) {
    console.error(`Server error: ${error.message}`)
  }
}
```

✅ **Verify:** Error responses are properly handled

---

### 9. **Success Response Handling**

**Check success flow:**

```typescript
if (response.status === 201) {
  const data = await response.json()
  
  // Show success modal
  showSuccessModal({
    teamId: data.team_id,
    teamName: data.team_name,
    playerCount: data.player_count,  // ← Use this
    message: data.message
  })
  
  // Redirect to admin dashboard
  navigate(`/admin/teams/${data.team_id}`)
}

// Duplicate submission should also show success (409)
if (response.status === 409) {
  showSuccessModal({
    teamId: data.team_id,
    message: "Team already registered"
  })
}
```

✅ **Verify:** Both HTTP 201 and 409 show success

---

## 🧪 Testing Checklist

### Local Testing

- [ ] Open browser DevTools (F12)
- [ ] Go to Network tab
- [ ] Fill in team details
- [ ] Add 2-3 players with files
- [ ] Submit form
- [ ] **Check Network tab:**
  - [ ] Request URL is `/api/register/team`
  - [ ] Request method is `POST`
  - [ ] Content-Type is `multipart/form-data` (no explicit header needed)
  - [ ] Form data includes `player_0_name`, `player_0_aadhar_file`, etc.
  - [ ] All player files are present
  
- [ ] **Check Console tab:**
  - [ ] No JavaScript errors
  - [ ] FormData debug logs show all files
  - [ ] Player file keys printed correctly

- [ ] **Check Response:**
  - [ ] Status code is 201
  - [ ] Response includes `team_id`
  - [ ] Response includes `player_count`
  - [ ] No `email_sent` field

### Production Testing

- [ ] Submit registration on production
- [ ] Check response (HTTP 201)
- [ ] Verify success modal shows correct info
- [ ] **Database verification:**
  ```sql
  SELECT player_id, name, aadhar_file, subscription_file
  FROM players
  WHERE team_id = 'ICCT-XXX'
  ```
  Should show Cloudinary URLs, not NULL
  
- [ ] **Cloudinary verification:**
  - [ ] Login to Cloudinary console
  - [ ] Check folder structure:
    ```
    ICCT26/players/ICCT-XXX/player_0/aadhar/
    ICCT26/players/ICCT-XXX/player_0/subscription/
    ```
  - [ ] Files are present and accessible

---

## 📝 Common Issues & Fixes

### Issue #1: Files showing as NULL in database

**Symptom:**
```sql
SELECT aadhar_file FROM players;
-- Result: NULL NULL NULL
```

**Cause:** Frontend not sending files in FormData

**Fix:** 
```typescript
// ✅ Add this to your player loop
if (player.aadharFile) {
  formData.append(`player_${i}_aadhar_file`, player.aadharFile)
}
if (player.subscriptionFile) {
  formData.append(`player_${i}_subscription_file`, player.subscriptionFile)
}
```

**Verify:**
```typescript
console.log("FormData entries:")
for (let [key, value] of formData.entries()) {
  console.log(`${key}: ${value instanceof File ? `File(${value.name})` : value}`)
}
```

---

### Issue #2: "Player field is required" error

**Error Response:**
```json
{
  "error_code": "VALIDATION_FAILED",
  "message": "Player 1 name is required (min 2 characters)",
  "details": { "field": "player_0_name" }
}
```

**Cause:** Form fields not named correctly (`player_0_name` vs `players[0].name`)

**Fix:**
```typescript
// ❌ WRONG
formData.append("players[0].name", player.name)

// ✅ CORRECT
formData.append("player_0_name", player.name)
```

---

### Issue #3: "player_0_aadhar_file" showing as MISSING in logs

**Backend Log:**
```
Player 0: name=Robin, role=Batsman, aadhar=MISSING, subscription=MISSING
```

**Cause:** Files not appended to FormData

**Fix:**
```typescript
// Ensure files are appended BEFORE sending
for (let i = 0; i < players.length; i++) {
  formData.append(`player_${i}_aadhar_file`, players[i].aadharFile)
  formData.append(`player_${i}_subscription_file`, players[i].subscriptionFile)
}

// Log to verify
console.log("Files appended to FormData")
for (let [key, value] of formData.entries()) {
  if (key.includes("aadhar") || key.includes("subscription")) {
    console.log(`${key}: ${value.name}`)
  }
}
```

---

### Issue #4: HTTP 409 (Duplicate) on first submission

**Response:**
```json
{
  "success": true,
  "team_id": "ICCT-001",
  "message": "Team registered successfully"
}
```

**Cause:** Same Idempotency-Key being sent multiple times

**Fix:**
```typescript
// ✅ Generate NEW unique key for each submission
const idempotencyKey = `registration-${Date.now()}-${Math.random()}`

fetch(..., {
  headers: {
    "Idempotency-Key": idempotencyKey
  }
})
```

---

### Issue #5: Network shows files but still NULL in database

**Network tab:** Shows all files present ✅  
**Database:** Still NULL ❌

**Cause:** Old code still trying to save to database without URLs

**Verify Backend:** Backend was updated to save URLs. If still NULL:
```sql
-- Check backend logs for upload errors
-- Look for: "❌ Player X aadhar upload failed"
```

---

## 🔍 Quick Verification Script

Run this in browser console to verify FormData:

```javascript
// Copy your form submission code and run this before fetch:

const formData = new FormData()

// Add all fields (team, captain, players)
// ... your form append logic ...

// Then verify:
console.group("🔍 FormData Verification")

const fieldCount = {}
for (let [key, value] of formData.entries()) {
  const category = key.split('_')[0]
  fieldCount[category] = (fieldCount[category] || 0) + 1
  
  if (value instanceof File) {
    console.log(`✅ ${key}: File(${value.name}, ${value.size} bytes)`)
  } else {
    console.log(`📝 ${key}: ${value}`)
  }
}

console.group("📊 Summary")
console.log("Field counts:", fieldCount)
console.log("Total entries:", Array.from(formData.entries()).length)

// Check for files
const playerFiles = Array.from(formData.entries())
  .filter(([k]) => k.includes('player_') && (k.includes('aadhar') || k.includes('subscription')))
  .map(([k, v]) => `${k}: ${v.name}`)

console.log("Player files found:", playerFiles.length > 0 ? playerFiles : "❌ NONE FOUND")
console.groupEnd()
```

---

## ✅ Final Checklist

Before submitting:

- [ ] Field names are correct (underscores, not hyphens)
- [ ] Players sent as `player_0_*`, `player_1_*` (not JSON)
- [ ] Player files appended to FormData
- [ ] Idempotency-Key is unique
- [ ] FormData console logs show all files
- [ ] Endpoint URL has `/api/register/team`
- [ ] Response handling updated (no `email_sent`)
- [ ] Error handling for all response codes (201, 400, 409, 500)
- [ ] Files are valid type and size
- [ ] No console errors

---

**Status:** ✅ Ready to test with backend  
**Next:** Run test submission and verify database + Cloudinary
