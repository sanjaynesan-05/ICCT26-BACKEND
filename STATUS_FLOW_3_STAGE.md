# Match Status Flow: 3-Stage System

## Overview
The match workflow has been simplified from 4 stages to **3 clear statuses**:

```
scheduled → live → done
```

---

## Status Definitions

### 1. **Scheduled** 
- Match created but not started
- Initial status when match is created
- Cannot have innings scores or results yet

### 2. **Live** 
- Match has started (toss completed, scorecard URL assigned)
- **Includes both score recording and match in-progress states**
- Both 1st innings and 2nd innings scores are recorded while in "live" status
- Status does NOT change when recording scores

### 3. **Done** 
- Match completed with final results
- Winner, margin, and match end time recorded
- Final and immutable status

---

## Status Transitions

| From | To | Action | Endpoint |
|------|-----|--------|----------|
| scheduled | live | Start match with toss details | `PUT /matches/{id}/start` |
| live | live | Record 1st innings score | `PUT /matches/{id}/first-innings-score` |
| live | live | Record 2nd innings score | `PUT /matches/{id}/second-innings-score` |
| live | done | Finish match with results | `PUT /matches/{id}/finish` |

**Key Point:** Status is `live` while recording both innings - it doesn't change to a separate "in-progress" state.

---

## API Workflow

### Step 1: Create Match (Status: scheduled)
```bash
POST /api/schedule/matches

{
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "SHARKS",
  "team2": "Thadaladi"
}

# Response status: "scheduled"
```

### Step 2: Start Match (Status: scheduled → live)
```bash
PUT /api/schedule/matches/{id}/start

{
  "toss_winner": "SHARKS",
  "toss_choice": "bat",
  "match_score_url": "https://example.com/scorecard",
  "actual_start_time": "2025-11-28T14:15:00"
}

# Response status: "live"
```

### Step 3A: Record 1st Innings (Status: live → live)
```bash
PUT /api/schedule/matches/{id}/first-innings-score

{
  "batting_team": "SHARKS",
  "score": 165
}

# Response status: still "live"
```

### Step 3B: Record 2nd Innings (Status: live → live)
```bash
PUT /api/schedule/matches/{id}/second-innings-score

{
  "batting_team": "Thadaladi",
  "score": 152
}

# Response status: still "live"
```

### Step 4: Finish Match (Status: live → done)
```bash
PUT /api/schedule/matches/{id}/finish

{
  "winner": "SHARKS",
  "margin": 13,
  "margin_type": "runs",
  "match_end_time": "2025-11-28T17:30:00"
}

# Response status: "done"
```

---

## Frontend Display

### Grouping Matches by Status

```javascript
// Group matches into 3 sections:

const scheduled = matches.filter(m => m.status === 'scheduled');  // Not started
const live = matches.filter(m => m.status === 'live');           // Ongoing (including score recording)
const done = matches.filter(m => m.status === 'done');           // Completed
```

---

## Important Notes

1. **Status stays "live" while recording scores**
   - First innings score recording: live → live (no change)
   - Second innings score recording: live → live (no change)

2. **Cannot skip stages**
   - Must go: scheduled → live → done
   - Cannot jump directly from scheduled to done

3. **Cannot go backwards**
   - scheduled cannot go back (only forward to live)
   - live cannot go back to scheduled (only forward to done)
   - done is final (no transitions from done)

4. **Match is "live" from start until finish**
   - All score recordings happen while status is "live"
   - Only the final finish changes it to "done"

---

## Code Changes Made

**Files Modified:**
- `app/routes/schedule.py` - All endpoint validations updated
- `app/schemas_schedule.py` - Status validator updated to accept: scheduled, live, done

**Tests:** ✅ All critical tests passing with new 3-status system

---

## Example Response with New Status

```json
{
  "success": true,
  "message": "Match finished successfully!",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "SHARKS",
    "team2": "Thadaladi",
    "status": "done",
    "toss_winner": "SHARKS",
    "toss_choice": "bat",
    "actual_start_time": "2025-11-28T14:15:00",
    "match_end_time": "2025-11-28T17:30:00",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": 152,
    "match_score_url": "https://example.com/scorecard",
    "result": {
      "winner": "SHARKS",
      "margin": 13,
      "margin_type": "runs",
      "won_by_batting_first": true
    }
  }
}
```

---

## Summary

✅ **3-Status System is Live**
- Scheduled → Live → Done
- Simpler workflow
- No separate "in-progress" status
- All score recording happens in "live" status
- All tests passing
