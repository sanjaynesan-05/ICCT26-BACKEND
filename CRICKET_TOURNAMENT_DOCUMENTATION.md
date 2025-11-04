# 🏏 ICCT26 Cricket Tournament - Complete Backend Documentation

**Fast, async team registration system with Google Sheets integration. Built with FastAPI.**

---

## 📑 Table of Contents

1. [Project Overview](#project-overview)
2. [Core Architecture](#core-architecture)
3. [Key Features](#key-features)
4. [API Endpoints](#api-endpoints)
5. [Registration Workflow](#registration-workflow)
6. [Duplicate Detection](#duplicate-detection)
7. [Email Notifications](#email-notifications)
8. [Google Sheets Integration](#google-sheets-integration)
9. [CORS Configuration](#cors-configuration)
10. [Data Models](#data-models-pydantic)
11. [Startup & Shutdown](#startup--shutdown)
12. [Performance Features](#performance-features)
13. [Environment Configuration](#environment-configuration)
14. [Quick Start](#quick-start)

---

## 📋 Project Overview

This is a **FastAPI-based asynchronous team registration system** for the **ICCT26 Cricket Tournament** organized by CSI St. Peter's Church, Coimbatore. It's designed to handle high-volume team registrations with real-time Google Sheets integration and automated email confirmations.

### **Purpose**
- Handle team registrations for cricket tournament
- Support teams with 11-15 players (including captain and vice-captain)
- Provide real-time data synchronization to Google Sheets
- Send automated confirmation emails with team ID
- Prevent duplicate team registrations
- Store payment receipt information
- Ensure no data loss during high-load periods

---

## 🏗️ Core Architecture

### **Technology Stack**
- **Framework:** FastAPI 0.104+ (async web framework)
- **Server:** Uvicorn (ASGI server)
- **Database Integration:** Google Sheets API v4
- **Authentication:** Google OAuth2 (Service Account)
- **Email:** SMTP (Gmail, Outlook, SendGrid compatible)
- **Data Validation:** Pydantic v2.5.0+
- **Package Management:** Python 3.8+

### **Dependencies**

```text
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
gspread>=5.12.0
google-auth>=2.23.4
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
python-dotenv>=1.0.0
```

### **Architecture Design**
```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           HTTP Request Handlers                     │   │
│  │  (Team Registration Endpoint)                       │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      Pydantic Data Validation                       │   │
│  │  (TeamRegistration + PlayerDetails)                 │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   Thread-Safe Registration Queue                    │   │
│  │  (Ensures no data loss during high load)            │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    Background Worker Thread                         │   │
│  │  (Processes registrations asynchronously)           │   │
│  └─┬─────────────────────────────────────────────────┬─┘   │
│    │                                                 │      │
│    ▼                                                 ▼      │
│ ┌────────────────┐                         ┌──────────────┐│
│ │ Duplicate      │                         │ Email        ││
│ │ Detection      │                         │ Confirmation ││
│ │ (Team Name +   │                         │ Sending      ││
│ │  Payment)      │                         │ (SMTP)       ││
│ └────────┬───────┘                         └──────┬───────┘│
│          │                                        │        │
│          ▼                                        ▼        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Google Sheets API Integration              │   │
│  │  (Real-time data sync, Append rows)                │   │
│  │  - Team Info Sheet                                 │   │
│  │  - Player Details Sheet                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### **1. Asynchronous Processing** ⚡
- **Non-blocking queue system** that ensures instant API responses
- Registrations are queued and processed in background threads
- No data loss even during high-load periods
- Immediate confirmation sent to users
- Prevents bottlenecks from Google Sheets API latency

### **2. Complete Team Management** 🏏
The system supports comprehensive team registration with:

#### **Team Information**
- Church Name (from participating churches)
- Team Name (unique identifier)
- Pastor's Letter/Church Letter upload (optional)
- Team Captain details
- Vice-Captain details
- Payment receipt number
- Registration fee confirmation

#### **Player Management**
- 11-15 players per team (including captain and vice-captain)
- Individual player details for each team member
- Player name, phone, email collection
- Role assignment (Batsman, Bowler, All-rounder, Wicket-keeper, Captain, Vice-Captain)
- Jersey number allocation

### **3. Thread-Safe Operations** 🔒
- Queue-based system with thread safety
- Multiple concurrent registrations handled without conflicts
- Daemon worker thread processes queue continuously
- Graceful shutdown ensures no data loss

### **4. Automatic Duplicate Detection** 🚫
- Validates based on combination of `team_name` + `payment_receipt`
- Prevents multiple registrations with same credentials
- Returns meaningful error messages

### **5. Real-time Google Sheets Integration** 📊
- Direct append to Google Sheets (no intermediate storage)
- Automatic timestamp addition
- Auto-creates headers if missing
- Separate sheets for team info and player details
- Team ID auto-generation (ICCT26-XXXX format)

### **6. Automated Email Confirmations** 📧
- Beautiful HTML-styled confirmation emails
- Includes team ID for reference
- Lists all team members
- Event information and next steps
- Registration details and payment confirmation

### **7. CORS Support** 🌐
- Pre-configured for cross-origin requests
- Customizable allowed origins
- Ready for frontend integration from any domain

### **8. Interactive API Documentation** 📚
- Swagger UI at `/docs`
- ReDoc at `/redoc`
- Auto-generated from code annotations
- Test endpoints directly in browser

---

## 📡 API Endpoints

### **1. Home / Information Endpoint** 🏠
```http
GET /
```

**Purpose:** Returns comprehensive API documentation and all available endpoints

**Response:**
```json
{
  "message": "ICCT26 Cricket Tournament Registration API - Asynchronous Team Registration System",
  "version": "1.0.0",
  "event": "ICCT26 Cricket Tournament 2026",
  "organizer": "CSI St. Peter's Church, Coimbatore",
  "features": [
    "Asynchronous queue-based processing",
    "Google Sheets integration",
    "Automated email confirmations",
    "Duplicate detection",
    "Team and player management"
  ],
  "endpoints": {
    "/": "API documentation",
    "/register/team": "Team registration endpoint",
    "/queue/status": "Queue status monitoring",
    "/docs": "Swagger UI documentation",
    "/redoc": "ReDoc documentation"
  }
}
```

---

### **2. Team Registration** 🏏
```http
POST /register/team
```

**Purpose:** Register a complete cricket team with all player details

**Request Body:**
```json
{
  "churchName": "CSI St. Peter's Church",
  "teamName": "Thunder Strikers",
  "pastorLetter": "letter_file_path_or_base64",
  "captainName": "John Doe",
  "captainPhone": "+919876543210",
  "captainWhatsapp": "919876543210",
  "captainEmail": "john.doe@example.com",
  "viceCaptainName": "Jane Smith",
  "viceCaptainPhone": "+919123456789",
  "viceCaptainWhatsapp": "919123456789",
  "viceCaptainEmail": "jane.smith@example.com",
  "paymentReceipt": "TXN123456789",
  "players": [
    {
      "name": "John Doe",
      "phone": "+919876543210",
      "email": "john.doe@example.com",
      "role": "Captain",
      "jerseyNumber": "1"
    },
    {
      "name": "Jane Smith",
      "phone": "+919123456789",
      "email": "jane.smith@example.com",
      "role": "Vice-Captain",
      "jerseyNumber": "2"
    }
  ]
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Team registration queued successfully",
  "status": "processing",
  "data": {
    "teamName": "Thunder Strikers",
    "churchName": "CSI St. Peter's Church",
    "captainName": "John Doe",
    "playerCount": 11,
    "queuedAt": "2026-01-15 10:30:45"
  }
}
```

**Response (Error - Duplicate):**
```json
{
  "error": "Duplicate registration",
  "message": "Team 'Thunder Strikers' with payment receipt 'TXN123456789' already exists"
}
```

**Response (Error - Invalid Player Count):**
```json
{
  "error": "Invalid player count",
  "message": "Team must have between 11-15 players"
}
```

**Stored in:**
- Google Sheet 1 (Team Information)
- Google Sheet 2 (Player Details)

---

### **3. Queue Status** 📊
```http
GET /queue/status
```

**Purpose:** Monitor real-time registration processing status

**Response:**
```json
{
  "queue_size": 5,
  "worker_active": true,
  "timestamp": "2026-01-15 10:40:15"
}
```

**Information Provided:**
- `queue_size` - Number of registrations waiting to be processed
- `worker_active` - Background worker thread status
- `timestamp` - Current server time

---

### **4. Swagger UI Documentation** 📖
```http
GET /docs
```

**Purpose:** Interactive API documentation with try-it-out feature

---

### **5. ReDoc Documentation** 📘
```http
GET /redoc
```

**Purpose:** Alternative API documentation format

---

## 🔄 Registration Workflow

### **Step-by-Step Process**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER SUBMITS TEAM REGISTRATION                           │
│    POST /register/team                                      │
│    ✓ HTTP Request received by FastAPI                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 2. DATA VALIDATION                                          │
│    Pydantic validates all required fields                   │
│    ✓ Team information validation                            │
│    ✓ Captain/Vice-captain details validation               │
│    ✓ Player count validation (11-15)                        │
│    ✓ Email format validation                                │
│    ✓ Phone number format validation                         │
│    ✗ If invalid → Return 422 error                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 3. ADD TO QUEUE                                             │
│    Registration added to thread-safe queue                  │
│    ✓ Data serialized as dictionary                          │
│    ✓ Callback function registered                           │
│    ✓ IMMEDIATE response sent to client                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 4. BACKGROUND PROCESSING BEGINS                             │
│    Background worker thread picks up registration           │
│    ✓ Connects to Google Cloud                               │
│    ✓ Authenticates with service account                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 5. DUPLICATE DETECTION                                      │
│    Check for existing team (team_name + payment_receipt)    │
│    ✓ Fetch all existing team records                        │
│    ✓ Compare with new registration                          │
│    ✗ If duplicate → Return error                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 6. GENERATE TEAM ID                                         │
│    Auto-generate unique team ID                             │
│    Format: ICCT26-XXXX (e.g., ICCT26-0001)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 7. ADD TIMESTAMP                                            │
│    Current server time added automatically                  │
│    Format: YYYY-MM-DD HH:MM:SS                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 8. SAVE TO GOOGLE SHEETS                                    │
│    Save team info and player details to separate sheets     │
│    ✓ Connect to spreadsheet                                 │
│    ✓ Append team info to Sheet 1                            │
│    ✓ Append all player details to Sheet 2                   │
│    ✓ Link players to team via Team ID                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 9. SEND CONFIRMATION EMAIL                                  │
│    HTML-styled email sent to captain                        │
│    ✓ Connect to SMTP server                                 │
│    ✓ Use team registration template                         │
│    ✓ Include Team ID and all player names                   │
│    ✓ Send email with TLS encryption                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 10. COMPLETION                                              │
│    ✓ Log success to console                                 │
│    ✓ Call callback function                                 │
│    ✓ Mark queue task as done                                │
│    ✓ Ready for next registration                            │
└─────────────────────────────────────────────────────────────┘
```

### **Timeline**
- **User Perspective:** Receives response in < 100ms
- **Total Processing:** 3-7 seconds (depending on network and player count)
- **Data Availability:** Visible in Google Sheets immediately after save

---

## 🔍 Duplicate Detection

### **Detection Mechanism**

The system prevents duplicate registrations using a **composite key approach**:

```
Duplicate Check: (team_name + payment_receipt) pair
```

### **Logic**
1. When registration is queued, background worker retrieves all existing team records
2. Iterates through all records comparing:
   - `team_name` (Team Name)
   - `payment_receipt` (Payment Receipt Number)
3. If both match an existing record → **Duplicate Found**
4. Registration rejected with error message

### **Examples**

**Scenario 1: Valid Registration**
```json
NEW:
{
  "teamName": "Thunder Strikers",
  "paymentReceipt": "TXN123456789"
}
// ✓ ACCEPTED - No duplicate found
```

**Scenario 2: Duplicate Attempt**
```json
NEW:
{
  "teamName": "Thunder Strikers",
  "paymentReceipt": "TXN123456789"
}

EXISTING IN SHEET:
{
  "teamName": "Thunder Strikers",
  "paymentReceipt": "TXN123456789"
}
// ✗ REJECTED - Duplicate found
```

**Scenario 3: Different Payment (Valid)**
```json
NEW:
{
  "teamName": "Thunder Strikers",
  "paymentReceipt": "TXN987654321"
}

EXISTING IN SHEET:
{
  "teamName": "Thunder Strikers",
  "paymentReceipt": "TXN123456789"
}
// ✓ ACCEPTED - Different payment receipt
```

---

## 📧 Email Notifications

### **Overview**
Automated HTML-formatted confirmation emails are sent to team captains after successful registration. Emails include beautiful styling, team ID, all player names, and event information.

### **Email Features**

#### **Visual Design**
- 📐 Responsive HTML layout
- 🎨 Cricket-themed gradient header (Gold to Dark Blue)
- ✅ Success icon (cricket ball emoji) and confirmation message
- 🏏 Team details section with Team ID
- 👥 Complete player roster
- 📅 Event information section
- 🔗 Clean, professional styling

#### **Team Registration Email Template**
- **Gradient Color:** Gold/Blue (`#FFCC29` to `#002B5C`)
- **Sections:**
  - Header with success confirmation and cricket ball icon
  - Team ID (ICCT26-XXXX)
  - Team details (name, church, captain, vice-captain)
  - Complete player roster with roles
  - Payment confirmation
  - Event details (date, venue, location, organizer)
  - Tournament rules and next steps
  - Footer with contact information

### **Email Content Example**

**Subject:** `🏏 ICCT26 Team Registration Confirmed - Thunder Strikers`

**Body Includes:**
```
🎉 Team Registration Confirmed!
Dear John Doe,

Congratulations! Your team "Thunder Strikers" has been successfully 
registered for ICCT26 Cricket Tournament 2026.

🏏 Team Details
- Team ID: ICCT26-0001
- Team Name: Thunder Strikers
- Church: CSI St. Peter's Church
- Captain: John Doe
- Vice-Captain: Jane Smith
- Total Players: 11

👥 Team Roster
1. John Doe (Captain) - Jersey #1
2. Jane Smith (Vice-Captain) - Jersey #2
3. [... remaining players]

💳 Payment Confirmation
- Receipt Number: TXN123456789
- Registration Status: CONFIRMED

📅 Tournament Details
- Event: ICCT26 Cricket Tournament 2026
- Dates: January 24-26, 2026
- Venue: CSI St. Peter's Church Cricket Ground
- Location: Coimbatore, Tamil Nadu
- Format: Red Tennis Ball Cricket

📋 What's Next?
- Keep your Team ID safe (ICCT26-0001)
- Check your email for match schedule
- Review tournament rules
- Prepare your team for exciting matches
- Arrive 30 minutes before match time
```

### **SMTP Configuration**

**Setup Steps:**
1. Copy `.env.example` to `.env`
2. Add SMTP credentials

**Environment Variables:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=icct26@example.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=icct26@example.com
SMTP_FROM_NAME=ICCT26 Cricket Tournament
```

### **Provider Configuration**

**Gmail:**
```
Server: smtp.gmail.com
Port: 587
Username: your-email@gmail.com
Password: App-specific password (generate at myaccount.google.com/apppasswords)
```

**Outlook:**
```
Server: smtp-mail.outlook.com
Port: 587
Username: your-email@outlook.com
Password: Your Outlook password
```

**SendGrid:**
```
Server: smtp.sendgrid.net
Port: 587
Username: apikey
Password: Your SendGrid API key
```

### **Email Error Handling**
- If SMTP not configured → Email silently skipped, registration still processed
- If SMTP fails → Error logged, but registration completed
- Ensures registration always succeeds even if email fails

---

## 🗂️ Google Sheets Integration

### **Architecture**

**Spreadsheet Structure:**
```
📄 Google Spreadsheet (Single File)
├── 📊 Sheet 1 (Team Information)
│   ├── Headers: Team ID | Team Name | Church Name | Captain Name | 
│   │           Captain Phone | Captain Email | Vice-Captain Name | 
│   │           Vice-Captain Phone | Vice-Captain Email | 
│   │           Payment Receipt | Player Count | Timestamp
│   └── Data rows (1 per team)
│
└── 📊 Sheet 2 (Player Details)
    ├── Headers: Team ID | Team Name | Player Name | Phone | Email | 
    │           Role | Jersey Number | Timestamp
    └── Data rows (11-15 per team)
```

### **Two-Sheet Approach Benefits**
- ✓ Clean separation of team info vs player details
- ✓ Normalized data structure (no redundancy)
- ✓ Easy filtering by team or player
- ✓ Scalable to unlimited teams
- ✓ Better data analysis and reporting
- ✓ Individual player tracking

### **Automatic Features**

#### **Header Auto-Creation**
If sheets are empty, headers are automatically created:
- **Team Sheet:** Team ID, Team Name, Church Name, Captain Name, Captain Phone, Captain Email, Vice-Captain Name, Vice-Captain Phone, Vice-Captain Email, Payment Receipt, Player Count, Timestamp
- **Player Sheet:** Team ID, Team Name, Player Name, Phone, Email, Role, Jersey Number, Timestamp

#### **Team ID Generation**
Every team automatically receives a unique ID:
- Format: `ICCT26-XXXX`
- Sequential numbering (0001, 0002, 0003, etc.)
- Used to link team info with player details

#### **Timestamp Addition**
Every record automatically includes server timestamp in format: `YYYY-MM-DD HH:MM:SS`

#### **Row Format**
Data is appended as complete rows with all fields in order

#### **Duplicate Prevention**
Before appending, all existing records are checked for duplicates (team_name + payment_receipt match)

### **Authentication Methods**

#### **Method 1: Environment Variables (Production)**
```env
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...
GOOGLE_PRIVATE_KEY_ID=key-id
GOOGLE_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=client-id
```

#### **Method 2: credentials.json File (Development)**
Place `credentials.json` in project root with service account key JSON.

### **Setup Instructions**

**Step 1: Create Google Cloud Project**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create new project named "ICCT26-Backend"

**Step 2: Enable APIs**
- Enable Google Sheets API
- Enable Google Drive API

**Step 3: Create Service Account**
- Go to Service Accounts page
- Create service account: "icct26-registration"
- Generate JSON key
- Download and save as `credentials.json`

**Step 4: Share Google Sheet**
- Get service account email from credentials.json
- Open your target Google Sheet
- Share it with service account email (Editor access required)

**Step 5: Get Spreadsheet ID**
- Open your Google Sheet
- ID is in URL: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`
- Set `SPREADSHEET_ID` environment variable

### **Real-time Sync**
- ✓ Data appears in Google Sheets immediately after save
- ✓ Multiple instances can read/write simultaneously (queue-based)
- ✓ No caching - always fresh data
- ✓ Works with Google Sheets built-in features (sorting, filtering, formulas)

---

## 🌐 CORS Configuration

### **What is CORS?**
Cross-Origin Resource Sharing (CORS) allows frontend applications on different domains to make requests to this API.

### **Default Configuration**
```python
allow_origins = ["*"]  # Accept requests from all origins
allow_credentials = True
allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allow_headers = ["*"]
```

### **Customization**

**Option 1: Allow All (Default)**
```env
ALLOWED_ORIGINS=*
```

**Option 2: Specific Domains**
```env
ALLOWED_ORIGINS=https://icct26.com,https://register.icct26.com,http://localhost:3000
```

**Option 3: Production Setup**
```env
ALLOWED_ORIGINS=https://icct26.com,https://www.icct26.com
```

### **Frontend Integration Examples**

**Fetch API:**
```javascript
const response = await fetch('http://localhost:8000/register/team', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    churchName: "CSI St. Peter's Church",
    teamName: "Thunder Strikers",
    captainName: "John Doe",
    captainPhone: "+919876543210",
    captainEmail: "john.doe@example.com",
    // ... rest of the data
  })
});
const data = await response.json();
```

**Axios:**
```javascript
import axios from 'axios';

const response = await axios.post('http://localhost:8000/register/team', {
  churchName: "CSI St. Peter's Church",
  teamName: "Thunder Strikers",
  // ... rest of the data
});
```

---

## 📦 Data Models (Pydantic)

### **PlayerDetails Model**

```python
class PlayerDetails(BaseModel):
    name: str = Field(..., description="Player full name")
    phone: str = Field(..., description="Player phone number")
    email: str = Field(..., description="Player email address")
    role: str = Field(..., description="Player role (Captain/Vice-Captain/Player)")
    jerseyNumber: str = Field(..., description="Jersey number (1-99)")
```

### **TeamRegistration Model**

```python
class TeamRegistration(BaseModel):
    churchName: str = Field(..., description="Church name")
    teamName: str = Field(..., description="Team name (unique)")
    pastorLetter: Optional[str] = Field(None, description="Pastor letter file/base64")
    captainName: str = Field(..., description="Captain name")
    captainPhone: str = Field(..., description="Captain phone")
    captainWhatsapp: str = Field(..., description="Captain WhatsApp")
    captainEmail: str = Field(..., description="Captain email")
    viceCaptainName: str = Field(..., description="Vice-captain name")
    viceCaptainPhone: str = Field(..., description="Vice-captain phone")
    viceCaptainWhatsapp: str = Field(..., description="Vice-captain WhatsApp")
    viceCaptainEmail: str = Field(..., description="Vice-captain email")
    paymentReceipt: str = Field(..., description="Payment receipt number")
    players: List[PlayerDetails] = Field(..., description="List of 11-15 players")
```

**Validation:**
- ✓ All required fields must be present
- ✓ Player count: 11-15 (enforced)
- ✓ Email format validation
- ✓ Phone number format validation
- ✗ Invalid data → 422 Unprocessable Entity

---

## 🚀 Startup & Shutdown

### **Startup Process**

```
1️⃣ Load Environment Variables
   ✓ Read .env file
   ✓ Populate configuration

2️⃣ Initialize FastAPI App
   ✓ Set title: "ICCT26 Cricket Tournament Registration API"
   ✓ Set description
   ✓ Set version: "1.0.0"

3️⃣ Configure CORS
   ✓ Set allowed origins
   ✓ Enable credentials

4️⃣ Initialize Queue System
   ✓ Create thread-safe queue
   ✓ Define queue processor

5️⃣ Start Background Worker Thread
   ✓ Create daemon thread
   ✓ Start processing registrations

6️⃣ Validate Google Credentials
   ✓ Check credentials
   ✓ Create Google Sheets client

7️⃣ Display Startup Banner
   ✓ Show environment info
   ✓ Show port number
```

**Startup Console Output:**
```
============================================================
🏏 ICCT26 Cricket Tournament Registration API Starting...
============================================================
Event: ICCT26 Cricket Tournament 2026
Organizer: CSI St. Peter's Church, Coimbatore
Environment: DEVELOPMENT
Port: 8000
CORS Origins: *
============================================================
✓ Environment variables loaded
✓ Background worker thread started
✓ Queue system initialized
✓ Google Sheets integration ready
✓ Google Cloud credentials validated successfully
============================================================
```

### **Shutdown Process**

```
1️⃣ Signal Shutdown Event
   ✓ Wait for queued registrations

2️⃣ Drain Queue
   ✓ Process remaining registrations
   ✓ Complete all callbacks

3️⃣ Graceful Termination
   ✓ Close connections
   ✓ Stop background threads

4️⃣ Exit
   ✓ All data safely persisted
   ✓ No data loss
```

---

## ⚙️ Performance Features

### **1. Non-blocking Async I/O** ⚡
- FastAPI handles thousands of concurrent requests
- Instant response times
- I/O operations don't block API

### **2. Thread-safe Queue** 🔒
- Python's `queue.Queue` ensures thread safety
- No race conditions
- Atomic operations

### **3. Background Processing** 🔄
- Registrations processed asynchronously
- Client receives response in < 100ms

### **4. Efficient Duplicate Checking** 🎯
- Fast in-memory comparison
- O(n) complexity

### **5. Batch Operations** 📦
- Efficient Google Sheets API usage
- Single API calls for team + players

### **Performance Metrics**

| Metric | Value |
|--------|-------|
| API Response Time | < 100ms |
| Queue Processing | 3-7 seconds per team |
| Concurrent Requests | Unlimited (hardware limited) |
| Email Sending | ~2-3 seconds |
| Player Per Team | 11-15 |

---

## 🔧 Environment Configuration

### **Complete Environment Variables**

```env
# Application Settings
ENVIRONMENT=development
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=*

# Google Sheets Configuration
SPREADSHEET_ID=your-spreadsheet-id

# Google Cloud Credentials
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
GOOGLE_PRIVATE_KEY_ID=key-id
GOOGLE_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=client-id
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...
GOOGLE_UNIVERSE_DOMAIN=googleapis.com

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=icct26@example.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=icct26@example.com
SMTP_FROM_NAME=ICCT26 Cricket Tournament
```

---

## 🚀 Quick Start

### **1. Installation**

```bash
# Clone repository
git clone <repository-url>
cd icct26-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Setup Google Credentials**

```bash
# Download service account JSON
# Save as credentials.json in project root
# Share Google Sheet with service account email
```

### **3. Setup Email**

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with SMTP credentials
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### **4. Run Server**

```bash
# Run with Python
python main.py

# Or use uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **5. Access API**

- **Home:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Queue Status:** http://localhost:8000/queue/status

### **6. Test Registration**

```bash
curl -X POST "http://localhost:8000/register/team" \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "CSI St. Peter'\''s Church",
    "teamName": "Thunder Strikers",
    "captainName": "John Doe",
    "captainPhone": "+919876543210",
    "captainWhatsapp": "919876543210",
    "captainEmail": "john.doe@example.com",
    "viceCaptainName": "Jane Smith",
    "viceCaptainPhone": "+919123456789",
    "viceCaptainWhatsapp": "919123456789",
    "viceCaptainEmail": "jane.smith@example.com",
    "paymentReceipt": "TXN123456789",
    "players": [
      {
        "name": "John Doe",
        "phone": "+919876543210",
        "email": "john.doe@example.com",
        "role": "Captain",
        "jerseyNumber": "1"
      }
    ]
  }'
```

---

## 📊 Summary Table

| Feature | Details |
|---------|---------|
| **Type** | RESTful API with async processing |
| **Purpose** | Cricket tournament team registration |
| **Framework** | FastAPI 0.104+ |
| **Server** | Uvicorn (ASGI) |
| **Python Version** | 3.8+ |
| **Registration Types** | Complete team (11-15 players) |
| **Queue System** | Thread-safe, non-blocking |
| **Data Storage** | Google Sheets (2 worksheets) |
| **Notifications** | HTML email confirmations (SMTP) |
| **Validation** | Pydantic + duplicate detection |
| **Documentation** | Swagger UI + ReDoc |
| **CORS** | Enabled, customizable |
| **Scalability** | Handles thousands of concurrent requests |
| **Team ID Format** | ICCT26-XXXX (auto-generated) |
| **Players Per Team** | 11-15 required |

---

## 🔗 Useful Links

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Pydantic Docs:** https://docs.pydantic.dev/
- **Google Sheets API:** https://developers.google.com/sheets/api
- **gspread Library:** https://docs.gspread.org/
- **Uvicorn Server:** https://www.uvicorn.org/

---

**Last Updated:** November 4, 2025  
**Version:** 1.0.0  
**Event:** ICCT26 Cricket Tournament 2026  
**Organizer:** CSI St. Peter's Church, Coimbatore

