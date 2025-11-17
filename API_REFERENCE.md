# API_REFERENCE.md

## ICCT26 Backend API Reference

**Base URL**: `https://api.icct26.com`  
**Version**: 1.0.0  
**Last Updated**: November 18, 2025

---

## Table of Contents

1. [Authentication](#authentication)
2. [Request/Response Format](#requestresponse-format)
3. [Team Registration](#team-registration)
4. [Admin Endpoints](#admin-endpoints)
5. [Utility Endpoints](#utility-endpoints)
6. [Error Codes](#error-codes)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

---

## Authentication

### API Key Authentication

All requests (except health check) require API key authentication.

```
Header: X-API-Key: your-api-key
```

### Idempotency

To prevent duplicate submissions, include an idempotency key:

```
Header: X-Idempotency-Key: unique-key-per-request
```

**Key Requirements**:
- Must be unique per request
- Format: UUID or any 32+ character string
- TTL: 10 minutes (after which key expires and duplicate is allowed)

---

## Request/Response Format

### Content-Type

- **Requests**: `multipart/form-data` (for file uploads)
- **Responses**: `application/json`

### Request Headers

```
Content-Type: multipart/form-data
X-API-Key: your-api-key
X-Idempotency-Key: unique-key-per-request
```

### Response Format

**All responses follow this format**:

```json
{
  "success": boolean,
  "team_id": "string (if successful)",
  "message": "string (human-readable message)",
  "error_code": "string (if error)",
  "details": {
    "field_errors": {},
    "errors": []
  }
}
```

### Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 408 | Request Timeout |
| 409 | Conflict (duplicate submission) |
| 413 | Payload Too Large |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

---

## Team Registration

### POST /api/registration

Register a new team for ICCT26.

#### Request

```http
POST /api/registration HTTP/1.1
Host: api.icct26.com
Content-Type: multipart/form-data
X-API-Key: your-api-key
X-Idempotency-Key: unique-key-per-request

---
Content-Disposition: form-data; name="team_name"

Warriors United
---
Content-Disposition: form-data; name="church_name"

Grace Community Church
---
Content-Disposition: form-data; name="captain_name"

John Doe
---
Content-Disposition: form-data; name="captain_phone"

1234567890
---
Content-Disposition: form-data; name="captain_email"

john@example.com
---
Content-Disposition: form-data; name="captain_whatsapp"

1234567890
---
Content-Disposition: form-data; name="coach_name"

Jane Smith
---
Content-Disposition: form-data; name="logo"; filename="logo.png"
Content-Type: image/png

[Binary PNG data]
---
Content-Disposition: form-data; name="players"

[
  {
    "name": "Player One",
    "role": "Batsman",
    "phone": "9876543210"
  },
  {
    "name": "Player Two",
    "role": "Bowler",
    "phone": "9876543211"
  }
]
---
```

#### Response (Success - 200)

```json
{
  "success": true,
  "team_id": "ICCT-001",
  "message": "Team registered successfully. Confirmation email sent."
}
```

#### Response (Validation Error - 422)

```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Input validation failed",
  "details": {
    "field_errors": {
      "team_name": "Team name must be between 3 and 80 characters",
      "captain_email": "Invalid email format"
    }
  }
}
```

#### Response (Duplicate - 409)

```json
{
  "success": false,
  "error_code": "DUPLICATE_SUBMISSION",
  "message": "Duplicate submission detected (within 10 minutes)"
}
```

#### Field Validation Rules

| Field | Type | Min | Max | Format | Required |
|-------|------|-----|-----|--------|----------|
| team_name | string | 3 | 80 | Alphanumeric, spaces, hyphens | Yes |
| church_name | string | 3 | 80 | Alphanumeric, spaces, hyphens | Yes |
| captain_name | string | 3 | 50 | Letters, spaces, hyphens, apostrophes | Yes |
| captain_phone | string | 10 | 10 | Numeric digits | Yes |
| captain_email | string | 5 | 255 | Valid email format | Yes |
| captain_whatsapp | string | 10 | 10 | Numeric digits | Yes |
| coach_name | string | 3 | 50 | Letters, spaces, hyphens, apostrophes | Yes |
| logo | file | - | 5MB | PNG, JPEG | Yes |
| players | array | 1 | 20 | JSON array of objects | Yes |

#### Players Array Format

```json
[
  {
    "name": "string (3-50 chars, required)",
    "role": "string (1-30 chars, required)",
    "phone": "string (10 digits, optional)"
  }
]
```

---

## Admin Endpoints

### GET /admin/teams

Get all registered teams (admin only).

#### Request

```http
GET /admin/teams HTTP/1.1
Host: api.icct26.com
X-API-Key: admin-api-key
```

#### Response

```json
{
  "success": true,
  "teams": [
    {
      "team_id": "ICCT-001",
      "team_name": "Warriors United",
      "registered_at": "2025-11-18T10:30:00Z",
      "captain": "John Doe"
    }
  ],
  "total_count": 1
}
```

### GET /admin/teams/{team_id}

Get specific team details.

#### Request

```http
GET /admin/teams/ICCT-001 HTTP/1.1
Host: api.icct26.com
X-API-Key: admin-api-key
```

#### Response

```json
{
  "success": true,
  "team": {
    "team_id": "ICCT-001",
    "team_name": "Warriors United",
    "church_name": "Grace Community Church",
    "captain": {
      "name": "John Doe",
      "phone": "1234567890",
      "email": "john@example.com",
      "whatsapp": "1234567890"
    },
    "coach": "Jane Smith",
    "logo_url": "https://res.cloudinary.com/...",
    "players": [
      {
        "name": "Player One",
        "role": "Batsman",
        "phone": "9876543210"
      }
    ],
    "registered_at": "2025-11-18T10:30:00Z"
  }
}
```

---

## Utility Endpoints

### GET /health

Health check endpoint.

```http
GET /health HTTP/1.1
Host: api.icct26.com

Response:
{
  "status": "healthy",
  "timestamp": "2025-11-18T10:30:00Z"
}
```

### GET /status

Server status and metrics.

```http
GET /status HTTP/1.1
Host: api.icct26.com

Response:
{
  "status": "running",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 3600,
  "database": "connected",
  "cloudinary": "connected"
}
```

### GET /docs

Swagger API documentation.

```
https://api.icct26.com/docs
```

---

## Error Codes

### Standard Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| VALIDATION_FAILED | 422 | Input validation failed |
| DUPLICATE_SUBMISSION | 409 | Duplicate submission (within idempotency window) |
| FILE_TOO_LARGE | 413 | File exceeds 5MB limit |
| INVALID_MIME_TYPE | 422 | File format not allowed |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests (>30/min) |
| REQUEST_TIMEOUT | 408 | Request exceeded 60s timeout |
| BODY_TOO_LARGE | 413 | Request body exceeds 10MB |
| DB_ERROR | 500 | Database connection error |
| CLOUDINARY_ERROR | 500 | File upload failed (retried 3x) |
| SMTP_ERROR | 500 | Email notification failed |
| INTERNAL_SERVER_ERROR | 500 | Unexpected server error |

---

## Rate Limiting

### Limits

- **30 requests per minute per IP address**
- Rate window: Rolling 1-minute window
- Applies to: All endpoints (except /health, /status)

### Headers

**Request**:
```
X-Idempotency-Key: unique-key
```

**Response** (when limited):
```
HTTP/1.1 429 Too Many Requests

{
  "success": false,
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Max 30 per minute."
}
```

### Retry Strategy

```python
# Recommended client-side retry logic
import time
import random

max_retries = 3
base_delay = 1

for attempt in range(max_retries):
    try:
        response = make_request()
        if response.status_code != 429:
            return response
    except Exception as e:
        pass
    
    if attempt < max_retries - 1:
        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
        time.sleep(delay)
```

---

## Examples

### cURL Examples

#### Team Registration

```bash
curl -X POST https://api.icct26.com/api/registration \
  -H "X-API-Key: your-api-key" \
  -H "X-Idempotency-Key: unique-key-123" \
  -F "team_name=Warriors United" \
  -F "church_name=Grace Church" \
  -F "captain_name=John Doe" \
  -F "captain_phone=1234567890" \
  -F "captain_email=john@example.com" \
  -F "captain_whatsapp=1234567890" \
  -F "coach_name=Jane Smith" \
  -F "logo=@logo.png" \
  -F 'players=[{"name":"Player One","role":"Batsman"}]'
```

#### Get All Teams

```bash
curl -X GET https://api.icct26.com/admin/teams \
  -H "X-API-Key: admin-api-key"
```

#### Get Team Details

```bash
curl -X GET https://api.icct26.com/admin/teams/ICCT-001 \
  -H "X-API-Key: admin-api-key"
```

### Python Examples

```python
import requests
import json
import uuid

# Setup
BASE_URL = "https://api.icct26.com"
API_KEY = "your-api-key"
IDEMPOTENCY_KEY = str(uuid.uuid4())

# Register Team
files = {
    'team_name': (None, 'Warriors United'),
    'church_name': (None, 'Grace Church'),
    'captain_name': (None, 'John Doe'),
    'captain_phone': (None, '1234567890'),
    'captain_email': (None, 'john@example.com'),
    'captain_whatsapp': (None, '1234567890'),
    'coach_name': (None, 'Jane Smith'),
    'logo': ('logo.png', open('logo.png', 'rb')),
    'players': (None, json.dumps([
        {"name": "Player One", "role": "Batsman"}
    ]))
}

headers = {
    'X-API-Key': API_KEY,
    'X-Idempotency-Key': IDEMPOTENCY_KEY
}

response = requests.post(
    f"{BASE_URL}/api/registration",
    files=files,
    headers=headers
)

print(response.json())
```

---

## Changelog

### Version 1.0.0 (November 18, 2025)

- Initial production release
- Team registration endpoint
- Admin endpoints
- Rate limiting (30 req/min/IP)
- Idempotency support
- File upload with Cloudinary
- Email notifications
- Structured logging
- Global exception handling

---

**Document Version**: 1.0.0  
**Last Updated**: November 18, 2025  
**API Status**: Production ✅
