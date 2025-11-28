# Backend Enhancement for 4-Stage Match Workflow

## Current State Analysis

✅ **Good News:** The backend model already has ALL required fields!

### Existing Match Model Fields:
```
- id (PK)
- round, round_number, match_number
- team1_id, team2_id (Foreign Keys to Team table)
- status (already supports 'scheduled', 'live', 'completed')
- toss_winner_id, toss_choice
- scheduled_start_time, actual_start_time, match_end_time
- team1_first_innings_score, team2_first_innings_score
- team1_second_innings_score, team2_second_innings_score (bonus!)
- winner_id, margin, margin_type, won_by_batting_first
- match_score_url
- created_at, updated_at
```

### Existing Endpoints:
```
✅ POST   /api/schedule/matches                    (Create match)
✅ PUT    /api/schedule/matches/{id}               (Full update)
✅ PUT    /api/schedule/matches/{id}/status        (Update status)
✅ PUT    /api/schedule/matches/{id}/toss          (Update toss)
✅ PUT    /api/schedule/matches/{id}/timing        (Update timing)
✅ PUT    /api/schedule/matches/{id}/scores        (Update scores)
✅ PUT    /api/schedule/matches/{id}/score-url     (Update URL)
✅ POST   /api/schedule/matches/{id}/result        (Set result)
✅ GET    /api/schedule/matches                    (List all)
✅ GET    /api/schedule/matches/{id}               (Get single)
✅ DELETE /api/schedule/matches/{id}               (Delete)
```

## 🎯 What We Need to Change

**Problem:** Current endpoints don't enforce workflow state transitions.
- User can set toss before creating match
- User can finish match without setting scores
- No clear indication of which steps to take next

**Solution:** Create workflow-specific endpoints that:
1. Enforce proper state transitions
2. Call existing logic under the hood
3. Provide clear error messages
4. Guide the user through the workflow

---

## 📋 New Workflow Endpoints

### Endpoint 1: START MATCH (Stage 2)
**Current:** `PUT /api/schedule/matches/{id}/status` + multiple calls  
**New:** `PUT /api/schedule/matches/{id}/start`

**What it does:**
- Validates match is in "upcoming" status
- Sets toss details, scorecard URL, actual start time
- Atomically updates to "live" status
- Single API call instead of multiple

**Request:**
```json
{
  "toss_winner": "Team A Name",
  "toss_choice": "bat",
  "match_score_url": "https://scorecard.com/match/123",
  "actual_start_time": "2025-11-28T10:15:00"
}
```

**Implementation Strategy:**
- Create new schema: `MatchStartRequest`
- Create new endpoint function: `start_match()`
- Reuse existing team lookup and validation
- Single DB commit at end
- Return full match response

---

### Endpoint 2: UPDATE FIRST INNINGS SCORE (Stage 3A)
**Current:** `PUT /api/schedule/matches/{id}/scores` (both teams at once)  
**New:** `PUT /api/schedule/matches/{id}/first-innings-score`

**What it does:**
- Validates match is in "live" or "in-progress" status
- Updates only the team that batted first score
- Validates score format
- Updates status to "in-progress" if still "live"

**Request:**
```json
{
  "batting_team": "Team A Name",
  "score": 165
}
```

**Implementation Strategy:**
- Create new schema: `FirstInningsScoreRequest`
- Create new endpoint function: `update_first_innings_score()`
- Determine which team_id matches batting_team name
- Update correct score field (team1 or team2)
- Auto-transition status from "live" to "in-progress"

---

### Endpoint 3: UPDATE SECOND INNINGS SCORE (Stage 3B)
**Current:** `PUT /api/schedule/matches/{id}/scores` (both teams at once)  
**New:** `PUT /api/schedule/matches/{id}/second-innings-score`

**What it does:**
- Validates match is in "in-progress" status
- Updates only the team that batted second score
- Validates first innings score exists
- Keeps status as "in-progress"

**Request:**
```json
{
  "batting_team": "Team B Name",
  "score": 152
}
```

**Implementation Strategy:**
- Create new schema: `SecondInningsScoreRequest`
- Create new endpoint function: `update_second_innings_score()`
- Determine which team_id matches batting_team name
- Validate first innings score already exists
- Update correct score field (team1 or team2)

---

### Endpoint 4: FINISH MATCH (Stage 4)
**Current:** `POST /api/schedule/matches/{id}/result` (just sets result)  
**New:** `PUT /api/schedule/matches/{id}/finish`

**What it does:**
- Validates match is in "in-progress" status
- Validates both innings scores exist
- Sets winner, margin, margin_type, end time
- Atomically updates status to "completed"
- Single DB commit

**Request:**
```json
{
  "winner": "Team A Name",
  "margin": 13,
  "margin_type": "runs",
  "match_end_time": "2025-11-28T13:45:00"
}
```

**Implementation Strategy:**
- Create new schema: `MatchFinishRequest`
- Create new endpoint function: `finish_match()`
- Validate both scores exist
- Lookup winner team by name
- Set all result fields atomically
- Update status to "completed"

---

## 🔧 Implementation Plan

### Phase 1: Add New Schemas (5 min)
File: `app/schemas_schedule.py`

Add these classes:
1. `MatchStartRequest` - for starting match
2. `FirstInningsScoreRequest` - for first innings
3. `SecondInningsScoreRequest` - for second innings
4. `MatchFinishRequest` - for finishing match

### Phase 2: Add New Endpoints (20 min)
File: `app/routes/schedule.py`

Add these endpoint functions:
1. `start_match()` - PUT /matches/{id}/start
2. `update_first_innings_score()` - PUT /matches/{id}/first-innings-score
3. `update_second_innings_score()` - PUT /matches/{id}/second-innings-score
4. `finish_match()` - PUT /matches/{id}/finish

### Phase 3: Create Comprehensive Tests (15 min)
File: `test_match_workflow.py` (NEW)

Test scenarios:
1. Create match → Verify "upcoming" status
2. Start match → Verify toss, URL, status="live"
3. Update 1st innings → Verify score, status="in-progress"
4. Update 2nd innings → Verify score, status still "in-progress"
5. Finish match → Verify winner, status="completed"
6. Test error cases (wrong status transitions, missing data)

### Phase 4: Documentation (10 min)
Create `WORKFLOW_API_COMPLETE.md` with:
- Full workflow diagram
- All 5 endpoints (create + 4 stages)
- Complete examples
- Error handling guide
- Frontend integration examples

---

## 💡 Key Design Decisions

### 1. Keep Existing Endpoints
- `/matches` - General CRUD (basic)
- `/matches/{id}/status` - Direct status update (advanced)
- `/matches/{id}/toss` - Direct toss update (advanced)
- `/matches/{id}/scores` - Direct score update (advanced)

**Why?** Backward compatibility + flexibility for admin/power users

### 2. Add Workflow Endpoints
- `/matches/{id}/start` - Workflow stage 2
- `/matches/{id}/first-innings-score` - Workflow stage 3A
- `/matches/{id}/second-innings-score` - Workflow stage 3B
- `/matches/{id}/finish` - Workflow stage 4

**Why?** Clear, sequential workflow for normal users

### 3. Smart Endpoint Functions
- Each workflow endpoint calls multiple internal operations
- Single DB commit (atomicity)
- Proper error handling with validation
- Logging for debugging

---

## 🛡️ Validation Rules

### For `start_match()`:
- ✅ Match must exist
- ✅ Match status must be "upcoming"
- ✅ toss_winner must match team1 or team2 name
- ✅ toss_choice must be "bat" or "bowl"
- ✅ match_score_url must be valid HTTP/HTTPS
- ✅ actual_start_time must be valid datetime
- ❌ Return 400 if status not "upcoming"
- ❌ Return 422 if validation fails

### For `update_first_innings_score()`:
- ✅ Match must exist
- ✅ Match status must be "live" or "in-progress"
- ✅ batting_team must match team1 or team2 name
- ✅ score must be positive integer
- ❌ Return 400 if status not "live" or "in-progress"
- ❌ Return 422 if validation fails

### For `update_second_innings_score()`:
- ✅ Match must exist
- ✅ Match status must be "in-progress"
- ✅ batting_team must match team1 or team2 name (and not be first innings team)
- ✅ score must be positive integer
- ✅ First innings score must exist
- ❌ Return 400 if first innings score not recorded
- ❌ Return 400 if batting_team same as first innings team
- ❌ Return 422 if validation fails

### For `finish_match()`:
- ✅ Match must exist
- ✅ Match status must be "in-progress"
- ✅ Both innings scores must exist
- ✅ winner must match team1 or team2 name
- ✅ margin must be positive integer
- ✅ margin_type must be "runs" or "wickets"
- ✅ match_end_time must be valid datetime
- ❌ Return 400 if status not "in-progress"
- ❌ Return 400 if scores not recorded
- ❌ Return 422 if validation fails

---

## 📊 Response Examples

### Start Match Response (200 OK)
```json
{
  "success": true,
  "message": "Match started successfully. First innings has begun!",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "Team A",
    "team2": "Team B",
    "status": "live",
    "toss_winner": "Team A",
    "toss_choice": "bat",
    "match_score_url": "https://scorecard.com/match/123",
    "actual_start_time": "2025-11-28T10:15:00",
    "team1_first_innings_score": null,
    "team2_first_innings_score": null,
    "winner": null,
    "created_at": "2025-11-28T09:00:00",
    "updated_at": "2025-11-28T10:15:00"
  }
}
```

### First Innings Update Response (200 OK)
```json
{
  "success": true,
  "message": "First innings score recorded. Match in progress!",
  "data": {
    "id": 1,
    "team1": "Team A",
    "team2": "Team B",
    "status": "in-progress",
    "toss_winner": "Team A",
    "toss_choice": "bat",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": null,
    "match_score_url": "https://scorecard.com/match/123",
    "updated_at": "2025-11-28T12:00:00"
  }
}
```

### Finish Match Response (200 OK)
```json
{
  "success": true,
  "message": "Match completed successfully!",
  "data": {
    "id": 1,
    "team1": "Team A",
    "team2": "Team B",
    "status": "completed",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": 152,
    "winner": "Team A",
    "margin": 13,
    "margin_type": "runs",
    "match_end_time": "2025-11-28T13:45:00",
    "match_score_url": "https://scorecard.com/match/123",
    "updated_at": "2025-11-28T13:45:00"
  }
}
```

---

## ⚠️ Error Response Examples

### Status Transition Error (400 Bad Request)
```json
{
  "detail": "Cannot start match: Status must be 'upcoming', but is 'live'. Match already started!"
}
```

### Validation Error (422 Unprocessable Entity)
```json
{
  "detail": "Toss winner 'Team C' does not match either team (Team A, Team B)"
}
```

### Missing Data Error (400 Bad Request)
```json
{
  "detail": "Cannot finish match: First innings score not recorded yet"
}
```

### Not Found Error (404 Not Found)
```json
{
  "detail": "Match not found"
}
```

---

## 🧪 Test Cases to Implement

### Happy Path Test
```
1. Create match (status=upcoming)
2. Start match (status=live)
3. Update 1st innings (status=in-progress)
4. Update 2nd innings (status=in-progress)
5. Finish match (status=completed)
✓ All transitions valid
✓ All data persisted
✓ Responses have correct structure
```

### Error Cases Test
```
1. Try to start match twice → 400
2. Try to update 1st innings before starting → 400
3. Try to finish without 1st innings score → 400
4. Try to finish without 2nd innings score → 400
5. Invalid toss winner name → 422
6. Invalid margin_type → 422
```

### Edge Cases Test
```
1. Update 1st innings multiple times (overwrite) ✓
2. Update 2nd innings multiple times (overwrite) ✓
3. Different team names for matching ✓
4. Very long URLs → 422 (if max enforced)
5. Score boundary values (0, 999) ✓
```

---

## 🚀 Frontend Integration Impact

### UI Changes Needed:
1. **Upcoming Section:**
   - Show "CREATE" form
   - After create: Show match card with "START" button

2. **Live Section:**
   - Show match card with toss info
   - Show scorecard link
   - Show "UPDATE SCORES" button for 1st innings

3. **In-Progress Section:**
   - Show both score input areas
   - Show "FINISH MATCH" button

4. **Completed Section:**
   - Show all details read-only
   - Show winner and margin
   - Show scorecard link

### API Calls by Frontend:
```javascript
// Stage 1: Create
POST /api/schedule/matches

// Stage 2: Start (RENAME from status update)
PUT /api/schedule/matches/{id}/start

// Stage 3A: First innings
PUT /api/schedule/matches/{id}/first-innings-score

// Stage 3B: Second innings
PUT /api/schedule/matches/{id}/second-innings-score

// Stage 4: Finish
PUT /api/schedule/matches/{id}/finish
```

---

## 📝 Files to Create/Modify

### Create New Files:
1. `test_match_workflow.py` - Complete workflow tests
2. `WORKFLOW_API_COMPLETE.md` - Complete documentation

### Modify Existing Files:
1. `app/schemas_schedule.py` - Add 4 new request schemas
2. `app/routes/schedule.py` - Add 4 new endpoint functions
3. `FRONTEND_UPDATE_PROMPT.md` - Update with new endpoints (optional)

---

## ⏱️ Estimated Implementation Time

- Add schemas: 10 minutes
- Add endpoints: 25 minutes
- Create tests: 20 minutes
- Document: 15 minutes
- **Total: ~70 minutes**

---

## ✨ Benefits of This Approach

1. **Clear Workflow:** Users follow a logical sequence
2. **Error Prevention:** Invalid transitions prevented at API level
3. **Better Messages:** "Match not started yet" vs "Status should be X"
4. **Backward Compatible:** Old endpoints still work
5. **Flexible:** Admin can still use old endpoints for direct updates
6. **Scalable:** Can add more stages in future if needed
7. **Testable:** Each stage independently testable

