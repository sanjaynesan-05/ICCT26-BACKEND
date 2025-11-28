# Frontend Update Prompt - Match Schedule API Integration

## Overview
The backend has been updated with comprehensive match details tracking and a new match score URL feature. This prompt provides all the information needed to update your frontend to integrate with these new endpoints and features.

---

## 🎯 What's New in the Backend

### 1. Complete Match Details Tracking
The API now supports:
- **Toss Information:** Winner and choice (bat/bowl)
- **Match Timing:** Scheduled start, actual start, and end times
- **Innings Scores:** First innings scores for both teams
- **Match Score URL:** External link to match scorecard (NEW)

### 2. New/Updated Endpoints

| Endpoint | Method | Purpose | Status Code |
|----------|--------|---------|------------|
| `/api/schedule/matches` | POST | Create match | 201 |
| `/api/schedule/matches` | GET | Get all matches | 200 |
| `/api/schedule/matches/{id}` | GET | Get single match | 200 |
| `/api/schedule/matches/{id}` | PUT | Full update | 200 |
| `/api/schedule/matches/{id}/status` | PUT | Update status | 200 |
| `/api/schedule/matches/{id}/toss` | PUT | Update toss | 200 |
| `/api/schedule/matches/{id}/timing` | PUT | Update timing | 200 |
| `/api/schedule/matches/{id}/scores` | PUT | Update scores | 200 |
| `/api/schedule/matches/{id}/score-url` | PUT | **Update scorecard URL (NEW)** | 200 |
| `/api/schedule/matches/{id}` | DELETE | Delete match | 204 |

---

## 📋 API Response Format

### Complete Match Object
```json
{
  "id": 1,
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "SHARKS",
  "team2": "Thadaladi",
  "status": "live",
  "toss_winner": "SHARKS",
  "toss_choice": "bat",
  "scheduled_start_time": "2025-11-28T10:00:00",
  "actual_start_time": "2025-11-28T10:15:00",
  "match_end_time": "2025-11-28T13:45:00",
  "team1_first_innings_score": 165,
  "team2_first_innings_score": 152,
  "match_score_url": "https://example.com/match/123/scorecard",
  "result": null,
  "created_at": "2025-11-28T13:31:38",
  "updated_at": "2025-11-28T14:35:22"
}
```

### Response Wrapper
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { /* match object or array */ }
}
```

---

## 🚀 Implementation Guide

### Step 1: Update State Management

#### React/Redux Example
```javascript
// state/matchSlice.js or similar
const initialState = {
  matches: [],
  currentMatch: null,
  loading: false,
  error: null
};

const matchSlice = createSlice({
  name: 'matches',
  initialState,
  reducers: {
    setMatches: (state, action) => {
      state.matches = action.payload;
    },
    setCurrentMatch: (state, action) => {
      state.currentMatch = action.payload;
    },
    updateMatchToss: (state, action) => {
      if (state.currentMatch) {
        state.currentMatch.toss_winner = action.payload.toss_winner;
        state.currentMatch.toss_choice = action.payload.toss_choice;
      }
    },
    updateMatchTiming: (state, action) => {
      if (state.currentMatch) {
        state.currentMatch.scheduled_start_time = action.payload.scheduled_start_time;
        state.currentMatch.actual_start_time = action.payload.actual_start_time;
        state.currentMatch.match_end_time = action.payload.match_end_time;
      }
    },
    updateMatchScores: (state, action) => {
      if (state.currentMatch) {
        state.currentMatch.team1_first_innings_score = action.payload.team1_first_innings_score;
        state.currentMatch.team2_first_innings_score = action.payload.team2_first_innings_score;
      }
    },
    updateMatchScoreUrl: (state, action) => {
      if (state.currentMatch) {
        state.currentMatch.match_score_url = action.payload.match_score_url;
      }
    }
  }
});
```

### Step 2: Create API Service Functions

```javascript
// services/matchService.js
const API_BASE = 'http://your-backend-url/api/schedule';

export const matchService = {
  // Create match
  createMatch: async (roundData) => {
    const response = await fetch(`${API_BASE}/matches`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(roundData)
    });
    return response.json();
  },

  // Get all matches
  getAllMatches: async (skip = 0, limit = 100) => {
    const response = await fetch(`${API_BASE}/matches?skip=${skip}&limit=${limit}`);
    return response.json();
  },

  // Get single match
  getMatch: async (matchId) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}`);
    return response.json();
  },

  // Update match status
  updateMatchStatus: async (matchId, status) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    return response.json();
  },

  // Update toss details
  updateToss: async (matchId, tossWinner, tossChoice) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}/toss`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        toss_winner: tossWinner,
        toss_choice: tossChoice
      })
    });
    return response.json();
  },

  // Update match timing
  updateTiming: async (matchId, scheduledStart, actualStart, endTime) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}/timing`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scheduled_start_time: scheduledStart,
        actual_start_time: actualStart,
        match_end_time: endTime
      })
    });
    return response.json();
  },

  // Update innings scores
  updateScores: async (matchId, team1Score, team2Score) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}/scores`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        team1_first_innings_score: team1Score,
        team2_first_innings_score: team2Score
      })
    });
    return response.json();
  },

  // Update match score URL (NEW)
  updateScoreUrl: async (matchId, scoreUrl) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}/score-url`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        match_score_url: scoreUrl
      })
    });
    return response.json();
  },

  // Delete match
  deleteMatch: async (matchId) => {
    const response = await fetch(`${API_BASE}/matches/${matchId}`, {
      method: 'DELETE'
    });
    return response.json();
  }
};
```

### Step 3: Create Custom Hooks

```javascript
// hooks/useMatches.js
import { useState } from 'react';
import { matchService } from '../services/matchService';

export const useMatches = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createMatch = async (data) => {
    setLoading(true);
    try {
      const result = await matchService.createMatch(data);
      setError(null);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateScoreUrl = async (matchId, scoreUrl) => {
    setLoading(true);
    try {
      const result = await matchService.updateScoreUrl(matchId, scoreUrl);
      setError(null);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    createMatch,
    updateScoreUrl,
    // ... other methods
  };
};
```

### Step 4: Create React Components

#### Match Details Component
```jsx
import React, { useState, useEffect } from 'react';
import { matchService } from '../services/matchService';

function MatchDetails({ matchId }) {
  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMatch();
  }, [matchId]);

  const fetchMatch = async () => {
    try {
      setLoading(true);
      const response = await matchService.getMatch(matchId);
      if (response.success) {
        setMatch(response.data);
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Failed to fetch match');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!match) return <div>No match found</div>;

  return (
    <div className="match-details">
      <h2>{match.team1} vs {match.team2}</h2>
      
      <div className="match-header">
        <p><strong>Round:</strong> {match.round}</p>
        <p><strong>Status:</strong> <span className={`status ${match.status}`}>{match.status}</span></p>
      </div>

      {match.toss_winner && (
        <div className="toss-section">
          <h3>Toss</h3>
          <p><strong>Winner:</strong> {match.toss_winner}</p>
          <p><strong>Choice:</strong> {match.toss_choice}</p>
        </div>
      )}

      {match.scheduled_start_time && (
        <div className="timing-section">
          <h3>Match Timing</h3>
          <p><strong>Scheduled:</strong> {new Date(match.scheduled_start_time).toLocaleString()}</p>
          <p><strong>Started:</strong> {new Date(match.actual_start_time).toLocaleString()}</p>
          <p><strong>Ended:</strong> {new Date(match.match_end_time).toLocaleString()}</p>
        </div>
      )}

      {match.team1_first_innings_score !== null && (
        <div className="scores-section">
          <h3>Scores</h3>
          <p><strong>{match.team1} 1st Innings:</strong> {match.team1_first_innings_score}</p>
          <p><strong>{match.team2} 1st Innings:</strong> {match.team2_first_innings_score}</p>
        </div>
      )}

      {match.match_score_url && (
        <div className="scorecard-section">
          <h3>Match Scorecard</h3>
          <a href={match.match_score_url} target="_blank" rel="noopener noreferrer" className="scorecard-link">
            View Full Scorecard →
          </a>
        </div>
      )}

      {match.result && (
        <div className="result-section">
          <h3>Match Result</h3>
          <p><strong>Winner:</strong> {match.result.winner}</p>
          <p><strong>Margin:</strong> {match.result.margin} {match.result.margin_type}</p>
        </div>
      )}
    </div>
  );
}

export default MatchDetails;
```

#### Update Match Score URL Component (NEW)
```jsx
import React, { useState } from 'react';
import { matchService } from '../services/matchService';

function UpdateScoreUrl({ matchId, onSuccess }) {
  const [scoreUrl, setScoreUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate URL format
      if (!scoreUrl.startsWith('http://') && !scoreUrl.startsWith('https://')) {
        setError('URL must start with http:// or https://');
        return;
      }

      const response = await matchService.updateScoreUrl(matchId, scoreUrl);
      
      if (response.success) {
        setSuccess(true);
        setScoreUrl('');
        setTimeout(() => setSuccess(false), 3000);
        
        if (onSuccess) {
          onSuccess(response.data);
        }
      } else {
        setError(response.message || 'Failed to update URL');
      }
    } catch (err) {
      setError('Error updating scorecard URL: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="update-score-url-form">
      <h3>Add Match Scorecard URL</h3>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="scoreUrl">Scorecard URL:</label>
          <input
            id="scoreUrl"
            type="text"
            placeholder="https://example.com/match/123/scorecard"
            value={scoreUrl}
            onChange={(e) => setScoreUrl(e.target.value)}
            disabled={loading}
            required
          />
          <small>Must be a valid HTTP or HTTPS URL</small>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">✓ Scorecard URL updated successfully</div>}

        <button type="submit" disabled={loading}>
          {loading ? 'Updating...' : 'Update Scorecard URL'}
        </button>
      </form>
    </div>
  );
}

export default UpdateScoreUrl;
```

#### Match Creation Form Component
```jsx
import React, { useState } from 'react';
import { matchService } from '../services/matchService';

function CreateMatchForm({ onSuccess }) {
  const [formData, setFormData] = useState({
    round: '',
    round_number: '',
    match_number: '',
    team1: '',
    team2: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await matchService.createMatch(formData);
      
      if (response.success) {
        // Reset form
        setFormData({
          round: '',
          round_number: '',
          match_number: '',
          team1: '',
          team2: ''
        });
        
        if (onSuccess) {
          onSuccess(response.data);
        }
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Failed to create match: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="create-match-form">
      <h2>Create New Match</h2>

      <div className="form-group">
        <label>Round:</label>
        <input
          type="text"
          name="round"
          placeholder="e.g., Round 1, Semi-Final"
          value={formData.round}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Round Number:</label>
          <input
            type="number"
            name="round_number"
            min="1"
            value={formData.round_number}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Match Number:</label>
          <input
            type="number"
            name="match_number"
            min="1"
            value={formData.match_number}
            onChange={handleChange}
            required
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Team 1:</label>
          <input
            type="text"
            name="team1"
            placeholder="Team name"
            value={formData.team1}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Team 2:</label>
          <input
            type="text"
            name="team2"
            placeholder="Team name"
            value={formData.team2}
            onChange={handleChange}
            required
          />
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Match'}
      </button>
    </form>
  );
}

export default CreateMatchForm;
```

### Step 5: Update Match List View

```jsx
import React, { useState, useEffect } from 'react';
import { matchService } from '../services/matchService';

function MatchesList() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    try {
      setLoading(true);
      const response = await matchService.getAllMatches();
      if (response.success) {
        setMatches(response.data);
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Failed to fetch matches');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading matches...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="matches-list">
      <h2>Cricket Matches</h2>
      
      {matches.length === 0 ? (
        <p>No matches scheduled</p>
      ) : (
        <table className="matches-table">
          <thead>
            <tr>
              <th>Round</th>
              <th>Match</th>
              <th>Team 1</th>
              <th>Team 2</th>
              <th>Status</th>
              <th>Score</th>
              <th>Scorecard</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {matches.map(match => (
              <tr key={match.id} className={`match-row ${match.status}`}>
                <td>{match.round}</td>
                <td>Match {match.match_number}</td>
                <td>{match.team1}</td>
                <td>{match.team2}</td>
                <td><span className={`status ${match.status}`}>{match.status}</span></td>
                <td>
                  {match.team1_first_innings_score !== null ? (
                    `${match.team1_first_innings_score} - ${match.team2_first_innings_score}`
                  ) : (
                    '-'
                  )}
                </td>
                <td>
                  {match.match_score_url ? (
                    <a href={match.match_score_url} target="_blank" rel="noopener noreferrer">
                      View
                    </a>
                  ) : (
                    '-'
                  )}
                </td>
                <td>
                  <button onClick={() => viewMatch(match.id)}>Details</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default MatchesList;
```

---

## 🔐 Input Validation

### URL Validation
```javascript
function isValidUrl(url) {
  try {
    const validUrl = new URL(url);
    return validUrl.protocol === 'http:' || validUrl.protocol === 'https:';
  } catch (_) {
    return false;
  }
}

// Usage
if (!isValidUrl(scoreUrl)) {
  setError('Please enter a valid HTTP or HTTPS URL');
}
```

### Toss Choice Validation
```javascript
const validTossChoices = ['bat', 'bowl'];
if (!validTossChoices.includes(tossChoice.toLowerCase())) {
  setError('Toss choice must be either "bat" or "bowl"');
}
```

### Match Status Validation
```javascript
const validStatuses = ['scheduled', 'live', 'completed'];
if (!validStatuses.includes(status)) {
  setError('Invalid match status');
}
```

---

## 💾 CSS Styling (Optional Reference)

```css
/* Match details styling */
.match-details {
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 20px;
}

.match-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.toss-section,
.timing-section,
.scores-section,
.scorecard-section,
.result-section {
  margin: 15px 0;
  padding: 15px;
  background-color: #f9f9f9;
  border-left: 4px solid #2196F3;
  border-radius: 4px;
}

.status {
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.85em;
}

.status.scheduled {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status.live {
  background-color: #fce4ec;
  color: #c2185b;
  animation: pulse 1.5s infinite;
}

.status.completed {
  background-color: #e8f5e9;
  color: #388e3c;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.scorecard-link {
  display: inline-block;
  padding: 10px 20px;
  background-color: #2196F3;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.scorecard-link:hover {
  background-color: #1976d2;
}

/* Form styling */
.update-score-url-form {
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1em;
}

.form-group input:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 5px rgba(33, 150, 243, 0.3);
}

.form-group small {
  display: block;
  margin-top: 5px;
  color: #999;
  font-size: 0.85em;
}

.error-message {
  padding: 10px;
  margin-bottom: 15px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  border-left: 4px solid #c62828;
}

.success-message {
  padding: 10px;
  margin-bottom: 15px;
  background-color: #e8f5e9;
  color: #388e3c;
  border-radius: 4px;
  border-left: 4px solid #388e3c;
}

button {
  padding: 10px 20px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #1976d2;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
```

---

## 🧪 Testing Checklist

- [ ] Create a new match (verify initial null values)
- [ ] Update match status to 'live'
- [ ] Update toss details (select team and choice)
- [ ] Update match timing (set all 3 timestamps)
- [ ] Update innings scores (enter scores for both teams)
- [ ] **Update match score URL (NEW)** - enter valid HTTPS link
- [ ] Test URL validation - try invalid URL and verify error
- [ ] Retrieve match details - verify all fields including scorecard URL
- [ ] List all matches - verify scorecard URL appears in list
- [ ] Update scorecard URL again - verify persistence
- [ ] Display scorecard link in UI - verify clickable and opens in new tab
- [ ] Test error handling - invalid match ID returns 404
- [ ] Test error handling - server errors handled gracefully

---

## 🔗 API Endpoints Quick Reference

### Base URL
```
http://your-backend-url/api/schedule
```

### GET Endpoints
```
GET /matches                    # Get all matches
GET /matches/{id}               # Get single match
```

### POST Endpoints
```
POST /matches                   # Create new match
```

### PUT Endpoints
```
PUT /matches/{id}               # Full match update
PUT /matches/{id}/status        # Update status
PUT /matches/{id}/toss          # Update toss
PUT /matches/{id}/timing        # Update timing
PUT /matches/{id}/scores        # Update scores
PUT /matches/{id}/score-url     # Update scorecard URL (NEW)
```

### DELETE Endpoints
```
DELETE /matches/{id}            # Delete match
```

---

## 📦 Dependencies

### Required Libraries
```
react                ^18.0.0    # UI framework
axios or fetch       (built-in)  # HTTP client
react-router-dom     ^6.0.0    # Routing (if using)
react-query          ^3.0.0    # Optional: for state management
```

### Install Commands
```bash
npm install react@latest
npm install axios
npm install react-router-dom@latest
```

---

## 🚀 Deployment Steps

1. **Update API Base URL**
   - Replace `http://your-backend-url` with actual backend URL
   - Example: `http://tournament.example.com/api`

2. **Test All Endpoints**
   - Run `test_match_score_url.py` on backend
   - Verify all 10 scenarios pass

3. **Deploy Frontend**
   - Build: `npm run build`
   - Test in staging environment
   - Deploy to production

4. **Verify Integration**
   - Create test match
   - Update all fields
   - Verify data persists
   - Verify UI displays correctly

---

## 📞 Support

**Backend Documentation:** See backend guides in `MATCH_SCORE_URL_API_REFERENCE.md`

**API Response Examples:** Check `test_match_score_url.py` for real examples

**Common Issues:**
- **CORS Errors:** Ensure backend allows frontend domain
- **404 Errors:** Verify match ID exists
- **422 Errors:** Check request body format and URL validation
- **Network Errors:** Verify backend server is running

---

## 🎯 Priority Implementation Order

1. **Phase 1 (Essential):**
   - Match list view
   - Match details view
   - Create match form

2. **Phase 2 (Core Features):**
   - Update match status
   - Update toss details
   - Update match timing
   - Update innings scores

3. **Phase 3 (New Feature):**
   - **Update match score URL (NEW)**
   - Display scorecard link
   - Link opens in new tab

4. **Phase 4 (Polish):**
   - Error handling
   - Loading states
   - Success messages
   - Responsive design

---

## 🔄 State Flow Diagram

```
User Action
    ↓
Frontend Component
    ↓
API Service Function
    ↓
HTTP Request to Backend
    ↓
Backend API Endpoint
    ↓
Database Update
    ↓
Response with Updated Match
    ↓
Frontend State Update
    ↓
UI Re-render with New Data
```

---

## ✅ Final Checklist

- [ ] Backend running and accessible
- [ ] API endpoints tested with Postman/curl
- [ ] Frontend environment configured
- [ ] API base URL updated in code
- [ ] Service functions created
- [ ] Components created and integrated
- [ ] Input validation implemented
- [ ] Error handling implemented
- [ ] Styling applied
- [ ] All features tested locally
- [ ] Unit tests written (optional)
- [ ] Ready for deployment

---

**Last Updated:** November 28, 2025  
**Backend Status:** ✅ Production Ready  
**Frontend Ready:** ✅ Use this prompt to integrate
