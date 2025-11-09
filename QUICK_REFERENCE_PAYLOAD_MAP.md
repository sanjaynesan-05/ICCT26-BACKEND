# 🎯 Quick Reference - Frontend to Backend Payload Mapping

## ✅ Status: **FULLY COMPATIBLE** - No Changes Needed!

Your frontend payload structure is **100% compatible** with the backend. Just send it directly to the `/register/team` endpoint.

---

## 📤 Frontend Sends This

```json
{
  "churchName": "CSI St. Peter's Church",
  "teamName": "Youth Fellowship Team",
  "pastorLetter": "data:image/jpeg;base64,...",
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
  "players": [/* 11 players */],
  "paymentReceipt": "data:image/jpeg;base64,..."
}
```

## 📥 Backend Receives This

```python
class TeamRegistration(BaseModel):
    churchName: str
    teamName: str
    pastorLetter: Optional[str]
    captain: CaptainInfo
    viceCaptain: ViceCaptainInfo
    players: List[PlayerDetails]
    paymentReceipt: Optional[str]
```

**✅ Perfect Match!**

---

## 🔗 API Integration

### Endpoint
```
POST https://icct26-backend.onrender.com/register/team
```

### Headers
```
Content-Type: application/json
```

### JavaScript/Fetch Example
```javascript
const formData = {
  churchName: "CSI St. Peter's Church",
  teamName: "Youth Fellowship Team",
  pastorLetter: "data:image/jpeg;base64,...",
  captain: { name: "John Doe", /* ... */ },
  viceCaptain: { name: "Jane Smith", /* ... */ },
  players: [/* 11 players */],
  paymentReceipt: "data:image/jpeg;base64,..."
};

fetch('https://icct26-backend.onrender.com/register/team', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(formData)
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    alert(`Registration successful! Team ID: ${data.data.team_id}`);
  } else {
    alert(`Error: ${data.detail}`);
  }
});
```

---

## ✅ Validation Checklist

Before sending to backend, verify:

- ✅ `churchName` - provided (1-200 chars)
- ✅ `teamName` - provided (1-100 chars)
- ✅ `captain` - all fields provided
  - ✅ name (1-100 chars)
  - ✅ phone (+919876543210 format)
  - ✅ whatsapp (919876543210 format)
  - ✅ email (valid email)
- ✅ `viceCaptain` - all fields provided (same as captain)
- ✅ `players` - exactly 11 players
  - ✅ name (1-100 chars)
  - ✅ age (15-60)
  - ✅ phone (E.164 format)
  - ✅ role (Batsman, Bowler, All-Rounder, or Wicket Keeper)
  - ✅ aadharFile (base64)
  - ✅ subscriptionFile (base64)
- ✅ `paymentReceipt` - provided (base64)
- ✅ `pastorLetter` - optional

---

## 🎯 Success Response

```json
{
  "success": true,
  "message": "Team registration successful",
  "data": {
    "team_id": "ICCT26-20251109093800",
    "team_name": "Youth Fellowship Team",
    "captain_name": "John Doe",
    "players_count": 11,
    "registration_date": "2025-11-09T09:38:00.123456",
    "confirmation_email_sent": true
  }
}
```

---

## ⚠️ Error Response

```json
{
  "detail": "Validation error details"
}
```

Common errors:
- Less than 11 players
- Invalid phone format
- Invalid role (must be exact match)
- Missing required fields
- Invalid email format

---

## 🧪 Test Endpoint

**Local Testing**: `http://localhost:8000/register/team`  
**Production**: `https://icct26-backend.onrender.com/register/team`

**Swagger Docs**: `http://localhost:8000/docs` (try it live!)

---

## 💡 Key Points

1. **No transformation needed** - Send exactly what frontend has
2. **All field names are camelCase** - Keep them as is
3. **11 players required** - Exactly 11, not 11-15 (based on frontend)
4. **Files as Base64** - No file uploads, send as data URIs
5. **Email confirmation** - Automatically sent to captain

---

## 🚀 You're Ready!

Your frontend and backend are **perfectly aligned**. Just integrate the API call and you're done! 🎉
