# 🔄 Frontend-Backend Integration Guide

## 📌 Executive Summary

Your **frontend payload is 100% compatible** with the backend. No changes needed to either frontend or backend code. Simply integrate the API call.

---

## 🎯 Complete Integration Flow

### Step 1: Frontend Collects Data

Frontend form collects:
- Church name
- Team name
- Pastor letter (optional)
- Captain details (name, phone, whatsapp, email)
- Vice-captain details (name, phone, whatsapp, email)
- Exactly 11 players with (name, age, phone, role, aadhar file, subscription file)
- Payment receipt

### Step 2: Frontend Validates Data

Validate before sending:
- ✅ All required fields present
- ✅ Phone numbers in E.164 format
- ✅ Emails valid
- ✅ Exactly 11 players
- ✅ Player roles are valid
- ✅ Files converted to Base64

### Step 3: Frontend Sends to Backend

```javascript
const payload = {
  churchName: form.churchName,
  teamName: form.teamName,
  pastorLetter: form.pastorLetter || null,
  captain: {
    name: form.captainName,
    phone: form.captainPhone,
    whatsapp: form.captainWhatsapp,
    email: form.captainEmail
  },
  viceCaptain: {
    name: form.viceCaptainName,
    phone: form.viceCaptainPhone,
    whatsapp: form.viceCaptainWhatsapp,
    email: form.viceCaptainEmail
  },
  players: form.players.map(p => ({
    name: p.name,
    age: p.age,
    phone: p.phone,
    role: p.role,
    aadharFile: p.aadharFileBase64,
    subscriptionFile: p.subscriptionFileBase64
  })),
  paymentReceipt: form.paymentReceiptBase64
};

// Send to backend
fetch('https://icct26-backend.onrender.com/register/team', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
})
.then(res => res.json())
.then(data => handleResponse(data));
```

### Step 4: Backend Processes Request

Backend will:
1. ✅ Validate all fields match expected format
2. ✅ Check required fields present
3. ✅ Generate unique Team ID: `ICCT26-YYYYMMDDHHMMSS`
4. ✅ Save to PostgreSQL database
5. ✅ Send confirmation email to captain
6. ✅ Return success response

### Step 5: Frontend Handles Response

#### Success Response
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

**Frontend should:**
- Show success message with Team ID
- Display "Confirmation email sent to [captain_email]"
- Redirect to confirmation page
- Save Team ID for reference

#### Error Response
```json
{
  "detail": "Team must have 11-15 players"
}
```

**Frontend should:**
- Display error message
- Show which field caused error
- Allow user to correct and resubmit

---

## 📊 Field Mapping Reference

### Direct 1:1 Mapping

```
Frontend Field          Backend Field          Type
───────────────────────────────────────────────────────
churchName      →      churchName      →      String
teamName        →      teamName        →      String
pastorLetter    →      pastorLetter    →      Base64
captain         →      captain         →      Object
viceCaptain     →      viceCaptain     →      Object
players         →      players         →      Array
paymentReceipt  →      paymentReceipt  →      Base64
```

### No Field Transformation Needed

- ✅ All field names use camelCase
- ✅ All data types match exactly
- ✅ Nested objects structure matches
- ✅ Array structure matches
- ✅ No renaming required
- ✅ No format conversion required (except Base64 for files)

---

## 🔐 Validation Rules to Implement on Frontend

### Church Name
- Required: Yes
- Min length: 1 character
- Max length: 200 characters
- Regex: `^.{1,200}$`

### Team Name
- Required: Yes
- Min length: 1 character
- Max length: 100 characters
- Unique: Yes (backend enforces)
- Regex: `^.{1,100}$`

### Phone Numbers (Captain & Vice-Captain)
- Required: Yes
- Format: E.164
- Example: `+919876543210`
- Pattern: `^\\+91[0-9]{10}$`

### WhatsApp Number
- Required: Yes
- Length: 10 digits
- Can include "91" prefix or not
- Examples: `919876543210` or `9876543210`

### Email
- Required: Yes
- Format: Standard email
- Validation: Use standard email regex
- Example: `john@example.com`

### Player Age
- Required: Yes
- Min: 15 years
- Max: 60 years
- Range: `15 <= age <= 60`

### Player Role
- Required: Yes
- Options: `Batsman`, `Bowler`, `All-Rounder`, `Wicket Keeper`
- Case-sensitive match required
- Validation: Must be exact match

### Players Array
- Required: Yes
- Min items: 11
- Max items: 11
- Note: Backend accepts 11-15 but frontend currently sends 11

### Files (Aadhar, Subscription, Payment Receipt)
- Format: Base64-encoded
- Type: Image JPEG or PDF
- Max size: ~5MB (before encoding)
- Encoding: `data:[mime-type];base64,[content]`

---

## 📱 Frontend Implementation Checklist

- [ ] Create registration form with all required fields
- [ ] Implement client-side validation
- [ ] Convert files to Base64 before sending
- [ ] Format phone numbers to E.164
- [ ] Validate email format
- [ ] Ensure exactly 11 players
- [ ] Show loading state while sending
- [ ] Handle success response
- [ ] Handle error response
- [ ] Display Team ID after success
- [ ] Show confirmation message
- [ ] Allow download of confirmation
- [ ] Implement retry logic for failed requests

---

## 🧪 Testing Integration

### Local Testing
```
URL: http://localhost:8000/register/team
Method: POST
Headers: { "Content-Type": "application/json" }
```

### Production Testing
```
URL: https://icct26-backend.onrender.com/register/team
Method: POST
Headers: { "Content-Type": "application/json" }
```

### Using Swagger UI (For Testing)
1. Open `http://localhost:8000/docs`
2. Find `/register/team` endpoint
3. Click "Try it out"
4. Paste your payload
5. Click "Execute"
6. See the response

---

## 📧 Email Confirmation

After successful registration, the captain will receive an email with:
- ✅ Team ID
- ✅ Team name
- ✅ Church name
- ✅ Captain details
- ✅ Complete player roster
- ✅ Registration date/time

Email is automatically sent from the backend to `captain.email` field.

---

## 🚨 Common Issues & Solutions

### Issue 1: "Team must have 11-15 players"
- **Cause**: Submitted player count not 11-15
- **Solution**: Verify exactly 11-15 players in array

### Issue 2: "Invalid phone format"
- **Cause**: Phone number not in E.164 format
- **Solution**: Ensure format is `+919876543210`

### Issue 3: "Invalid role"
- **Cause**: Role not in exact list
- **Solution**: Use one of: `Batsman`, `Bowler`, `All-Rounder`, `Wicket Keeper`

### Issue 4: "Invalid email format"
- **Cause**: Email validation failed
- **Solution**: Use valid email like `john@example.com`

### Issue 5: "Team name already exists"
- **Cause**: Another team registered with same name
- **Solution**: Use a unique team name

---

## 💡 Best Practices

1. **Validate on Frontend**: Don't rely on backend validation alone
2. **Use HTTPS**: Always use HTTPS in production
3. **Handle Timeouts**: Set request timeout to 30s
4. **Show Loading**: Show loading indicator while sending
5. **Clear Errors**: Clear previous errors when user modifies field
6. **Save Locally**: Save form data locally while uploading
7. **Retry Logic**: Implement exponential backoff retry
8. **Error Messages**: Show clear, user-friendly error messages
9. **Success Page**: Display Team ID prominently after success
10. **Confirmation**: Send confirmation email info to user

---

## 🔗 API Endpoints Reference

### Registration
```
POST /register/team
```

### Admin Panel
```
GET /admin/teams              (All teams)
GET /admin/teams/{team_id}    (Team details)
GET /admin/players/{player_id} (Player details)
```

### Health Check
```
GET /                         (API health)
GET /health                   (Health status)
GET /docs                     (Swagger UI)
```

---

## 📞 Support & Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **GitHub**: `https://github.com/sanjaynesan-05/ICCT26-BACKEND`
- **API Status**: Check `/` endpoint for health status

---

## ✅ Final Checklist

- ✅ Payload structure matches backend models
- ✅ All field names are correct (camelCase)
- ✅ No field transformations needed
- ✅ Validation rules implemented
- ✅ Error handling in place
- ✅ Success response processing implemented
- ✅ Email confirmation understanding
- ✅ Backend is production-ready
- ✅ All tests passing
- ✅ Documentation complete

---

## 🎉 You're Ready to Integrate!

The backend is fully operational and ready to accept registrations. Integrate the API call in your frontend and you're done! 🚀

**Backend Status**: ✅ Production Ready
**API Health**: ✅ All Systems Operational
**Database**: ✅ Connected and Initialized
**Email System**: ✅ Working

---

**Questions?** Check the Swagger documentation at `/docs` or review the error messages from the backend. Happy coding! 🎯
