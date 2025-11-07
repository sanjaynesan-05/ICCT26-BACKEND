# Admin Panel API Endpoints Documentation

**API Base URL:** `http://localhost:8000` (Development) | `https://icct26-backend.onrender.com` (Production)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
   - [GET /admin/teams](#get-admintems)
   - [GET /admin/teams/{teamId}](#get-adminteamsteamid)
   - [GET /admin/players/{playerId}](#get-adminplayersplayerid)
4. [Response Formats](#response-formats)
5. [Error Handling](#error-handling)
6. [Usage Examples](#usage-examples)
7. [Testing with cURL](#testing-with-curl)

---

## Overview

The Admin Panel provides three powerful endpoints for managing teams and players registered in the ICCT26 Cricket Tournament:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/admin/teams` | GET | List all registered teams |
| `/admin/teams/{teamId}` | GET | Get detailed team info with players |
| `/admin/players/{playerId}` | GET | Get specific player details with team context |

**Response Status Codes:**
- `200 OK` - Successful request
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

---

## Authentication

Currently, these endpoints are **public** for development. For production, implement authentication:

```python
# Example: Add bearer token authentication
from fastapi.security import HTTPBearer, HTTPAuthenticationCredentials

security = HTTPBearer()

async def verify_admin_token(credentials: HTTPAuthenticationCredentials = Depends(security)):
    if credentials.credentials != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return credentials
```

---

## Endpoints

### GET /admin/teams

**Description:** Retrieve a list of all registered teams with essential information.

**Method:** `GET`

**URL:** `/admin/teams`

**Parameters:** None

**Response:** 

```json
{
  "success": true,
  "count": 4,
  "teams": [
    {
      "teamId": "ICCT26-20250101120000",
      "teamName": "Grace Warriors",
      "churchName": "CSI St. Michael's Church",
      "captainName": "Rajesh Kumar",
      "captainPhone": "9876543210",
      "captainEmail": "rajesh@example.com",
      "viceCaptainName": "Ananya Singh",
      "viceCaptainPhone": "9876543211",
      "viceCaptainEmail": "ananya@example.com",
      "paymentReceipt": true,
      "registrationDate": "2025-01-01T12:00:00",
      "playerCount": 11
    }
  ]
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request status (always true for 200 response) |
| `count` | integer | Total number of teams |
| `teams` | array | Array of team objects |
| `teamId` | string | Unique team identifier |
| `teamName` | string | Name of the team |
| `churchName` | string | Church affiliation |
| `captainName` | string | Captain's full name |
| `captainPhone` | string | Captain's phone number |
| `captainEmail` | string | Captain's email address |
| `viceCaptainName` | string | Vice-captain's full name |
| `viceCaptainPhone` | string | Vice-captain's phone number |
| `viceCaptainEmail` | string | Vice-captain's email address |
| `paymentReceipt` | boolean | Whether payment receipt is uploaded |
| `registrationDate` | string | ISO 8601 registration timestamp |
| `playerCount` | integer | Total players in team |

---

### GET /admin/teams/{teamId}

**Description:** Retrieve detailed information about a specific team and its complete player roster.

**Method:** `GET`

**URL:** `/admin/teams/{teamId}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `teamId` | string | Yes | Unique team identifier (e.g., "ICCT26-20250101120000") |

**Response (Success - 200):**

```json
{
  "success": true,
  "team": {
    "teamId": "ICCT26-20250101120000",
    "teamName": "Grace Warriors",
    "churchName": "CSI St. Michael's Church",
    "captain": {
      "name": "Rajesh Kumar",
      "phone": "9876543210",
      "whatsapp": "9876543210",
      "email": "rajesh@example.com"
    },
    "viceCaptain": {
      "name": "Ananya Singh",
      "phone": "9876543211",
      "whatsapp": "9876543211",
      "email": "ananya@example.com"
    },
    "pastorLetter": true,
    "paymentReceipt": true,
    "registrationDate": "2025-01-01T12:00:00",
    "players": [
      {
        "playerId": 1,
        "name": "Arjun Patel",
        "age": 25,
        "phone": "9876543220",
        "role": "Batsman",
        "aadharFile": true,
        "subscriptionFile": true
      },
      {
        "playerId": 2,
        "name": "Vikram Singh",
        "age": 28,
        "phone": "9876543221",
        "role": "Bowler",
        "aadharFile": true,
        "subscriptionFile": true
      }
    ],
    "playerCount": 11
  }
}
```

**Response (Not Found - 404):**

```json
{
  "success": false,
  "error": "Not Found",
  "message": "Team with ID 'INVALID-TEAM-ID' not found",
  "detail": "No team exists with the given team_id: INVALID-TEAM-ID"
}
```

**Response (Server Error - 500):**

```json
{
  "success": false,
  "error": "Internal Server Error",
  "message": "Failed to fetch team details",
  "detail": "Database connection failed"
}
```

**Field Descriptions (Team Object):**

| Field | Type | Description |
|-------|------|-------------|
| `teamId` | string | Unique team identifier |
| `teamName` | string | Team name |
| `churchName` | string | Church affiliation |
| `captain` | object | Captain details (name, phone, whatsapp, email) |
| `viceCaptain` | object | Vice-captain details |
| `pastorLetter` | boolean | Whether pastor letter is uploaded |
| `paymentReceipt` | boolean | Whether payment receipt is uploaded |
| `registrationDate` | string | ISO 8601 registration timestamp |
| `players` | array | List of player objects |
| `playerCount` | integer | Total number of players |

**Player Object Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `playerId` | integer | Unique player database ID |
| `name` | string | Player's full name |
| `age` | integer | Player's age |
| `phone` | string | Player's phone number |
| `role` | string | Player role: "Batsman", "Bowler", "All-Rounder", "Wicket Keeper" |
| `aadharFile` | boolean | Whether Aadhar document is uploaded |
| `subscriptionFile` | boolean | Whether subscription document is uploaded |

---

### GET /admin/players/{playerId}

**Description:** Fetch detailed information about a specific player with team context.

**Method:** `GET`

**URL:** `/admin/players/{playerId}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `playerId` | integer | Yes | Unique player database identifier (e.g., 1, 2, 3) |

**Response (Success - 200):**

```json
{
  "success": true,
  "player": {
    "playerId": 5,
    "name": "Arjun Patel",
    "age": 25,
    "phone": "9876543220",
    "role": "Batsman",
    "aadharFile": true,
    "subscriptionFile": true,
    "team": {
      "teamId": "ICCT26-20250101120000",
      "teamName": "Grace Warriors",
      "churchName": "CSI St. Michael's Church"
    }
  }
}
```

**Response (Not Found - 404):**

```json
{
  "success": false,
  "error": "Not Found",
  "message": "Player with ID '999' not found",
  "detail": "No player exists with the given player_id: 999"
}
```

**Response (Server Error - 500):**

```json
{
  "success": false,
  "error": "Internal Server Error",
  "message": "Failed to fetch player details",
  "detail": "Database connection failed"
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request status |
| `player` | object | Player information object |
| `playerId` | integer | Unique player ID |
| `name` | string | Player's full name |
| `age` | integer | Player's age |
| `phone` | string | Player's phone number |
| `role` | string | Player role: "Batsman", "Bowler", "All-Rounder", "Wicket Keeper" |
| `aadharFile` | boolean | Whether Aadhar file exists |
| `subscriptionFile` | boolean | Whether subscription file exists |
| `team` | object | Team information (teamId, teamName, churchName) |

---

## Response Formats

### Success Response (200 OK)

All successful responses follow this pattern:

```json
{
  "success": true,
  "data": { /* Endpoint-specific data */ }
}
```

### Error Response Format

All error responses include:

```json
{
  "success": false,
  "error": "Error Category",
  "message": "Human-readable error message",
  "detail": "Technical details for debugging"
}
```

---

## Error Handling

| Status Code | Scenario | Response |
|-------------|----------|----------|
| 200 OK | Successful request | Data returned with `success: true` |
| 404 Not Found | Resource doesn't exist | Error with specific resource not found message |
| 500 Server Error | Database/server error | Error with technical details |

**Common Error Scenarios:**

1. **Invalid Team ID:** Returns 404 with "Team with ID '...' not found"
2. **Invalid Player ID:** Returns 404 with "Player with ID '...' not found"
3. **Database Connection Error:** Returns 500 with connection details
4. **Malformed Requests:** Returns 422 with validation error

---

## Usage Examples

### JavaScript/React

```javascript
// Get all teams
async function getAllTeams() {
  try {
    const response = await fetch('http://localhost:8000/admin/teams');
    const data = await response.json();
    
    if (data.success) {
      console.log(`Found ${data.count} teams:`, data.teams);
    } else {
      console.error(data.message);
    }
  } catch (error) {
    console.error('API Error:', error);
  }
}

// Get team details
async function getTeamDetails(teamId) {
  try {
    const response = await fetch(`http://localhost:8000/admin/teams/${teamId}`);
    const data = await response.json();
    
    if (data.success) {
      console.log('Team:', data.team);
      console.log('Players:', data.team.players);
    } else {
      console.error(data.message);
    }
  } catch (error) {
    console.error('API Error:', error);
  }
}

// Get player details
async function getPlayerDetails(playerId) {
  try {
    const response = await fetch(`http://localhost:8000/admin/players/${playerId}`);
    const data = await response.json();
    
    if (data.success) {
      console.log('Player:', data.player);
      console.log('Team:', data.player.team);
    } else {
      console.error(data.message);
    }
  } catch (error) {
    console.error('API Error:', error);
  }
}
```

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Get all teams
def get_all_teams():
    response = requests.get(f"{BASE_URL}/admin/teams")
    data = response.json()
    if data.get('success'):
        print(f"Found {data['count']} teams")
        for team in data['teams']:
            print(f"  - {team['teamName']} ({team['playerCount']} players)")
    else:
        print(f"Error: {data['message']}")

# Get team details
def get_team_details(team_id):
    response = requests.get(f"{BASE_URL}/admin/teams/{team_id}")
    data = response.json()
    if data.get('success'):
        team = data['team']
        print(f"Team: {team['teamName']}")
        print(f"Players: {len(team['players'])}")
        for player in team['players']:
            print(f"  - {player['name']} ({player['role']})")
    else:
        print(f"Error: {data['message']}")

# Get player details
def get_player_details(player_id):
    response = requests.get(f"{BASE_URL}/admin/players/{player_id}")
    data = response.json()
    if data.get('success'):
        player = data['player']
        print(f"Player: {player['name']}")
        print(f"Team: {player['team']['teamName']}")
        print(f"Role: {player['role']}")
    else:
        print(f"Error: {data['message']}")
```

---

## Testing with cURL

### Test 1: Get All Teams

```bash
curl -X GET "http://localhost:8000/admin/teams" \
  -H "Content-Type: application/json"
```

**Expected Output:**
```json
{
  "success": true,
  "count": 4,
  "teams": [...]
}
```

---

### Test 2: Get Team Details

```bash
curl -X GET "http://localhost:8000/admin/teams/ICCT26-20250101120000" \
  -H "Content-Type: application/json"
```

**Expected Output:**
```json
{
  "success": true,
  "team": {
    "teamId": "ICCT26-20250101120000",
    "teamName": "Grace Warriors",
    "players": [...]
  }
}
```

---

### Test 3: Get Team Details (Invalid Team ID)

```bash
curl -X GET "http://localhost:8000/admin/teams/INVALID-ID" \
  -H "Content-Type: application/json"
```

**Expected Output (404):**
```json
{
  "success": false,
  "error": "Not Found",
  "message": "Team with ID 'INVALID-ID' not found",
  "detail": "No team exists with the given team_id: INVALID-ID"
}
```

---

### Test 4: Get Player Details

```bash
curl -X GET "http://localhost:8000/admin/players/1" \
  -H "Content-Type: application/json"
```

**Expected Output:**
```json
{
  "success": true,
  "player": {
    "playerId": 1,
    "name": "Arjun Patel",
    "age": 25,
    "role": "Batsman",
    "team": {
      "teamId": "ICCT26-20250101120000",
      "teamName": "Grace Warriors"
    }
  }
}
```

---

### Test 5: Get Player Details (Invalid Player ID)

```bash
curl -X GET "http://localhost:8000/admin/players/999" \
  -H "Content-Type: application/json"
```

**Expected Output (404):**
```json
{
  "success": false,
  "error": "Not Found",
  "message": "Player with ID '999' not found",
  "detail": "No player exists with the given player_id: 999"
}
```

---

## Integration Steps

### 1. Verify Server is Running

```bash
cd "d:\ICCT26 BACKEND"
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### 2. Test Endpoints

Use the cURL commands above or access the interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 3. Integrate with Frontend

Update your React/Vue admin dashboard to call these endpoints:

```javascript
const API_BASE = 'http://localhost:8000';

// In your admin component:
useEffect(() => {
  fetch(`${API_BASE}/admin/teams`)
    .then(res => res.json())
    .then(data => setTeams(data.teams));
}, []);
```

---

## Best Practices

✅ **Do:**
- Validate user input before sending to API
- Handle error responses gracefully
- Show loading states while fetching
- Cache data when appropriate
- Use pagination for large datasets (future enhancement)

❌ **Don't:**
- Expose API URLs in frontend code (use environment variables)
- Store sensitive data in local storage
- Make requests for every user action (debounce)
- Ignore error responses
- Log sensitive player information

---

## Future Enhancements

Potential features to add:

1. **Pagination** - Add `limit` and `offset` parameters to `/admin/teams`
2. **Filtering** - Filter teams by church, date range, payment status
3. **Sorting** - Sort by team name, registration date, player count
4. **Search** - Search teams and players by name
5. **Export** - Export team/player data as CSV/PDF
6. **Authentication** - Add bearer token validation
7. **Audit Logging** - Track who accessed what data and when
8. **Rate Limiting** - Prevent API abuse

---

## Database Schema Reference

### teams Table
```sql
CREATE TABLE team_registrations (
  id SERIAL PRIMARY KEY,
  team_id VARCHAR(50) UNIQUE,
  team_name VARCHAR(100),
  church_name VARCHAR(200),
  pastor_letter TEXT,
  payment_receipt TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### captains Table
```sql
CREATE TABLE captains (
  id SERIAL PRIMARY KEY,
  registration_id INTEGER REFERENCES team_registrations(id),
  name VARCHAR(100),
  phone VARCHAR(15),
  whatsapp VARCHAR(10),
  email VARCHAR(255)
);
```

### vice_captains Table
```sql
CREATE TABLE vice_captains (
  id SERIAL PRIMARY KEY,
  registration_id INTEGER REFERENCES team_registrations(id),
  name VARCHAR(100),
  phone VARCHAR(15),
  whatsapp VARCHAR(10),
  email VARCHAR(255)
);
```

### players Table
```sql
CREATE TABLE players (
  id SERIAL PRIMARY KEY,
  registration_id INTEGER REFERENCES team_registrations(id),
  name VARCHAR(100),
  age INTEGER,
  phone VARCHAR(15),
  role VARCHAR(20),
  aadhar_file TEXT,
  subscription_file TEXT
);
```

---

## Support

For issues or questions:
1. Check the error response detail field
2. Review the API documentation at `/docs`
3. Check database connectivity
4. Review server logs for debug information

---

**Last Updated:** November 7, 2025
**API Version:** 1.0.0
**Status:** ✅ Production Ready
