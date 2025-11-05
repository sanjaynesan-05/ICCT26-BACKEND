# 🎯 FRONTEND TO BACKEND INTEGRATION DIAGRAM

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Your App)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Registration Form                                                 │
│  ├─ Team Info (Church, Team Name)                                 │
│  ├─ Captain Details (Name, Email, Phone)                          │
│  ├─ Vice-Captain Details (Name, Email, Phone)                     │
│  ├─ Players (11-15 rows)                                          │
│  └─ Optional Files (PDFs)                                         │
│                                                                     │
│  Form Validation (JavaScript)                                     │
│  ├─ Check 11-15 players                                           │
│  ├─ Validate emails                                               │
│  ├─ Validate ages (15-60)                                         │
│  └─ Check required fields                                         │
│                                                                     │
│  User clicks "Submit"                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                           ↓
                    POST /register/team
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI - Port 8000)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  @app.post("/register/team")                                       │
│  async def register_team(data: TeamRegistration):                 │
│      ↓                                                             │
│  1. RECEIVE REQUEST                                               │
│     ├─ Parse JSON body                                            │
│     └─ Extract all fields                                         │
│      ↓                                                             │
│  2. PYDANTIC VALIDATION                                           │
│     ├─ Check all required fields                                  │
│     ├─ Validate email format                                      │
│     ├─ Verify 11-15 players                                       │
│     ├─ Check age range (15-60)                                    │
│     ├─ Validate phone formats                                     │
│     └─ Return 422 if invalid                                      │
│      ↓                                                             │
│  3. DATABASE TRANSACTION                                          │
│     ├─ Create Team Registration                                   │
│     ├─ Add Captain Record                                         │
│     ├─ Add Vice-Captain Record                                    │
│     ├─ Add 11-15 Player Records                                   │
│     └─ Save all to PostgreSQL                                     │
│      ↓                                                             │
│  4. GENERATE TEAM ID                                              │
│     └─ Format: ICCT26-{timestamp}                                │
│      ↓                                                             │
│  5. SEND EMAIL                                                    │
│     ├─ Connect to Gmail SMTP                                      │
│     ├─ Compose confirmation email                                 │
│     ├─ Send to captain email                                      │
│     └─ Log success/failure                                        │
│      ↓                                                             │
│  6. RETURN RESPONSE (HTTP 200)                                    │
│     ├─ success: true                                              │
│     ├─ team_id: "ICCT26-..."                                     │
│     ├─ message: "Registration successful"                         │
│     ├─ email_sent: true                                           │
│     └─ database_saved: true                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                           ↓
           HTTP 200 with Success JSON
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│              FRONTEND (Your App)                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. HANDLE RESPONSE                                               │
│     ├─ Parse JSON                                                 │
│     └─ Check success flag                                         │
│      ↓                                                             │
│  2. DISPLAY SUCCESS                                               │
│     ├─ Show team_id to user                                       │
│     ├─ Display confirmation message                               │
│     ├─ Show "Email sent to captain"                               │
│     └─ Clear form                                                 │
│      ↓                                                             │
│  3. OPTIONAL ACTIONS                                              │
│     ├─ Save team_id locally                                       │
│     ├─ Print confirmation                                         │
│     ├─ Redirect to success page                                   │
│     └─ Send analytics event                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                           ↓
        [USER SEES SUCCESS CONFIRMATION]
```

---

## Database Storage

```
PostgreSQL Database (icct26_db)
│
├─ team_registrations (1 row per team)
│  ├─ id: 1
│  ├─ team_id: "ICCT26-20251105143934"
│  ├─ church_name: "CSI St. Peter's"
│  ├─ team_name: "Warriors"
│  ├─ created_at: 2025-11-05 14:39:34
│  └─ updated_at: 2025-11-05 14:39:34
│   ↓
│   ├─ captains (1 row)
│   │  ├─ id: 1
│   │  ├─ registration_id: 1
│   │  ├─ name: "John Doe"
│   │  ├─ email: "john@example.com"
│   │  └─ phone: "9876543210"
│   │
│   ├─ vice_captains (1 row)
│   │  ├─ id: 1
│   │  ├─ registration_id: 1
│   │  ├─ name: "Jane Smith"
│   │  ├─ email: "jane@example.com"
│   │  └─ phone: "9876543211"
│   │
│   └─ players (11-15 rows)
│      ├─ id: 1, registration_id: 1, name: "Player 1", role: "Batsman", age: 25
│      ├─ id: 2, registration_id: 1, name: "Player 2", role: "Bowler", age: 26
│      ├─ ...
│      └─ id: 11, registration_id: 1, name: "Player 11", role: "Wicket Keeper", age: 25
```

---

## Request & Response Example

### Frontend Sends (POST /register/team)

```json
{
  "churchName": "CSI St. Peter's Church",
  "teamName": "Warriors",
  "captain": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "whatsapp": "9876543210"
  },
  "viceCaptain": {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "9876543211",
    "whatsapp": "9876543211"
  },
  "players": [
    {
      "name": "Player 1",
      "age": 25,
      "phone": "9876543212",
      "role": "Batsman",
      "aadharFile": null,
      "subscriptionFile": null
    },
    ... (10 more players)
  ],
  "pastorLetter": null,
  "paymentReceipt": null
}
```

### Backend Returns (HTTP 200)

```json
{
  "success": true,
  "message": "Team registration successful",
  "data": {
    "team_id": "ICCT26-20251105143934",
    "team_name": "Warriors",
    "captain_name": "John Doe",
    "players_count": 11,
    "registered_at": "2025-11-05T14:39:34.123456",
    "email_sent": true,
    "database_saved": true
  }
}
```

---

## Error Handling Flow

```
┌─ Frontend Sends Invalid Data
│
├─ Validation Error (422)
│  ├─ Return: {"detail": [...errors...]}
│  └─ Frontend: Display error messages
│
├─ Server Error (500)
│  ├─ Database connection failed
│  ├─ SMTP error
│  └─ Frontend: Show "Try again later"
│
└─ Success (200)
   ├─ Data saved
   ├─ Email sent
   └─ Return success with team_id
```

---

## Validation Workflow

```
Frontend Form Input
   ↓
[User clicks Submit]
   ↓
JavaScript Validation (Optional but recommended)
├─ Check 11-15 players? ✅
├─ Valid emails? ✅
├─ Ages 15-60? ✅
├─ All required fields? ✅
└─ If error → Show message, don't send
   ↓
Send POST to /register/team
   ↓
Backend Pydantic Validation (Required)
├─ Parse JSON? ✅
├─ Check required fields? ✅
├─ Validate email format? ✅
├─ Check email regex? ✅
├─ Verify 11-15 players? ✅
├─ Check ages 15-60? ✅
└─ If error → Return 422 with details
   ↓
Process and Save
   ↓
Return Success (200)
   ↓
Frontend Shows Confirmation
```

---

## Timeline

```
User Starts Form
│
├─ T+0s    User fills in team info
├─ T+30s   User adds 11 players
├─ T+60s   User reviews form
├─ T+62s   User clicks "Submit"
│
├─ T+62.1s Frontend validates
├─ T+62.2s POST sent to backend
│
├─ T+62.3s Backend receives request
├─ T+62.4s Pydantic validates
├─ T+62.5s Database saves team
├─ T+62.6s Database saves captain
├─ T+62.7s Database saves vice-captain
├─ T+62.8s Database saves players (11)
├─ T+62.9s Generate team ID
│
├─ T+63s   SMTP connects to Gmail
├─ T+63.5s Email composed
├─ T+64s   Email sent ✅
│
├─ T+64.1s Response returned (200)
│
├─ T+64.2s Frontend receives response
├─ T+64.3s JavaScript parses JSON
├─ T+64.4s Display team_id
├─ T+64.5s Show "Registration successful"
│
└─ T+65s   User sees confirmation
           DONE! ✅
```

---

## Files Involved

```
Browser (Frontend)
  ├─ index.html
  ├─ registration-form.js
  └─ styles.css
       │
       └─── HTTP POST ──→ main.py (FastAPI)

Backend Server (Port 8000)
  ├─ main.py
  │  ├─ @app.post("/register/team")
  │  ├─ Pydantic models (validation)
  │  └─ SMTP functions (email)
  │
  ├─ database.py
  │  ├─ PostgreSQL connection
  │  └─ SQLAlchemy session
  │
  ├─ models.py
  │  ├─ TeamRegistrationDB
  │  ├─ CaptainDB
  │  ├─ ViceCaptainDB
  │  └─ PlayerDB
  │
  └─ .env
     ├─ DATABASE_URL
     ├─ SMTP_SERVER
     └─ SMTP credentials

PostgreSQL Database
  └─ icct26_db
     ├─ team_registrations table
     ├─ captains table
     ├─ vice_captains table
     └─ players table
```

---

## Integration Checklist

```
BACKEND SETUP
☑ FastAPI installed
☑ PostgreSQL running
☑ Database created (icct26_db)
☑ Tables created
☑ SMTP configured (.env)
☑ main.py working
☑ /docs shows endpoint

FRONTEND SETUP
☑ Create HTML form
☑ Add JavaScript validation
☑ Implement POST to backend
☑ Handle success response
☑ Handle error response
☑ Show user messages

TESTING
☑ Test via /docs (Swagger)
☑ Test from JavaScript
☑ Verify data in database
☑ Verify email sent
☑ Test error cases
☑ Test with multiple teams

DEPLOYMENT
☑ Update API URL (production)
☑ Configure CORS origins
☑ Set environment variables
☑ Enable HTTPS
☑ Add rate limiting
☑ Monitor logs
```

---

## Success Criteria

✅ Frontend sends data to backend
✅ Backend receives and validates
✅ Data persists in PostgreSQL
✅ Email sent to captain
✅ Team ID generated and returned
✅ Frontend displays confirmation
✅ User sees success message

---

**You're ready to build! Start with FRONTEND_READY.md** 🚀
