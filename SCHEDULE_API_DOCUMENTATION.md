# Cricket Schedule & Results API Documentation

## Overview

Complete backend implementation for ICCT26 cricket tournament match scheduling and result tracking. Integrates with the frontend schedule manager for admin operations and public schedule display.

---

## Database Schema

### Matches Table
```sql
CREATE TABLE matches (
  id INTEGER PRIMARY KEY,
  round VARCHAR(50) NOT NULL,
  round_number INTEGER NOT NULL,
  match_number INTEGER NOT NULL,
  team1_id INTEGER NOT NULL,
  team2_id INTEGER NOT NULL,
  status VARCHAR(20) DEFAULT 'scheduled',
  winner_id INTEGER,
  margin INTEGER,
  margin_type VARCHAR(20),
  won_by_batting_first BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  
  FOREIGN KEY (team1_id) REFERENCES teams(id),
  FOREIGN KEY (team2_id) REFERENCES teams(id),
  FOREIGN KEY (winner_id) REFERENCES teams(id)
);
```

### Fields Explained

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | INTEGER | ✅ | Primary key, auto-increment |
| `round` | VARCHAR | ✅ | Round name (e.g., "Round 1", "Semi-Final") |
| `round_number` | INTEGER | ✅ | Numeric round (1, 2, 3...) |
| `match_number` | INTEGER | ✅ | Match number within round (1, 2, 3...) |
| `team1_id` | INTEGER | ✅ | FK to teams table |
| `team2_id` | INTEGER | ✅ | FK to teams table |
| `status` | VARCHAR | ✅ | 'scheduled', 'live', or 'completed' |
| `winner_id` | INTEGER | ❌ | FK to teams (NULL until match completes) |
| `margin` | INTEGER | ❌ | Numeric margin value (NULL until result) |
| `margin_type` | VARCHAR | ❌ | 'runs' or 'wickets' |
| `won_by_batting_first` | BOOLEAN | ❌ | Whether batting first team won |
| `created_at` | TIMESTAMP | ✅ | Auto-set on creation |
| `updated_at` | TIMESTAMP | ✅ | Auto-updated on every change |

---

## API Endpoints

### 1. GET `/api/schedule/matches` - Fetch All Matches

**Purpose**: Get all matches for public schedule display

**Method**: GET  
**Auth**: None (public)  
**Response Code**: 200 OK

**Response Body**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "round": "Round 1",
      "round_number": 1,
      "match_number": 1,
      "team1": "Mumbai Kings",
      "team2": "Delhi Warriors",
      "status": "completed",
      "result": {
        "winner": "Mumbai Kings",
        "margin": 45,
        "margin_type": "runs",
        "won_by_batting_first": true
      },
      "created_at": "2025-11-27T10:00:00",
      "updated_at": "2025-11-27T12:00:00"
    },
    {
      "id": 2,
      "round": "Round 1",
      "round_number": 1,
      "match_number": 2,
      "team1": "Chennai Super Kings",
      "team2": "Bangalore United",
      "status": "scheduled",
      "result": null,
      "created_at": "2025-11-27T10:30:00",
      "updated_at": "2025-11-27T10:30:00"
    }
  ]
}
```

**Notes**:
- Returns all matches sorted by `round_number` then `match_number`
- Team names returned (not IDs)
- `result` object only included if status is 'completed'
- No pagination (all matches returned)

---

### 2. POST `/api/schedule/matches` - Create Match

**Purpose**: Admin creates a new match

**Method**: POST  
**Auth**: Admin required  
**Request Body**:
```json
{
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "Mumbai Kings",
  "team2": "Delhi Warriors"
}
```

**Validation**:
- ✅ Both teams must exist in `teams` table
- ✅ Cannot create if round_number + match_number already exists
- ✅ Teams must be different (cannot play against itself)
- ✅ round_number must be > 0
- ✅ match_number must be > 0

**Response (201 Created)**:
```json
{
  "success": true,
  "message": "Match created successfully",
  "data": {
    "id": 3,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 3,
    "team1": "Mumbai Kings",
    "team2": "Delhi Warriors",
    "status": "scheduled",
    "result": null,
    "created_at": "2025-11-27T11:00:00",
    "updated_at": "2025-11-27T11:00:00"
  }
}
```

**Error Responses**:

❌ Team Not Found (400):
```json
{
  "detail": "Team 'Invalid Team' not found in database"
}
```

❌ Duplicate Match (400):
```json
{
  "detail": "Match already exists for Round 1, Match 1"
}
```

❌ Same Team (400):
```json
{
  "detail": "A team cannot play against itself"
}
```

---

### 3. PUT `/api/schedule/matches/{matchId}` - Update Match

**Purpose**: Admin edits match details

**Method**: PUT  
**Auth**: Admin required  
**URL Parameter**: `matchId` (integer)

**Request Body**:
```json
{
  "round": "Round 1",
  "round_number": 1,
  "match_number": 2,
  "team1": "Chennai Super Kings",
  "team2": "Bangalore United"
}
```

**Validation**:
- ✅ Match must exist
- ✅ Cannot update if match status is 'completed'
- ✅ New teams must exist
- ✅ New match number must be unique within round

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Match updated successfully",
  "data": {
    "id": 2,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 2,
    "team1": "Chennai Super Kings",
    "team2": "Bangalore United",
    "status": "scheduled",
    "result": null,
    "created_at": "2025-11-27T10:30:00",
    "updated_at": "2025-11-27T11:05:00"
  }
}
```

**Error Responses**:

❌ Match Not Found (404):
```json
{
  "detail": "Match not found"
}
```

❌ Completed Match (409):
```json
{
  "detail": "Cannot update a match that is completed"
}
```

---

### 4. DELETE `/api/schedule/matches/{matchId}` - Delete Match

**Purpose**: Admin deletes a match

**Method**: DELETE  
**Auth**: Admin required  
**URL Parameter**: `matchId` (integer)

**Validation**:
- ✅ Can only delete if status is 'scheduled'
- ✅ Cannot delete live or completed matches

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Match deleted successfully"
}
```

**Error Responses**:

❌ Match Not Found (404):
```json
{
  "detail": "Match not found"
}
```

❌ Live/Completed Match (409):
```json
{
  "detail": "Cannot delete a match that is live or completed"
}
```

---

### 5. PUT `/api/schedule/matches/{matchId}/status` - Update Status

**Purpose**: Change match status (scheduled → live → completed)

**Method**: PUT  
**Auth**: Admin required  
**URL Parameter**: `matchId` (integer)

**Request Body**:
```json
{
  "status": "live"
}
```

**Valid Status Transitions**:
```
scheduled → live
scheduled → completed
live → completed
completed → (no transitions allowed)
```

**Validation**:
- ✅ Status must be 'scheduled', 'live', or 'completed'
- ✅ Cannot downgrade status (e.g., live → scheduled)
- ✅ Match must exist

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Match status updated to live",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "Mumbai Kings",
    "team2": "Delhi Warriors",
    "status": "live",
    "result": null,
    "created_at": "2025-11-27T10:00:00",
    "updated_at": "2025-11-27T12:30:00"
  }
}
```

**Important**: Result data is NOT cleared when status changes. Keeps result intact.

**Error Responses**:

❌ Invalid Transition (400):
```json
{
  "detail": "Cannot transition from 'live' to 'scheduled'"
}
```

---

### 6. POST `/api/schedule/matches/{matchId}/result` - Set Match Result ⭐

**Purpose**: Admin sets the final result (CRITICAL ENDPOINT)

**Method**: POST  
**Auth**: Admin required  
**URL Parameter**: `matchId` (integer)

**Request Body**:
```json
{
  "winner": "Mumbai Kings",
  "margin": 45,
  "marginType": "runs",
  "wonByBattingFirst": true
}
```

**Field Descriptions**:

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `winner` | string | Team name | Exact match of team1 or team2 |
| `margin` | integer | 1-999 (runs) or 1-10 (wickets) | Numeric margin |
| `marginType` | string | "runs" or "wickets" | Type of margin |
| `wonByBattingFirst` | boolean | true/false | Did batting first team win? |

**Cricket Logic Examples**:

**Example 1: Batting First Win**
```json
{
  "winner": "Mumbai Kings",
  "margin": 45,
  "marginType": "runs",
  "wonByBattingFirst": true
}
```
→ Mumbai batted first, opposition fell 45 runs short

**Example 2: Chasing Win**
```json
{
  "winner": "Delhi Warriors",
  "margin": 3,
  "marginType": "wickets",
  "wonByBattingFirst": false
}
```
→ Delhi chased successfully with 3 wickets remaining

**Server-Side Validation**:

✅ All validations:
```
1. Match exists
2. Winner is team1 or team2
3. Margin > 0
4. If marginType="runs": margin ≤ 999
5. If marginType="wickets": margin ≤ 10
6. marginType is "runs" or "wickets"
7. wonByBattingFirst is boolean
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Match result saved successfully",
  "data": {
    "id": 1,
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "Mumbai Kings",
    "team2": "Delhi Warriors",
    "status": "completed",
    "result": {
      "winner": "Mumbai Kings",
      "margin": 45,
      "margin_type": "runs",
      "won_by_batting_first": true
    },
    "created_at": "2025-11-27T10:00:00",
    "updated_at": "2025-11-27T14:00:00"
  }
}
```

**Auto-Action**: Match status automatically set to 'completed'

**Error Responses**:

❌ Invalid Winner (400):
```json
{
  "detail": "Invalid winner. Winner must be one of the teams: Mumbai Kings, Delhi Warriors"
}
```

❌ Margin Out of Range (400):
```json
{
  "detail": "Runs margin cannot exceed 999"
}
```

❌ Wickets Out of Range (400):
```json
{
  "detail": "Wickets margin cannot exceed 10"
}
```

---

### 7. POST `/api/schedule/export` - Export Schedule

**Purpose**: Export entire schedule as JSON

**Method**: POST  
**Auth**: Admin required

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "round": "Round 1",
      "round_number": 1,
      "match_number": 1,
      "team1": "Mumbai Kings",
      "team2": "Delhi Warriors",
      "status": "completed",
      "result": {
        "winner": "Mumbai Kings",
        "margin": 45,
        "margin_type": "runs",
        "won_by_batting_first": true
      },
      "created_at": "2025-11-27T10:00:00",
      "updated_at": "2025-11-27T14:00:00"
    }
  ]
}
```

---

## Implementation Checklist

### ✅ Database
- [x] Match model created in `models.py`
- [x] Foreign keys to teams table
- [x] Indexes for performance
- [x] Migration script created

### ✅ API Routes
- [x] GET /api/schedule/matches
- [x] POST /api/schedule/matches
- [x] PUT /api/schedule/matches/{id}
- [x] DELETE /api/schedule/matches/{id}
- [x] PUT /api/schedule/matches/{id}/status
- [x] POST /api/schedule/matches/{id}/result
- [x] POST /api/schedule/export

### ✅ Validation & Error Handling
- [x] Input validation on all endpoints
- [x] Proper HTTP status codes
- [x] Error messages with details
- [x] Foreign key constraints
- [x] Duplicate match prevention
- [x] Cricket rules validation

### ✅ Response Format
- [x] All responses have `success` boolean
- [x] Team names returned (not IDs)
- [x] Result object included only when completed
- [x] Timestamps on all records

---

## Setup Instructions

### 1. Run Migration

```bash
cd d:\ICCT26 BACKEND
.\venv\Scripts\python.exe scripts/create_matches_table.py
```

**Output**:
```
✅ Database migration completed successfully!
Matches table is now ready for use.
```

### 2. Verify Backend

Start the server:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Test endpoint:
```bash
curl http://127.0.0.1:8000/api/schedule/matches
```

Should return:
```json
{
  "success": true,
  "data": []
}
```

### 3. Test in Frontend

Frontend can now:
- ✅ Fetch all matches: `GET /api/schedule/matches`
- ✅ Create matches: `POST /api/schedule/matches`
- ✅ Edit matches: `PUT /api/schedule/matches/{id}`
- ✅ Delete matches: `DELETE /api/schedule/matches/{id}`
- ✅ Update status: `PUT /api/schedule/matches/{id}/status`
- ✅ Set results: `POST /api/schedule/matches/{id}/result`
- ✅ Export: `POST /api/schedule/export`

---

## Testing Examples

### Create Match
```bash
curl -X POST http://127.0.0.1:8000/api/schedule/matches \
  -H "Content-Type: application/json" \
  -d '{
    "round": "Round 1",
    "round_number": 1,
    "match_number": 1,
    "team1": "Mumbai Kings",
    "team2": "Delhi Warriors"
  }'
```

### Set Result
```bash
curl -X POST http://127.0.0.1:8000/api/schedule/matches/1/result \
  -H "Content-Type: application/json" \
  -d '{
    "winner": "Mumbai Kings",
    "margin": 45,
    "marginType": "runs",
    "wonByBattingFirst": true
  }'
```

### Update Status
```bash
curl -X PUT http://127.0.0.1:8000/api/schedule/matches/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "live"
  }'
```

---

## Key Features

✅ **Complete Cricket Integration**
- Proper runs/wickets margin handling
- Batting first/chasing logic
- Valid team names required

✅ **State Management**
- Proper status transitions
- Cannot downgrade status
- Cannot delete completed matches

✅ **Data Integrity**
- Foreign key constraints
- Unique match numbers per round
- Null result fields until completion

✅ **Performance**
- Indexed on status, round, teams
- Sorted queries for consistency
- Efficient lookups

✅ **Error Handling**
- Detailed error messages
- Proper HTTP status codes
- Input validation on all fields

---

## Deployment

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "Add cricket schedule API"
   git push origin schedule
   ```

2. **Merge to main**:
   ```bash
   git checkout main
   git merge schedule
   git push origin main
   ```

3. **Run migration on production**:
   ```bash
   python scripts/create_matches_table.py
   ```

4. **Verify endpoints**:
   ```bash
   curl https://your-backend.com/api/schedule/matches
   ```

---

## Support

For issues or questions:
1. Check validation error messages
2. Verify teams exist in database
3. Check match status transitions
4. Review cricket logic (margin ranges)
5. Check logs for detailed errors

