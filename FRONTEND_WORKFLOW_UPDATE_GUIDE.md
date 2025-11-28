# Frontend Integration Guide - 4-Stage Match Workflow

Complete guide to integrate the new 4-stage match workflow endpoints in your frontend.

---

## 📌 Quick Overview

The backend now supports a **4-stage match workflow**:
1. **Stage 1:** Create match (status: `scheduled`)
2. **Stage 2:** Start match (status: `live`) - Add toss & scorecard URL
3. **Stage 3A:** Record 1st innings score (status: `in-progress`)
4. **Stage 3B:** Record 2nd innings score (status: remains `in-progress`)
5. **Stage 4:** Finish match (status: `completed`) - Add winner & margin

---

## 🔄 New Workflow Endpoints

### Stage 1: Create Match
```
POST /api/schedule/matches
```
**Request:**
```json
{
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "SHARKS",
  "team2": "Thadaladi"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Match created successfully!",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "SHARKS",
    "team2": "Thadaladi",
    "status": "scheduled",
    "toss_winner": null,
    "toss_choice": null,
    "scheduled_start_time": null,
    "actual_start_time": null,
    "match_end_time": null,
    "team1_first_innings_score": null,
    "team2_first_innings_score": null,
    "match_score_url": null,
    "result": null,
    "created_at": "2025-11-28T10:00:00",
    "updated_at": "2025-11-28T10:00:00"
  }
}
```

---

### Stage 2: Start Match
```
PUT /api/schedule/matches/{match_id}/start
```

Transitions: `scheduled` → `live`

**Request:**
```json
{
  "toss_winner": "SHARKS",
  "toss_choice": "bat",
  "match_score_url": "https://example.com/match/123/scorecard",
  "actual_start_time": "2025-11-28T10:15:00"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Match started successfully. First innings has begun!",
  "data": {
    "id": 1,
    "status": "live",
    "toss_winner": "SHARKS",
    "toss_choice": "bat",
    "match_score_url": "https://example.com/match/123/scorecard",
    "actual_start_time": "2025-11-28T10:15:00",
    ...
  }
}
```

**Error Cases:**
- Status must be `scheduled`: Returns 400
- Toss winner must match team1 or team2: Returns 400
- Invalid URL format: Returns 422

---

### Stage 3A: Record 1st Innings Score
```
PUT /api/schedule/matches/{match_id}/first-innings-score
```

Transitions: `live` → `in-progress`

**Request:**
```json
{
  "batting_team": "SHARKS",
  "score": 165
}
```

**Response:**
```json
{
  "success": true,
  "message": "First innings score recorded successfully!",
  "data": {
    "id": 1,
    "status": "in-progress",
    "team1_first_innings_score": 165,
    ...
  }
}
```

**Error Cases:**
- Status must be `live` or `in-progress`: Returns 400
- Batting team invalid: Returns 400
- Score not in range 1-999: Returns 422

---

### Stage 3B: Record 2nd Innings Score
```
PUT /api/schedule/matches/{match_id}/second-innings-score
```

Transitions: `in-progress` → `in-progress` (no status change)

**Request:**
```json
{
  "batting_team": "Thadaladi",
  "score": 152
}
```

**Response:**
```json
{
  "success": true,
  "message": "Second innings score recorded successfully!",
  "data": {
    "id": 1,
    "status": "in-progress",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": 152,
    ...
  }
}
```

**Error Cases:**
- Status must be `in-progress`: Returns 400
- 1st innings score must exist: Returns 400
- Batting team invalid: Returns 400

---

### Stage 4: Finish Match
```
PUT /api/schedule/matches/{match_id}/finish
```

Transitions: `in-progress` → `completed`

**Request:**
```json
{
  "winner": "SHARKS",
  "margin": 13,
  "margin_type": "runs",
  "match_end_time": "2025-11-28T13:45:00"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Match completed successfully!",
  "data": {
    "id": 1,
    "status": "completed",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": 152,
    "result": {
      "winner": "SHARKS",
      "margin": 13,
      "margin_type": "runs",
      "won_by_batting_first": true
    },
    ...
  }
}
```

**Error Cases:**
- Status must be `in-progress`: Returns 400
- Both innings scores required: Returns 400
- Winner must match team1 or team2: Returns 400
- Margin type must be `runs` or `wickets`: Returns 422
- If `wickets`, margin cannot exceed 10: Returns 422

---

## 💻 Frontend Implementation

### 1. Service Functions

```javascript
// services/matchWorkflowService.js

const API_BASE = 'http://your-backend-url/api/schedule';

export const workflowService = {
  // Stage 1: Create Match
  createMatch: async (round, roundNumber, matchNumber, team1, team2) => {
    const response = await fetch(`${API_BASE}/matches`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        round,
        round_number: roundNumber,
        match_number: matchNumber,
        team1,
        team2
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to create match');
    return data.data;
  },

  // Stage 2: Start Match
  startMatch: async (matchId, tossWinner, tossChoice, scoreUrl, actualStartTime) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}/start`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        toss_winner: tossWinner,
        toss_choice: tossChoice,
        match_score_url: scoreUrl,
        actual_start_time: actualStartTime.toISOString()
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to start match');
    return data.data;
  },

  // Stage 3A: Record 1st Innings
  recordFirstInnings: async (matchId, battingTeam, score) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}/first-innings-score`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        batting_team: battingTeam,
        score: parseInt(score)
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to record 1st innings');
    return data.data;
  },

  // Stage 3B: Record 2nd Innings
  recordSecondInnings: async (matchId, battingTeam, score) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}/second-innings-score`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        batting_team: battingTeam,
        score: parseInt(score)
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to record 2nd innings');
    return data.data;
  },

  // Stage 4: Finish Match
  finishMatch: async (matchId, winner, margin, marginType, matchEndTime) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}/finish`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        winner,
        margin: parseInt(margin),
        margin_type: marginType,
        match_end_time: matchEndTime.toISOString()
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to finish match');
    return data.data;
  }
};
```

---

### 2. React Component Example

```jsx
// components/MatchWorkflow.jsx
import React, { useState } from 'react';
import { workflowService } from '../services/matchWorkflowService';

export default function MatchWorkflow() {
  const [currentStage, setCurrentStage] = useState('create'); // create, start, score, finish
  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Stage 1: Create
  const handleCreateMatch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData(e.target);
      const newMatch = await workflowService.createMatch(
        formData.get('round'),
        parseInt(formData.get('round_number')),
        parseInt(formData.get('match_number')),
        formData.get('team1'),
        formData.get('team2')
      );
      setMatch(newMatch);
      setCurrentStage('start');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Stage 2: Start
  const handleStartMatch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData(e.target);
      const updated = await workflowService.startMatch(
        match.id,
        formData.get('toss_winner'),
        formData.get('toss_choice'),
        formData.get('score_url'),
        new Date(formData.get('actual_start_time'))
      );
      setMatch(updated);
      setCurrentStage('score');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Stage 3A: 1st Innings
  const handleFirstInnings = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData(e.target);
      const updated = await workflowService.recordFirstInnings(
        match.id,
        formData.get('batting_team'),
        formData.get('score')
      );
      setMatch(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Stage 3B: 2nd Innings
  const handleSecondInnings = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData(e.target);
      const updated = await workflowService.recordSecondInnings(
        match.id,
        formData.get('batting_team'),
        formData.get('score')
      );
      setMatch(updated);
      setCurrentStage('finish');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Stage 4: Finish
  const handleFinishMatch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData(e.target);
      const updated = await workflowService.finishMatch(
        match.id,
        formData.get('winner'),
        formData.get('margin'),
        formData.get('margin_type'),
        new Date(formData.get('match_end_time'))
      );
      setMatch(updated);
      alert('Match completed!');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="match-workflow">
      {error && <div className="error-alert">{error}</div>}

      {currentStage === 'create' && (
        <form onSubmit={handleCreateMatch}>
          <h2>Stage 1: Create Match</h2>
          <input type="text" name="round" placeholder="Round (e.g., Round 1)" required />
          <input type="number" name="round_number" placeholder="Round #" required />
          <input type="number" name="match_number" placeholder="Match #" required />
          <input type="text" name="team1" placeholder="Team 1" required />
          <input type="text" name="team2" placeholder="Team 2" required />
          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Match'}
          </button>
        </form>
      )}

      {currentStage === 'start' && match && (
        <form onSubmit={handleStartMatch}>
          <h2>Stage 2: Start Match</h2>
          <p>Match {match.match_number}: {match.team1} vs {match.team2}</p>
          <select name="toss_winner" required>
            <option value="">Select Toss Winner</option>
            <option value={match.team1}>{match.team1}</option>
            <option value={match.team2}>{match.team2}</option>
          </select>
          <select name="toss_choice" required>
            <option value="">Toss Choice</option>
            <option value="bat">Bat</option>
            <option value="bowl">Bowl</option>
          </select>
          <input type="url" name="score_url" placeholder="Scorecard URL" required />
          <input type="datetime-local" name="actual_start_time" required />
          <button type="submit" disabled={loading}>
            {loading ? 'Starting...' : 'Start Match'}
          </button>
        </form>
      )}

      {currentStage === 'score' && match && (
        <>
          {!match.team1_first_innings_score ? (
            <form onSubmit={handleFirstInnings}>
              <h2>Stage 3A: Record 1st Innings</h2>
              <select name="batting_team" required>
                <option value="">Select Batting Team</option>
                <option value={match.team1}>{match.team1}</option>
                <option value={match.team2}>{match.team2}</option>
              </select>
              <input type="number" name="score" placeholder="Score" min="1" max="999" required />
              <button type="submit" disabled={loading}>
                {loading ? 'Recording...' : 'Record 1st Innings'}
              </button>
            </form>
          ) : !match.team2_first_innings_score ? (
            <form onSubmit={handleSecondInnings}>
              <h2>Stage 3B: Record 2nd Innings</h2>
              <select name="batting_team" required>
                <option value="">Select Batting Team</option>
                <option value={match.team1}>{match.team1}</option>
                <option value={match.team2}>{match.team2}</option>
              </select>
              <input type="number" name="score" placeholder="Score" min="1" max="999" required />
              <button type="submit" disabled={loading}>
                {loading ? 'Recording...' : 'Record 2nd Innings'}
              </button>
            </form>
          ) : null}
        </>
      )}

      {currentStage === 'finish' && match && match.team1_first_innings_score && (
        <form onSubmit={handleFinishMatch}>
          <h2>Stage 4: Finish Match</h2>
          <p>Scores: {match.team1} {match.team1_first_innings_score} vs {match.team2} {match.team2_first_innings_score}</p>
          <select name="winner" required>
            <option value="">Select Winner</option>
            <option value={match.team1}>{match.team1}</option>
            <option value={match.team2}>{match.team2}</option>
          </select>
          <input type="number" name="margin" placeholder="Margin" min="1" max="999" required />
          <select name="margin_type" required>
            <option value="">Margin Type</option>
            <option value="runs">Runs</option>
            <option value="wickets">Wickets</option>
          </select>
          <input type="datetime-local" name="match_end_time" required />
          <button type="submit" disabled={loading}>
            {loading ? 'Finishing...' : 'Finish Match'}
          </button>
        </form>
      )}

      {match && (
        <div className="match-details">
          <h3>Match Status: {match.status}</h3>
          <p>Round: {match.round}</p>
          <p>Match: {match.match_number}</p>
          <p>Status: {match.status}</p>
          {match.result && (
            <div>
              <h4>Result</h4>
              <p>Winner: {match.result.winner} by {match.result.margin} {match.result.margin_type}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

### 3. Display Match Lists by Status

```jsx
// components/MatchSchedule.jsx
import React, { useState, useEffect } from 'react';

export default function MatchSchedule() {
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    const response = await fetch('http://your-backend-url/api/schedule/matches');
    const data = await response.json();
    setMatches(data.data);
  };

  const scheduledMatches = matches.filter(m => m.status === 'scheduled');
  const liveMatches = matches.filter(m => m.status === 'live');
  const inProgressMatches = matches.filter(m => m.status === 'in-progress');
  const completedMatches = matches.filter(m => m.status === 'completed');

  return (
    <div className="schedule-container">
      {/* Scheduled/Upcoming Section */}
      <section className="section-scheduled">
        <h2>📅 Upcoming Matches</h2>
        {scheduledMatches.map(match => (
          <div key={match.id} className="match-card">
            <h3>{match.team1} vs {match.team2}</h3>
            <p>Round {match.round_number}, Match {match.match_number}</p>
            <button>Start Match</button>
          </div>
        ))}
      </section>

      {/* Live Section */}
      <section className="section-live">
        <h2>🔴 Live Now</h2>
        {liveMatches.map(match => (
          <div key={match.id} className="match-card live">
            <h3>{match.team1} vs {match.team2}</h3>
            <p>Toss: {match.toss_winner} won, chose to {match.toss_choice}</p>
            <p>Scorecard: <a href={match.match_score_url} target="_blank">View</a></p>
            <button>Record 1st Innings</button>
          </div>
        ))}
      </section>

      {/* In Progress Section */}
      <section className="section-progress">
        <h2>⚙️ In Progress</h2>
        {inProgressMatches.map(match => (
          <div key={match.id} className="match-card">
            <h3>{match.team1} vs {match.team2}</h3>
            <p>{match.team1}: {match.team1_first_innings_score} runs</p>
            <p>{match.team2}: {match.team2_first_innings_score} runs</p>
            <button>Finish Match</button>
          </div>
        ))}
      </section>

      {/* Completed Section */}
      <section className="section-completed">
        <h2>✅ Completed</h2>
        {completedMatches.map(match => (
          <div key={match.id} className="match-card completed">
            <h3>{match.team1} vs {match.team2}</h3>
            <p>{match.team1}: {match.team1_first_innings_score} runs</p>
            <p>{match.team2}: {match.team2_first_innings_score} runs</p>
            {match.result && (
              <p className="result">
                <strong>Winner:</strong> {match.result.winner} by {match.result.margin} {match.result.margin_type}
              </p>
            )}
            <a href={match.match_score_url} target="_blank">View Scorecard</a>
          </div>
        ))}
      </section>
    </div>
  );
}
```

---

## ✅ Validation Rules

| Field | Rules |
|-------|-------|
| `toss_choice` | Must be `bat` or `bowl` |
| `match_score_url` | Must start with `http://` or `https://` |
| `score` | Must be between 1-999 |
| `margin` | Runs: 1-999, Wickets: 1-10 |
| `margin_type` | Must be `runs` or `wickets` |
| Status transitions | `scheduled` → `live` → `in-progress` → `completed` |

---

## 🐛 Error Handling

All errors return standard format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Errors:**
- 400: Business logic error (wrong status, team mismatch, etc.)
- 422: Validation error (invalid data format, out of range, etc.)
- 404: Match not found
- 500: Server error

---

## 📝 Testing the Endpoints

### Using cURL:

```bash
# Create match
curl -X POST http://localhost:8000/api/schedule/matches \
  -H "Content-Type: application/json" \
  -d '{
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "SHARKS",
    "team2": "Thadaladi"
  }'

# Start match
curl -X PUT http://localhost:8000/api/schedule/matches/1/start \
  -H "Content-Type: application/json" \
  -d '{
    "toss_winner": "SHARKS",
    "toss_choice": "bat",
    "match_score_url": "https://example.com/scorecard",
    "actual_start_time": "2025-11-28T10:15:00"
  }'

# Record 1st innings
curl -X PUT http://localhost:8000/api/schedule/matches/1/first-innings-score \
  -H "Content-Type: application/json" \
  -d '{
    "batting_team": "SHARKS",
    "score": 165
  }'

# Record 2nd innings
curl -X PUT http://localhost:8000/api/schedule/matches/1/second-innings-score \
  -H "Content-Type: application/json" \
  -d '{
    "batting_team": "Thadaladi",
    "score": 152
  }'

# Finish match
curl -X PUT http://localhost:8000/api/schedule/matches/1/finish \
  -H "Content-Type: application/json" \
  -d '{
    "winner": "SHARKS",
    "margin": 13,
    "margin_type": "runs",
    "match_end_time": "2025-11-28T13:45:00"
  }'
```

---

## 🎯 Summary Checklist

- [ ] Understand the 4-stage workflow
- [ ] Create API service functions
- [ ] Build forms for each stage
- [ ] Implement state management
- [ ] Display matches by status sections
- [ ] Add error handling
- [ ] Test all endpoints
- [ ] Deploy to production

---

**Backend Status:** ✅ Ready  
**All 10 tests passing:** ✅ Yes  
**Documentation:** ✅ Complete  
**Ready for frontend implementation:** ✅ Yes
