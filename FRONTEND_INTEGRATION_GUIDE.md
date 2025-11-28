# Frontend Integration Guide - Match Schedule API Updates

## Overview
The backend has been updated with comprehensive match details tracking. This guide provides all the necessary information to update your frontend to work with the new API endpoints and response formats.

---

## API Base URL
```
http://your-backend-url/api/schedule
```

---

## Endpoints Summary

### 1. Create Match
**Endpoint:** `POST /matches`

**Request Body:**
```json
{
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "SHARKS",
  "team2": "Thadaladi"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Match created successfully",
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
    "result": null,
    "created_at": "2025-11-28T13:31:38.738333",
    "updated_at": "2025-11-28T13:31:38.738333"
  }
}
```

---

### 2. Get All Matches
**Endpoint:** `GET /matches`

**Query Parameters:** (optional)
- `skip`: Number of matches to skip (default: 0)
- `limit`: Maximum number of matches to return (default: 100)

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
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
      "result": null,
      "created_at": "2025-11-28T13:31:38.738333",
      "updated_at": "2025-11-28T13:31:38.738333"
    }
  ]
}
```

---

### 3. Get Single Match (NEW)
**Endpoint:** `GET /matches/{match_id}`

**Path Parameters:**
- `match_id`: The ID of the match to fetch

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Match fetched successfully",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "SHARKS",
    "team2": "Thadaladi",
    "status": "live",
    "toss_winner": "SHARKS",
    "toss_choice": "bat",
    "scheduled_start_time": "2025-11-28T13:31:55.321528",
    "actual_start_time": "2025-11-28T13:46:55.321528",
    "match_end_time": "2025-11-28T17:01:55.321528",
    "team1_first_innings_score": 165,
    "team2_first_innings_score": 152,
    "result": null,
    "created_at": "2025-11-28T13:31:38.738333",
    "updated_at": "2025-11-28T13:32:04.450496"
  }
}
```

---

### 4. Update Match Status
**Endpoint:** `PUT /matches/{match_id}/status`

**Request Body:**
```json
{
  "status": "live"
}
```

**Valid Status Values:** `scheduled`, `live`, `completed`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Match status updated successfully",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "SHARKS",
    "team2": "Thadaladi",
    "status": "live",
    "toss_winner": null,
    "toss_choice": null,
    "scheduled_start_time": null,
    "actual_start_time": null,
    "match_end_time": null,
    "team1_first_innings_score": null,
    "team2_first_innings_score": null,
    "result": null,
    "created_at": "2025-11-28T13:31:38.738333",
    "updated_at": "2025-11-28T13:31:38.738333"
  }
}
```

---

### 5. Update Toss Details (NEW)
**Endpoint:** `PUT /matches/{match_id}/toss`

**Request Body:**
```json
{
  "toss_winner": "SHARKS",
  "toss_choice": "bat"
}
```

**Field Details:**
- `toss_winner`: Team name that won the toss (must match team1 or team2)
- `toss_choice`: Either "bat" or "bowl"

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Toss details updated successfully",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "SHARKS",
    "team2": "Thadaladi",
    "status": "live",
    "toss_winner": "SHARKS",
    "toss_choice": "bat",
    "scheduled_start_time": null,
    "actual_start_time": null,
    "match_end_time": null,
    "team1_first_innings_score": null,
    "team2_first_innings_score": null,
    "result": null,
    "created_at": "2025-11-28T13:31:38.738333",
    "updated_at": "2025-11-28T13:31:55.321528"
  }
}
```

---

### 6. Update Match Timing (NEW)
**Endpoint:** `PUT /matches/{match_id}/timing`

**Request Body:**
```json
{
  "scheduled_start_time": "2025-11-28T10:00:00",
  "actual_start_time": "2025-11-28T10:15:00",
  "match_end_time": "2025-11-28T13:45:00"
}
```

**Field Details:**
- `scheduled_start_time`: When the match is scheduled to start (ISO 8601 format)
- `actual_start_time`: When the match actually started (ISO 8601 format)
- `match_end_time`: When the match ended (ISO 8601 format)
- All fields are optional

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Match timing updated successfully",
  "data": {
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
    "team1_first_innings_score": null,
    "team2_first_innings_score": null,
    "result": null,
    "created_at": "2025-11-28T13:31:38.738333",
    "updated_at": "2025-11-28T13:32:04.450496"
  }
}
```

---

### 7. Update Innings Scores (NEW - FIRST INNINGS ONLY)
**Endpoint:** `PUT /matches/{match_id}/scores`

**Request Body:**
```json
{
  "team1_first_innings_score": 165,
  "team2_first_innings_score": 152
}
```

**Field Details:**
- `team1_first_innings_score`: Team 1 first innings score (positive integer)
- `team2_first_innings_score`: Team 2 first innings score (positive integer)
- Both fields are optional

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Innings scores updated successfully",
  "data": {
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
    "result": null,
    "created_at": "2025-11-28T13:31:38.738333",
    "updated_at": "2025-11-28T13:32:04.450496"
  }
}
```

---

### 8. Update Match Score URL (NEW)
**Endpoint:** `PUT /matches/{match_id}/score-url`

**Request Body:**
```json
{
  "match_score_url": "https://example.com/matches/123/scorecard"
}
```

**Field Details:**
- `match_score_url`: URL to the match score/scorecard (must be valid HTTP or HTTPS URL)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Match score URL updated successfully",
  "data": {
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
    "match_score_url": "https://example.com/matches/123/scorecard",
    "result": null,
    "created_at": "2025-11-28T13:31:38.738333",
    "updated_at": "2025-11-28T13:32:04.450496"
  }
}
```

---

## Response Data Model

All API responses return a `Match` object with the following fields:

```typescript
interface Match {
  // Identifiers
  id: number;
  
  // Round Information
  round: string;              // e.g., "Round 1", "Semi-Final"
  round_number: number;       // Numeric round (1, 2, 3, etc.)
  match_number: number;       // Match number within the round
  
  // Teams
  team1: string;              // Team 1 name
  team2: string;              // Team 2 name
  
  // Match Status
  status: "scheduled" | "live" | "completed";
  
  // Toss Information
  toss_winner: string | null; // Team that won the toss
  toss_choice: "bat" | "bowl" | null; // What toss winner chose
  
  // Timing
  scheduled_start_time: string | null;  // ISO 8601 datetime
  actual_start_time: string | null;     // ISO 8601 datetime
  match_end_time: string | null;        // ISO 8601 datetime
  
  // Scores (First Innings Only)
  team1_first_innings_score: number | null;
  team2_first_innings_score: number | null;
  
  // Match Score URL
  match_score_url: string | null;  // URL to external match scorecard
  
  // Result (Only populated when match is completed)
  result: {
    winner: string;                    // Winning team name
    margin: number;                    // Margin of victory
    margin_type: "runs" | "wickets";  // Type of margin
    won_by_batting_first: boolean;    // True if batting first team won
  } | null;
  
  // Timestamps
  created_at: string;  // ISO 8601 datetime
  updated_at: string;  // ISO 8601 datetime
}
```

---

## Frontend Implementation Examples

### JavaScript/TypeScript - Fetch API

#### Get Single Match
```javascript
async function getMatch(matchId) {
  try {
    const response = await fetch(`/api/schedule/matches/${matchId}`);
    const result = await response.json();
    
    if (result.success) {
      const match = result.data;
      console.log(`Match: ${match.team1} vs ${match.team2}`);
      console.log(`Status: ${match.status}`);
      console.log(`Toss: ${match.toss_winner} chose to ${match.toss_choice}`);
      console.log(`Scores: ${match.team1_first_innings_score} - ${match.team2_first_innings_score}`);
    }
  } catch (error) {
    console.error('Error fetching match:', error);
  }
}
```

#### Update Toss Details
```javascript
async function updateToss(matchId, tossWinner, tossChoice) {
  try {
    const response = await fetch(`/api/schedule/matches/${matchId}/toss`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        toss_winner: tossWinner,
        toss_choice: tossChoice
      })
    });
    
    const result = await response.json();
    if (result.success) {
      console.log('Toss updated successfully');
      return result.data;
    }
  } catch (error) {
    console.error('Error updating toss:', error);
  }
}
```

#### Update Match Timing
```javascript
async function updateTiming(matchId, scheduledStart, actualStart, endTime) {
  try {
    const response = await fetch(`/api/schedule/matches/${matchId}/timing`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        scheduled_start_time: scheduledStart,
        actual_start_time: actualStart,
        match_end_time: endTime
      })
    });
    
    const result = await response.json();
    if (result.success) {
      console.log('Timing updated successfully');
      return result.data;
    }
  } catch (error) {
    console.error('Error updating timing:', error);
  }
}
```

#### Update Innings Scores
```javascript
async function updateScores(matchId, team1Score, team2Score) {
  try {
    const response = await fetch(`/api/schedule/matches/${matchId}/scores`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        team1_first_innings_score: team1Score,
        team2_first_innings_score: team2Score
      })
    });
    
    const result = await response.json();
    if (result.success) {
      console.log('Scores updated successfully');
      return result.data;
    }
  } catch (error) {
    console.error('Error updating scores:', error);
  }
}
```

#### Update Match Score URL (NEW)
```javascript
async function updateMatchScoreUrl(matchId, scoreUrl) {
  try {
    const response = await fetch(`/api/schedule/matches/${matchId}/score-url`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        match_score_url: scoreUrl
      })
    });
    
    const result = await response.json();
    if (result.success) {
      console.log('Match score URL updated successfully');
      return result.data;
    }
  } catch (error) {
    console.error('Error updating match score URL:', error);
  }
}
```

### React Example Component

```javascript
import React, { useState, useEffect } from 'react';

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
      const response = await fetch(`/api/schedule/matches/${matchId}`);
      const result = await response.json();
      
      if (result.success) {
        setMatch(result.data);
      } else {
        setError('Failed to fetch match');
      }
    } catch (err) {
      setError('Error fetching match: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateScores = async (team1Score, team2Score) => {
    try {
      const response = await fetch(`/api/schedule/matches/${matchId}/scores`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team1_first_innings_score: team1Score,
          team2_first_innings_score: team2Score
        })
      });
      
      const result = await response.json();
      if (result.success) {
        setMatch(result.data);
      }
    } catch (err) {
      setError('Error updating scores: ' + err.message);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!match) return <div>No match found</div>;

  return (
    <div className="match-details">
      <h2>{match.team1} vs {match.team2}</h2>
      
      <div className="match-info">
        <p><strong>Round:</strong> {match.round}</p>
        <p><strong>Status:</strong> {match.status}</p>
      </div>

      {match.toss_winner && (
        <div className="toss-info">
          <p><strong>Toss:</strong> {match.toss_winner} won, chose to {match.toss_choice}</p>
        </div>
      )}

      {match.scheduled_start_time && (
        <div className="timing-info">
          <p><strong>Scheduled:</strong> {new Date(match.scheduled_start_time).toLocaleString()}</p>
          <p><strong>Started:</strong> {new Date(match.actual_start_time).toLocaleString()}</p>
          <p><strong>Ended:</strong> {new Date(match.match_end_time).toLocaleString()}</p>
        </div>
      )}

      {match.team1_first_innings_score !== null && (
        <div className="scores">
          <p><strong>{match.team1} 1st Innings:</strong> {match.team1_first_innings_score}</p>
          <p><strong>{match.team2} 1st Innings:</strong> {match.team2_first_innings_score}</p>
        </div>
      )}

      {match.result && (
        <div className="result">
          <p><strong>Winner:</strong> {match.result.winner}</p>
          <p><strong>Margin:</strong> {match.result.margin} {match.result.margin_type}</p>
        </div>
      )}
    </div>
  );
}

export default MatchDetails;
```

### Vue.js Example Component

```vue
<template>
  <div class="match-details">
    <div v-if="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="match">
      <h2>{{ match.team1 }} vs {{ match.team2 }}</h2>
      
      <div class="match-info">
        <p><strong>Round:</strong> {{ match.round }}</p>
        <p><strong>Status:</strong> {{ match.status }}</p>
      </div>

      <div v-if="match.toss_winner" class="toss-info">
        <p><strong>Toss:</strong> {{ match.toss_winner }} won, chose to {{ match.toss_choice }}</p>
      </div>

      <div v-if="match.scheduled_start_time" class="timing-info">
        <p><strong>Scheduled:</strong> {{ formatDate(match.scheduled_start_time) }}</p>
        <p><strong>Started:</strong> {{ formatDate(match.actual_start_time) }}</p>
        <p><strong>Ended:</strong> {{ formatDate(match.match_end_time) }}</p>
      </div>

      <div v-if="match.team1_first_innings_score !== null" class="scores">
        <p><strong>{{ match.team1 }} 1st Innings:</strong> {{ match.team1_first_innings_score }}</p>
        <p><strong>{{ match.team2 }} 1st Innings:</strong> {{ match.team2_first_innings_score }}</p>
      </div>

      <div v-if="match.result" class="result">
        <p><strong>Winner:</strong> {{ match.result.winner }}</p>
        <p><strong>Margin:</strong> {{ match.result.margin }} {{ match.result.margin_type }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['matchId'],
  data() {
    return {
      match: null,
      loading: true,
      error: null
    };
  },
  mounted() {
    this.fetchMatch();
  },
  methods: {
    async fetchMatch() {
      try {
        this.loading = true;
        const response = await fetch(`/api/schedule/matches/${this.matchId}`);
        const result = await response.json();
        
        if (result.success) {
          this.match = result.data;
        } else {
          this.error = 'Failed to fetch match';
        }
      } catch (err) {
        this.error = 'Error fetching match: ' + err.message;
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleString();
    }
  }
};
</script>
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Error Response Format:
```json
{
  "success": false,
  "message": "Error description",
  "status_code": 400
}
```

---

## Important Notes for Frontend Developers

1. **DateTime Format**: All datetime fields use ISO 8601 format (e.g., "2025-11-28T13:31:55.321528")

2. **First Innings Only**: The API now only tracks first innings scores. Second innings fields are not returned in responses.

3. **Optional Fields**: Most match detail fields (toss, timing, scores) are optional and will be `null` until updated.

4. **Team Names**: The `toss_winner` must match either `team1` or `team2` names exactly.

5. **Validation**: 
   - `toss_choice` must be either "bat" or "bowl"
   - `status` must be one of: "scheduled", "live", "completed"
   - Scores must be positive integers (if provided)

6. **Timestamps**: The `created_at` and `updated_at` fields are automatically managed by the backend and should not be sent in request bodies.

---

## Quick Reference Table

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/matches` | POST | Create new match |
| `/matches` | GET | Get all matches |
| `/matches/{id}` | GET | Get single match |
| `/matches/{id}` | PUT | Full match update |
| `/matches/{id}/status` | PUT | Update match status |
| `/matches/{id}/toss` | PUT | Update toss details |
| `/matches/{id}/timing` | PUT | Update match timing |
| `/matches/{id}/scores` | PUT | Update innings scores |
| `/matches/{id}/score-url` | PUT | Update match score URL |
| `/matches/{id}` | DELETE | Delete match |

---

## Support & Questions

For any issues or questions about these endpoints, refer to the backend API documentation or contact the backend team.
