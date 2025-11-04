# 🧪 Test Google Sheets & Drive Integration

## Quick Start

Follow these steps to test the Google Sheets and Google Drive file upload integration:

### Step 1: Start the Server

Open a terminal and navigate to the project directory:

```bash
cd "D:\ICCT26 BACKEND"
python main.py
```

Wait until you see the message indicating the server is running:
```
INFO:     Started server process [XXXX]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Run the Test (in another terminal)

Once the server is running, open another terminal and run:

```bash
cd "D:\ICCT26 BACKEND"
python test_drive_sheets.py
```

### Step 3: Watch the Test Run

The test will:

1. **Load rulebook.pdf** (13 KB)
2. **Convert to base64** for upload
3. **Create test team data** with 11 players
4. **Send registration** with all files
5. **Display results** showing:
   - Google Sheets worksheet created
   - Google Drive files uploaded
   - File links and IDs

### Expected Results

If successful, you'll see:

```
✅ REGISTRATION SUCCESSFUL!

📊 Registration Response:
   Team ID: ICCT26-0XX
   Players Count: 11
   Sheet Name: ICCT26-0XX_Test_Warriors_HHMMSS
   Processing Time: X.XX seconds

📄 Google Sheets:
   Sheet Link: https://docs.google.com/spreadsheets/d/...

📁 Google Drive Upload:
   Status: ✅ SUCCESS
   Team Folder ID: 1AbC...
   Message: Uploaded 24/24 files

📤 File Uploads (24 total):
   ✅ Pastor Letter: 1/1
   ✅ Payment Receipt: 1/1
   ✅ Aadhar: 11/11
   ✅ Subscription: 11/11
```

### Manual Verification

After running the test:

#### In Google Sheets:
1. Open your Google Sheets file
2. Look for new tab: `ICCT26-0XX_Test_Warriors_HHMMSS`
3. Verify content:
   - Team Information section ✓
   - Captain & Vice-Captain details ✓
   - Uploaded Files section with Drive links ✓
   - Players table with 11 rows ✓
   - File links for each player ✓

#### In Google Drive:
1. Open folder: "ICCT26 Team Registrations"
2. Look for new folder: `ICCT26-0XX_Test_Warriors_HHMMSS`
3. Verify files inside (should be 24 total):
   - `ICCT26-0XX_Pastor_Letter.pdf`
   - `ICCT26-0XX_Payment_Receipt.pdf`
   - `ICCT26-0XX_Player1_Player_1_Aadhar.pdf`
   - `ICCT26-0XX_Player1_Player_1_Subscription.pdf`
   - ... (for all 11 players)

### Troubleshooting

#### "Connection Error: Cannot connect to http://localhost:8000"
- Make sure server is running in first terminal
- Check that you used `python main.py` command

#### "File not found: ./rulebook.pdf"
- Make sure you're in `D:\ICCT26 BACKEND` directory
- Verify `rulebook.pdf` exists in that directory

#### "Drive folder not configured"
- Check `.env` file has `GOOGLE_DRIVE_FOLDER_ID` set
- See `docs/GOOGLE_DRIVE_SETUP.md` for configuration

#### "Insufficient permissions" error
- Make sure service account has **Editor** access to Drive folder
- Re-share the folder with service account email

#### Server crash during startup
- Check for Python errors in the console
- Try: `pip install -r requirements.txt`
- Ensure all `.env` variables are set correctly

### Files Involved

- `main.py` - Backend server with upload functionality
- `test_drive_sheets.py` - Comprehensive test script
- `rulebook.pdf` - Test file for uploads
- `.env` - Configuration with Google credentials

### What Gets Tested

✅ **Google Drive:**
- Creates folder for team
- Uploads all files (Pastor Letter, Payment Receipt)
- Uploads player documents (Aadhar, Subscription cards)
- Returns direct links to files

✅ **Google Sheets:**
- Creates new worksheet per team
- Formats team information
- Adds captain & vice-captain details
- Displays file links
- Creates player table with links
- Updates Teams_Index master sheet

✅ **Integration:**
- Files upload to Drive
- Links appear in Sheets
- Everything organized and accessible

### Performance

Expected test duration: **10-30 seconds**
- File conversion: ~1 second
- Registration: ~5-20 seconds (depends on file size and network)
- Sheet creation: ~2-5 seconds

### Next Steps

Once test passes:
1. ✅ Integration is working!
2. 🎉 Ready for production
3. 📝 Test with real registrations
4. 🚀 Deploy to server

---

**Need help?** Check:
- `README.md` - Full documentation
- `docs/GOOGLE_DRIVE_SETUP.md` - Setup guide
- `SHEETS_STRUCTURE.md` - Data structure details
