# 🧪 QUICK TESTING CHECKLIST

## 🚀 Start Here (2 minutes)

### 1. Verify Server is Running
```powershell
# Terminal shows:
# Uvicorn running on http://127.0.0.1:8001
```

### 2. Open API Docs
- **Swagger UI:** <http://localhost:8001/docs>
- **ReDoc:** <http://localhost:8001/redoc>

### 3. Create Google Sheet (if needed)
1. Go to <https://sheets.google.com>
2. Create new blank spreadsheet
3. Copy spreadsheet ID from URL
4. Update `.env`: `SPREADSHEET_ID=YOUR_ID`

### 4. Share with Service Account
1. Click **Share** in Google Sheet
2. Add: `icct26@icct26.iam.gserviceaccount.com`
3. Give **Editor** access

---

## 📋 Test Registration (5 minutes)

### Quick Test
1. Open <http://localhost:8001/docs>
2. Find `POST /register/team`
3. Click "Try it out"
4. Copy test JSON below
5. Click "Execute"

### Minimal Test Data
```json
{
  "churchName": "Test Church",
  "teamName": "Test Team 001",
  "pastorLetter": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "captain": {
    "name": "Captain Test",
    "phone": "9876543210",
    "whatsapp": "9876543210",
    "email": "captain@test.com"
  },
  "viceCaptain": {
    "name": "Vice Test",
    "phone": "9123456789",
    "whatsapp": "9123456789",
    "email": "vice@test.com"
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
    {"name": "P11", "age": 35, "phone": "9101010101", "role": "Batsman", "aadharFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "subscriptionFile": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}
  ],
  "paymentReceipt": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

---

## ✅ Verify in Google Sheets (3 minutes)

### Expected Results After Registration

| Sheet | What to Look For |
|-------|------------------|
| Teams | New row with "Test Team 001" |
| Players | 11 new rows (P1-P11) |
| Files | Document entries |

### Check Response
- Status: `"processing"`
- Success: `true`
- Message: Contains "queued successfully"

---

## 🎯 Quick Commands

### Start Server (if not running)
```powershell
cd D:\ICCT26 BACKEND
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

### Check Queue Status
```bash
curl http://localhost:8001/queue/status
```

### Run Test Script
```powershell
cd D:\ICCT26 BACKEND
python test_google_sheets.py
```

---

## 📍 Key URLs

| Resource | URL |
|----------|-----|
| Swagger UI | <http://localhost:8001/docs> |
| ReDoc | <http://localhost:8001/redoc> |
| Queue Status | <http://localhost:8001/queue/status> |
| Google Sheets | <https://sheets.google.com> |

---

## ✅ Testing Completed When:

- [ ] Server running on port 8001
- [ ] Swagger UI accessible
- [ ] Registration request accepted (status 200/202)
- [ ] Response shows "processing"
- [ ] Google Sheet updated within 5 seconds
- [ ] All 11 players appear in sheet
- [ ] Team data matches submission

---

**👉 Next:** See [QUICK_START_TESTING.md](./QUICK_START_TESTING.md) for detailed guide
