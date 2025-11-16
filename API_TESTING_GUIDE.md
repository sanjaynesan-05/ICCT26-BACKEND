# API Testing Guide - ICCT26 Backend

## Quick Links

- **Production API**: https://icct26-backend.onrender.com
- **API Documentation**: https://icct26-backend.onrender.com/docs
- **Alternative Docs**: https://icct26-backend.onrender.com/redoc
- **OpenAPI Schema**: https://icct26-backend.onrender.com/openapi.json

---

## Testing Tools

### Option 1: Python Test Suite (Recommended)
```bash
# Run comprehensive tests
python test_production_render.py

# Shows:
# - Health check
# - Team registration (with and without group photo)
# - Get all teams
# - Get team details
# - Error handling
```

### Option 2: Quick Shell Script
```bash
bash test_quick.sh
```

### Option 3: Manual cURL Commands
```bash
# Health Check
curl https://icct26-backend.onrender.com/health

# Get All Teams
curl https://icct26-backend.onrender.com/admin/teams

# Get Team Details
curl https://icct26-backend.onrender.com/admin/teams/ICCT26-0001

# OpenAPI Schema
curl https://icct26-backend.onrender.com/openapi.json
```

### Option 4: Postman/Insomnia
1. Import OpenAPI schema from: `https://icct26-backend.onrender.com/openapi.json`
2. Or manually create requests in Postman

### Option 5: Browser
Simply visit:
- https://icct26-backend.onrender.com/health - Status
- https://icct26-backend.onrender.com/docs - Interactive API docs
- https://icct26-backend.onrender.com/admin/teams - Teams JSON

---

## API Endpoints

### Core Endpoints

#### 1. Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "ICCT26 Registration API",
  "timestamp": "2025-11-16T16:17:23.654061",
  "version": "1.0.0"
}
```

#### 2. Register Team (NEW WITH GROUP PHOTO)
```
POST /api/register/team
```
**Request Body:**
```json
{
  "churchName": "Church Name",
  "teamName": "Team Name",
  "pastorLetter": "base64_pdf_string",
  "paymentReceipt": "base64_png_string",
  "groupPhoto": "base64_png_string",
  "captain": {
    "name": "Captain Name",
    "phone": "9876543210",
    "email": "captain@example.com",
    "whatsapp": "9876543210"
  },
  "viceCaptain": {
    "name": "Vice Captain Name",
    "phone": "9876543211",
    "email": "vice@example.com",
    "whatsapp": "9876543211"
  },
  "players": [
    {
      "name": "Player Name",
      "role": "Batsman",
      "aadharFile": "base64_pdf_string",
      "subscriptionFile": "base64_pdf_string"
    }
  ]
}
```

**Response (201/200):**
```json
{
  "success": true,
  "message": "Team registered successfully",
  "team_id": "ICCT26-0001",
  "team_name": "Team Name",
  "church_name": "Church Name",
  "captain_name": "Captain Name",
  "vice_captain_name": "Vice Captain Name",
  "player_count": 11,
  "registration_date": "2025-11-16T16:17:23"
}
```

#### 3. Get All Teams (NOW INCLUDES GROUP PHOTO)
```
GET /admin/teams
```
**Response:**
```json
[
  {
    "teamId": "ICCT26-0001",
    "teamName": "Team Name",
    "churchName": "Church Name",
    "captainName": "Captain Name",
    "captainPhone": "9876543210",
    "captainEmail": "captain@example.com",
    "viceCaptainName": "Vice Captain Name",
    "viceCaptainPhone": "9876543211",
    "viceCaptainEmail": "vice@example.com",
    "playerCount": 11,
    "registrationDate": "2025-11-16T16:17:23",
    "paymentReceipt": "data:image/png;base64,iVBORw0K...",
    "pastorLetter": "data:application/pdf;base64,JVBERi0...",
    "groupPhoto": "data:image/png;base64,iVBORw0K..."
  }
]
```

#### 4. Get Team Details (NOW INCLUDES GROUP PHOTO)
```
GET /admin/teams/{team_id}
```
**Response:**
```json
{
  "team": {
    "teamId": "ICCT26-0001",
    "teamName": "Team Name",
    "churchName": "Church Name",
    "captain": {
      "name": "Captain Name",
      "phone": "9876543210",
      "email": "captain@example.com"
    },
    "viceCaptain": {
      "name": "Vice Captain Name",
      "phone": "9876543211",
      "email": "vice@example.com"
    },
    "paymentReceipt": "data:image/png;base64,iVBORw0K...",
    "pastorLetter": "data:application/pdf;base64,JVBERi0...",
    "groupPhoto": "data:image/png;base64,iVBORw0K...",
    "registrationDate": "2025-11-16T16:17:23"
  },
  "players": [
    {
      "playerId": "ICCT26-0001-P01",
      "name": "Player Name",
      "role": "Batsman",
      "aadharFile": "data:application/pdf;base64,JVBERi0...",
      "subscriptionFile": "data:application/pdf;base64,JVBERi0..."
    }
  ]
}
```

#### 5. Get Teams List
```
GET /api/teams
```
**Response:** Array of teams

#### 6. Get Single Team (by ID)
```
GET /api/teams/{team_id}
```

#### 7. Get Player Details
```
GET /admin/players/{player_id}
```

#### 8. Server Status
```
GET /status
```

#### 9. Queue Status
```
GET /queue/status
```

---

## Testing the Group Photo Feature

### Manual Test 1: Register WITH Group Photo

Using cURL:
```bash
curl -X POST https://icct26-backend.onrender.com/api/register/team \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "Test Church",
    "teamName": "Test Team with Photo",
    "pastorLetter": "base64_string_here",
    "paymentReceipt": "base64_string_here",
    "groupPhoto": "base64_string_here",
    "captain": {
      "name": "John Doe",
      "phone": "9876543210",
      "email": "john@example.com",
      "whatsapp": "9876543210"
    },
    "viceCaptain": {
      "name": "Jane Doe",
      "phone": "9876543211",
      "email": "jane@example.com",
      "whatsapp": "9876543211"
    },
    "players": [
      {
        "name": "Player 1",
        "role": "Batsman",
        "aadharFile": "base64_string_here",
        "subscriptionFile": "base64_string_here"
      }
    ]
  }'
```

### Manual Test 2: Register WITHOUT Group Photo (Optional)

Same as above but omit the `groupPhoto` field.

### Manual Test 3: Verify Group Photo in Response

```bash
# Get all teams
curl https://icct26-backend.onrender.com/admin/teams

# Check response for:
# - groupPhoto field present
# - Value starts with "data:image/png;base64,"
# - Or is null if not uploaded

# Get specific team
curl https://icct26-backend.onrender.com/admin/teams/{team_id}

# Check response team object for groupPhoto field
```

---

## File Format Reference

### Base64 Encoding (for file fields)

Files must be sent as Base64-encoded strings:

```javascript
// JavaScript example
const file = document.getElementById('fileInput').files[0];
const reader = new FileReader();

reader.onload = (e) => {
  const base64String = e.target.result.split(',')[1]; // Remove data URI prefix
  // Use base64String in API request
};

reader.readAsDataURL(file);
```

### Accepted File Types

| Field | Type | Format |
|-------|------|--------|
| groupPhoto | Image | JPEG, PNG |
| paymentReceipt | Image | PNG |
| pastorLetter | Document | PDF |
| aadharFile | Document | PDF |
| subscriptionFile | Document | PDF |

### Response File Format

Files in responses are returned as **data URIs**:

```
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==
```

✅ Can be used directly in `<img src="">` tags in HTML/JavaScript

---

## Troubleshooting

### Issue: Service Timeout
**Solution:**
1. Wait 30-60 seconds (Render free tier spins down)
2. Try again - service will wake up
3. Check Render dashboard for errors

### Issue: 404 on Endpoints
**Solution:**
1. Verify correct endpoint path (check OpenAPI schema)
2. Ensure URL has correct prefix: `/api/register/team` or `/admin/teams`

### Issue: Invalid Base64
**Solution:**
1. Ensure file is properly Base64 encoded
2. Remove `data:image/...;base64,` prefix before sending
3. Check file size (max recommended 5MB)

### Issue: Missing Fields
**Solution:**
1. Check all required fields are present
2. Verify field names (camelCase: `groupPhoto`, `teamName`)
3. Check data types (strings, not objects for file fields)

### Issue: Database Connection Error
**Solution:**
1. Check Neon PostgreSQL connection in Render dashboard
2. Verify DATABASE_URL environment variable
3. Check if database tables exist (migration ran)

---

## Performance Notes

- Average response time: 200-500ms
- Maximum request size: Depends on server config
- File field maximum: Unlimited (stored as TEXT)
- Payload size: Recommend keep Base64 files under 5MB each

---

## Security Notes

⚠️ **Important for Production:**

1. **CORS**: Configure for your frontend domain
2. **Rate Limiting**: Consider adding for `/api/register/team`
3. **Input Validation**: All files are validated for MIME type
4. **File Storage**: Base64 encoded in database (not filesystem)
5. **Database**: Use environment variables for credentials

---

## Testing Checklist

### ✓ Basic Connectivity
- [ ] Health check returns 200
- [ ] API documentation accessible
- [ ] OpenAPI schema loads

### ✓ Team Registration
- [ ] Register with all fields
- [ ] Register without groupPhoto (optional)
- [ ] Register with invalid data (should fail)
- [ ] Response includes team_id

### ✓ Group Photo Feature
- [ ] groupPhoto field accepted in request
- [ ] groupPhoto stored in database
- [ ] groupPhoto returned in GET all teams
- [ ] groupPhoto formatted as data URI
- [ ] groupPhoto can be displayed in browser

### ✓ Admin Endpoints
- [ ] Get all teams returns teams array
- [ ] Get team details returns team + players
- [ ] All file fields have data URI format
- [ ] Invalid team_id returns 404

### ✓ Error Handling
- [ ] Invalid team_id returns 404
- [ ] Missing required fields returns error
- [ ] Invalid file format returns error

---

## Files Generated

| File | Purpose |
|------|---------|
| `test_production_render.py` | Comprehensive Python test suite |
| `test_quick.sh` | Quick shell script tests |
| `TEST_REPORT_GROUP_PHOTO.md` | Test execution report |
| `API_TESTING_GUIDE.md` | This file - testing reference |

---

## Example: Complete Team Registration

See `docs/FRONTEND_GROUP_PHOTO_IMPLEMENTATION.md` for:
- Full code examples
- Step-by-step implementation
- TypeScript interfaces
- Validation rules
- React component examples

---

## Contact & Support

For issues or questions:
1. Check API documentation: `/docs`
2. Review OpenAPI schema: `/openapi.json`
3. Check test files for example requests
4. Review backend commit: `a95b899`

---

**Last Updated**: November 16, 2025  
**Feature**: Group Photo Upload for Teams  
**Status**: ✅ Ready for testing
