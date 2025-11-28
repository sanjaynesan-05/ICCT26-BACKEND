# 🎯 FRONTEND INTEGRATION GUIDE - UPDATED BACKEND

**Date:** November 29, 2025  
**Backend Version:** 1.0.1 with Cricket Match Schedule Management  
**Status:** Production Ready

---

## 📌 EXECUTIVE SUMMARY

The backend has been fully updated with:
- ✅ **Cricket Match Management** - Complete 4-stage workflow
- ✅ **Separate Runs & Wickets Tracking** - No longer combined values
- ✅ **Enhanced Data Schema** - Better match result handling
- ✅ **Consistent API Response Format** - CamelCase field names

**No Breaking Changes** - Backward compatible where possible

---

## 🔄 4-STAGE MATCH WORKFLOW

The match management follows a strict 4-stage workflow:

```
Stage 1: CREATE         → Match scheduled
   ↓
Stage 2: START          → Toss decided, scorecard URL set
   ↓
Stage 3A: FIRST INNINGS → Team 1 scores recorded (runs + wickets)
   ↓
Stage 3B: SECOND INNINGS → Team 2 scores recorded (runs + wickets)
   ↓
Stage 4: FINISH         → Match completed, winner declared
```

---

## 🔑 CRITICAL CHANGES FOR FRONTEND

### 1. ⚠️ RUNS & WICKETS ARE NOW SEPARATE

**BEFORE (Old API):**
```json
{
  "team1_first_innings_score": 100,  // Just runs
  "team2_first_innings_score": 90    // Just runs
}
```

**AFTER (New API):**
```json
{
  "team1_first_innings_runs": 100,
  "team1_first_innings_wickets": 8,
  "team2_first_innings_runs": 90,
  "team2_first_innings_wickets": 8
}
```

**ACTION REQUIRED:**
- Update UI to display runs and wickets separately
- Use new field names in all API calls
- Update scorecard display to show: `100/8` instead of just `100`

---

### 2. ✅ RESPONSE FORMAT - ALL ENDPOINTS

All API responses follow this structure:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Match object or array of matches
  }
}
```

**KEY FIELDS IN MATCH OBJECT:**
```javascript
{
  // Match identification
  "id": 45,
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  
  // Teams
  "team1": "Team A Name",
  "team2": "Team B Name",
  
  // Status
  "status": "done",  // scheduled, live, done
  
  // Toss information
  "toss_winner": "Team A Name",
  "toss_choice": "bat",  // or "bowl"
  
  // Match timing
  "scheduled_start_time": "2025-11-28T10:00:00",
  "actual_start_time": "2025-11-28T10:15:00",
  "match_end_time": "2025-11-28T13:45:00",
  
  // **NEW: Separate runs and wickets**
  "team1_first_innings_runs": 165,
  "team1_first_innings_wickets": 8,
  "team2_first_innings_runs": 152,
  "team2_first_innings_wickets": 5,
  
  // External scorecard
  "match_score_url": "https://example.com/scorecard",
  
  // Match result (only when status = "done")
  "result": {
    "winner": "Team A Name",
    "margin": 13,
    "marginType": "runs",        // or "wickets"
    "wonByBattingFirst": true
  },
  
  // Timestamps
  "created_at": "2025-11-28T10:00:00",
  "updated_at": "2025-11-28T13:45:00"
}
```

---

## 📡 API ENDPOINTS - COMPLETE LIST

### 1. GET ALL MATCHES
```
GET /api/schedule/matches
Response: { success: true, data: [Match, ...] }
```

### 2. GET SINGLE MATCH
```
GET /api/schedule/matches/{match_id}
Response: { success: true, message: "...", data: Match }
```

### 3. CREATE MATCH (Stage 1)
```
POST /api/schedule/matches
Body: {
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "Team A",
  "team2": "Team B",
  "scheduled_start_time": "2025-11-28T10:00:00"  // Optional
}
Response: { success: true, message: "...", data: Match }
```

### 4. START MATCH (Stage 2) ⭐ IMPORTANT
```
PUT /api/schedule/matches/{match_id}/start
Body: {
  "toss_winner": "Team A",
  "toss_choice": "bat",                      // "bat" or "bowl"
  "match_score_url": "https://scorecard.com",
  "actual_start_time": "2025-11-28T10:15:00"
}
Response: { success: true, message: "...", data: Match }
```

### 5. UPDATE FIRST INNINGS SCORE (Stage 3A) ⭐ CRITICAL
```
PUT /api/schedule/matches/{match_id}/first-innings-score
Body: {
  "batting_team": "Team A",     // Must match team1 or team2
  "runs": 165,                   // 0-999
  "wickets": 8                   // 0-10 (NEW: separate field!)
}
Response: { success: true, message: "...", data: Match }
```

### 6. UPDATE SECOND INNINGS SCORE (Stage 3B) ⭐ CRITICAL
```
PUT /api/schedule/matches/{match_id}/second-innings-score
Body: {
  "batting_team": "Team B",     // Must match team1 or team2
  "runs": 152,                   // 0-999
  "wickets": 5                   // 0-10 (NEW: separate field!)
}
Response: { success: true, message: "...", data: Match }
```

### 7. FINISH MATCH (Stage 4) ⭐ CRITICAL
```
PUT /api/schedule/matches/{match_id}/finish
Body: {
  "winner": "Team A",
  "margin": 13,
  "margin_type": "runs",                    // or "wickets"
  "match_end_time": "2025-11-28T13:45:00"
}
Response: { success: true, message: "...", data: Match }

Notes:
- Status transitions from "live" to "done"
- Both teams' runs and wickets must be recorded first
- winner must match team1 or team2
- margin_type must be "runs" or "wickets"
```

### 8. UPDATE MATCH DETAILS
```
PUT /api/schedule/matches/{match_id}
Body: {
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "Team A",
  "team2": "Team B"
}
Response: { success: true, message: "...", data: Match }
Note: Cannot update if match is already "done"
```

### 9. DELETE MATCH
```
DELETE /api/schedule/matches/{match_id}
Response: { success: true, message: "Match deleted successfully" }
Note: Cannot delete if status is "live" or "done"
```

### 10. EXPORT SCHEDULE
```
POST /api/schedule/export
Response: { success: true, data: [Match, ...] }
```

---

## 🎨 FRONTEND UI REQUIREMENTS

### Match Display Card
Show these fields:
```
┌─────────────────────────────────────┐
│ Round 1 - Match 1                   │
├─────────────────────────────────────┤
│ Team A (100/8) vs Team B (90/8)     │
│ Status: Done                        │
│ Toss: Team A won, chose to bat      │
│ Result: Team A won by 10 runs       │
├─────────────────────────────────────┤
│ Start: 10:15 AM | End: 1:45 PM     │
│ Scorecard: [Link]                   │
└─────────────────────────────────────┘
```

### Score Input Forms
**First Innings Input:**
```
Batting Team: [Dropdown] 
Runs: [0-999]
Wickets: [0-10]  ← NEW FIELD
[Submit] [Cancel]
```

**Second Innings Input:**
```
Batting Team: [Dropdown]
Runs: [0-999]
Wickets: [0-10]  ← NEW FIELD
[Submit] [Cancel]
```

**Match Result Input:**
```
Winner: [Dropdown]
Margin: [1-999]
Margin Type: [runs / wickets]
Match End Time: [DateTime Picker]
[Submit] [Cancel]
```

---

## 💡 IMPLEMENTATION TIPS

### 1. Display Scores
```javascript
// OLD WAY (Don't use)
`Score: ${match.team1_first_innings_score}`

// NEW WAY (Use this)
`Score: ${match.team1_first_innings_runs}/${match.team1_first_innings_wickets}`
```

### 2. Form Validation
```javascript
// Validate wickets are 0-10
if (wickets < 0 || wickets > 10) {
  showError("Wickets must be between 0 and 10");
}

// Validate runs are 0-999
if (runs < 0 || runs > 999) {
  showError("Runs must be between 0 and 999");
}

// Validate both innings are recorded before finishing
if (!match.team1_first_innings_runs || !match.team1_first_innings_wickets ||
    !match.team2_first_innings_runs || !match.team2_first_innings_wickets) {
  showError("Both teams' runs and wickets must be recorded first");
}
```

### 3. Workflow Navigation
```javascript
// Stage 1: Show "Create Match" button
if (matchList.length === 0) {
  showButton("Create Match", () => showCreateDialog());
}

// Stage 2: Show "Start Match" button
if (match.status === "scheduled") {
  showButton("Start Match", () => showTossDialog());
}

// Stage 3A: Show "Record First Innings" button
if (match.status === "live" && !match.team1_first_innings_runs) {
  showButton("Record First Innings", () => showFirstInningsDialog());
}

// Stage 3B: Show "Record Second Innings" button
if (match.status === "live" && match.team1_first_innings_runs && 
    !match.team2_first_innings_runs) {
  showButton("Record Second Innings", () => showSecondInningsDialog());
}

// Stage 4: Show "Finish Match" button
if (match.status === "live" && match.team1_first_innings_runs && 
    match.team2_first_innings_runs) {
  showButton("Finish Match", () => showFinishDialog());
}
```

### 4. Error Handling
```javascript
// Consistent error response format
if (!response.ok) {
  const error = await response.json();
  showError(error.detail || error.message || "An error occurred");
}

// Always check match status before operations
if (match.status === "done") {
  showError("Cannot modify a completed match");
  return;
}
```

---

## 🔍 TESTING CHECKLIST FOR FRONTEND

- [ ] Display runs and wickets separately in scorecard
- [ ] First innings form has separate "runs" and "wickets" inputs
- [ ] Second innings form has separate "runs" and "wickets" inputs
- [ ] Match result displays marginType as "runs" or "wickets"
- [ ] Match result displays wonByBattingFirst boolean
- [ ] Error messages show correctly for invalid inputs
- [ ] 4-stage workflow buttons show/hide correctly
- [ ] Can complete full match workflow (create → start → score → finish)
- [ ] Display format shows scores as "100/8" not just "100"
- [ ] API responses parse correctly with new field names

---

## 📊 EXAMPLE DATA

### Complete Match Workflow

**1. After Create:**
```json
{
  "id": 45,
  "round": "Round 1",
  "match_number": 1,
  "team1": "Mumbai Kings",
  "team2": "Delhi Warriors",
  "status": "scheduled"
}
```

**2. After Start:**
```json
{
  ...previous data...,
  "status": "live",
  "toss_winner": "Mumbai Kings",
  "toss_choice": "bat",
  "actual_start_time": "2025-11-28T10:15:00",
  "match_score_url": "https://..."
}
```

**3. After First Innings:**
```json
{
  ...previous data...,
  "team1_first_innings_runs": 165,
  "team1_first_innings_wickets": 8
}
```

**4. After Second Innings:**
```json
{
  ...previous data...,
  "team2_first_innings_runs": 152,
  "team2_first_innings_wickets": 5
}
```

**5. After Finish:**
```json
{
  ...previous data...,
  "status": "done",
  "match_end_time": "2025-11-28T13:45:00",
  "result": {
    "winner": "Mumbai Kings",
    "margin": 13,
    "marginType": "runs",
    "wonByBattingFirst": true
  }
}
```

---

## ⚠️ IMPORTANT NOTES

### Breaking Changes
1. **Score fields renamed** - Use new field names
2. **Wickets now required** - Must be submitted with runs
3. **Field names in camelCase** - marginType, wonByBattingFirst (not snake_case)

### Backward Compatibility
- Old score fields still exist in database for legacy data
- New code uses new fields
- Both can coexist temporarily

### Validation Rules
- **Runs:** 0-999
- **Wickets:** 0-10
- **Margin:** 1-999
- **Margin Type:** "runs" or "wickets"
- **Toss Choice:** "bat" or "bowl"

---

## 📞 SUPPORT & DEBUGGING

### Common Errors

**"Cannot update first innings: Match status must be 'live'"**
- Solution: Call `/start` endpoint first (Stage 2)

**"Cannot finish match: Both innings scores must be recorded first"**
- Solution: Record both teams' runs AND wickets before finishing

**"Wickets must be between 0 and 10"**
- Solution: Ensure wickets input is 0-10

**"Team 'X' is not part of this match"**
- Solution: Use team names exactly as they appear in the match

---

## 🚀 DEPLOYMENT TIMELINE

- **Backend:** Production Ready NOW
- **Frontend:** Update and test (2-3 days)
- **Combined Testing:** 1 day
- **Go Live:** Ready after frontend updates

---

## 📝 QUICK REFERENCE

**Base URL:** `http://localhost:8000/api/schedule` (or production URL)

**Key Endpoints:**
- `GET /matches` - List matches
- `POST /matches` - Create match
- `PUT /matches/{id}/start` - Start (Stage 2)
- `PUT /matches/{id}/first-innings-score` - First innings (Stage 3A)
- `PUT /matches/{id}/second-innings-score` - Second innings (Stage 3B)
- `PUT /matches/{id}/finish` - Finish (Stage 4)

**Field Names to Update:**
- `team1_first_innings_runs` ✅ NEW
- `team1_first_innings_wickets` ✅ NEW
- `team2_first_innings_runs` ✅ NEW
- `team2_first_innings_wickets` ✅ NEW
- `marginType` (camelCase)
- `wonByBattingFirst` (camelCase)

---

**Status:** ✅ READY FOR FRONTEND INTEGRATION  
**Version:** 1.0.1  
**Last Updated:** November 29, 2025
