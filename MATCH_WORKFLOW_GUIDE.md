# Cricket Match Workflow Guide

## 🎯 Match Lifecycle Overview

You're describing a **4-Stage Match Workflow**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MATCH LIFECYCLE FLOW                              │
└─────────────────────────────────────────────────────────────────────────┘

    STAGE 1: CREATE MATCH (Upcoming)
    ─────────────────────────────────
    Create new match with:
    • Round number, Round name
    • Match number
    • Team A name, Team B name
    • Scheduled start time
    Status: "upcoming"
    Display: Upcoming section
                    │
                    ↓
    STAGE 2: START MATCH (Live)
    ───────────────────────────
    Click START button to update with:
    • Toss winner (Team A or Team B)
    • Toss choice (bat or bowl)
    • Match score URL (external scorecard link)
    • Actual start time
    Status: "live"
    Display: Live section / Match starting
                    │
                    ↓
    STAGE 3A: FIRST INNINGS UPDATE
    ──────────────────────────────
    After first innings ends:
    • Team that batted first: score
    • Update Team A or Team B score
    Status: "in-progress" (or "first-innings-completed")
    Display: Match in-progress section
                    │
                    ↓
    STAGE 3B: SECOND INNINGS UPDATE
    ───────────────────────────────
    After second innings ends:
    • Team that batted second: score
    • Update remaining team score
    Status: "in-progress" (or "second-innings-completed")
    Display: Match in-progress section
                    │
                    ↓
    STAGE 4: FINISH MATCH (Done)
    ────────────────────────────
    Click FINISH button to complete with:
    • Winner (Team A or Team B)
    • Margin (runs/wickets)
    • Match end time
    Status: "completed"
    Display: Completed section / Results
```

---

## 📊 Backend Requirements by Stage

### STAGE 1: CREATE MATCH
**User Action:** Fill form and submit  
**API Endpoint:** `POST /api/schedule/matches`

**Required Fields:**
```json
{
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "Team A Name",
  "team2": "Team B Name",
  "scheduled_start_time": "2025-11-28T10:00:00"
}
```

**Database State:**
- `status = "upcoming"`
- `toss_winner = NULL`
- `toss_choice = NULL`
- `match_score_url = NULL`
- `actual_start_time = NULL`
- `match_end_time = NULL`
- `team1_first_innings_score = NULL`
- `team2_first_innings_score = NULL`
- `winner = NULL`
- `margin = NULL`

**Response:**
```json
{
  "success": true,
  "message": "Match created successfully",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "Team A Name",
    "team2": "Team B Name",
    "status": "upcoming",
    "scheduled_start_time": "2025-11-28T10:00:00",
    "toss_winner": null,
    "toss_choice": null,
    "match_score_url": null,
    "actual_start_time": null,
    "match_end_time": null,
    "team1_first_innings_score": null,
    "team2_first_innings_score": null,
    "winner": null,
    "margin": null
  }
}
```

---

### STAGE 2: START MATCH (Click START Button)
**User Action:** Click START button on match card  
**API Endpoint:** `PUT /api/schedule/matches/{id}/start`

**Required Fields:**
```json
{
  "toss_winner": "Team A Name",
  "toss_choice": "bat",
  "match_score_url": "https://cricketscoreboard.com/match/123",
  "actual_start_time": "2025-11-28T10:15:00"
}
```

**Validation:**
- `toss_winner` must match either `team1` or `team2`
- `toss_choice` must be "bat" or "bowl"
- `match_score_url` must start with http:// or https://
- `actual_start_time` must be valid ISO datetime

**Database State Changes:**
- `status = "live"` ← Changed from "upcoming"
- `toss_winner = "Team A Name"`
- `toss_choice = "bat"`
- `match_score_url = "https://cricketscoreboard.com/match/123"`
- `actual_start_time = "2025-11-28T10:15:00"`

**Response:**
```json
{
  "success": true,
  "message": "Match started successfully",
  "data": {
    "id": 1,
    "team1": "Team A Name",
    "team2": "Team B Name",
    "status": "live",
    "toss_winner": "Team A Name",
    "toss_choice": "bat",
    "match_score_url": "https://cricketscoreboard.com/match/123",
    "actual_start_time": "2025-11-28T10:15:00",
    ...rest of match data...
  }
}
```

---

### STAGE 3A: UPDATE FIRST INNINGS SCORE
**User Action:** After first innings ends, enter batting team's score  
**API Endpoint:** `PUT /api/schedule/matches/{id}/first-innings-score`

**Scenario:** Team A (chose to bat) scored 165 runs

**Required Fields:**
```json
{
  "batting_team": "Team A Name",
  "score": 165
}
```

**Validation:**
- `batting_team` must match either `team1` or `team2`
- `score` must be a positive integer (0-999)
- Team must have batted first (check against toss_choice logic)

**Database State Changes:**
- If `batting_team == team1`:
  - `team1_first_innings_score = 165`
- If `batting_team == team2`:
  - `team2_first_innings_score = 165`
- Status remains: `status = "in-progress"` (or "first-innings-completed")

**Response:**
```json
{
  "success": true,
  "message": "First innings score updated successfully",
  "data": {
    "id": 1,
    "team1": "Team A Name",
    "team2": "Team B Name",
    "status": "in-progress",
    "toss_winner": "Team A Name",
    "toss_choice": "bat",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": null,
    "match_score_url": "https://cricketscoreboard.com/match/123",
    ...rest of match data...
  }
}
```

---

### STAGE 3B: UPDATE SECOND INNINGS SCORE
**User Action:** After second innings ends, enter other team's score  
**API Endpoint:** `PUT /api/schedule/matches/{id}/second-innings-score`

**Scenario:** Team B (chased) scored 152 runs

**Required Fields:**
```json
{
  "batting_team": "Team B Name",
  "score": 152
}
```

**Validation:**
- `batting_team` must be the OTHER team (not first innings batting team)
- `score` must be a positive integer (0-999)
- First innings score must already be recorded

**Database State Changes:**
- If `batting_team == team2`:
  - `team2_first_innings_score = 152`
- Status remains: `status = "in-progress"`

**Response:**
```json
{
  "success": true,
  "message": "Second innings score updated successfully",
  "data": {
    "id": 1,
    "team1": "Team A Name",
    "team2": "Team B Name",
    "status": "in-progress",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": 152,
    "match_score_url": "https://cricketscoreboard.com/match/123",
    ...rest of match data...
  }
}
```

---

### STAGE 4: FINISH MATCH (Click FINISH Button)
**User Action:** Click FINISH button, enter winner and margin  
**API Endpoint:** `PUT /api/schedule/matches/{id}/finish`

**Scenario:** Team A won by 13 runs

**Required Fields:**
```json
{
  "winner": "Team A Name",
  "margin": 13,
  "margin_type": "runs",
  "match_end_time": "2025-11-28T13:45:00"
}
```

**Validation:**
- `winner` must match either `team1` or `team2`
- `margin` must be positive integer
- `margin_type` must be "runs", "wickets", or "super-over"
- `match_end_time` must be valid ISO datetime
- Both innings scores must be recorded before finishing

**Database State Changes:**
- `status = "completed"` ← Changed from "in-progress"
- `winner = "Team A Name"`
- `margin = 13`
- `margin_type = "runs"`
- `match_end_time = "2025-11-28T13:45:00"`

**Response:**
```json
{
  "success": true,
  "message": "Match completed successfully",
  "data": {
    "id": 1,
    "team1": "Team A Name",
    "team2": "Team B Name",
    "status": "completed",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": 152,
    "winner": "Team A Name",
    "margin": 13,
    "margin_type": "runs",
    "match_end_time": "2025-11-28T13:45:00",
    "match_score_url": "https://cricketscoreboard.com/match/123",
    ...rest of match data...
  }
}
```

---

## 🗂️ Frontend Display by Status

### UPCOMING Section
Shows all matches with `status = "upcoming"`
```
┌─────────────────────────────────────────┐
│ Round 1 - Match 1                       │
│ Team A vs Team B                        │
│ Scheduled: Nov 28, 10:00 AM             │
│ [START] [DELETE]                        │
└─────────────────────────────────────────┘
```

### LIVE Section
Shows all matches with `status = "live"`
```
┌─────────────────────────────────────────┐
│ Round 1 - Match 1                       │
│ Team A vs Team B                        │
│ Status: 🔴 LIVE                         │
│ Toss: Team A won, chose to bat          │
│ Scorecard: [View Score]                 │
│ [END FIRST INNINGS] [DELETE]            │
└─────────────────────────────────────────┘
```

### IN-PROGRESS Section
Shows all matches with `status = "in-progress"`
```
┌─────────────────────────────────────────┐
│ Round 1 - Match 1                       │
│ Team A vs Team B                        │
│ Status: ⚙️ IN PROGRESS                 │
│ Team A (Bat): 165 runs                  │
│ Team B (Chase): 152 runs                │
│ [FINISH MATCH] [DELETE]                 │
└─────────────────────────────────────────┘
```

### COMPLETED Section
Shows all matches with `status = "completed"`
```
┌─────────────────────────────────────────┐
│ Round 1 - Match 1                       │
│ Team A vs Team B                        │
│ Status: ✅ COMPLETED                   │
│ Team A: 165 runs                        │
│ Team B: 152 runs                        │
│ Winner: Team A (by 13 runs)             │
│ Scorecard: [View Score]                 │
│ [VIEW DETAILS] [DELETE]                 │
└─────────────────────────────────────────┘
```

---

## 📝 Updated ORM Model (models.py)

Current Match model needs to be verified/updated:

```python
class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    round = Column(String(100), nullable=False)
    round_number = Column(Integer, nullable=False)
    match_number = Column(Integer, nullable=False)
    team1 = Column(String(100), nullable=False)
    team2 = Column(String(100), nullable=False)
    
    # Status tracking (CRITICAL)
    status = Column(String(50), default="upcoming", nullable=False, index=True)
    # Values: "upcoming", "live", "in-progress", "completed"
    
    # Toss information
    toss_winner = Column(String(100), nullable=True)
    toss_choice = Column(String(10), nullable=True)  # "bat" or "bowl"
    
    # Timing
    scheduled_start_time = Column(DateTime, nullable=False)
    actual_start_time = Column(DateTime, nullable=True)
    match_end_time = Column(DateTime, nullable=True)
    
    # Scores
    team1_first_innings_score = Column(Integer, nullable=True)
    team2_first_innings_score = Column(Integer, nullable=True)
    
    # Result
    winner = Column(String(100), nullable=True)
    margin = Column(Integer, nullable=True)
    margin_type = Column(String(20), nullable=True)  # "runs", "wickets", "super-over"
    
    # Scorecard link
    match_score_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 🔌 Endpoint Summary

```
Stage 1 (Create):        POST   /api/schedule/matches
                         ↓
                         Create match with basic info
                         Status: "upcoming"

Stage 2 (Start):         PUT    /api/schedule/matches/{id}/start
                         ↓
                         Add toss, URL, actual time
                         Status: "live"

Stage 3A (1st Innings):  PUT    /api/schedule/matches/{id}/first-innings-score
                         ↓
                         Update first batting team score
                         Status: "in-progress"

Stage 3B (2nd Innings):  PUT    /api/schedule/matches/{id}/second-innings-score
                         ↓
                         Update second batting team score
                         Status: "in-progress"

Stage 4 (Finish):        PUT    /api/schedule/matches/{id}/finish
                         ↓
                         Add winner, margin, end time
                         Status: "completed"
```

---

## ✅ What Already Exists

Based on backend analysis:
- ✅ Match model with most fields
- ✅ POST /matches endpoint (create)
- ✅ PUT /matches/{id}/status endpoint (update status)
- ✅ PUT /matches/{id}/toss endpoint (update toss)
- ✅ PUT /matches/{id}/timing endpoint (update timing)
- ✅ PUT /matches/{id}/scores endpoint (update scores)
- ✅ PUT /matches/{id}/score-url endpoint (update URL)
- ✅ GET /matches and GET /matches/{id} (retrieve)
- ✅ DELETE /matches/{id} (delete)

**Note:** Current endpoints need to be reorganized/combined to match the 4-stage workflow

---

## 🔄 Proposed Endpoint Reorganization

### Option A: Keep Current Endpoints, Add Workflow Endpoints
```
POST   /api/schedule/matches                    # Create (Stage 1) ✅ EXISTS
PUT    /api/schedule/matches/{id}/start         # Start match (Stage 2) - RENAME from /status
PUT    /api/schedule/matches/{id}/first-innings-score  # Stage 3A - NEW
PUT    /api/schedule/matches/{id}/second-innings-score # Stage 3B - NEW
PUT    /api/schedule/matches/{id}/finish        # Finish match (Stage 4) - NEW
GET    /api/schedule/matches                    # List all ✅ EXISTS
GET    /api/schedule/matches/{id}               # Get single ✅ EXISTS
DELETE /api/schedule/matches/{id}               # Delete ✅ EXISTS
```

### Option B: Create Unified Update Endpoint
```
PUT    /api/schedule/matches/{id}               # Universal update (smart routing based on status)
```

---

## 🎯 Recommendation

**Use a combination approach:**
1. Keep existing endpoints but add workflow-specific ones
2. New endpoints clearly show the workflow stage
3. Clear status transitions prevent invalid state changes
4. Better error messages: "Cannot finish match before both innings are recorded"

---

**Next Steps:**
1. Confirm this workflow matches your requirements
2. Check existing endpoints in backend
3. Update models.py if needed
4. Create new workflow endpoints
5. Create comprehensive test suite
6. Update frontend with new workflow UI

