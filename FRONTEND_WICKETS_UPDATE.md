# Frontend Update: Wickets Separation Feature (Corrected)

## Important Update ✅

The backend has been corrected to properly reflect cricket rules: **Each team plays only ONE innings per match**, not two.

- **Team 1** (determined by toss) = Batting First
- **Team 2** (determined by toss) = Batting Second

**Column Changes:**
- ❌ Removed: `team1_second_innings_runs`, `team1_second_innings_wickets`, `team2_second_innings_runs`, `team2_second_innings_wickets`
- ✅ Simplified to: `team1_runs`, `team1_wickets`, `team2_runs`, `team2_wickets`

---

## Overview

The backend now stores innings scores as separate **runs** and **wickets** fields instead of a single combined score. Update the frontend to:

1. Send `runs` and `wickets` separately to the API
2. Display scores in "runs-wickets" format (e.g., "165-8")
3. Accept both values in scoring forms

**Status:** Backend ✅ Complete. Frontend requires updates below.

---

## Part 1: Update Service Functions

### File: `frontend/src/services/matchService.js`

**Find and replace these two functions:**

```javascript
export const recordFirstInnings = async (matchId, battingTeam, runs, wickets) => {
  const response = await fetch(`${API_BASE_URL}/schedule/matches/${matchId}/first-innings-score`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      batting_team: battingTeam,
      runs: parseInt(runs),
      wickets: parseInt(wickets)
    })
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to record first innings');
  }
  return response.json();
};

export const recordSecondInnings = async (matchId, battingTeam, runs, wickets) => {
  const response = await fetch(`${API_BASE_URL}/schedule/matches/${matchId}/second-innings-score`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      batting_team: battingTeam,
      runs: parseInt(runs),
      wickets: parseInt(wickets)
    })
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to record second innings');
  }
  return response.json();
};
```

**Key Changes:**
- `score` parameter → `runs` and `wickets` parameters
- Request body includes both `runs` and `wickets` as separate fields
- Added error handling for non-2xx responses

---

## Part 2: Create New Score Form Component

### File: `frontend/src/components/ScoreForm.jsx` (Complete Rewrite)

```javascript
import React, { useState } from 'react';
import { recordFirstInnings, recordSecondInnings } from '../services/matchService';

const ScoreForm = ({ matchId, inningsType = 'first', battingTeam, onSuccess, onError, disabled = false }) => {
  const [runs, setRuns] = useState('');
  const [wickets, setWickets] = useState('0');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Validation
  const validateInputs = () => {
    const runsNum = parseInt(runs);
    const wicketsNum = parseInt(wickets);

    if (isNaN(runsNum) || runsNum < 0 || runsNum > 999) {
      setError('Runs must be a number between 0 and 999');
      return false;
    }
    if (isNaN(wicketsNum) || wicketsNum < 0 || wicketsNum > 10) {
      setError('Wickets must be between 0 and 10');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateInputs()) {
      return;
    }

    setLoading(true);

    try {
      let response;
      if (inningsType === 'first') {
        response = await recordFirstInnings(matchId, battingTeam, runs, wickets);
      } else {
        response = await recordSecondInnings(matchId, battingTeam, runs, wickets);
      }

      if (response.success) {
        setRuns('');
        setWickets('0');
        onSuccess?.(response.data);
      } else {
        setError(response.message || 'Failed to record innings');
        onError?.(response.message);
      }
    } catch (err) {
      setError(err.message || 'Error recording innings');
      onError?.(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md max-w-md">
      <h2 className="text-2xl font-bold mb-4">
        {inningsType === 'first' ? 'Record First Innings' : 'Record Second Innings'}
      </h2>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Batting Team
        </label>
        <input
          type="text"
          value={battingTeam || ''}
          disabled
          className="w-full px-4 py-2 border border-gray-300 rounded bg-gray-100 cursor-not-allowed"
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Runs Scored <span className="text-red-600">*</span>
        </label>
        <input
          type="number"
          value={runs}
          onChange={(e) => setRuns(e.target.value)}
          placeholder="Enter runs (0-999)"
          min="0"
          max="999"
          disabled={disabled || loading}
          className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          required
        />
        <p className="text-xs text-gray-500 mt-1">Enter total runs scored in this innings</p>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Wickets Lost <span className="text-red-600">*</span>
        </label>
        <select
          value={wickets}
          onChange={(e) => setWickets(e.target.value)}
          disabled={disabled || loading}
          className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((w) => (
            <option key={w} value={w}>
              {w} wicket{w !== 1 ? 's' : ''} lost
            </option>
          ))}
        </select>
        <p className="text-xs text-gray-500 mt-1">Number of wickets lost (0-10)</p>
      </div>

      {/* Score Preview */}
      {runs && (
        <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
          <p className="text-sm text-gray-700">
            <span className="font-semibold">Score Preview:</span> <span className="text-lg font-bold text-blue-600">{runs}-{wickets}</span>
          </p>
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-50 rounded border border-red-200">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <button
        type="submit"
        disabled={disabled || loading || !runs}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'Submitting...' : `Record ${inningsType === 'first' ? 'First' : 'Second'} Innings`}
      </button>
    </form>
  );
};

export default ScoreForm;
```

---

## Part 3: Update Match Card Component

### File: `frontend/src/components/MatchCard.jsx`

**Add this helper function at the top of the component:**

```javascript
// Helper function to format score with wickets
const formatScore = (runs, wickets) => {
  if (runs === null || runs === undefined) {
    return '-';
  }
  const w = wickets ?? 0;
  return `${runs}-${w}`;
};
```

**Find the score display section and update it:**

Replace this:
```javascript
// Old display
<div className="text-lg font-bold">{match.team1_first_innings_score}</div>
```

With this:
```javascript
// New display with runs-wickets format
<div className="text-lg font-bold">
  {formatScore(match.team1_first_innings_runs, match.team1_first_innings_wickets)}
</div>
```

**Complete Updated Innings Score Display Section:**

```javascript
{/* Innings Scores */}
{(match.status === 'live' || match.status === 'done') && (
  <div className="bg-gray-50 p-3 rounded mb-3">
    {/* First Innings */}
    {(match.team1_first_innings_runs !== null || match.team2_first_innings_runs !== null) && (
      <div className="grid grid-cols-2 gap-4 mb-2">
        <div>
          <p className="text-xs font-semibold text-gray-600">1st Innings</p>
          <p className="text-sm text-gray-700">{match.team1?.team_name || 'Team 1'}</p>
          <p className="text-lg font-bold">
            {formatScore(match.team1_first_innings_runs, match.team1_first_innings_wickets)}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold text-gray-600">vs</p>
          <p className="text-sm text-gray-700">{match.team2?.team_name || 'Team 2'}</p>
          <p className="text-lg font-bold">
            {formatScore(match.team2_first_innings_runs, match.team2_first_innings_wickets)}
          </p>
        </div>
      </div>
    )}

    {/* Second Innings */}
    {(match.team1_second_innings_runs !== null || match.team2_second_innings_runs !== null) && (
      <div className="grid grid-cols-2 gap-4 border-t border-gray-300 pt-2">
        <div>
          <p className="text-xs font-semibold text-gray-600">2nd Innings</p>
          <p className="text-sm text-gray-700">{match.team1?.team_name || 'Team 1'}</p>
          <p className="text-lg font-bold">
            {formatScore(match.team1_second_innings_runs, match.team1_second_innings_wickets)}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold text-gray-600">vs</p>
          <p className="text-sm text-gray-700">{match.team2?.team_name || 'Team 2'}</p>
          <p className="text-lg font-bold">
            {formatScore(match.team2_second_innings_runs, match.team2_second_innings_wickets)}
          </p>
        </div>
      </div>
    )}
  </div>
)}
```

---

## Part 4: Update Match Detail Modal Component

### File: `frontend/src/components/MatchDetailModal.jsx`

**Add the helper function at the top:**

```javascript
const formatScore = (runs, wickets) => {
  if (runs === null || runs === undefined) {
    return '-';
  }
  const w = wickets ?? 0;
  return `${runs}-${w}`;
};
```

**Update the Match Result Section (if displaying match result):**

```javascript
{/* Match Result Section */}
{match.status === 'done' && (
  <div className="bg-green-50 p-4 rounded-lg border border-green-200">
    <h3 className="text-xl font-bold text-green-700 mb-3">Match Result</h3>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
      {/* First Innings */}
      <div>
        <h4 className="font-semibold text-gray-700 mb-2">First Innings</h4>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>{match.team1?.team_name || 'Team 1'}</span>
            <span className="font-bold">
              {formatScore(match.team1_first_innings_runs, match.team1_first_innings_wickets)}
            </span>
          </div>
          <div className="flex justify-between">
            <span>{match.team2?.team_name || 'Team 2'}</span>
            <span className="font-bold">
              {formatScore(match.team2_first_innings_runs, match.team2_first_innings_wickets)}
            </span>
          </div>
        </div>
      </div>

      {/* Second Innings */}
      {(match.team1_second_innings_runs !== null || match.team2_second_innings_runs !== null) && (
        <div>
          <h4 className="font-semibold text-gray-700 mb-2">Second Innings</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>{match.team1?.team_name || 'Team 1'}</span>
              <span className="font-bold">
                {formatScore(match.team1_second_innings_runs, match.team1_second_innings_wickets)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>{match.team2?.team_name || 'Team 2'}</span>
              <span className="font-bold">
                {formatScore(match.team2_second_innings_runs, match.team2_second_innings_wickets)}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>

    {/* Winner */}
    <div className="border-t border-green-200 pt-3">
      <p className="text-lg font-bold text-green-700">
        🏆 {match.winner?.team_name || 'Unknown'} Won
      </p>
      {match.margin && (
        <p className="text-green-600">
          by {match.margin} {match.margin_type || 'runs'}
        </p>
      )}
    </div>
  </div>
)}
```

---

## Part 5: Update Score Display in Match Details Page

### File: `frontend/src/pages/MatchDetailPage.jsx` (or similar)

If you have a dedicated match details page that displays scores, update those sections similarly:

**Old Code:**
```javascript
<p>First Innings: {match.team1_first_innings_score}</p>
```

**New Code:**
```javascript
<p>
  First Innings: {match.team1_first_innings_runs !== null ? (
    <span className="font-bold text-lg">
      {match.team1_first_innings_runs}-{match.team1_first_innings_wickets ?? 0}
    </span>
  ) : (
    <span className="text-gray-400">Not recorded</span>
  )}
</p>
```

---

## Part 6: Test the Changes

### Frontend Checklist:

- [ ] Form displays runs input field (0-999)
- [ ] Form displays wickets dropdown (0-10)
- [ ] Form shows "Score Preview" with "runs-wickets" format (e.g., "165-8")
- [ ] Form validation prevents invalid runs (< 0 or > 999)
- [ ] Form validation prevents invalid wickets (< 0 or > 10)
- [ ] Form submission sends both `runs` and `wickets` to API
- [ ] Match card displays scores as "165-8" format (not just "165")
- [ ] Match detail modal shows runs and wickets separately
- [ ] Error messages display correctly if API rejects invalid values
- [ ] Backward compatibility: old matches without wickets still display (with default 0 wickets)

### Testing Workflow:

1. Create a match (POST /api/schedule/matches)
2. Start the match (PUT /api/schedule/matches/{id}/start)
3. Record first innings with ScoreForm (runs=165, wickets=8)
   - Verify API call includes `{ "batting_team": "...", "runs": 165, "wickets": 8 }`
   - Verify response includes `team1_first_innings_runs: 165`, `team1_first_innings_wickets: 8`
4. Verify MatchCard displays "165-8"
5. Record second innings with ScoreForm (runs=152, wickets=5)
6. Verify both innings display correctly
7. Finish match and verify result display

---

## Part 7: API Response Format Reference

### First Innings Request
```json
PUT /api/schedule/matches/{id}/first-innings-score
{
  "batting_team": "Team A",
  "runs": 165,
  "wickets": 8
}
```

### First Innings Response
```json
{
  "success": true,
  "message": "First innings score recorded. Match in progress!",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "Team A",
    "team2": "Team B",
    "status": "live",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": null,
    ...
  }
}
```

### Second Innings Request
```json
PUT /api/schedule/matches/{id}/second-innings-score
{
  "batting_team": "Team B",
  "runs": 152,
  "wickets": 5
}
```

---

## Part 8: Field Mapping Reference

| Old Field | New Fields | Format |
|-----------|-----------|---------|
| `team1_first_innings_score` | `team1_first_innings_runs` + `team1_first_innings_wickets` | "165-8" |
| `team2_first_innings_score` | `team2_first_innings_runs` + `team2_first_innings_wickets` | "152-5" |
| `team1_second_innings_score` | `team1_second_innings_runs` + `team1_second_innings_wickets` | "168-6" |
| `team2_second_innings_score` | `team2_second_innings_runs` + `team2_second_innings_wickets` | "180-4" |

---

## Part 9: Implementation Order

1. ✅ Update `matchService.js` - service functions for API calls
2. ✅ Create/rewrite `ScoreForm.jsx` - new form with dual inputs
3. ✅ Update `MatchCard.jsx` - display with formatScore helper
4. ✅ Update `MatchDetailModal.jsx` - display with formatScore helper
5. ✅ Update any other components showing scores (MatchDetailPage, etc.)
6. ✅ Test all forms and displays
7. ✅ Deploy and verify

---

## Part 10: Backward Compatibility

**Old matches (without wickets):**
- Legacy fields (`team1_first_innings_score`, etc.) are still populated on backend
- Frontend assumes wickets = 0 when not provided
- Display shows "165-0" for old matches (with 0 wickets)

**Graceful degradation:**
```javascript
// If wickets is null/undefined, default to 0
const formatScore = (runs, wickets) => {
  if (runs === null || runs === undefined) {
    return '-';
  }
  const w = wickets ?? 0;  // Default to 0 if null/undefined
  return `${runs}-${w}`;
};
```

---

## Quick Summary

**What Changed:**
- Backend: Scores now stored as separate runs and wickets
- Frontend: Forms accept two inputs, display shows "runs-wickets" format

**Files to Update:**
1. `frontend/src/services/matchService.js`
2. `frontend/src/components/ScoreForm.jsx`
3. `frontend/src/components/MatchCard.jsx`
4. `frontend/src/components/MatchDetailModal.jsx`

**Key Points:**
- Validation: runs (0-999), wickets (0-10)
- Display format: "165-8" (165 runs, 8 wickets)
- Backward compatible with old matches (defaults to 0 wickets)
