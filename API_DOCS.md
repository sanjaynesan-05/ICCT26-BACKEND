# ICCT26 Backend API Documentation

## Production-Hardened Registration Endpoint

### Base URL
```
Production: https://your-domain.com/api
Development: http://localhost:8000/api
```

---

## POST /register/team

Register a new team with full validation, duplicate protection, and reliability features.

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | Must be `multipart/form-data` |
| `Idempotency-Key` | No | Unique identifier to prevent duplicate submissions (recommended) |

### Form Fields

#### Team Information

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `team_name` | string | Yes | 3-80 chars | Team name |
| `church_name` | string | Yes | 3-50 chars | Church name |

#### Captain Information

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `captain_name` | string | Yes | 3-50 chars, letters/spaces/hyphens/apostrophes | Captain full name |
| `captain_phone` | string | Yes | Exactly 10 digits | Captain phone number |
| `captain_email` | string | Yes | Valid email (RFC 5322) | Captain email address |
| `captain_whatsapp` | string | Yes | Exactly 10 digits | Captain WhatsApp number |

#### Vice-Captain Information

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `vice_name` | string | Yes | 3-50 chars, letters/spaces/hyphens/apostrophes | Vice-captain full name |
| `vice_phone` | string | Yes | Exactly 10 digits | Vice-captain phone number |
| `vice_email` | string | Yes | Valid email (RFC 5322) | Vice-captain email address |
| `vice_whatsapp` | string | Yes | Exactly 10 digits | Vice-captain WhatsApp number |

#### Players (Optional)

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `players_json` | string | No | Valid JSON array | JSON array of player objects |

**Player Object Structure:**
```json
{
  "name": "Player Name",
  "role": "Batsman/Bowler/All-rounder/Wicket-keeper"
}
```

#### File Uploads

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `pastor_letter` | file | Yes | PNG/JPEG/PDF, max 5MB | Pastor recommendation letter |
| `payment_receipt` | file | No | PNG/JPEG/PDF, max 5MB | Payment receipt |
| `group_photo` | file | No | PNG/JPEG/PDF, max 5MB | Team group photo |

### Request Example

```bash
curl -X POST "https://your-domain.com/api/register/team" \
  -H "Idempotency-Key: unique-client-id-12345" \
  -F "team_name=Warriors" \
  -F "church_name=Grace Chapel" \
  -F "captain_name=John Doe" \
  -F "captain_phone=1234567890" \
  -F "captain_email=captain@example.com" \
  -F "captain_whatsapp=1234567890" \
  -F "vice_name=Jane Smith" \
  -F "vice_phone=0987654321" \
  -F "vice_email=vice@example.com" \
  -F "vice_whatsapp=0987654321" \
  -F 'players_json=[{"name":"Player 1","role":"Batsman"},{"name":"Player 2","role":"Bowler"}]' \
  -F "pastor_letter=@pastor_letter.pdf" \
  -F "payment_receipt=@receipt.png" \
  -F "group_photo=@team_photo.jpg"
```

### Success Response

**Status Code:** `201 Created`

```json
{
  "success": true,
  "team_id": "ICCT-001",
  "team_name": "Warriors",
  "message": "Team registered successfully",
  "email_sent": true,
  "player_count": 15
}
```

### Error Responses

#### Validation Error (400)

```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Captain phone must be exactly 10 digits",
  "details": {
    "field": "captain_phone",
    "value": "123"
  }
}
```

#### Duplicate Submission (409)

```json
{
  "success": false,
  "error_code": "DUPLICATE_SUBMISSION",
  "message": "Team with this name and captain phone already exists",
  "details": {
    "field": "team_name/captain_phone",
    "existing_value": "Warriors"
  }
}
```

#### File Too Large (400)

```json
{
  "success": false,
  "error_code": "FILE_TOO_LARGE",
  "message": "Pastor letter file size exceeds 5MB limit",
  "details": {
    "field": "pastor_letter",
    "max_size": "5MB"
  }
}
```

#### Invalid File Type (400)

```json
{
  "success": false,
  "error_code": "INVALID_MIME_TYPE",
  "message": "Pastor letter must be PNG, JPEG, or PDF",
  "details": {
    "field": "pastor_letter",
    "detected_type": "text/plain",
    "allowed_types": ["image/png", "image/jpeg", "application/pdf"]
  }
}
```

#### Upload Failed (500)

```json
{
  "success": false,
  "error_code": "CLOUDINARY_UPLOAD_FAILED",
  "message": "Failed to upload pastor_letter after 3 retries",
  "details": {
    "field": "pastor_letter",
    "retry_count": 3
  }
}
```

#### Internal Server Error (500)

```json
{
  "success": false,
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred during registration",
  "details": {
    "exception_type": "ValueError"
  }
}
```

---

## Error Code Reference

| Error Code | HTTP Status | Description | Common Causes |
|------------|-------------|-------------|---------------|
| `VALIDATION_FAILED` | 400 | Input validation error | Invalid format, too short/long, wrong characters |
| `DUPLICATE_SUBMISSION` | 409 | Team already registered | Same team_name + captain_phone, or same idempotency key |
| `FILE_TOO_LARGE` | 400 | File exceeds size limit | File > 5MB |
| `INVALID_MIME_TYPE` | 400 | Invalid file type | File is not PNG, JPEG, or PDF |
| `DB_WRITE_FAILED` | 500 | Database operation failed | Database connection issues, constraint violations |
| `CLOUDINARY_UPLOAD_FAILED` | 500 | File upload failed | Cloudinary service down, network issues (after 3 retries) |
| `EMAIL_FAILED` | 500 | Email send failed | SMTP service down (non-fatal, registration succeeds) |
| `TEAM_ID_GENERATION_FAILED` | 500 | Could not generate team ID | Database locking issues (rare) |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error | Unhandled exception, code bug |

---

## Validation Rules

### Names (Captain, Vice-Captain, Church, Players)

- **Length:** 3-50 characters
- **Allowed:** Letters (A-Z, a-z), spaces, hyphens (-), apostrophes (')
- **Examples:**
  - ✅ "John Doe"
  - ✅ "Mary-Jane O'Connor"
  - ✅ "José García"
  - ❌ "AB" (too short)
  - ❌ "John123" (contains numbers)

### Team Name

- **Length:** 3-80 characters
- **Allowed:** Letters, numbers, spaces, hyphens, apostrophes
- **Examples:**
  - ✅ "Warriors"
  - ✅ "Team Alpha 2024"
  - ❌ "AB" (too short)

### Phone Numbers

- **Format:** Exactly 10 digits
- **Allowed:** Numeric only (0-9)
- **Examples:**
  - ✅ "1234567890"
  - ✅ "9876543210"
  - ❌ "123456789" (too short)
  - ❌ "12345678901" (too long)
  - ❌ "abcdefghij" (non-numeric)

### Email Addresses

- **Format:** RFC 5322 compliant
- **Examples:**
  - ✅ "user@example.com"
  - ✅ "user.name+tag@domain.co.uk"
  - ❌ "invalid"
  - ❌ "@example.com"
  - ❌ "user@"

### Files

- **Size Limit:** 5MB (5,242,880 bytes)
- **Allowed Types:** PNG, JPEG, PDF
- **MIME Detection:** Uses `python-magic` for true file type detection (not just extension)
- **Security:** Filename sanitization to prevent path traversal attacks

---

## Idempotency

### What is Idempotency?

Idempotency ensures that duplicate requests don't create duplicate registrations. If the same request is sent multiple times (e.g., due to network issues, user double-clicking), only the first request is processed.

### How to Use

1. **Generate a unique key** on the client side (UUID recommended):
   ```javascript
   const idempotencyKey = crypto.randomUUID(); // "550e8400-e29b-41d4-a716-446655440000"
   ```

2. **Send the key in the header**:
   ```bash
   curl -X POST "https://your-domain.com/api/register/team" \
     -H "Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000" \
     -F "team_name=Warriors" \
     ...
   ```

3. **If the same key is sent again within 10 minutes**:
   - The cached response is returned immediately
   - No database write occurs
   - HTTP 409 status code is returned

### Key Properties

- **TTL:** 10 minutes (600 seconds)
- **Storage:** PostgreSQL database table
- **Cleanup:** Automatic (expired keys are removed)

---

## Retry Logic

### Cloudinary Uploads

- **Max Retries:** 3
- **Backoff Strategy:** Exponential
- **Delays:**
  - Attempt 1: Immediate
  - Attempt 2: +0.5 seconds
  - Attempt 3: +1.0 seconds
  - Attempt 4: +2.0 seconds

**Retried Errors:**
- Connection errors
- Timeout errors
- HTTP 5xx errors

### Email Sending

- **Max Retries:** 2
- **Backoff Strategy:** Exponential
- **Delays:**
  - Attempt 1: Immediate
  - Attempt 2: +1.0 seconds
  - Attempt 3: +2.0 seconds

**Behavior:**
- Email failures are **non-fatal**
- Registration succeeds even if email fails
- `email_sent` field in response indicates success/failure

---

## Monitoring & Logging

### Request Tracking

Every request is assigned a unique **Request ID** (`X-Request-ID` header) for tracing through logs.

### Structured Logs

All operations are logged in JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "request_id": "req_abc123",
  "event": "registration_started",
  "team_name": "Warriors",
  "client_ip": "192.168.1.1",
  "duration_ms": 1250
}
```

### Events Logged

| Event | Description |
|-------|-------------|
| `registration_started` | Request received |
| `validation_error` | Input validation failed |
| `file_upload` | File uploaded (success/failed) |
| `db_operation` | Database insert/update |
| `email_sent` | Email sent (success/failed) |
| `exception` | Unexpected error with stack trace |

---

## Rate Limiting (Recommended)

While not implemented in this backend, it's **strongly recommended** to add rate limiting at the API gateway or reverse proxy level:

- **Per IP:** 10 requests/minute
- **Per Idempotency Key:** 1 request/10 minutes

---

## Security Best Practices

### For Clients

1. ✅ **Always use HTTPS** in production
2. ✅ **Use Idempotency-Key** to prevent duplicates
3. ✅ **Validate files client-side** before upload (size, type)
4. ✅ **Sanitize user inputs** before sending
5. ✅ **Handle errors gracefully** with user-friendly messages

### For Backend

1. ✅ **Strong input validation** (implemented)
2. ✅ **Database constraints** (implemented)
3. ✅ **File size limits** (implemented)
4. ✅ **MIME type validation** (implemented)
5. ✅ **Request ID tracking** (implemented)
6. ✅ **Structured logging** (implemented)

---

## Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx aiosqlite

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_validation.py

# Run with coverage
pytest --cov=app tests/
```

### Test Files

- `tests/test_race_safe_id.py` - Team ID generation tests
- `tests/test_validation.py` - Input validation tests
- `tests/test_idempotency.py` - Idempotency key tests
- `tests/test_registration_integration.py` - End-to-end tests

---

## Support

For issues or questions:
- Check error codes and validation rules above
- Review structured logs for request ID
- Verify file sizes and MIME types
- Ensure database constraints are met
