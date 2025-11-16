# ICCT26 Backend - Complete API Endpoints Documentation

**Last Updated**: November 16, 2025  
**API Version**: 1.0.0  
**Base URL (Production)**: `https://icct26-backend.onrender.com`  
**Base URL (Local)**: `http://localhost:8000`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Health & Status Endpoints](#health--status-endpoints)
4. [Team Registration Endpoints](#team-registration-endpoints)
5. [Admin Panel Endpoints](#admin-panel-endpoints)
6. [Data Models](#data-models)
7. [Error Handling](#error-handling)
8. [Testing Guide](#testing-guide)

---

## Overview

The ICCT26 Backend API provides endpoints for:
- Team registration with captain, vice-captain, and 11-15 players
- File uploads (Base64 encoded): Pastor Letter, Payment Receipt, Group Photo, Aadhar, Subscription
- Admin panel for viewing registered teams and players
- Health monitoring and status checks

**Key Features:**
- ✅ Async SQLAlchemy + PostgreSQL (Neon)
- ✅ Base64 file handling with data URI formatting
- ✅ Comprehensive validation with Pydantic
- ✅ CamelCase and snake_case support
- ✅ Automatic jersey number assignment
- ✅ Detailed error messages

---

## Authentication

**Current Status**: No authentication required (public registration)

**Future Implementation**: Admin endpoints will require JWT authentication

---

## Health & Status Endpoints

### 1. Home Endpoint

**GET** `/`

Returns basic API information.

#### Request

```bash
curl -X GET "http://localhost:8000/"
```

#### Response (200 OK)

```json
{
  "message": "ICCT26 Cricket Tournament Registration API",
  "version": "1.0.0",
  "status": "active",
  "db": "PostgreSQL Connected",
  "tournament": "ICCT26 Cricket Tournament"
}
```

---

### 2. Health Check

**GET** `/health`

Quick health check endpoint.

#### Request

```bash
curl -X GET "http://localhost:8000/health"
```

#### Response (200 OK)

```json
{
  "status": "healthy",
  "service": "ICCT26 Registration API",
  "timestamp": "2025-11-16T10:30:45.123456",
  "version": "1.0.0"
}
```

---

### 3. API Status (with DB Check)

**GET** `/status`

Detailed API status with database connection verification.

#### Request

```bash
curl -X GET "http://localhost:8000/status"
```

#### Response (200 OK)

```json
{
  "status": "operational",
  "api_version": "1.0.0",
  "database": "connected",
  "email_service": "configured",
  "tournament": "ICCT26 Cricket Tournament",
  "timestamp": "2025-11-16T10:30:45.123456"
}
```

**Response (Database Error)**

```json
{
  "status": "operational",
  "api_version": "1.0.0",
  "database": "error: connection timeout",
  "email_service": "configured",
  "tournament": "ICCT26 Cricket Tournament",
  "timestamp": "2025-11-16T10:30:45.123456"
}
```

---

### 4. Queue Status

**GET** `/queue/status`

Check registration queue status (placeholder for future implementation).

#### Request

```bash
curl -X GET "http://localhost:8000/queue/status"
```

#### Response (200 OK)

```json
{
  "status": "active",
  "pending_registrations": 0,
  "processed_registrations": 0,
  "message": "Queue system ready"
}
```

---

## Team Registration Endpoints

### 5. Register Team

**POST** `/api/register/team`

Register a complete team with captain, vice-captain, and 11-15 players.

#### Request Headers

```
Content-Type: application/json
```

#### Request Body

```json
{
  "churchName": "St. Mary's Church",
  "teamName": "Warriors",
  "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "paymentReceipt": "data:image/png;base64,iVBORw0KGgo...",
  "groupPhoto": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "captain": {
    "name": "John Doe",
    "phone": "+919876543210",
    "whatsapp": "9876543210",
    "email": "john@example.com"
  },
  "viceCaptain": {
    "name": "Jane Smith",
    "phone": "+919876543211",
    "whatsapp": "9876543211",
    "email": "jane@example.com"
  },
  "players": [
    {
      "name": "Player One",
      "age": 25,
      "phone": "+919800000001",
      "role": "Batsman",
      "jersey_number": "10",
      "aadharFile": "data:application/pdf;base64,JVBERi0xLj...",
      "subscriptionFile": "data:application/pdf;base64,JVBERi0xLj..."
    },
    {
      "name": "Player Two",
      "age": 28,
      "phone": "+919800000002",
      "role": "Bowler",
      "aadharFile": "data:application/pdf;base64,JVBERi0xLj...",
      "subscriptionFile": "data:application/pdf;base64,JVBERi0xLj..."
    }
    // ... 9-13 more players (11-15 total required)
  ]
}
```

#### cURL Example

```bash
curl -X POST "http://localhost:8000/api/register/team" \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "St. Mary'\''s Church",
    "teamName": "Warriors",
    "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "paymentReceipt": "data:image/png;base64,iVBORw0KGgo...",
    "captain": {
      "name": "John Doe",
      "phone": "+919876543210",
      "whatsapp": "9876543210",
      "email": "john@example.com"
    },
    "viceCaptain": {
      "name": "Jane Smith",
      "phone": "+919876543211",
      "whatsapp": "9876543211",
      "email": "jane@example.com"
    },
    "players": [
      {
        "name": "Player One",
        "age": 25,
        "phone": "+919800000001",
        "role": "Batsman",
        "aadharFile": "data:application/pdf;base64,JVBERi0xLj...",
        "subscriptionFile": "data:application/pdf;base64,JVBERi0xLj..."
      }
    ]
  }'
```

#### Response (201 Created)

```json
{
  "success": true,
  "message": "Team and players registered successfully",
  "team_id": "ICCT26-20251116103045",
  "team_name": "Warriors",
  "church_name": "St. Mary's Church",
  "captain_name": "John Doe",
  "vice_captain_name": "Jane Smith",
  "player_count": 11,
  "registration_date": "2025-11-16T10:30:45.123456"
}
```

#### Response (422 Validation Error)

```json
{
  "success": false,
  "message": "Validation failed: Invalid player count. Expected 11-15 players, got 8",
  "field": "players",
  "error_type": "value_error",
  "details": [
    {
      "type": "value_error",
      "loc": ["body", "players"],
      "msg": "Invalid player count",
      "input": []
    }
  ],
  "status_code": 422
}
```

#### Response (400 Bad Request - Database Error)

```json
{
  "success": false,
  "message": "Jersey number is required or invalid. Backend auto-assigns if omitted.",
  "error": "not null constraint violated: jersey_number"
}
```

#### Response (500 Internal Server Error)

```json
{
  "success": false,
  "message": "Registration failed due to database error",
  "error": "connection timeout"
}
```

---

### 6. Registration Health Check

**GET** `/api/register/health`

Health check for registration endpoint.

#### Request

```bash
curl -X GET "http://localhost:8000/api/register/health"
```

#### Response (200 OK)

```json
{
  "status": "healthy",
  "endpoint": "/api/register/team",
  "method": "POST",
  "description": "Register a team and players for ICCT26"
}
```

---

### 7. Get All Teams (Public)

**GET** `/api/teams`

Get paginated list of all registered teams (public view).

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | int | 0 | Number of records to skip |
| limit | int | 10 | Maximum records to return (max 100) |

#### Request

```bash
curl -X GET "http://localhost:8000/api/teams?skip=0&limit=10"
```

#### Response (200 OK)

```json
{
  "success": true,
  "total_teams": 25,
  "returned": 10,
  "skip": 0,
  "limit": 10,
  "teams": [
    {
      "team_id": "ICCT26-20251116103045",
      "team_name": "Warriors",
      "church_name": "St. Mary's Church",
      "captain_name": "John Doe",
      "registration_date": "2025-11-16T10:30:45.123456"
    },
    {
      "team_id": "ICCT26-20251116104512",
      "team_name": "Champions",
      "church_name": "Holy Cross Church",
      "captain_name": "Mike Johnson",
      "registration_date": "2025-11-16T10:45:12.789012"
    }
    // ... 8 more teams
  ]
}
```

---

### 8. Get Team Details (Public)

**GET** `/api/teams/{team_id}`

Get complete details of a specific team including all players.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| team_id | string | Unique team identifier (e.g., "ICCT26-20251116103045") |

#### Request

```bash
curl -X GET "http://localhost:8000/api/teams/ICCT26-20251116103045"
```

#### Response (200 OK)

```json
{
  "success": true,
  "team": {
    "team_id": "ICCT26-20251116103045",
    "team_name": "Warriors",
    "church_name": "St. Mary's Church",
    "captain": {
      "name": "John Doe",
      "phone": "+919876543210",
      "email": "john@example.com",
      "whatsapp": "9876543210"
    },
    "viceCaptain": {
      "name": "Jane Smith",
      "phone": "+919876543211",
      "email": "jane@example.com",
      "whatsapp": "9876543211"
    },
    "pastor_letter": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "payment_receipt": "data:image/png;base64,iVBORw0KGgo...",
    "registration_date": "2025-11-16T10:30:45.123456"
  },
  "players": [
    {
      "player_id": "ICCT26-20251116103045-P01",
      "name": "Player One",
      "age": 25,
      "phone": "+919800000001",
      "role": "Batsman",
      "aadhar_file": "data:application/pdf;base64,JVBERi0xLj...",
      "subscription_file": "data:application/pdf;base64,JVBERi0xLj..."
    },
    {
      "player_id": "ICCT26-20251116103045-P02",
      "name": "Player Two",
      "age": 28,
      "phone": "+919800000002",
      "role": "Bowler",
      "aadhar_file": "data:application/pdf;base64,JVBERi0xLj...",
      "subscription_file": "data:application/pdf;base64,JVBERi0xLj..."
    }
    // ... 9 more players
  ]
}
```

#### Response (404 Not Found)

```json
{
  "detail": "Team ICCT26-99999999999999 not found"
}
```

---

## Admin Panel Endpoints

### 9. Get All Teams (Admin View)

**GET** `/admin/teams`

Get all registered teams with comprehensive details (admin view).

#### Request

```bash
curl -X GET "http://localhost:8000/admin/teams"
```

#### Response (200 OK)

```json
{
  "success": true,
  "teams": [
    {
      "teamId": "ICCT26-20251116103045",
      "teamName": "Warriors",
      "churchName": "St. Mary's Church",
      "captainName": "John Doe",
      "captainPhone": "+919876543210",
      "captainEmail": "john@example.com",
      "viceCaptainName": "Jane Smith",
      "viceCaptainPhone": "+919876543211",
      "playerCount": 11,
      "registrationDate": "2025-11-16T10:30:45.123456",
      "paymentReceipt": "data:image/png;base64,iVBORw0KGgo...",
      "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
      "groupPhoto": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
    },
    {
      "teamId": "ICCT26-20251116104512",
      "teamName": "Champions",
      "churchName": "Holy Cross Church",
      "captainName": "Mike Johnson",
      "captainPhone": "+919876543299",
      "captainEmail": "mike@example.com",
      "viceCaptainName": "Sarah Williams",
      "viceCaptainPhone": "+919876543288",
      "playerCount": 12,
      "registrationDate": "2025-11-16T10:45:12.789012",
      "paymentReceipt": "data:image/png;base64,iVBORw0KGgo...",
      "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
      "groupPhoto": null
    }
    // ... more teams
  ]
}
```

---

### 10. Get Team Details (Admin View)

**GET** `/admin/teams/{team_id}`

Get complete team and player details with all files (admin view).

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| team_id | string | Unique team identifier |

#### Request

```bash
curl -X GET "http://localhost:8000/admin/teams/ICCT26-20251116103045"
```

#### Response (200 OK)

```json
{
  "team": {
    "teamId": "ICCT26-20251116103045",
    "teamName": "Warriors",
    "churchName": "St. Mary's Church",
    "captainName": "John Doe",
    "captainPhone": "+919876543210",
    "captainEmail": "john@example.com",
    "captainWhatsapp": "9876543210",
    "viceCaptainName": "Jane Smith",
    "viceCaptainPhone": "+919876543211",
    "viceCaptainEmail": "jane@example.com",
    "viceCaptainWhatsapp": "9876543211",
    "registrationDate": "2025-11-16T10:30:45.123456",
    "paymentReceipt": "data:image/png;base64,iVBORw0KGgo...",
    "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "groupPhoto": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  },
  "players": [
    {
      "playerId": "ICCT26-20251116103045-P01",
      "name": "Player One",
      "age": 25,
      "phone": "+919800000001",
      "role": "Batsman",
      "jerseyNumber": "10",
      "aadharFile": "data:application/pdf;base64,JVBERi0xLj...",
      "subscriptionFile": "data:application/pdf;base64,JVBERi0xLj..."
    },
    {
      "playerId": "ICCT26-20251116103045-P02",
      "name": "Player Two",
      "age": 28,
      "phone": "+919800000002",
      "role": "Bowler",
      "jerseyNumber": "2",
      "aadharFile": "data:application/pdf;base64,JVBERi0xLj...",
      "subscriptionFile": "data:application/pdf;base64,JVBERi0xLj..."
    }
    // ... 9 more players
  ]
}
```

#### Response (404 Not Found)

```json
{
  "detail": "Team not found"
}
```

---

### 11. Get Player Details (Admin View)

**GET** `/admin/players/{player_id}`

Get detailed information about a specific player with team context.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| player_id | int | Unique player identifier (database ID) |

#### Request

```bash
curl -X GET "http://localhost:8000/admin/players/123"
```

#### Response (200 OK)

```json
{
  "playerId": "ICCT26-20251116103045-P01",
  "name": "Player One",
  "age": 25,
  "phone": "+919800000001",
  "role": "Batsman",
  "jerseyNumber": "10",
  "aadharFile": "data:application/pdf;base64,JVBERi0xLj...",
  "subscriptionFile": "data:application/pdf;base64,JVBERi0xLj...",
  "teamId": "ICCT26-20251116103045",
  "teamName": "Warriors",
  "churchName": "St. Mary's Church"
}
```

#### Response (404 Not Found)

```json
{
  "detail": "Player not found"
}
```

---

## Data Models

### Team Registration Request

```typescript
interface TeamRegistrationRequest {
  churchName: string;          // 1-200 chars
  teamName: string;             // 1-200 chars
  pastorLetter?: string;        // Base64 with data URI (JPEG/PNG/PDF)
  paymentReceipt?: string;      // Base64 with data URI (JPEG/PNG/PDF)
  groupPhoto?: string;          // Base64 with data URI (JPEG/PNG only)
  captain: CaptainInfo;
  viceCaptain: ViceCaptainInfo;
  players: PlayerInfo[];        // 11-15 players required
}

interface CaptainInfo {
  name: string;                 // 1-150 chars
  phone: string;                // 7-20 chars (digits or +prefix)
  whatsapp: string;             // 10-20 chars (digits or +prefix)
  email: string;                // Valid email
}

interface ViceCaptainInfo {
  name: string;                 // 1-150 chars
  phone: string;                // 7-20 chars
  whatsapp: string;             // 10-20 chars
  email: string;                // Valid email
}

interface PlayerInfo {
  name: string;                 // 1-150 chars
  age: number;                  // 15-65
  phone: string;                // 7-15 chars
  role: string;                 // 1-20 chars (e.g., "Batsman", "Bowler")
  jersey_number?: string;       // Optional, auto-assigned if missing (1-3 chars)
  aadharFile?: string;          // Base64 with data URI (PDF)
  subscriptionFile?: string;    // Base64 with data URI (PDF)
}
```

### Team Registration Response

```typescript
interface TeamRegistrationResponse {
  success: boolean;
  message: string;
  team_id: string;
  team_name: string;
  church_name: string;
  captain_name: string;
  vice_captain_name: string;
  player_count: number;
  registration_date: string;    // ISO 8601 format
}
```

### Error Response

```typescript
interface ErrorResponse {
  success: boolean;
  message: string;
  field?: string;               // Field that caused error
  error_type?: string;          // Type of error
  details?: ValidationError[];  // Detailed validation errors
  status_code: number;
}

interface ValidationError {
  type: string;
  loc: string[];
  msg: string;
  input: any;
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful team registration |
| 400 | Bad Request | Database constraint violation, invalid data |
| 404 | Not Found | Team or player not found |
| 422 | Unprocessable Entity | Validation error (invalid input format) |
| 500 | Internal Server Error | Database error, unexpected server error |

### Common Error Scenarios

#### 1. Invalid Player Count

**Request**: Less than 11 or more than 15 players

**Response (422)**:
```json
{
  "success": false,
  "message": "Validation failed: Invalid player count. Expected 11-15 players, got 8",
  "field": "players",
  "error_type": "value_error",
  "status_code": 422
}
```

#### 2. Invalid Email Format

**Request**: Invalid email address

**Response (422)**:
```json
{
  "success": false,
  "message": "Validation failed: value is not a valid email address",
  "field": "captain -> email",
  "error_type": "value_error.email",
  "status_code": 422
}
```

#### 3. Missing Required Field

**Request**: Missing required field (e.g., captain name)

**Response (422)**:
```json
{
  "success": false,
  "message": "Validation failed: field required",
  "field": "captain -> name",
  "error_type": "missing",
  "status_code": 422
}
```

#### 4. Invalid Base64 File

**Request**: Invalid Base64 data or wrong file type

**Response (422)**:
```json
{
  "success": false,
  "message": "Validation failed: Invalid file format. Only JPEG, PNG, and PDF are allowed",
  "field": "pastorLetter",
  "error_type": "value_error",
  "status_code": 422
}
```

#### 5. Database Constraint Violation

**Request**: Duplicate team_id or null constraint

**Response (400)**:
```json
{
  "success": false,
  "message": "Duplicate entry (team_id or player_id already exists)",
  "error": "duplicate key value violates unique constraint"
}
```

#### 6. Team Not Found

**Request**: GET /api/teams/INVALID-ID

**Response (404)**:
```json
{
  "detail": "Team INVALID-ID not found"
}
```

---

## Testing Guide

### Prerequisites

1. **Local Server Running**:
   ```bash
   python main.py
   ```
   Server should start on `http://localhost:8000`

2. **Database Connected**: Ensure PostgreSQL (Neon) is accessible

3. **Test Tools**:
   - cURL (command line)
   - Postman (GUI)
   - Python requests library (automated tests)

### Quick Test Suite

#### 1. Health Check Tests

```bash
# Test 1: Home endpoint
curl -X GET "http://localhost:8000/" | jq

# Test 2: Health check
curl -X GET "http://localhost:8000/health" | jq

# Test 3: API status with database
curl -X GET "http://localhost:8000/status" | jq

# Test 4: Queue status
curl -X GET "http://localhost:8000/queue/status" | jq
```

#### 2. Registration Tests

```bash
# Test 5: Register team (minimal payload - adjust player count to 11)
curl -X POST "http://localhost:8000/api/register/team" \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "Test Church",
    "teamName": "Test Warriors",
    "captain": {
      "name": "Test Captain",
      "phone": "+919876543210",
      "whatsapp": "9876543210",
      "email": "captain@test.com"
    },
    "viceCaptain": {
      "name": "Test Vice Captain",
      "phone": "+919876543211",
      "whatsapp": "9876543211",
      "email": "vice@test.com"
    },
    "players": [
      {"name": "Player 1", "age": 25, "phone": "+919800000001", "role": "Batsman"},
      {"name": "Player 2", "age": 26, "phone": "+919800000002", "role": "Bowler"},
      {"name": "Player 3", "age": 27, "phone": "+919800000003", "role": "All-rounder"},
      {"name": "Player 4", "age": 28, "phone": "+919800000004", "role": "Batsman"},
      {"name": "Player 5", "age": 29, "phone": "+919800000005", "role": "Bowler"},
      {"name": "Player 6", "age": 30, "phone": "+919800000006", "role": "All-rounder"},
      {"name": "Player 7", "age": 24, "phone": "+919800000007", "role": "Batsman"},
      {"name": "Player 8", "age": 23, "phone": "+919800000008", "role": "Bowler"},
      {"name": "Player 9", "age": 22, "phone": "+919800000009", "role": "All-rounder"},
      {"name": "Player 10", "age": 21, "phone": "+919800000010", "role": "Batsman"},
      {"name": "Player 11", "age": 20, "phone": "+919800000011", "role": "Wicket Keeper"}
    ]
  }' | jq
```

**Expected Response**: 201 Created with team_id

#### 3. Team Retrieval Tests

```bash
# Test 6: Get all teams (public)
curl -X GET "http://localhost:8000/api/teams?skip=0&limit=10" | jq

# Test 7: Get team details (replace TEAM_ID)
TEAM_ID="ICCT26-20251116103045"
curl -X GET "http://localhost:8000/api/teams/$TEAM_ID" | jq
```

#### 4. Admin Panel Tests

```bash
# Test 8: Get all teams (admin view)
curl -X GET "http://localhost:8000/admin/teams" | jq

# Test 9: Get team details (admin view)
TEAM_ID="ICCT26-20251116103045"
curl -X GET "http://localhost:8000/admin/teams/$TEAM_ID" | jq

# Test 10: Get player details (replace PLAYER_ID with actual DB ID)
PLAYER_ID=1
curl -X GET "http://localhost:8000/admin/players/$PLAYER_ID" | jq
```

#### 5. Error Handling Tests

```bash
# Test 11: Invalid player count (expect 422)
curl -X POST "http://localhost:8000/api/register/team" \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "Test Church",
    "teamName": "Invalid Team",
    "captain": {"name": "Test", "phone": "+919876543210", "whatsapp": "9876543210", "email": "test@test.com"},
    "viceCaptain": {"name": "Test2", "phone": "+919876543211", "whatsapp": "9876543211", "email": "test2@test.com"},
    "players": [
      {"name": "Player 1", "age": 25, "phone": "+919800000001", "role": "Batsman"}
    ]
  }' | jq

# Test 12: Invalid email (expect 422)
curl -X POST "http://localhost:8000/api/register/team" \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "Test Church",
    "teamName": "Invalid Email Team",
    "captain": {"name": "Test", "phone": "+919876543210", "whatsapp": "9876543210", "email": "invalid-email"},
    "viceCaptain": {"name": "Test2", "phone": "+919876543211", "whatsapp": "9876543211", "email": "test2@test.com"},
    "players": []
  }' | jq

# Test 13: Team not found (expect 404)
curl -X GET "http://localhost:8000/api/teams/INVALID-TEAM-ID" | jq
```

### Automated Testing with Python

Save as `test_api_complete.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_endpoints():
    """Test all health and status endpoints"""
    endpoints = [
        ("/", "Home"),
        ("/health", "Health Check"),
        ("/status", "API Status"),
        ("/queue/status", "Queue Status")
    ]
    
    for endpoint, name in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"✓ {name}: {response.status_code}")
        assert response.status_code == 200

def test_team_registration():
    """Test team registration"""
    payload = {
        "churchName": "Automated Test Church",
        "teamName": "Automation Warriors",
        "captain": {
            "name": "Auto Captain",
            "phone": "+919876543210",
            "whatsapp": "9876543210",
            "email": "auto@test.com"
        },
        "viceCaptain": {
            "name": "Auto Vice",
            "phone": "+919876543211",
            "whatsapp": "9876543211",
            "email": "autovice@test.com"
        },
        "players": [
            {"name": f"Player {i}", "age": 20+i, "phone": f"+91980000000{i}", "role": "Batsman"}
            for i in range(1, 12)  # 11 players
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/register/team", json=payload)
    print(f"✓ Team Registration: {response.status_code}")
    assert response.status_code == 201
    data = response.json()
    return data["team_id"]

def test_team_retrieval(team_id):
    """Test team retrieval endpoints"""
    # Public teams list
    response = requests.get(f"{BASE_URL}/api/teams")
    print(f"✓ Get All Teams (Public): {response.status_code}")
    assert response.status_code == 200
    
    # Public team details
    response = requests.get(f"{BASE_URL}/api/teams/{team_id}")
    print(f"✓ Get Team Details (Public): {response.status_code}")
    assert response.status_code == 200
    
    # Admin teams list
    response = requests.get(f"{BASE_URL}/admin/teams")
    print(f"✓ Get All Teams (Admin): {response.status_code}")
    assert response.status_code == 200
    
    # Admin team details
    response = requests.get(f"{BASE_URL}/admin/teams/{team_id}")
    print(f"✓ Get Team Details (Admin): {response.status_code}")
    assert response.status_code == 200

def test_error_handling():
    """Test error responses"""
    # Invalid player count
    payload = {
        "churchName": "Error Test",
        "teamName": "Error Team",
        "captain": {"name": "Test", "phone": "+919876543210", "whatsapp": "9876543210", "email": "test@test.com"},
        "viceCaptain": {"name": "Test2", "phone": "+919876543211", "whatsapp": "9876543211", "email": "test2@test.com"},
        "players": []  # Empty players
    }
    response = requests.post(f"{BASE_URL}/api/register/team", json=payload)
    print(f"✓ Invalid Player Count Error: {response.status_code}")
    assert response.status_code == 422
    
    # Team not found
    response = requests.get(f"{BASE_URL}/api/teams/INVALID-ID")
    print(f"✓ Team Not Found Error: {response.status_code}")
    assert response.status_code == 404

if __name__ == "__main__":
    print("Starting API Tests...\n")
    
    print("1. Testing Health Endpoints...")
    test_health_endpoints()
    
    print("\n2. Testing Team Registration...")
    team_id = test_team_registration()
    
    print(f"\n3. Testing Team Retrieval (Team ID: {team_id})...")
    test_team_retrieval(team_id)
    
    print("\n4. Testing Error Handling...")
    test_error_handling()
    
    print("\n✅ All tests passed!")
```

Run with:
```bash
python test_api_complete.py
```

### Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "ICCT26 Backend API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health & Status",
      "item": [
        {
          "name": "Home",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/"
          }
        },
        {
          "name": "Health Check",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/health"
          }
        },
        {
          "name": "API Status",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/status"
          }
        },
        {
          "name": "Queue Status",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/queue/status"
          }
        }
      ]
    },
    {
      "name": "Registration",
      "item": [
        {
          "name": "Register Team",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"churchName\": \"Test Church\",\n  \"teamName\": \"Test Warriors\",\n  \"captain\": {\n    \"name\": \"Test Captain\",\n    \"phone\": \"+919876543210\",\n    \"whatsapp\": \"9876543210\",\n    \"email\": \"captain@test.com\"\n  },\n  \"viceCaptain\": {\n    \"name\": \"Test Vice Captain\",\n    \"phone\": \"+919876543211\",\n    \"whatsapp\": \"9876543211\",\n    \"email\": \"vice@test.com\"\n  },\n  \"players\": [\n    {\"name\": \"Player 1\", \"age\": 25, \"phone\": \"+919800000001\", \"role\": \"Batsman\"},\n    {\"name\": \"Player 2\", \"age\": 26, \"phone\": \"+919800000002\", \"role\": \"Bowler\"},\n    {\"name\": \"Player 3\", \"age\": 27, \"phone\": \"+919800000003\", \"role\": \"All-rounder\"},\n    {\"name\": \"Player 4\", \"age\": 28, \"phone\": \"+919800000004\", \"role\": \"Batsman\"},\n    {\"name\": \"Player 5\", \"age\": 29, \"phone\": \"+919800000005\", \"role\": \"Bowler\"},\n    {\"name\": \"Player 6\", \"age\": 30, \"phone\": \"+919800000006\", \"role\": \"All-rounder\"},\n    {\"name\": \"Player 7\", \"age\": 24, \"phone\": \"+919800000007\", \"role\": \"Batsman\"},\n    {\"name\": \"Player 8\", \"age\": 23, \"phone\": \"+919800000008\", \"role\": \"Bowler\"},\n    {\"name\": \"Player 9\", \"age\": 22, \"phone\": \"+919800000009\", \"role\": \"All-rounder\"},\n    {\"name\": \"Player 10\", \"age\": 21, \"phone\": \"+919800000010\", \"role\": \"Batsman\"},\n    {\"name\": \"Player 11\", \"age\": 20, \"phone\": \"+919800000011\", \"role\": \"Wicket Keeper\"}\n  ]\n}"
            },
            "url": "{{base_url}}/api/register/team"
          }
        },
        {
          "name": "Registration Health",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/api/register/health"
          }
        }
      ]
    },
    {
      "name": "Teams (Public)",
      "item": [
        {
          "name": "Get All Teams",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/api/teams?skip=0&limit=10",
              "query": [
                {"key": "skip", "value": "0"},
                {"key": "limit", "value": "10"}
              ]
            }
          }
        },
        {
          "name": "Get Team Details",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/api/teams/{{team_id}}"
          }
        }
      ]
    },
    {
      "name": "Admin",
      "item": [
        {
          "name": "Get All Teams",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/admin/teams"
          }
        },
        {
          "name": "Get Team Details",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/admin/teams/{{team_id}}"
          }
        },
        {
          "name": "Get Player Details",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/admin/players/{{player_id}}"
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "team_id",
      "value": "ICCT26-20251116103045"
    },
    {
      "key": "player_id",
      "value": "1"
    }
  ]
}
```

---

## Best Practices

### 1. File Upload Guidelines

- **Always use data URI format**: `data:image/jpeg;base64,<base64_data>`
- **Supported formats**:
  - Images: JPEG, PNG
  - Documents: PDF
- **Size limit**: 5MB per file
- **Optional fields**: All file fields are optional
- **Group photo**: JPEG/PNG only (not PDF)

### 2. Phone Number Formats

Both formats accepted:
- International: `+919876543210`
- Local: `9876543210`

### 3. Player Count

- Minimum: 11 players
- Maximum: 15 players
- Validation enforced on backend

### 4. Jersey Numbers

- Optional field
- Backend auto-assigns (1, 2, 3, ...) if not provided
- Can be customized from frontend

### 5. Error Handling

- Always check `success` field in response
- Parse `message` for user-friendly error
- Use `details` array for field-specific errors
- Log `error` field for debugging

---

## OpenAPI / Swagger Documentation

**Interactive API Docs**: `http://localhost:8000/docs`  
**ReDoc Documentation**: `http://localhost:8000/redoc`  
**OpenAPI JSON Schema**: `http://localhost:8000/openapi.json`

---

## Support & Troubleshooting

### Common Issues

**Issue 1: 422 Validation Error - Player Count**
- **Cause**: Less than 11 or more than 15 players
- **Solution**: Ensure players array has 11-15 items

**Issue 2: 422 Validation Error - Invalid Email**
- **Cause**: Email format incorrect
- **Solution**: Use valid email format (e.g., user@example.com)

**Issue 3: 400 Bad Request - Jersey Number**
- **Cause**: Null or invalid jersey number
- **Solution**: Omit jersey_number field (backend auto-assigns)

**Issue 4: 404 Not Found - Team**
- **Cause**: Invalid team_id
- **Solution**: Verify team_id from registration response

**Issue 5: 500 Internal Server Error**
- **Cause**: Database connection or server error
- **Solution**: Check server logs and database connectivity

### Debug Mode

Enable debug logging in `.env`:
```
LOG_LEVEL=DEBUG
```

Check server logs for detailed error information.

---

## Changelog

### Version 1.0.0 (Current)
- ✅ Initial release
- ✅ Team registration with 11-15 players
- ✅ Base64 file uploads
- ✅ Admin panel endpoints
- ✅ Group photo support
- ✅ Comprehensive validation
- ✅ Auto jersey number assignment

---

## Contact & Support

- **Project Repository**: [ICCT26-BACKEND](https://github.com/sanjaynesan-05/ICCT26-BACKEND)
- **API Base URL**: `https://icct26-backend.onrender.com`
- **Documentation**: `/docs` (Swagger UI)

---

**Last Updated**: November 16, 2025  
**API Version**: 1.0.0  
**Maintained By**: ICCT26 Backend Team
