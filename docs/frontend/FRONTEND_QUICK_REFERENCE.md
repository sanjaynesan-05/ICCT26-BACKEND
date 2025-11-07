# 🚀 Frontend Integration - Quick Reference

## ✅ Backend Status
**Your API is 100% ready for frontend connection!**

---

## 📍 API Endpoint

```
POST http://localhost:8000/register/team
Content-Type: application/json
```

---

## 📦 Minimum Required Payload

```json
{
  "churchName": "Your Church Name",
  "teamName": "Team Name",
  "captain": {
    "name": "Captain Name",
    "email": "captain@example.com",
    "phone": null,
    "whatsapp": null
  },
  "viceCaptain": {
    "name": "Vice Captain Name",
    "email": "vice@example.com",
    "phone": null,
    "whatsapp": null
  },
  "players": [
    { "name": "Player 1", "age": 25, "phone": null, "role": "Batsman", "aadharFile": null, "subscriptionFile": null },
    { "name": "Player 2", "age": 26, "phone": null, "role": "Bowler", "aadharFile": null, "subscriptionFile": null },
    { "name": "Player 3", "age": 27, "phone": null, "role": "All-Rounder", "aadharFile": null, "subscriptionFile": null },
    { "name": "Player 4", "age": 28, "phone": null, "role": "Wicket Keeper", "aadharFile": null, "subscriptionFile": null },
    { "name": "Player 5", "age": 24, "phone": null, "role": "Batsman", "aadharFile": null, "subscriptionFile": null },
    { "name": "Player 6", "age": 25, "phone": null, "role": "Bowler", "aadharFile": null, "subscriptionFile": null },
    { "name": "Player 7", "age": 26, "phone": null, "role": "All-Rounder", "aadharFile": null, "subscriptionFile": null },
    { "name": "Player 8", "age": 27, "phone": null, "role": "Batsman", "aadharFile": null, "subscriptionFile": null },
    { "name": "Player 9", "age": 28, "phone": null, "role": "Bowler", "aadharFile": null, "subscriptionFile": null },
    { "name": "Player 10", "age": 24, "phone": null, "role": "All-Rounder", "aadharFile": null, "subscriptionFile": null },
    { "name": "Player 11", "age": 25, "phone": null, "role": "Wicket Keeper", "aadharFile": null, "subscriptionFile": null }
  ],
  "pastorLetter": null,
  "paymentReceipt": null
}
```

---

## ✔️ Validation Rules

| Field | Min | Max | Required |
|-------|-----|-----|----------|
| players | 11 | 15 | ✅ |
| age | 15 | 60 | ✅ |
| email | - | - | ✅ Format |
| phone | 10 | 15 | ❌ Optional |

### Player Roles
- Batsman
- Bowler
- All-Rounder
- Wicket Keeper

---

## 📄 Success Response

```json
{
  "success": true,
  "message": "Team registration successful",
  "data": {
    "team_id": "ICCT26-20251105143934",
    "team_name": "Team Name",
    "captain_name": "Captain Name",
    "players_count": 11,
    "registered_at": "2025-11-05T14:39:34.123456",
    "email_sent": true,
    "database_saved": true
  }
}
```

---

## ❌ Error Response

```json
{
  "detail": [
    {
      "loc": ["body", "players"],
      "msg": "Team must have 11-15 players",
      "type": "value_error"
    }
  ]
}
```

---

## 🔥 JavaScript Example (Copy-Paste Ready)

```javascript
async function registerTeam() {
  const payload = {
    churchName: "Church Name",
    teamName: "Team Name",
    captain: {
      name: "Captain",
      email: "captain@email.com",
      phone: null,
      whatsapp: null
    },
    viceCaptain: {
      name: "Vice Captain",
      email: "vice@email.com",
      phone: null,
      whatsapp: null
    },
    players: [
      { name: "Player 1", age: 25, phone: null, role: "Batsman", aadharFile: null, subscriptionFile: null },
      { name: "Player 2", age: 26, phone: null, role: "Bowler", aadharFile: null, subscriptionFile: null },
      { name: "Player 3", age: 27, phone: null, role: "All-Rounder", aadharFile: null, subscriptionFile: null },
      { name: "Player 4", age: 28, phone: null, role: "Wicket Keeper", aadharFile: null, subscriptionFile: null },
      { name: "Player 5", age: 24, phone: null, role: "Batsman", aadharFile: null, subscriptionFile: null },
      { name: "Player 6", age: 25, phone: null, role: "Bowler", aadharFile: null, subscriptionFile: null },
      { name: "Player 7", age: 26, phone: null, role: "All-Rounder", aadharFile: null, subscriptionFile: null },
      { name: "Player 8", age: 27, phone: null, role: "Batsman", aadharFile: null, subscriptionFile: null },
      { name: "Player 9", age: 28, phone: null, role: "Bowler", aadharFile: null, subscriptionFile: null },
      { name: "Player 10", age: 24, phone: null, role: "All-Rounder", aadharFile: null, subscriptionFile: null },
      { name: "Player 11", age: 25, phone: null, role: "Wicket Keeper", aadharFile: null, subscriptionFile: null }
    ],
    pastorLetter: null,
    paymentReceipt: null
  };

  try {
    const response = await fetch("http://localhost:8000/register/team", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (response.ok) {
      console.log("✅ Success!", result.data.team_id);
    } else {
      console.error("❌ Error:", result.detail);
    }
  } catch (error) {
    console.error("❌ Request failed:", error);
  }
}

registerTeam();
```

---

## 🧪 Quick Test with cURL

```bash
curl -X POST http://localhost:8000/register/team \
  -H "Content-Type: application/json" \
  -d @payload.json
```

Save above JSON to `payload.json` file.

---

## 🔗 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 📋 Integration Checklist

- [ ] Backend running: `uvicorn main:app --reload --port 8000`
- [ ] API responds at: http://localhost:8000/docs
- [ ] Frontend ready to POST to: http://localhost:8000/register/team
- [ ] Form validates 11-15 players
- [ ] Email validation on captain/vice-captain
- [ ] Age validation (15-60)
- [ ] Role selection dropdown
- [ ] Success/error message display
- [ ] Database stores data correctly

---

## 🚨 Common Errors & Fixes

### ❌ "Team must have 11-15 players"
**Fix**: Ensure exactly 11-15 players in array

### ❌ "Invalid email"
**Fix**: Use valid email format (captain@example.com)

### ❌ "Connection refused"
**Fix**: Start backend with `uvicorn main:app --reload --port 8000`

### ❌ CORS Error
**Fix**: Backend has CORS enabled. Check browser console.

---

## 📞 Support Links

- Full Guide: `FRONTEND_INTEGRATION.md`
- Database Setup: `POSTGRESQL_SETUP.md`
- Simple API: `SIMPLE_API_README.md`
- Main README: `README.md`

---

**Ready to build the frontend? You have everything! 🚀**
