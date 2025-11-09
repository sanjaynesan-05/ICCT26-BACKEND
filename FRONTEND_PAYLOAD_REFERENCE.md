# 🎯 Frontend Payload Reference - ICCT26 Registration API

## ✅ Updated Backend - Now Matches Frontend Payload Exactly!

The backend has been updated to accept the **exact payload structure** you're sending from the frontend.

---

## 📋 Exact Payload Structure

```json
{
  "churchName": "CSI St. Peter's Church",
  "teamName": "Youth Fellowship Team",
  "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
  "captain": {
    "name": "John Doe",
    "phone": "+919876543210",
    "whatsapp": "919876543210",
    "email": "john@example.com"
  },
  "viceCaptain": {
    "name": "Jane Smith",
    "phone": "+919123456789",
    "whatsapp": "919123456789",
    "email": "jane@example.com"
  },
  "players": [
    {
      "name": "Player One",
      "age": 25,
      "phone": "+919800000001",
      "role": "Batsman",
      "aadharFile": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "subscriptionFile": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
    },
    {
      "name": "Player Two",
      "age": 24,
      "phone": "+919800000002",
      "role": "Bowler",
      "aadharFile": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "subscriptionFile": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
    },
    // ... 9-13 more players (11-15 total required)
  ],
  "paymentReceipt": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

---

## 📊 Payload Field Definitions

### Root Level Fields

| Field | Type | Required | Format | Example | Notes |
|-------|------|----------|--------|---------|-------|
| **churchName** | String | ✅ Yes | 1-200 chars | "CSI St. Peter's Church" | Church/Organization name |
| **teamName** | String | ✅ Yes | 1-100 chars | "Youth Fellowship Team" | Unique team name |
| **pastorLetter** | String | ❌ No | Base64 Image/PDF | "data:image/jpeg;base64,..." | Pastor's authorization letter |
| **captain** | Object | ✅ Yes | CaptainInfo | See below | Team captain details |
| **viceCaptain** | Object | ✅ Yes | ViceCaptainInfo | See below | Vice-captain details |
| **players** | Array | ✅ Yes | 11-15 items | Array of PlayerDetails | Player roster |
| **paymentReceipt** | String | ❌ No | Base64 Image/PDF | "data:image/jpeg;base64,..." | Payment proof |

### Captain Object (captain)

| Field | Type | Required | Format | Example | Notes |
|-------|------|----------|--------|---------|-------|
| **name** | String | ✅ Yes | 1-100 chars | "John Doe" | Captain's full name |
| **phone** | String | ✅ Yes | E.164 Format | "+919876543210" | International format |
| **whatsapp** | String | ✅ Yes | 10-20 chars | "919876543210" | With or without +91 |
| **email** | String | ✅ Yes | Valid Email | "john@example.com" | Captain's email |

### Vice-Captain Object (viceCaptain)

| Field | Type | Required | Format | Example | Notes |
|-------|------|----------|--------|---------|-------|
| **name** | String | ✅ Yes | 1-100 chars | "Jane Smith" | Vice-captain's full name |
| **phone** | String | ✅ Yes | E.164 Format | "+919123456789" | International format |
| **whatsapp** | String | ✅ Yes | 10-20 chars | "919123456789" | With or without +91 |
| **email** | String | ✅ Yes | Valid Email | "jane@example.com" | Vice-captain's email |

### Player Object (players array - 11-15 items)

| Field | Type | Required | Format | Example | Notes |
|-------|------|----------|--------|---------|-------|
| **name** | String | ✅ Yes | 1-100 chars | "Player One" | Player's full name |
| **age** | Integer | ✅ Yes | 15-60 | 25 | Player's age |
| **phone** | String | ✅ Yes | E.164 Format | "+919800000001" | International format |
| **role** | String | ✅ Yes | 1 of 4 options | "Batsman" | See roles table below |
| **aadharFile** | String | ❌ No | Base64 Image | "data:image/jpeg;base64,..." | Aadhar ID copy |
| **subscriptionFile** | String | ❌ No | Base64 Image | "data:image/jpeg;base64,..." | Church subscription proof |

### Valid Player Roles

```
1. "Batsman"
2. "Bowler"
3. "All-Rounder"
4. "Wicket Keeper"
```

---

## 🔄 Request Example (cURL)

```bash
curl -X POST "https://icct26-backend.onrender.com/register/team" \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "CSI St. Peter's Church",
    "teamName": "Youth Fellowship Team",
    "pastorLetter": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "captain": {
      "name": "John Doe",
      "phone": "+919876543210",
      "whatsapp": "919876543210",
      "email": "john@example.com"
    },
    "viceCaptain": {
      "name": "Jane Smith",
      "phone": "+919123456789",
      "whatsapp": "919123456789",
      "email": "jane@example.com"
    },
    "players": [
      {
        "name": "Player One",
        "age": 25,
        "phone": "+919800000001",
        "role": "Batsman",
        "aadharFile": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
        "subscriptionFile": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
      },
      // ... more players
    ],
    "paymentReceipt": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
  }'
```

---

## ✅ Success Response

```json
{
  "success": true,
  "message": "Team registration successful",
  "data": {
    "team_id": "ICCT26-20251109093800",
    "team_name": "Youth Fellowship Team",
    "church_name": "CSI St. Peter's Church",
    "captain_name": "John Doe",
    "vice_captain_name": "Jane Smith",
    "players_count": 11,
    "registered_at": "2025-11-09T09:38:00.123456",
    "email_sent": true,
    "database_saved": true
  }
}
```

---

## ❌ Error Responses

### Invalid Player Count
```json
{
  "success": false,
  "message": "Invalid player count. Expected 11-15 players, got 10"
}
```

### Validation Error (e.g., Invalid Email)
```json
{
  "success": false,
  "message": "Validation error: invalid email format"
}
```

### Missing Required Field
```json
{
  "detail": [
    {
      "loc": ["body", "captain", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Invalid Role
```json
{
  "success": false,
  "message": "Validation error: Role must be one of ['Batsman', 'Bowler', 'All-Rounder', 'Wicket Keeper']"
}
```

---

## 📝 Field Validation Rules

### String Fields
- **churchName**: 1-200 characters
- **teamName**: 1-100 characters (must be unique)
- **name** (all): 1-100 characters
- **role**: Must be one of: Batsman, Bowler, All-Rounder, Wicket Keeper

### Phone Fields
- **phone**: E.164 format (e.g., +919876543210)
- **whatsapp**: Can be with or without +91 (e.g., 919876543210 or +919876543210)
- Length: 10-20 characters

### Email Fields
- Must be valid email format (e.g., john@example.com)
- Domain validation enabled

### Age Field
- Must be integer between 15-60

### Player Count
- Minimum: 11 players
- Maximum: 15 players
- **Required**: Exactly 11-15 players must be provided

### Base64 Files
- **pastorLetter**: Optional, Image or PDF
- **paymentReceipt**: Optional, Image or PDF
- **aadharFile**: Optional, Image
- **subscriptionFile**: Optional, Image
- Format: "data:image/jpeg;base64,..." or "data:application/pdf;base64,..."

---

## 🔌 JavaScript/Fetch Example

```javascript
const payload = {
  churchName: "CSI St. Peter's Church",
  teamName: "Youth Fellowship Team",
  pastorLetter: "data:image/jpeg;base64,...",
  captain: {
    name: "John Doe",
    phone: "+919876543210",
    whatsapp: "919876543210",
    email: "john@example.com"
  },
  viceCaptain: {
    name: "Jane Smith",
    phone: "+919123456789",
    whatsapp: "919123456789",
    email: "jane@example.com"
  },
  players: [
    // 11-15 player objects
  ],
  paymentReceipt: "data:image/jpeg;base64,..."
};

fetch('https://icct26-backend.onrender.com/register/team', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(payload)
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('✅ Registration successful!');
    console.log('Team ID:', data.data.team_id);
  } else {
    console.error('❌ Registration failed:', data.message);
  }
})
.catch(error => console.error('Error:', error));
```

---

## 🔗 Admin Endpoints (For Checking Registrations)

Once teams are registered, use these endpoints to view data:

### Get All Teams
```
GET /admin/teams
Response: {"success": true, "teams": [...]}
```

### Get Team Details
```
GET /admin/teams/{team_id}
Response: {"team": {...}, "players": [...]}
```

### Get Player Details
```
GET /admin/players/{player_id}
Response: {"playerId": ..., "name": ..., "team": {...}}
```

---

## ✨ Key Changes in Backend

1. **Phone Field**: Now accepts 10-20 characters to accommodate both E.164 and plain formats
2. **WhatsApp Field**: Accepts with or without +91 prefix
3. **File Descriptions**: Clarified that files can be images or PDFs
4. **Response**: Now includes church_name and vice_captain_name in response
5. **Error Messages**: Structured error responses with `success` flag and `message`
6. **Validation**: Separate handling for ValueError vs general exceptions

---

## 🎯 Testing Checklist

- [ ] All required fields present in payload
- [ ] Player count is 11-15
- [ ] Phone numbers in E.164 format or with country code
- [ ] All email addresses valid
- [ ] Base64 files properly encoded
- [ ] All player roles valid
- [ ] Age between 15-60
- [ ] Test registration on both local and production
- [ ] Verify email sent to captain
- [ ] Check team appears in /admin/teams

---

## 📞 Support

If you encounter any issues:

1. Check that all required fields are present
2. Verify phone number format
3. Ensure exactly 11-15 players are included
4. Check console logs for detailed error messages
5. Review the error response for specific validation issues

---

**Backend Updated**: November 9, 2025
**API Version**: 1.0.0
**Status**: ✅ Production Ready
