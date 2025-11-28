# Wickets Separation Feature - Complete Backend & Frontend Update

## Overview
Currently, innings scores are stored as single integers (e.g., `team1_first_innings_score = 165`). This update separates runs and wickets into distinct fields, enabling display format like "165-8" (165 runs, 8 wickets lost).

**Changes Required:**
1. Database schema (4 new columns)
2. Pydantic validation schemas
3. Backend endpoints (2 endpoints updated)
4. Frontend service functions (2 functions updated)
5. Frontend form component (ScoreForm.jsx - complete rewrite)
6. Frontend display components (MatchCard.jsx, MatchDetailModal.jsx)

---

## PART 1: BACKEND UPDATES

### Step 1.1: Update Database Schema (models.py)

**Location:** `d:\ICCT26 BACKEND\models.py` - Around line 139-142

**Current Code (Lines 139-142):**
```python
    # Innings scores
    team1_first_innings_score = Column(Integer, nullable=True)  # Team 1 score (first innings or batting first)
    team2_first_innings_score = Column(Integer, nullable=True)  # Team 2 score (first innings or batting first)
    team1_second_innings_score = Column(Integer, nullable=True)  # Team 1 score in second innings
    team2_second_innings_score = Column(Integer, nullable=True)  # Team 2 score in second innings
```

**Replace With:**
```python
    # Innings scores - First Innings
    team1_first_innings_runs = Column(Integer, nullable=True, default=0)  # Team 1 runs (first innings)
    team1_first_innings_wickets = Column(Integer, nullable=True, default=0)  # Team 1 wickets (first innings, 0-10)
    team2_first_innings_runs = Column(Integer, nullable=True, default=0)  # Team 2 runs (first innings)
    team2_first_innings_wickets = Column(Integer, nullable=True, default=0)  # Team 2 wickets (first innings, 0-10)
    
    # Innings scores - Second Innings
    team1_second_innings_runs = Column(Integer, nullable=True, default=0)  # Team 1 runs (second innings)
    team1_second_innings_wickets = Column(Integer, nullable=True, default=0)  # Team 1 wickets (second innings, 0-10)
    team2_second_innings_runs = Column(Integer, nullable=True, default=0)  # Team 2 runs (second innings)
    team2_second_innings_wickets = Column(Integer, nullable=True, default=0)  # Team 2 wickets (second innings, 0-10)
    
    # Legacy fields - DEPRECATED (keep for backward compatibility, will be removed in v2.0)
    team1_first_innings_score = Column(Integer, nullable=True)  # DEPRECATED: Use team1_first_innings_runs + team1_first_innings_wickets
    team2_first_innings_score = Column(Integer, nullable=True)  # DEPRECATED: Use team2_first_innings_runs + team2_first_innings_wickets
    team1_second_innings_score = Column(Integer, nullable=True)  # DEPRECATED: Use team1_second_innings_runs + team1_second_innings_wickets
    team2_second_innings_score = Column(Integer, nullable=True)  # DEPRECATED: Use team2_second_innings_runs + team2_second_innings_wickets
```

**Migration Command (PowerShell Terminal):**
```powershell
# Run these SQL commands directly in PostgreSQL

# Connect to database first, then execute:
# ALTER TABLE matches ADD COLUMN team1_first_innings_runs INTEGER DEFAULT 0;
# ALTER TABLE matches ADD COLUMN team1_first_innings_wickets INTEGER DEFAULT 0;
# ALTER TABLE matches ADD COLUMN team2_first_innings_runs INTEGER DEFAULT 0;
# ALTER TABLE matches ADD COLUMN team2_first_innings_wickets INTEGER DEFAULT 0;
# ALTER TABLE matches ADD COLUMN team1_second_innings_runs INTEGER DEFAULT 0;
# ALTER TABLE matches ADD COLUMN team1_second_innings_wickets INTEGER DEFAULT 0;
# ALTER TABLE matches ADD COLUMN team2_second_innings_runs INTEGER DEFAULT 0;
# ALTER TABLE matches ADD COLUMN team2_second_innings_wickets INTEGER DEFAULT 0;

# Or use Python script to run migrations
python scripts/run_migration.py
```

---

### Step 1.2: Update Pydantic Schemas (app/schemas_schedule.py)

**Find and Replace the Following Classes:**

**Current Code:**
```python
class FirstInningsScoreRequest(BaseModel):
    batting_team: str  # 'SHARKS' or other team name
    score: int
    
    class Config:
        from_attributes = True


class SecondInningsScoreRequest(BaseModel):
    batting_team: str  # 'SHARKS' or other team name
    score: int
    
    class Config:
        from_attributes = True
```

**Replace With:**
```python
class FirstInningsScoreRequest(BaseModel):
    batting_team: str  # 'SHARKS' or other team name
    runs: int = Field(..., ge=0, le=999, description="Runs scored in first innings")
    wickets: int = Field(..., ge=0, le=10, description="Wickets lost in first innings (0-10)")
    
    model_config = ConfigDict(from_attributes=True)


class SecondInningsScoreRequest(BaseModel):
    batting_team: str  # 'SHARKS' or other team name
    runs: int = Field(..., ge=0, le=999, description="Runs scored in second innings")
    wickets: int = Field(..., ge=0, le=10, description="Wickets lost in second innings (0-10)")
    
    model_config = ConfigDict(from_attributes=True)
```

---

### Step 1.3: Update Backend Endpoints (app/routes/schedule.py)

**Find the First Innings Endpoint - Update `update_first_innings_score()` Function:**

**Current Code Pattern:**
```python
@router.put("/matches/{match_id}/first-innings-score")
async def update_first_innings_score(
    match_id: int,
    request: FirstInningsScoreRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Update score based on batting team
    if request.batting_team == "SHARKS":
        match.team1_first_innings_score = request.score
    else:
        match.team2_first_innings_score = request.score
    
    db.commit()
    return {"success": True, "data": match}
```

**Replace With:**
```python
@router.put("/matches/{match_id}/first-innings-score")
async def update_first_innings_score(
    match_id: int,
    request: FirstInningsScoreRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.status != "live":
        raise HTTPException(status_code=400, detail="Match must be in 'live' status to record innings")
    
    # Validate wickets range
    if not (0 <= request.wickets <= 10):
        raise HTTPException(status_code=400, detail="Wickets must be between 0 and 10")
    
    # Validate runs range
    if not (0 <= request.runs <= 999):
        raise HTTPException(status_code=400, detail="Runs must be between 0 and 999")
    
    # Update score based on batting team
    if request.batting_team == "SHARKS":
        match.team1_first_innings_runs = request.runs
        match.team1_first_innings_wickets = request.wickets
        # Backward compatibility
        match.team1_first_innings_score = request.runs
    else:
        match.team2_first_innings_runs = request.runs
        match.team2_first_innings_wickets = request.wickets
        # Backward compatibility
        match.team2_first_innings_score = request.runs
    
    db.commit()
    db.refresh(match)
    return {
        "success": True,
        "data": {
            "id": match.id,
            "team1_first_innings_runs": match.team1_first_innings_runs,
            "team1_first_innings_wickets": match.team1_first_innings_wickets,
            "team2_first_innings_runs": match.team2_first_innings_runs,
            "team2_first_innings_wickets": match.team2_first_innings_wickets,
            "status": match.status
        }
    }
```

**Find and Update `update_second_innings_score()` Function:**

**Current Code Pattern:**
```python
@router.put("/matches/{match_id}/second-innings-score")
async def update_second_innings_score(
    match_id: int,
    request: SecondInningsScoreRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Update score based on batting team
    if request.batting_team == "SHARKS":
        match.team1_second_innings_score = request.score
    else:
        match.team2_second_innings_score = request.score
    
    db.commit()
    return {"success": True, "data": match}
```

**Replace With:**
```python
@router.put("/matches/{match_id}/second-innings-score")
async def update_second_innings_score(
    match_id: int,
    request: SecondInningsScoreRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.status != "live":
        raise HTTPException(status_code=400, detail="Match must be in 'live' status to record innings")
    
    # Validate wickets range
    if not (0 <= request.wickets <= 10):
        raise HTTPException(status_code=400, detail="Wickets must be between 0 and 10")
    
    # Validate runs range
    if not (0 <= request.runs <= 999):
        raise HTTPException(status_code=400, detail="Runs must be between 0 and 999")
    
    # Update score based on batting team
    if request.batting_team == "SHARKS":
        match.team1_second_innings_runs = request.runs
        match.team1_second_innings_wickets = request.wickets
        # Backward compatibility
        match.team1_second_innings_score = request.runs
    else:
        match.team2_second_innings_runs = request.runs
        match.team2_second_innings_wickets = request.wickets
        # Backward compatibility
        match.team2_second_innings_score = request.runs
    
    db.commit()
    db.refresh(match)
    return {
        "success": True,
        "data": {
            "id": match.id,
            "team1_second_innings_runs": match.team1_second_innings_runs,
            "team1_second_innings_wickets": match.team1_second_innings_wickets,
            "team2_second_innings_runs": match.team2_second_innings_runs,
            "team2_second_innings_wickets": match.team2_second_innings_wickets,
            "status": match.status
        }
    }
```

---

## PART 2: FRONTEND UPDATES

### Step 2.1: Update Service Functions (frontend/src/services/matchService.js)

**Find and Replace:**

**Current Code:**
```javascript
export const recordFirstInnings = async (matchId, battingTeam, score) => {
  const response = await fetch(`${API_BASE_URL}/schedule/matches/${matchId}/first-innings-score`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ batting_team: battingTeam, score })
  });
  return response.json();
};

export const recordSecondInnings = async (matchId, battingTeam, score) => {
  const response = await fetch(`${API_BASE_URL}/schedule/matches/${matchId}/second-innings-score`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ batting_team: battingTeam, score })
  });
  return response.json();
};
```

**Replace With:**
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

---

### Step 2.2: Update Score Form Component (frontend/src/components/ScoreForm.jsx)

**This is a COMPLETE REWRITE of ScoreForm.jsx:**

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

### Step 2.3: Update Match Card Component (frontend/src/components/MatchCard.jsx)

**Find and Replace the Score Display Section:**

**Current Code Pattern (Search for score display):**
```javascript
// Old display (shows single number)
<div className="text-lg font-bold">{match.team1_first_innings_score}</div>
```

**Replace Score Display With:**
```javascript
// New display (shows runs-wickets format)
<div className="text-lg font-bold">
  {match.team1_first_innings_runs !== null ? (
    <span>
      {match.team1_first_innings_runs}-{match.team1_first_innings_wickets ?? 0}
    </span>
  ) : (
    <span className="text-gray-400">-</span>
  )}
</div>
```

**Complete Updated MatchCard.jsx (if you need full component):**

```javascript
import React from 'react';
import { useNavigate } from 'react-router-dom';

const MatchCard = ({ match }) => {
  const navigate = useNavigate();
  const isLive = match.status === 'live';
  const isDone = match.status === 'done';

  // Helper function to format score with wickets
  const formatScore = (runs, wickets) => {
    if (runs === null || runs === undefined) {
      return '-';
    }
    const w = wickets ?? 0;
    return `${runs}-${w}`;
  };

  // Get team names
  const team1Name = match.team1?.team_name || 'Team 1';
  const team2Name = match.team2?.team_name || 'Team 2';

  return (
    <div
      onClick={() => navigate(`/matches/${match.id}`)}
      className={`cursor-pointer p-4 rounded-lg shadow-md hover:shadow-lg transition ${
        isLive ? 'border-2 border-red-500 bg-red-50' : 'bg-white'
      }`}
    >
      {/* Header with status */}
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-bold text-gray-800">{team1Name} vs {team2Name}</h3>
        {isLive && (
          <span className="px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full animate-pulse">
            LIVE
          </span>
        )}
        {isDone && (
          <span className="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded">
            COMPLETED
          </span>
        )}
      </div>

      {/* Match Time */}
      <p className="text-sm text-gray-600 mb-3">
        {match.scheduled_start_time ? (
          <span>
            {new Date(match.scheduled_start_time).toLocaleString()}
          </span>
        ) : (
          <span className="text-gray-400">Date & time TBD</span>
        )}
      </p>

      {/* Scores */}
      {(match.status === 'live' || match.status === 'done') && (
        <div className="bg-gray-50 p-3 rounded mb-3">
          {/* First Innings */}
          {(match.team1_first_innings_runs !== null || match.team2_first_innings_runs !== null) && (
            <div className="grid grid-cols-2 gap-4 mb-2">
              <div>
                <p className="text-xs font-semibold text-gray-600">1st Innings</p>
                <p className="text-sm text-gray-700">{team1Name}</p>
                <p className="text-lg font-bold">
                  {formatScore(match.team1_first_innings_runs, match.team1_first_innings_wickets)}
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold text-gray-600">vs</p>
                <p className="text-sm text-gray-700">{team2Name}</p>
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
                <p className="text-sm text-gray-700">{team1Name}</p>
                <p className="text-lg font-bold">
                  {formatScore(match.team1_second_innings_runs, match.team1_second_innings_wickets)}
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold text-gray-600">vs</p>
                <p className="text-sm text-gray-700">{team2Name}</p>
                <p className="text-lg font-bold">
                  {formatScore(match.team2_second_innings_runs, match.team2_second_innings_wickets)}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Result if match is done */}
      {isDone && match.winner_id && (
        <div className="bg-green-50 p-2 rounded text-sm">
          <p className="font-bold text-green-700">
            {match.winner?.team_name || 'Unknown Team'} Won
          </p>
          {match.margin && (
            <p className="text-green-600">
              by {match.margin} {match.margin_type || 'runs'}
            </p>
          )}
        </div>
      )}

      {/* View Details Button */}
      <button className="mt-3 w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold py-2 px-3 rounded transition">
        View Details →
      </button>
    </div>
  );
};

export default MatchCard;
```

---

### Step 2.4: Update Match Detail Modal Component (frontend/src/components/MatchDetailModal.jsx)

**Find Score Display Sections and Update:**

**Current Pattern:**
```javascript
// Old display
<p>First Innings: {match.team1_first_innings_score}</p>
```

**Replace With:**
```javascript
// New display
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

**Complete Updated Result Section (if displaying match result):**

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
            <span>{match.team1?.team_name}</span>
            <span className="font-bold">
              {match.team1_first_innings_runs}-{match.team1_first_innings_wickets ?? 0}
            </span>
          </div>
          <div className="flex justify-between">
            <span>{match.team2?.team_name}</span>
            <span className="font-bold">
              {match.team2_first_innings_runs}-{match.team2_first_innings_wickets ?? 0}
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
              <span>{match.team1?.team_name}</span>
              <span className="font-bold">
                {match.team1_second_innings_runs ?? '-'}-{match.team1_second_innings_wickets ?? 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span>{match.team2?.team_name}</span>
              <span className="font-bold">
                {match.team2_second_innings_runs ?? '-'}-{match.team2_second_innings_wickets ?? 0}
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

## PART 3: API ENDPOINT CHANGES SUMMARY

### Old API (Current)
```
PUT /api/schedule/matches/{id}/first-innings-score
Request:  { "batting_team": "SHARKS", "score": 165 }
Response: { "success": true, "data": {..., "team1_first_innings_score": 165, ...} }
```

### New API (After Update)
```
PUT /api/schedule/matches/{id}/first-innings-score
Request:  { "batting_team": "SHARKS", "runs": 165, "wickets": 8 }
Response: {
  "success": true,
  "data": {
    "id": 1,
    "team1_first_innings_runs": 165,
    "team1_first_innings_wickets": 8,
    "team2_first_innings_runs": null,
    "team2_first_innings_wickets": null,
    "status": "live"
  }
}
```

---

## PART 4: TESTING CHECKLIST

**Backend Tests:**
- [ ] Test wickets validation (0-10 range)
- [ ] Test runs validation (0-999 range)
- [ ] Test invalid runs (e.g., 1000) returns 400 error
- [ ] Test invalid wickets (e.g., 11) returns 400 error
- [ ] Test first innings endpoint stores runs and wickets correctly
- [ ] Test second innings endpoint stores runs and wickets correctly
- [ ] Test backward compatibility (old score field still populated)
- [ ] Run: `python -m pytest tests/test_endpoints.py -q`

**Frontend Tests:**
- [ ] Form displays runs and wickets inputs
- [ ] Form shows "Score Preview" with "runs-wickets" format
- [ ] Wickets dropdown shows 0-10 options
- [ ] Form validation prevents invalid runs (< 0 or > 999)
- [ ] Form validation prevents invalid wickets (< 0 or > 10)
- [ ] Form submission sends correct data to API
- [ ] Match card displays score as "165-8" format
- [ ] Match detail modal shows runs and wickets separately
- [ ] Error handling displays API error messages

---

## PART 5: QUICK REFERENCE - ALL CHANGES

### Files to Modify:

1. **models.py** - Add 8 new columns (runs/wickets for both innings, both teams)
2. **app/schemas_schedule.py** - Update FirstInningsScoreRequest and SecondInningsScoreRequest
3. **app/routes/schedule.py** - Update update_first_innings_score() and update_second_innings_score()
4. **frontend/src/services/matchService.js** - Update recordFirstInnings() and recordSecondInnings()
5. **frontend/src/components/ScoreForm.jsx** - Complete rewrite with dual inputs
6. **frontend/src/components/MatchCard.jsx** - Update score display format
7. **frontend/src/components/MatchDetailModal.jsx** - Update score display format

### Score Display Format Changes:

**Old:** Single integer (165)
**New:** Runs-Wickets format (165-8)

### Validation Rules:

- Runs: 0-999
- Wickets: 0-10
- Both fields required

---

## IMPLEMENTATION ORDER (RECOMMENDED)

1. ✅ Update `models.py` (add 8 new columns)
2. ✅ Update `app/schemas_schedule.py` (update request schemas)
3. ✅ Update `app/routes/schedule.py` (update endpoint logic)
4. ✅ Test backend endpoints with Postman/curl
5. ✅ Update `frontend/src/services/matchService.js` (update service functions)
6. ✅ Update `frontend/src/components/ScoreForm.jsx` (complete rewrite)
7. ✅ Update `frontend/src/components/MatchCard.jsx` (update display)
8. ✅ Update `frontend/src/components/MatchDetailModal.jsx` (update display)
9. ✅ Test frontend forms and display
10. ✅ Run full test suite (backend + frontend)
11. ✅ Deploy and verify

---

## ROLLBACK PLAN (If Issues Occur)

The legacy fields (`team1_first_innings_score`, etc.) are still populated during the update, so:
- Frontend can fall back to using the old fields if needed
- Gradually migrate frontend to use new fields
- Full backward compatibility maintained for at least 1 version

