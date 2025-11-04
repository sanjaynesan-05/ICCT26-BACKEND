# 🏏 ICCT26 Cricket Tournament Backend - README

## 🎯 Project Overview

A **FastAPI-based asynchronous team registration system** for the **ICCT26 Cricket Tournament** organized by **CSI St. Peter's Church, Coimbatore**. This backend handles high-volume team registrations with real-time Google Sheets integration and automated email confirmations.

**Event:** ICCT26 Cricket Tournament 2026  
**Format:** Red Tennis Ball Cricket  
**Dates:** January 24-26, 2026  
**Location:** CSI St. Peter's Church Cricket Ground, Coimbatore, Tamil Nadu

---

## ⚡ Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
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

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials:
# - Google Cloud credentials
# - SMTP credentials for email
# - Spreadsheet ID
# - Port and CORS settings
```

### 3. Setup Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account
5. Generate a JSON key file
6. Save as `credentials.json` in project root
7. Share your Google Sheet with the service account email

### 4. Run the Server

```bash
# Using Python directly
python main.py

# Or using Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the API

- **API Home:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Queue Status:** http://localhost:8000/queue/status

---

## 📚 Documentation

### Complete Documentation Files:

1. **CRICKET_TOURNAMENT_DOCUMENTATION.md** - Complete backend documentation
   - All features and functionality
   - API endpoints with examples
   - Setup instructions
   - Architecture diagrams

2. **CONVERSION_SUMMARY.md** - Conversion history
   - Changes from CTF to Cricket Tournament
   - Data structure updates
   - Processing changes

3. **BACKEND_DOCUMENTATION.md** - Old documentation (for reference)

---

## 🚀 API Endpoints

### Register Team
```http
POST /register/team
```
Register a cricket team with 11-15 players

**Request:**
```json
{
  "churchName": "CSI St. Peter's Church",
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
    // ... 10-14 more players
  ]
}
```

**Response:**
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

### Get Queue Status
```http
GET /queue/status
```
Get current registration queue status

**Response:**
```json
{
  "queue_size": 3,
  "worker_active": true,
  "timestamp": "2026-01-15 10:40:15"
}
```

### API Documentation
```http
GET /
GET /docs
GET /redoc
```

---

## 🔑 Key Features

✅ **Asynchronous Processing** - Queue-based registration system  
✅ **Team Management** - Support for 11-15 players per team  
✅ **Real-time Sync** - Google Sheets integration  
✅ **Auto Team ID** - ICCT26-XXXX format  
✅ **Email Confirmations** - Cricket-themed HTML emails  
✅ **Duplicate Prevention** - Team name + payment receipt check  
✅ **Data Normalization** - Separate team and player sheets  
✅ **No Data Loss** - Thread-safe queue system  
✅ **CORS Enabled** - Cross-origin request support  
✅ **Auto Documentation** - Swagger UI and ReDoc  

---

## 📊 Data Models

### PlayerDetails
```python
- name: str
- phone: str
- email: str
- role: str (Captain/Vice-Captain/Player)
- jerseyNumber: str
```

### TeamRegistration
```python
- churchName: str
- teamName: str (unique)
- pastorLetter: Optional[str]
- captainName: str
- captainPhone: str
- captainWhatsapp: str
- captainEmail: str
- viceCaptainName: str
- viceCaptainPhone: str
- viceCaptainWhatsapp: str
- viceCaptainEmail: str
- paymentReceipt: str (unique with team name)
- players: List[PlayerDetails] (11-15 required)
```

---

## 🗂️ Google Sheets Structure

### Sheet 1: Team Information
```
Team ID | Team Name | Church Name | Captain Name | Captain Phone | 
Captain Email | Vice-Captain Name | Vice-Captain Phone | 
Vice-Captain Email | Payment Receipt | Player Count | Timestamp
```

### Sheet 2: Player Details
```
Team ID | Team Name | Player Name | Phone | Email | Role | Jersey Number | Timestamp
```

---

## 🔧 Environment Variables

```env
# Application
ENVIRONMENT=development
PORT=8000

# CORS
ALLOWED_ORIGINS=*

# Google Sheets
SPREADSHEET_ID=your-spreadsheet-id

# Google Cloud
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY=your-private-key
GOOGLE_PRIVATE_KEY_ID=your-key-id
GOOGLE_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_X509_CERT_URL=your-cert-url
GOOGLE_UNIVERSE_DOMAIN=googleapis.com

# SMTP (Email)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=ICCT26 Cricket Tournament
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| API Response Time | < 100ms |
| Registration Processing | 3-7 seconds |
| Concurrent Requests | Unlimited (hardware dependent) |
| Email Delivery | 2-3 seconds per team |
| Players Per Team | 11-15 |

---

## 🛡️ Duplicate Detection

The system prevents duplicate team registrations using:
- **Team Name** + **Payment Receipt** composite key
- If both match an existing team → Registration rejected
- Ensures each payment maps to one unique team

---

## 💌 Email Notifications

Teams receive automatic HTML-formatted confirmation emails with:
- 🏏 Team ID (ICCT26-XXXX)
- 👥 Complete player roster
- 📅 Tournament details
- 💳 Payment confirmation
- 📋 Next steps

---

## 🚨 Error Handling

| Status | Error | Solution |
|--------|-------|----------|
| 400 | Invalid player count | Must have 11-15 players |
| 400 | Duplicate team | Team + payment already exists |
| 422 | Invalid request format | Check all required fields |
| 500 | Google Sheets error | Check credentials and permissions |
| 500 | SMTP error | Email fails but registration completes |

---

## 📝 Logging

All important events are logged to console:

```
✓ Team registration request received
✓ Team ID generated: ICCT26-0001
✓ Duplicate detection passed
✓ Team data saved to Google Sheets
✓ Player data saved to Google Sheets
✓ Confirmation email sent
✓ Registration complete
```

---

## 🧪 Testing

### Test Registration
```bash
curl -X POST "http://localhost:8000/register/team" \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "CSI St. Peter'\''s Church",
    "teamName": "Test Team",
    "captainName": "Test Captain",
    "captainPhone": "+919999999999",
    "captainWhatsapp": "919999999999",
    "captainEmail": "test@example.com",
    "viceCaptainName": "Test Vice",
    "viceCaptainPhone": "+919999999998",
    "viceCaptainWhatsapp": "919999999998",
    "viceCaptainEmail": "vice@example.com",
    "paymentReceipt": "TEST001",
    "players": [
      {"name": "Player 1", "phone": "+911", "email": "p1@example.com", "role": "Captain", "jerseyNumber": "1"},
      {"name": "Player 2", "phone": "+912", "email": "p2@example.com", "role": "Player", "jerseyNumber": "2"},
      {"name": "Player 3", "phone": "+913", "email": "p3@example.com", "role": "Player", "jerseyNumber": "3"},
      {"name": "Player 4", "phone": "+914", "email": "p4@example.com", "role": "Player", "jerseyNumber": "4"},
      {"name": "Player 5", "phone": "+915", "email": "p5@example.com", "role": "Player", "jerseyNumber": "5"},
      {"name": "Player 6", "phone": "+916", "email": "p6@example.com", "role": "Player", "jerseyNumber": "6"},
      {"name": "Player 7", "phone": "+917", "email": "p7@example.com", "role": "Player", "jerseyNumber": "7"},
      {"name": "Player 8", "phone": "+918", "email": "p8@example.com", "role": "Player", "jerseyNumber": "8"},
      {"name": "Player 9", "phone": "+919", "email": "p9@example.com", "role": "Player", "jerseyNumber": "9"},
      {"name": "Player 10", "phone": "+9110", "email": "p10@example.com", "role": "Player", "jerseyNumber": "10"},
      {"name": "Player 11", "phone": "+9111", "email": "p11@example.com", "role": "Vice-Captain", "jerseyNumber": "11"}
    ]
  }'
```

---

## 📞 Support & Contact

- **Event:** ICCT26 Cricket Tournament 2026
- **Organizer:** CSI St. Peter's Church, Coimbatore
- **Format:** Red Tennis Ball Cricket
- **Venue:** CSI St. Peter's Church Cricket Ground

---

## 📋 Project Files

- **main.py** - Main FastAPI application
- **requirements.txt** - Python dependencies
- **.env.example** - Environment variables template
- **CRICKET_TOURNAMENT_DOCUMENTATION.md** - Complete documentation
- **CONVERSION_SUMMARY.md** - Conversion from CTF to Cricket Tournament
- **README.md** - This file

---

## 🔄 Workflow

1. User submits team registration via API
2. FastAPI validates data (Pydantic)
3. Registration added to queue
4. Immediate response sent to user (< 100ms)
5. Background worker processes registration:
   - Generates Team ID
   - Checks for duplicates
   - Saves to Google Sheets (team + players)
   - Sends confirmation email
6. User receives email with Team ID
7. Team data visible in Google Sheets

---

## ✨ Created By

**Backend Conversion:** November 4, 2025  
**Version:** 1.0.0  
**Event:** ICCT26 Cricket Tournament 2026  
**Organizer:** CSI St. Peter's Church, Coimbatore

---

**Status: ✅ Production Ready**

🏏 Ready to handle team registrations for ICCT26 Cricket Tournament!

