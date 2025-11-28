# Quick Reference: What Changed

## Backend ✅ Complete

### Old API
```
PUT /api/schedule/matches/{id}/first-innings-score
{ "batting_team": "Team A", "score": 165 }
```

### New API
```
PUT /api/schedule/matches/{id}/first-innings-score
{ "batting_team": "Team A", "runs": 165, "wickets": 8 }
```

---

## Display Format

### Old
```
Score: 165
```

### New
```
Score: 165-8  (165 runs, 8 wickets lost)
```

---

## Frontend Files to Update

1. **frontend/src/services/matchService.js**
   - recordFirstInnings(matchId, battingTeam, runs, wickets)
   - recordSecondInnings(matchId, battingTeam, runs, wickets)

2. **frontend/src/components/ScoreForm.jsx**
   - New form with two inputs: runs + wickets
   - Validation: runs (0-999), wickets (0-10)
   - Add score preview "165-8"

3. **frontend/src/components/MatchCard.jsx**
   - Display scores as "165-8" format
   - Use formatScore helper function

4. **frontend/src/components/MatchDetailModal.jsx**
   - Display scores as "165-8" format
   - Use formatScore helper function

---

## Complete Documentation

**Backend Implementation**: `BACKEND_IMPLEMENTATION_STATUS.md`
**Frontend Update Guide**: `FRONTEND_WICKETS_UPDATE.md`
**Full Technical Details**: `WICKETS_SEPARATION_COMPLETE_UPDATE.md`

---

## Test Status

✅ Backend tests: 5/5 passing
⏳ Frontend tests: Ready to implement

---

## Deployment Checklist

- [ ] Backend deployed and running
- [ ] Database schema migrated (if needed)
- [ ] Frontend ScoreForm component updated
- [ ] Frontend display components updated
- [ ] Frontend service functions updated
- [ ] Test form with sample data
- [ ] Verify "runs-wickets" format displays correctly
- [ ] Verify API validation (reject runs > 999, wickets > 10)
- [ ] Production deployment
