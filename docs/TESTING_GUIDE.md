# 🧪 Testing Guide - Google Sheets Integration

This guide walks you through testing the ICCT26 backend with Google Sheets integration.

---

## ✅ Pre-Testing Checklist

Before you start testing, make sure:

- [ ] Backend server is running (`uvicorn main:app --reload`)
- [ ] `.env` file has all required Google credentials
- [ ] `SPREADSHEET_ID` is set in `.env`
- [ ] Google Sheets spreadsheet exists and is shared with service account
- [ ] SMTP credentials are configured (for email testing)
- [ ] All Python dependencies are installed

---

## 📊 Google Sheets Setup

### 1. Create a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet titled **"ICCT26 Cricket Tournament"**
3. Copy the Spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit
   ```
4. Update your `.env` file:
   ```bash
   SPREADSHEET_ID=YOUR_SPREADSHEET_ID
   ```

### 2. Create Required Sheets

Create the following sheets (tabs) in your spreadsheet:

**Sheet 1: Teams**
- Headers: `Team ID`, `Team Name`, `Church Name`, `Captain Name`, `Captain Phone`, `Captain Email`, `Vice Captain Name`, `Vice Captain Phone`, `Vice Captain Email`, `Player Count`, `Registration Date`

**Sheet 2: Players**
- Headers: `Player ID`, `Team ID`, `Player Name`, `Age`, `Phone`, `Role`, `Registration Date`

**Sheet 3: Files**
- Headers: `File ID`, `Team ID`, `File Type`, `File Name`, `File Size`, `Upload Date`

### 3. Share Sheet with Service Account

1. Click **Share** button in Google Sheet
2. Add the service account email from your `.env`:
   ```
   icct26@icct26.iam.gserviceaccount.com
   ```
3. Give **Editor** access
4. Click **Share**

---

## 🚀 Running the Backend Server

### Start the Server

```bash
cd D:\ICCT26 BACKEND
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Access API Documentation

- **Swagger UI:** <http://localhost:8000/docs>
- **ReDoc:** <http://localhost:8000/redoc>
- **Queue Status:** <http://localhost:8000/queue/status>

---

## 🧪 Testing Methods

### Method 1: Using Swagger UI (Interactive Testing)

1. Open <http://localhost:8000/docs>
2. Click on **POST /register/team** endpoint
3. Click **Try it out**
4. Fill in the request body with test data
5. Click **Execute**

#### Sample Test Data

```json
{
  "churchName": "CSI St. Peter's Church",
  "teamName": "Test Strikers",
  "pastorLetter": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "captain": {
    "name": "John Doe",
    "phone": "9876543210",
    "whatsapp": "9876543210",
    "email": "john@example.com"
  },
  "viceCaptain": {
    "name": "Jane Smith",
    "phone": "9123456789",
    "whatsapp": "9123456789",
    "email": "jane@example.com"
  },
  "players": [
    {
      "name": "Player One",
      "age": 25,
      "phone": "9111111111",
      "role": "Batsman",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player Two",
      "age": 28,
      "phone": "9122222222",
      "role": "Bowler",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player Three",
      "age": 30,
      "phone": "9133333333",
      "role": "All-rounder",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }
  ],
  "paymentReceipt": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

**Minimum 11 players required!** Add 8 more players following the same structure.

### Method 2: Using cURL (Command Line)

Create a file `test_registration.json`:

```json
{
  "churchName": "CSI St. Peter's Church",
  "teamName": "Thunder Team",
  "pastorLetter": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "captain": {
    "name": "Test Captain",
    "phone": "9876543210",
    "whatsapp": "9876543210",
    "email": "captain@test.com"
  },
  "viceCaptain": {
    "name": "Vice Captain",
    "phone": "9123456789",
    "whatsapp": "9123456789",
    "email": "vicecaptain@test.com"
  },
  "players": [
    {"name": "P1", "age": 25, "phone": "9111111111", "role": "Batsman", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
    {"name": "P2", "age": 26, "phone": "9122222222", "role": "Bowler", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
    {"name": "P3", "age": 27, "phone": "9133333333", "role": "All-rounder", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
    {"name": "P4", "age": 28, "phone": "9144444444", "role": "Wicket-keeper", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
    {"name": "P5", "age": 29, "phone": "9155555555", "role": "Batsman", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
    {"name": "P6", "age": 30, "phone": "9166666666", "role": "Bowler", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
    {"name": "P7", "age": 31, "phone": "9177777777", "role": "All-rounder", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
    {"name": "P8", "age": 32, "phone": "9188888888", "role": "Batsman", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
    {"name": "P9", "age": 33, "phone": "9199999999", "role": "Bowler", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
    {"name": "P10", "age": 34, "phone": "9100000000", "role": "All-rounder", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
    {"name": "P11", "age": 35, "phone": "9101010101", "role": "Wicket-keeper", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}
  ],
  "paymentReceipt": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

Then run:

```bash
curl -X POST http://localhost:8000/register/team `
  -H "Content-Type: application/json" `
  -d @test_registration.json
```

### Method 3: Check Queue Status

```bash
curl http://localhost:8000/queue/status
```

Expected response:

```json
{
  "queue_size": 1,
  "worker_active": true,
  "timestamp": "2026-01-15T10:40:15Z"
}
```

---

## 📊 Verifying Google Sheets Updates

After sending a registration request:

1. **Wait 2-5 seconds** for background processing
2. Open your Google Sheet
3. Check the **Teams** sheet - new row should appear
4. Check the **Players** sheet - 11 player rows should appear
5. Check the **Files** sheet - 4 file entries should appear (pastor letter, payment receipt, aadhar files from first 2 players as sample)

### Expected Data Format in Sheets

**Teams Sheet:**
```
Test Strikers | CSI St. Peter's Church | John Doe | 9876543210 | john@example.com | Jane Smith | 9123456789 | jane@example.com | 11 | 2026-01-15T10:30:45Z
```

**Players Sheet:**
```
1 | Player One | 25 | 9111111111 | Batsman | 2026-01-15T10:30:45Z
2 | Player Two | 28 | 9122222222 | Bowler | 2026-01-15T10:30:45Z
...
```

---

## ✅ Testing Checklist

After running a test registration:

- [ ] **Instant Response:** API responds immediately with `"status": "processing"`
- [ ] **Queue Processing:** Queue processes registration in background
- [ ] **Teams Sheet:** New team row appears within 5 seconds
- [ ] **Players Sheet:** All 11+ players appear in sheet
- [ ] **Files Sheet:** Document files are tracked
- [ ] **Email Confirmation:** Confirmation email sent (check spam folder)
- [ ] **No Duplicate:** Same team name in different request creates separate entry
- [ ] **Validation:** Invalid data (e.g., age < 15) is rejected with error message

---

## 🐛 Troubleshooting

### "SPREADSHEET_ID not found" Error

**Solution:**
1. Copy your spreadsheet ID from the URL
2. Update `.env`: `SPREADSHEET_ID=your-id`
3. Restart the server

### "Permission denied" Error

**Solution:**
1. Go to your Google Sheet
2. Click **Share**
3. Add: `icct26@icct26.iam.gserviceaccount.com`
4. Give **Editor** access
5. Verify service account email matches in `.env`

### "Invalid credentials" Error

**Solution:**
1. Check all Google credentials in `.env` are correct
2. Verify `GOOGLE_PRIVATE_KEY` has proper newlines: `\n` not actual line breaks
3. Download fresh credentials JSON from Google Cloud Console
4. Update `.env` with new credentials

### Server Crashes with "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt
```

### "Port 8000 already in use"

**Solution:**
```bash
uvicorn main:app --port 8001 --reload
```

---

## 📈 Performance Testing

### Test with Multiple Registrations

1. Send 5 registrations with different team names
2. Verify all appear in Google Sheets within 10 seconds
3. Check queue status doesn't show errors
4. Monitor response times (should be < 500ms)

### Test with Invalid Data

1. Missing players (< 11) → Should reject
2. Player age < 15 or > 60 → Should reject
3. Invalid email format → Should reject
4. Missing required fields → Should reject
5. Invalid base64 files → Should reject

---

## 📝 Test Results Template

**Date:** ____________________
**Tester:** __________________

### Registration Test
- [ ] Request accepted
- [ ] Instant response: YES / NO
- [ ] Response time: _______ ms
- [ ] Team appears in sheet: YES / NO
- [ ] Time to appear: _______ seconds
- [ ] Player count correct: YES / NO
- [ ] Email received: YES / NO

### Data Validation Tests
- [ ] Invalid age rejected: YES / NO
- [ ] Missing players rejected: YES / NO
- [ ] Invalid email rejected: YES / NO
- [ ] Duplicate team allowed: YES / NO

### Performance
- [ ] Queue processing works: YES / NO
- [ ] No data loss: YES / NO
- [ ] Sheet updates accurate: YES / NO

### Issues Found:
_________________________________
_________________________________

---

**Next Steps:** After successful testing, proceed with frontend integration using [REGISTRATION_REFACTOR.md](./REGISTRATION_REFACTOR.md)
