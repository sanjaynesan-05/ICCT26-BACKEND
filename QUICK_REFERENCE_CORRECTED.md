# Quick Reference - Corrected Wickets Implementation

## ✅ Backend Complete & Tested

All 5 endpoint tests pass. Database schema corrected to match cricket rules.

---

## Database Schema (Corrected)

**4 Main Columns (Simple & Clean):**

```
team1_runs      → Runs for team batting first
team1_wickets   → Wickets lost by team batting first
team2_runs      → Runs for team batting second  
team2_wickets   → Wickets lost by team batting second
```

---

## API Changes

### Old Format ❌
```json
{ "batting_team": "Team A", "score": 165 }
```

### New Format ✅
```json
{ "batting_team": "Team A", "runs": 165, "wickets": 8 }
```

---

## Display Format

### Old ❌
```
Score: 165
```

### New ✅
```
Score: 165-8  (runs-wickets)
```

---

## Endpoints (Same Two)

**1. First Innings (Team batting first)**
```
PUT /api/schedule/matches/{id}/first-innings-score
```

**2. Second Innings (Team batting second)**
```
PUT /api/schedule/matches/{id}/second-innings-score
```

Both use the same simplified database fields.

---

## Frontend Files to Update

1. **services/matchService.js**
   - recordFirstInnings(matchId, battingTeam, runs, wickets)
   - recordSecondInnings(matchId, battingTeam, runs, wickets)

2. **components/ScoreForm.jsx**
   - New form with runs input + wickets dropdown
   - Validation: runs (0-999), wickets (0-10)

3. **components/MatchCard.jsx**
   - Display scores as "165-8" format
   - Use formatScore helper

4. **components/MatchDetailModal.jsx**
   - Display scores as "165-8" format
   - Show batting order

---

## Test Status

✅ Backend: 5/5 tests passing
⏳ Frontend: Ready to implement

---

## Complete Docs

- **Backend Status:** `BACKEND_IMPLEMENTATION_CORRECTED.md`
- **Frontend Guide:** `FRONTEND_WICKETS_UPDATE.md`

---

## What to Tell Frontend Dev

> "Backend is ready. Each team plays one innings. Database has 4 columns:
> - team1_runs, team1_wickets (first innings)
> - team2_runs, team2_wickets (second innings)
> 
> Update forms to accept runs + wickets separately. Display as '165-8' format."

---

## Cricket Match Example

```
Team A vs Team B

Toss: Team A wins, chooses bat
→ Team A bats FIRST

Scores:
First Innings:  Team A = 165-8 (165 runs, 8 wickets)
Second Innings: Team B = 152-5 (152 runs, 5 wickets)

Result: Team A wins by 13 runs
```

---

## Backward Compatibility

Old matches still work:
- Legacy fields keep populated
- Frontend shows "165-0" (defaults to 0 wickets)
- No data migration needed
