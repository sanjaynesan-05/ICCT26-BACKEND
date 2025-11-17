# KNOWN_ERROR_CODES.md

## Error Codes Reference

**Last Updated**: November 18, 2025

---

## Overview

All API errors follow a standardized JSON format:

```json
{
  "success": false,
  "error_code": "ERROR_CODE_HERE",
  "message": "Human-readable error message",
  "details": {
    "field_errors": {},
    "errors": []
  }
}
```

---

## Error Categories

### Validation Errors (4xx)

| Code | HTTP | Message | Cause | Fix |
|------|------|---------|-------|-----|
| VALIDATION_FAILED | 422 | Input validation failed | One or more fields invalid | Check field validation rules in API_REFERENCE.md |
| INVALID_FILE_MIME | 422 | File format not allowed | Logo is not PNG/JPEG | Use PNG or JPEG format |
| FILE_TOO_LARGE | 413 | File exceeds 5MB limit | Logo file > 5MB | Compress image to <5MB |
| INVALID_EMAIL | 422 | Invalid email format | Email doesn't match RFC 5322 | Use valid email address |
| INVALID_PHONE | 422 | Invalid phone format | Phone not 10 digits | Use exactly 10 digits |
| NAME_TOO_SHORT | 422 | Name too short | Name < 3 characters | Use at least 3 characters |
| NAME_TOO_LONG | 422 | Name too long | Name > limit | Shorten name |
| INVALID_CHARACTERS | 422 | Field contains invalid characters | Special characters not allowed | Use only alphanumeric, spaces, hyphens |

### Duplicate & Idempotency Errors (4xx)

| Code | HTTP | Message | Cause | Fix |
|------|------|---------|-------|-----|
| DUPLICATE_SUBMISSION | 409 | Duplicate submission detected | Same idempotency key within 10 min | Use new unique idempotency key |
| IDEMPOTENCY_CONFLICT | 409 | Idempotency key already used | Different request with same key | Generate new idempotency key |

### Rate Limiting (4xx)

| Code | HTTP | Message | Cause | Fix |
|------|------|---------|-------|-----|
| RATE_LIMIT_EXCEEDED | 429 | Too many requests | >30 requests per minute from IP | Wait 1 minute, implement exponential backoff |

### Timeout (4xx)

| Code | HTTP | Message | Cause | Fix |
|------|------|---------|-------|-----|
| REQUEST_TIMEOUT | 408 | Request timeout exceeded | Request took >60 seconds | Check server load, retry with backoff |
| BODY_TOO_LARGE | 413 | Request body too large | Request body > 10MB | Reduce payload size |

### Server Errors (5xx)

| Code | HTTP | Message | Cause | Fix |
|------|------|---------|-------|-----|
| INTERNAL_SERVER_ERROR | 500 | Internal server error | Unexpected server error | Contact support, check logs |
| DB_ERROR | 500 | Database connection error | Cannot connect to database | Check database is running, network is accessible |
| CLOUDINARY_ERROR | 500 | File upload failed (retried 3x) | Cloudinary API unreachable | Check Cloudinary API status, retry later |
| SMTP_ERROR | 500 | Email notification failed | SMTP server unreachable | Check SMTP configuration, retry later |

---

## Common Error Scenarios

### Scenario 1: Team Name Validation

**Request**:
```json
{
  "team_name": "AB"  // Too short
}
```

**Response**:
```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Input validation failed",
  "details": {
    "field_errors": {
      "team_name": "Name must be between 3 and 80 characters"
    }
  }
}
```

**Fix**: Use team name with 3+ characters

### Scenario 2: Invalid Email

**Request**:
```json
{
  "captain_email": "invalid-email"  // Missing @
}
```

**Response**:
```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Input validation failed",
  "details": {
    "field_errors": {
      "captain_email": "Invalid email format"
    }
  }
}
```

**Fix**: Use valid email address (e.g., user@example.com)

### Scenario 3: Phone Number Format

**Request**:
```json
{
  "captain_phone": "123456789"  // 9 digits
}
```

**Response**:
```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Input validation failed",
  "details": {
    "field_errors": {
      "captain_phone": "Phone must be exactly 10 digits"
    }
  }
}
```

**Fix**: Use exactly 10 digit phone number

### Scenario 4: File Too Large

**Request**:
```
POST /api/registration
[Binary file: 6MB PNG]
```

**Response**:
```json
{
  "success": false,
  "error_code": "FILE_TOO_LARGE",
  "message": "File exceeds 5MB limit",
  "details": {
    "max_size": 5242880,
    "received_size": 6291456
  }
}
```

**Fix**: Compress image to <5MB

### Scenario 5: Invalid File Format

**Request**:
```
POST /api/registration
[Binary file: logo.gif]
```

**Response**:
```json
{
  "success": false,
  "error_code": "INVALID_FILE_MIME",
  "message": "File format not allowed",
  "details": {
    "received": "image/gif",
    "allowed": ["image/png", "image/jpeg"]
  }
}
```

**Fix**: Use PNG or JPEG format

### Scenario 6: Duplicate Submission

**Request 1**:
```
POST /api/registration
X-Idempotency-Key: key-123
[Team data]
```

**Response**: 200 OK

**Request 2** (same idempotency key within 10 minutes):
```
POST /api/registration
X-Idempotency-Key: key-123
[Different team data]
```

**Response**:
```json
{
  "success": false,
  "error_code": "DUPLICATE_SUBMISSION",
  "message": "Duplicate submission detected (within 10 minutes)"
}
```

**Fix**: Use new unique idempotency key, or wait 10+ minutes

### Scenario 7: Rate Limit

**Request**: 31 requests in 60 seconds from same IP

**Response**:
```json
{
  "success": false,
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Max 30 per minute."
}
```

**Fix**: Implement exponential backoff retry strategy

### Scenario 8: Request Timeout

**Request**: Large file upload that takes >60 seconds

**Response**:
```json
{
  "success": false,
  "error_code": "REQUEST_TIMEOUT",
  "message": "Request timeout exceeded (60s limit)"
}
```

**Fix**: 
1. Compress file before uploading
2. Check network connectivity
3. Retry with backoff

### Scenario 9: Database Error

**Cause**: Database server down or unreachable

**Response**:
```json
{
  "success": false,
  "error_code": "DB_ERROR",
  "message": "Database connection failed",
  "details": {
    "retry_after": 5
  }
}
```

**Fix**: 
1. Check database server is running
2. Check network connectivity
3. Retry after 5+ seconds

### Scenario 10: Cloudinary Error

**Cause**: File upload to Cloudinary fails (retried 3x)

**Response**:
```json
{
  "success": false,
  "error_code": "CLOUDINARY_ERROR",
  "message": "File upload failed after 3 retries",
  "details": {
    "reason": "API rate limit exceeded"
  }
}
```

**Fix**: 
1. Check Cloudinary API credentials
2. Check Cloudinary API status
3. Retry after 60+ seconds
4. Contact Cloudinary support if persistent

---

## Error Code Matrix

### By HTTP Status Code

```
4xx Client Errors
├── 400 Bad Request
│   ├── VALIDATION_FAILED
│   └── INVALID_CHARACTERS
├── 408 Request Timeout
│   └── REQUEST_TIMEOUT
├── 409 Conflict
│   ├── DUPLICATE_SUBMISSION
│   └── IDEMPOTENCY_CONFLICT
├── 413 Payload Too Large
│   ├── FILE_TOO_LARGE
│   └── BODY_TOO_LARGE
├── 422 Unprocessable Entity
│   ├── VALIDATION_FAILED
│   ├── INVALID_FILE_MIME
│   ├── INVALID_EMAIL
│   ├── INVALID_PHONE
│   ├── NAME_TOO_SHORT
│   ├── NAME_TOO_LONG
│   └── INVALID_CHARACTERS
└── 429 Too Many Requests
    └── RATE_LIMIT_EXCEEDED

5xx Server Errors
└── 500 Internal Server Error
    ├── INTERNAL_SERVER_ERROR
    ├── DB_ERROR
    ├── CLOUDINARY_ERROR
    └── SMTP_ERROR
```

---

## Recovery Procedures

### Transient Errors (Retry)

Errors that may resolve with retry:
- `REQUEST_TIMEOUT` (408)
- `RATE_LIMIT_EXCEEDED` (429)
- `DB_ERROR` (500)
- `CLOUDINARY_ERROR` (500)
- `SMTP_ERROR` (500)

**Strategy**: Exponential backoff, max 3 retries

### Permanent Errors (No Retry)

Errors that won't resolve with retry:
- `VALIDATION_FAILED` (422)
- `INVALID_FILE_MIME` (422)
- `FILE_TOO_LARGE` (413)
- `INVALID_EMAIL` (422)
- `INVALID_PHONE` (422)
- `DUPLICATE_SUBMISSION` (409)

**Strategy**: Fix input, don't retry

---

## Error Logging

All errors are logged with:
- Timestamp
- Request ID (for correlation)
- Error code
- User-facing message
- Internal details (not exposed to client)
- Stack trace (for 5xx errors)

**Log Location**: `logs/app.log` (JSON format)

---

## Support

For errors not in this document:

1. **Check logs**: `tail -f logs/app.log | grep REQUEST_ID`
2. **Review API_REFERENCE.md**: Full API specification
3. **Check system status**: `curl https://api.icct26.com/status`
4. **Contact support**: Provide error code and request ID

---

**Document Version**: 1.0.0  
**Last Updated**: November 18, 2025
