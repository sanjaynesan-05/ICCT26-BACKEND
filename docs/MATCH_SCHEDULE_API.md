# Cricket Match Schedule Management - API Integration Guide

**Date:** November 29, 2025  
**Backend Version:** 1.0.1  
**Status:** Production Ready

---

## 🎯 Overview

The backend includes a comprehensive **4-Stage Match Workflow** for cricket tournament match management. This guide is for frontend developers integrating with the match schedule API endpoints.

---

## 📋 4-Stage Match Workflow

```
Stage 1: CREATE MATCH (POST /api/schedule/matches)
   ↓
Stage 2: START MATCH (PUT /api/schedule/matches/{id}/start)
   ↓  
Stage 3A: RECORD FIRST INNINGS (PUT /api/schedule/matches/{id}/first-innings-score)
   ↓
Stage 3B: RECORD SECOND INNINGS (PUT /api/schedule/matches/{id}/second-innings-score)
   ↓
Stage 4: FINISH MATCH (PUT /api/schedule/matches/{id}/finish)
```

---

## 🔑 Critical Changes

### ✅ Runs & Wickets Separation

**Now stored as separate fields:**
- `team1_first_innings_runs` (Integer: 0-999)
- `team1_first_innings_wickets` (Integer: 0-10)
- `team2_first_innings_runs` (Integer: 0-999)
- `team2_first_innings_wickets` (Integer: 0-10)

**Display Format:** `165/8` (runs/wickets)

---

## 📡 API Endpoints

### 1. Create Match (Stage 1)
```
POST /api/schedule/matches
Content-Type: application/json

{
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "Team A",
  "team2": "Team B",
  "scheduled_start_time": "2025-11-28T10:00:00"  // Optional
}

Response (200):
{
  "success": true,
  "message": "Match created successfully",
  "data": {
    "id": 45,
    "status": "scheduled",
    ...
  }
}
```

### 2. Start Match (Stage 2)
```
PUT /api/schedule/matches/{match_id}/start
Content-Type: application/json

{
  "toss_winner": "Team A",
  "toss_choice": "bat",  // or "bowl"
  "match_score_url": "https://scorecard.com",
  "actual_start_time": "2025-11-28T10:15:00"
}

Response (200):
{
  "success": true,
  "message": "Match started successfully",
  "data": {
    "id": 45,
    "status": "live",
    "toss_winner": "Team A",
    ...
  }
}
```

### 3. Record First Innings (Stage 3A)
```
PUT /api/schedule/matches/{match_id}/first-innings-score
Content-Type: application/json

{
  "batting_team": "Team A",
  "runs": 165,
  "wickets": 8
}

Response (200):
{
  "success": true,
  "message": "First innings score recorded",
  "data": {
    "team1_first_innings_runs": 165,
    "team1_first_innings_wickets": 8,
    ...
  }
}
```

### 4. Record Second Innings (Stage 3B)
```
PUT /api/schedule/matches/{match_id}/second-innings-score
Content-Type: application/json

{
  "batting_team": "Team B",
  "runs": 152,
  "wickets": 5
}

Response (200):
{
  "success": true,
  "message": "Second innings score recorded",
  "data": {
    "team2_first_innings_runs": 152,
    "team2_first_innings_wickets": 5,
    ...
  }
}
```

### 5. Finish Match (Stage 4)
```
PUT /api/schedule/matches/{match_id}/finish
Content-Type: application/json

{
  "winner": "Team A",
  "margin": 13,
  "margin_type": "runs",  // or "wickets"
  "match_end_time": "2025-11-28T13:45:00"
}

Response (200):
{
  "success": true,
  "message": "Match completed successfully!",
  "data": {
    "status": "done",
    "result": {
      "winner": "Team A",
      "margin": 13,
      "marginType": "runs",
      "wonByBattingFirst": true
    },
    ...
  }
}
```

### 6. Other Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/schedule/matches` | List all matches |
| GET | `/api/schedule/matches/{id}` | Get single match |
| PUT | `/api/schedule/matches/{id}` | Update match details |
| DELETE | `/api/schedule/matches/{id}` | Delete match |
| POST | `/api/schedule/export` | Export schedule |

---

## 📊 Match Response Format

```json
{
  "id": 45,
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "Team A",
  "team2": "Team B",
  "status": "done",
  
  "toss_winner": "Team A",
  "toss_choice": "bat",
  
  "scheduled_start_time": "2025-11-28T10:00:00",
  "actual_start_time": "2025-11-28T10:15:00",
  "match_end_time": "2025-11-28T13:45:00",
  
  "team1_first_innings_runs": 165,
  "team1_first_innings_wickets": 8,
  "team2_first_innings_runs": 152,
  "team2_first_innings_wickets": 5,
  
  "match_score_url": "https://scorecard.com",
  
  "result": {
    "winner": "Team A",
    "margin": 13,
    "marginType": "runs",
    "wonByBattingFirst": true
  },
  
  "created_at": "2025-11-28T10:00:00",
  "updated_at": "2025-11-28T13:45:00"
}
```

---

## ✅ Frontend Checklist

- [ ] Update scorecard display: `165/8` instead of `165`
- [ ] Add wickets input field to innings forms
- [ ] Update field names to match API response
- [ ] Add form validation (wickets 0-10, runs 0-999)
- [ ] Implement 4-stage workflow buttons
- [ ] Handle all response fields correctly
- [ ] Test complete match workflow

---

## 🔗 Related Documentation

- See `DEPLOYMENT_READY.md` for full integration guide
- See main `README.md` for project overview
