# API Quick Reference Guide

**ICCT26 Backend API** - Quick reference for developers

---

## Base URLs

- **Production**: `https://icct26-backend.onrender.com`
- **Local**: `http://localhost:8000`
- **Interactive Docs**: `/docs`

---

## Quick Endpoints List

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Home / API info | No |
| GET | `/health` | Health check | No |
| GET | `/status` | API status with DB check | No |
| GET | `/queue/status` | Queue status | No |
| POST | `/api/register/team` | Register team + players | No |
| GET | `/api/register/health` | Registration health | No |
| GET | `/api/teams` | List all teams (paginated) | No |
| GET | `/api/teams/{team_id}` | Get team details | No |
| GET | `/admin/teams` | Admin: all teams | No* |
| GET | `/admin/teams/{team_id}` | Admin: team details | No* |
| GET | `/admin/players/{player_id}` | Admin: player details | No* |

*Admin endpoints will require authentication in future

---

## Most Used Endpoints

### 1. Register Team (POST `/api/register/team`)

**Minimal Request**:
```json
{
  "churchName": "Church Name",
  "teamName": "Team Name",
  "captain": {
    "name": "Captain Name",
    "phone": "+919876543210",
    "whatsapp": "9876543210",
    "email": "captain@example.com"
  },
  "viceCaptain": {
    "name": "Vice Captain Name",
    "phone": "+919876543211",
    "whatsapp": "9876543211",
    "email": "vice@example.com"
  },
  "players": [
    {"name": "Player 1", "age": 25, "phone": "+919800000001", "role": "Batsman"},
    {"name": "Player 2", "age": 26, "phone": "+919800000002", "role": "Bowler"}
    // ... 9 more players (11 total minimum)
  ]
}
```

**Response (201)**:
```json
{
  "success": true,
  "message": "Team and players registered successfully",
  "team_id": "ICCT26-20251116103045",
  "team_name": "Team Name",
  "player_count": 11,
  "registration_date": "2025-11-16T10:30:45.123456"
}
```

---

### 2. Get All Teams (GET `/api/teams`)

**Request**:
```bash
curl "http://localhost:8000/api/teams?skip=0&limit=10"
```

**Response (200)**:
```json
{
  "success": true,
  "total_teams": 25,
  "teams": [
    {
      "team_id": "ICCT26-20251116103045",
      "team_name": "Warriors",
      "church_name": "St. Mary's Church",
      "captain_name": "John Doe",
      "registration_date": "2025-11-16T10:30:45.123456"
    }
  ]
}
```

---

### 3. Get Team Details (GET `/api/teams/{team_id}`)

**Request**:
```bash
curl "http://localhost:8000/api/teams/ICCT26-20251116103045"
```

**Response (200)**:
```json
{
  "success": true,
  "team": {
    "team_id": "ICCT26-20251116103045",
    "team_name": "Warriors",
    "captain": {...},
    "viceCaptain": {...}
  },
  "players": [...]
}
```

---

## Field Requirements

### Team Registration

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| churchName | string | ✅ Yes | 1-200 chars |
| teamName | string | ✅ Yes | 1-200 chars |
| pastorLetter | string | ❌ No | Base64 (JPEG/PNG/PDF) |
| paymentReceipt | string | ❌ No | Base64 (JPEG/PNG/PDF) |
| groupPhoto | string | ❌ No | Base64 (JPEG/PNG only) |
| captain | object | ✅ Yes | See below |
| viceCaptain | object | ✅ Yes | See below |
| players | array | ✅ Yes | 11-15 items |

### Captain / Vice-Captain

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| name | string | ✅ Yes | 1-150 chars |
| phone | string | ✅ Yes | 7-20 chars, digits or +prefix |
| whatsapp | string | ✅ Yes | 10-20 chars, digits or +prefix |
| email | string | ✅ Yes | Valid email format |

### Player

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| name | string | ✅ Yes | 1-150 chars |
| age | number | ✅ Yes | 15-65 |
| phone | string | ✅ Yes | 7-15 chars |
| role | string | ✅ Yes | 1-20 chars |
| jersey_number | string | ❌ No | Auto-assigned if missing |
| aadharFile | string | ❌ No | Base64 PDF |
| subscriptionFile | string | ❌ No | Base64 PDF |

---

## File Upload Format

**Required Format**:
```
data:image/jpeg;base64,/9j/4AAQSkZJRg...
```

**Supported MIME Types**:
- `image/jpeg` - JPEG images
- `image/png` - PNG images  
- `application/pdf` - PDF documents

**File Size Limit**: 5MB per file

**Example**:
```json
{
  "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "groupPhoto": "data:image/png;base64,iVBORw0KGgo..."
}
```

---

## Common Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | GET requests successful |
| 201 | Created | Team registered successfully |
| 400 | Bad Request | Database constraint violation |
| 404 | Not Found | Team/player not found |
| 422 | Validation Error | Invalid input format |
| 500 | Server Error | Database connection failed |

---

## Quick Test Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### Register Team (11 players)
```bash
curl -X POST http://localhost:8000/api/register/team \
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
      "name": "Test Vice",
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
  }'
```

### Get All Teams
```bash
curl http://localhost:8000/api/teams?skip=0&limit=10
```

### Get Team Details
```bash
curl http://localhost:8000/api/teams/ICCT26-20251116103045
```

---

## Response Format

**Success Response**:
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {...}
}
```

**Error Response**:
```json
{
  "success": false,
  "message": "Error description",
  "field": "fieldName",
  "error_type": "validation_error",
  "status_code": 422
}
```

---

## Tips & Tricks

1. **Use Interactive Docs**: Visit `/docs` for interactive API testing
2. **Jersey Numbers**: Omit jersey_number field for auto-assignment
3. **Phone Formats**: Both `+919876543210` and `9876543210` accepted
4. **Player Count**: Must be 11-15 players (strict validation)
5. **File Size**: Keep files under 5MB for best performance
6. **Pagination**: Use `skip` and `limit` for large team lists
7. **Team IDs**: Format is `ICCT26-YYYYMMDDHHmmss`

---

## Need More Details?

📚 **Complete Documentation**: `docs/api-reference/COMPLETE_API_ENDPOINTS.md`  
🔗 **Interactive Docs**: `http://localhost:8000/docs`  
📖 **ReDoc**: `http://localhost:8000/redoc`

---

**Quick Reference v1.0** | Last Updated: November 16, 2025
