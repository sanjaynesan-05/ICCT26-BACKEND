# Frontend Integration Quick Reference

**Version:** 1.0.1  
**Last Updated:** November 29, 2025

---

## 🔴 CRITICAL CHANGE: Runs & Wickets Separation

The API now returns **separate fields** for runs and wickets. This is a **breaking change**.

### Old Response (❌ NO LONGER VALID)
```json
{
  "team1_first_innings_score": 165  // Combined runs + wickets
}
```

### New Response (✅ CURRENT)
```json
{
  "team1_first_innings_runs": 165,    // Runs only
  "team1_first_innings_wickets": 8,   // Wickets only
  "team2_first_innings_runs": 152,    // Runs only
  "team2_first_innings_wickets": 5    // Wickets only
}
```

### Display Format
- **Old:** `165` (unclear - is this runs or wickets?)
- **New:** `165/8` (clear: 165 runs, 8 wickets)

---

## 📝 Form Input Changes

### Innings Score Form - OLD (❌)
```html
<form>
  <input type="number" name="batting_team" />
  <input type="number" name="score" placeholder="e.g., 165" />
  <button>Submit</button>
</form>
```

### Innings Score Form - NEW (✅)
```html
<form>
  <input type="text" name="batting_team" placeholder="Team name" />
  <input type="number" name="runs" placeholder="Runs (0-999)" min="0" max="999" />
  <input type="number" name="wickets" placeholder="Wickets (0-10)" min="0" max="10" />
  <button>Submit</button>
</form>
```

---

## 🔗 API Endpoints Summary

### 1. Record First Innings
```
PUT /api/schedule/matches/{match_id}/first-innings-score
Content-Type: application/json

{
  "batting_team": "Team A",
  "runs": 165,
  "wickets": 8
}

Response:
{
  "success": true,
  "data": {
    "team1_first_innings_runs": 165,
    "team1_first_innings_wickets": 8
  }
}
```

### 2. Record Second Innings
```
PUT /api/schedule/matches/{match_id}/second-innings-score
Content-Type: application/json

{
  "batting_team": "Team B",
  "runs": 152,
  "wickets": 5
}

Response:
{
  "success": true,
  "data": {
    "team2_first_innings_runs": 152,
    "team2_first_innings_wickets": 5
  }
}
```

### 3. Get Match Details
```
GET /api/schedule/matches/{match_id}

Response:
{
  "success": true,
  "data": {
    "id": 45,
    "team1": "Team A",
    "team2": "Team B",
    "status": "live",
    "team1_first_innings_runs": 165,
    "team1_first_innings_wickets": 8,
    "team2_first_innings_runs": 152,
    "team2_first_innings_wickets": 5,
    "result": {
      "winner": "Team A",
      "margin": 13,
      "marginType": "runs"
    }
  }
}
```

---

## 🔄 Match Workflow Stages

```
Stage 1: CREATE
POST /api/schedule/matches
Payload: { team1, team2, round, match_number }

    ↓

Stage 2: START
PUT /api/schedule/matches/{id}/start
Payload: { toss_winner, toss_choice: "bat" | "bowl" }

    ↓

Stage 3A: FIRST INNINGS
PUT /api/schedule/matches/{id}/first-innings-score
Payload: { batting_team, runs, wickets }  ← NEW FORMAT

    ↓

Stage 3B: SECOND INNINGS
PUT /api/schedule/matches/{id}/second-innings-score
Payload: { batting_team, runs, wickets }  ← NEW FORMAT

    ↓

Stage 4: FINISH
PUT /api/schedule/matches/{id}/finish
Payload: { winner, margin, margin_type: "runs" | "wickets" }
```

---

## ✅ Frontend Checklist

- [ ] **Runs/Wickets Fields**
  - [ ] Add separate input fields for runs and wickets
  - [ ] Add validation: runs 0-999, wickets 0-10
  - [ ] Display format: `165/8` (runs/wickets)

- [ ] **API Requests**
  - [ ] Update first innings endpoint to send `runs` and `wickets`
  - [ ] Update second innings endpoint to send `runs` and `wickets`
  - [ ] Remove old `score` field from requests

- [ ] **API Responses**
  - [ ] Update response parsing for new field names
  - [ ] Store `team1_first_innings_runs` and `team1_first_innings_wickets`
  - [ ] Store `team2_first_innings_runs` and `team2_first_innings_wickets`

- [ ] **Display Logic**
  - [ ] Scorecard shows: `Team A: 165/8` (runs/wickets)
  - [ ] Match result shows correct margin and type
  - [ ] Innings details display correctly

- [ ] **Testing**
  - [ ] Test full match workflow
  - [ ] Verify runs display correctly
  - [ ] Verify wickets display correctly
  - [ ] Test edge cases (0 runs, 10 wickets, etc.)

---

## 🧪 Manual Test Workflow

### 1. Create Match
```bash
curl -X POST http://localhost:8000/api/schedule/matches \
  -H "Content-Type: application/json" \
  -d '{
    "team1": "Team A",
    "team2": "Team B",
    "round": "Round 1",
    "match_number": 1
  }'
# Returns: {"success": true, "data": {"id": 45}}
```

### 2. Start Match
```bash
curl -X PUT http://localhost:8000/api/schedule/matches/45/start \
  -H "Content-Type: application/json" \
  -d '{
    "toss_winner": "Team A",
    "toss_choice": "bat"
  }'
```

### 3. Record First Innings
```bash
curl -X PUT http://localhost:8000/api/schedule/matches/45/first-innings-score \
  -H "Content-Type: application/json" \
  -d '{
    "batting_team": "Team A",
    "runs": 165,
    "wickets": 8
  }'
# Check: team1_first_innings_runs: 165, team1_first_innings_wickets: 8
```

### 4. Record Second Innings
```bash
curl -X PUT http://localhost:8000/api/schedule/matches/45/second-innings-score \
  -H "Content-Type: application/json" \
  -d '{
    "batting_team": "Team B",
    "runs": 152,
    "wickets": 5
  }'
# Check: team2_first_innings_runs: 152, team2_first_innings_wickets: 5
```

### 5. Finish Match
```bash
curl -X PUT http://localhost:8000/api/schedule/matches/45/finish \
  -H "Content-Type: application/json" \
  -d '{
    "winner": "Team A",
    "margin": 13,
    "margin_type": "runs"
  }'
```

### 6. Verify Match
```bash
curl http://localhost:8000/api/schedule/matches/45
# Should return all fields with correct values
```

---

## 🎯 Key Points

1. **Runs and wickets are SEPARATE** - Don't combine them
2. **Input validation required** - Runs: 0-999, Wickets: 0-10
3. **Display format** - Use `165/8` format on scorecard
4. **Response field names** - Use exact names from API response
5. **Test thoroughly** - Complete workflow must be verified

---

## 📚 Related Documentation

- Complete API reference: `docs/api-reference/COMPLETE_API_ENDPOINTS.md`
- Match schedule API: `docs/MATCH_SCHEDULE_API.md`
- Deployment guide: `docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md`

---

## ❓ Common Issues

### Issue: Wickets field missing in response
**Solution:** Server may need restart after code update
```bash
# Stop the server (Ctrl+C)
# Then restart it
python main.py
```

### Issue: Validation error on wickets
**Solution:** Ensure wickets are 0-10, runs are 0-999
```javascript
// Frontend validation
if (wickets < 0 || wickets > 10) {
  showError("Wickets must be between 0 and 10");
}
```

### Issue: "batting_team not found" error
**Solution:** Team name must match exactly (case-sensitive)
```javascript
// Correct
{ "batting_team": "Team A", ... }

// Wrong
{ "batting_team": "team a", ... }
```

---

## 📞 Support

For backend API issues:
1. Check the complete API documentation in `docs/api-reference/`
2. Review the deployment checklist in `docs/deployment/`
3. Test with curl commands (examples above)
4. Check backend logs in `logs/` directory

**Backend Status:** ✅ Ready for Production
**Frontend Integration Status:** 🔄 In Progress
