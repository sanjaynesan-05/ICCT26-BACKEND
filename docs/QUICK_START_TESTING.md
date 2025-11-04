# 🚀 Google Sheets Integration - Testing Instructions

## ✅ Current Status

Your ICCT26 backend is **fully configured and running** with Google Sheets integration ready!

**Server Status:** ✅ Running on `http://localhost:8001`
**API Documentation:** ✅ Available at <http://localhost:8001/docs>
**Environment:** ✅ All Google credentials loaded
**Google Sheets:** ✅ Integration ready

---

## 📊 Step 1: Create Google Sheet

### Option A: Use Existing Spreadsheet (Recommended)
If you already have a spreadsheet ID in `.env`, **skip to Step 2**.

### Option B: Create New Spreadsheet

1. Open [Google Sheets](https://sheets.google.com)
2. Click **"+ New"** → **"Blank spreadsheet"**
3. Name it: **"ICCT26 Cricket Tournament"**
4. Copy the spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/[COPY_THIS_ID]/edit
   ```
5. Update your `.env` file:
   ```bash
   SPREADSHEET_ID=YOUR_COPIED_ID
   ```
6. Restart the server (or it will auto-reload if configured)

---

## 🔐 Step 2: Share with Service Account

1. In your Google Sheet, click **Share** (top-right)
2. Add this email:
   ```
   icct26@icct26.iam.gserviceaccount.com
   ```
3. Select **Editor** permission
4. Click **Share**

⚠️ **Important:** Without this step, the backend cannot write to the sheet.

---

## 📋 Step 3: Create Sheet Tabs

Create three worksheets by clicking the **"+"** icon at the bottom:

### Tab 1: Teams

| Team ID | Team Name | Church Name | Captain Name | Captain Phone | Captain Email | Vice Captain Name | Vice Captain Phone | Vice Captain Email | Player Count | Registration Date |
|---------|-----------|-------------|--------------|----------------|----------------|-------------------|-------------------|-------------------|--------------|-------------------|

(Headers only needed - backend will auto-populate rows)

### Tab 2: Players

| Player ID | Team ID | Player Name | Age | Phone | Role | Registration Date |
|----------|---------|-------------|-----|-------|------|-------------------|

### Tab 3: Files

| File ID | Team ID | File Type | File Name | File Size | Upload Date |
|---------|---------|-----------|-----------|-----------|-------------|

---

## 🧪 Step 4: Test Registration

### Method A: Using Swagger UI (Easy - Recommended!)

1. Open <http://localhost:8001/docs>
2. Scroll down to find **`POST /register/team`**
3. Click **"Try it out"**
4. Replace the request body with this test data:

```json
{
  "churchName": "CSI St. Peter's Church",
  "teamName": "Test Team One",
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
      "name": "Player 1",
      "age": 25,
      "phone": "9111111111",
      "role": "Batsman",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player 2",
      "age": 28,
      "phone": "9122222222",
      "role": "Bowler",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player 3",
      "age": 30,
      "phone": "9133333333",
      "role": "All-rounder",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player 4",
      "age": 32,
      "phone": "9144444444",
      "role": "Batsman",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player 5",
      "age": 34,
      "phone": "9155555555",
      "role": "Bowler",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player 6",
      "age": 36,
      "phone": "9166666666",
      "role": "All-rounder",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player 7",
      "age": 38,
      "phone": "9177777777",
      "role": "Wicket-keeper",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player 8",
      "age": 40,
      "phone": "9188888888",
      "role": "Batsman",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player 9",
      "age": 42,
      "phone": "9199999999",
      "role": "Bowler",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player 10",
      "age": 44,
      "phone": "9100000001",
      "role": "All-rounder",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    },
    {
      "name": "Player 11",
      "age": 46,
      "phone": "9100000002",
      "role": "Batsman",
      "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }
  ],
  "paymentReceipt": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

5. Click **"Execute"**
6. Check the response - should see:
   ```json
   {
     "success": true,
     "message": "Team registration queued successfully",
     "status": "processing"
   }
   ```

### Method B: Using Python Test Script

```bash
cd D:\ICCT26 BACKEND
python test_google_sheets.py
```

---

## ✅ Step 5: Verify Google Sheets Update

After sending a registration request:

1. **Wait 3-5 seconds** for background processing
2. Go to your Google Sheet
3. Click the **"Teams"** tab
4. You should see a new row with:
   - Team name: "Test Team One"
   - Church name: "CSI St. Peter's Church"
   - Captain: "John Doe"
   - Player count: 11

5. Click the **"Players"** tab
6. You should see 11 new rows with all player data

---

## 📊 What Gets Synced to Google Sheets?

### Teams Sheet
- Team ID (auto-generated)
- Team Name
- Church Name
- Captain Name & Contact
- Vice Captain Name & Contact
- Player Count
- Registration Date

### Players Sheet
- Player ID (auto-generated)
- Team ID (links to Teams)
- Player Name
- Age
- Phone
- Role
- Registration Date

### Files Sheet
- File ID (auto-generated)
- Team ID (links to Teams)
- File Type (Pastor Letter, Payment Receipt, Aadhar, Subscription)
- File Name
- File Size
- Upload Date

---

## 🎯 Expected Test Results

| Check | Expected Result |
|-------|-----------------|
| API Response Time | < 500ms |
| Status | "processing" |
| Google Sheets Update | Within 5 seconds |
| Teams Row Added | ✅ Yes |
| Players Row Added | ✅ 11 rows |
| Data Accuracy | ✅ All fields correct |
| No Data Loss | ✅ Queue thread-safe |

---

## 🔍 Queue Status Endpoint

To check real-time queue status:

```bash
curl http://localhost:8001/queue/status
```

Response:

```json
{
  "queue_size": 0,
  "worker_active": true,
  "timestamp": "2026-01-15T10:40:15Z"
}
```

- **queue_size**: 0 = no pending registrations, 1+ = being processed
- **worker_active**: true = background worker running
- **timestamp**: Current server time

---

## 📧 Email Notifications

After registration, an email should be sent to the captain's email with:

- ✅ Team name and church name
- ✅ Number of registered players
- ✅ Registration timestamp
- ✅ Confirmation message

**Check your email spam folder if not in inbox!**

---

## ❌ Troubleshooting

### Problem: "Permission denied" Error in Console

**Solution:**
- Go to Google Sheet → Share
- Add: `icct26@icct26.iam.gserviceaccount.com`
- Select Editor access
- Click Share

### Problem: Google Sheet Not Updating

**Solution:**
- Check SPREADSHEET_ID in `.env` is correct
- Verify service account is shared with Editor access
- Check backend console for errors
- Restart server: Stop and run `python -m uvicorn main:app --host 127.0.0.1 --port 8001`

### Problem: "SPREADSHEET_ID not found"

**Solution:**
- Update SPREADSHEET_ID in `.env`
- Restart server

### Problem: API Returns 422 Validation Error

**Solution:**
- Check you have exactly 11+ players
- All players must have age 15-60
- All emails must be valid format
- All phone numbers must be 10 digits

---

## 🎉 Success Indicators

✅ **You've successfully integrated Google Sheets when:**

1. Backend starts without errors
2. API responds to requests instantly
3. New teams appear in Google Sheet within 5 seconds
4. All 11 players are recorded
5. Document files are tracked
6. Confirmation emails are received

---

## 📖 Next Steps

1. ✅ **Test Complete** - Backend is working with Google Sheets
2. 🔄 **Frontend Integration** - See [REGISTRATION_REFACTOR.md](./REGISTRATION_REFACTOR.md)
3. 📊 **Production Setup** - Configure for live deployment
4. 🚀 **Go Live** - Launch registration for event

---

## 📞 Support

- **API Docs:** <http://localhost:8001/docs>
- **Testing Guide:** [docs/TESTING_GUIDE.md](./TESTING_GUIDE.md)
- **Models Reference:** [docs/MODELS_DOCUMENTATION.md](./MODELS_DOCUMENTATION.md)
- **Google Setup:** [docs/GOOGLE_CREDENTIALS_SETUP.md](./GOOGLE_CREDENTIALS_SETUP.md)

---

**Last Updated:** November 4, 2025
**Backend Status:** ✅ Ready for Testing
**Google Sheets Integration:** ✅ Ready for Testing
