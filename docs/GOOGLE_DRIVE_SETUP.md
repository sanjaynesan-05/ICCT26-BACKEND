# 🗂️ Google Drive File Upload Setup Guide

## Overview

This guide will help you set up Google Drive integration to automatically upload registration files (Aadhar cards, subscription cards, pastor letters, and payment receipts) from team registrations.

## 📋 Prerequisites

- Google Cloud Project with Drive API enabled
- Service Account with credentials (from GOOGLE_CREDENTIALS_SETUP.md)
- Google Drive folder to store registration files

---

## 🚀 Setup Steps

### Step 1: Enable Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (e.g., "battle-of-binaries")
3. Navigate to **APIs & Services** → **Library**
4. Search for "Google Drive API"
5. Click **Enable**

### Step 2: Create Google Drive Folder

1. Go to [Google Drive](https://drive.google.com/)
2. Click **+ New** → **Folder**
3. Name it: **"ICCT26 Team Registrations"** (or your preferred name)
4. Click **Create**

### Step 3: Get Folder ID

1. Open the folder you just created
2. Look at the URL in your browser:
   ```
   https://drive.google.com/drive/folders/1AbC2DeFgHiJkLmN3oPqRsTuVwXyZ
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                          This is your FOLDER ID
   ```
3. Copy the **Folder ID** (the random string after `/folders/`)

### Step 4: Share Folder with Service Account

1. In the folder, click the **Share** button (top right)
2. In the "Add people and groups" field, paste your service account email:
   ```
   icct26@battle-of-binaries.iam.gserviceaccount.com
   ```
   (Use YOUR service account email from `.env`)
3. Set permission to **Editor**
4. **Uncheck** "Notify people" (it's a service account, not a real person)
5. Click **Share**

### Step 5: Update .env File

Add the folder ID to your `.env` file:

```bash
# Google Drive Configuration
GOOGLE_DRIVE_FOLDER_ID=1AbC2DeFgHiJkLmN3oPqRsTuVwXyZ
```

Replace with your actual folder ID from Step 3.

### Step 6: Install Required Package

Install the Google API client library:

```bash
pip install google-api-python-client
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

---

## 📁 File Organization

When a team registers, the system will:

1. **Create a team folder** in your main folder:
   - Format: `ICCT26-0XX_TeamName`
   - Example: `ICCT26-0001_Warriors`

2. **Upload files** to the team folder:
   - `ICCT26-0XX_Pastor_Letter.pdf`
   - `ICCT26-0XX_Payment_Receipt.pdf`
   - `ICCT26-0XX_Player1_PlayerName_Aadhar.pdf`
   - `ICCT26-0XX_Player1_PlayerName_Subscription.pdf`
   - ... (for each player)

### Example Folder Structure:

```
📁 ICCT26 Team Registrations/
├── 📁 ICCT26-0001_Warriors/
│   ├── 📄 ICCT26-0001_Pastor_Letter.pdf
│   ├── 📄 ICCT26-0001_Payment_Receipt.pdf
│   ├── 📄 ICCT26-0001_Player1_John_Doe_Aadhar.pdf
│   ├── 📄 ICCT26-0001_Player1_John_Doe_Subscription.pdf
│   ├── 📄 ICCT26-0001_Player2_Jane_Smith_Aadhar.pdf
│   ├── 📄 ICCT26-0001_Player2_Jane_Smith_Subscription.pdf
│   └── ... (more players)
├── 📁 ICCT26-0002_Crusaders/
│   └── ... (team files)
└── 📁 ICCT26-0003_Champions/
    └── ... (team files)
```

---

## ✅ Testing

### Test the Setup

1. Start your server:
   ```bash
   python main.py
   ```

2. Submit a test registration through your frontend or API

3. Check your Google Drive folder - you should see:
   - A new folder for the team
   - All uploaded files inside that folder

### Verify in Console

Watch the server console for upload messages:

```
✅ Created team folder: 1XyZ...abc
✅ Uploaded file 'ICCT26-0001_Pastor_Letter.pdf' to Google Drive (ID: 1AbC...)
✅ Uploaded file 'ICCT26-0001_Payment_Receipt.pdf' to Google Drive (ID: 1DeF...)
✅ Uploaded file 'ICCT26-0001_Player1_John_Doe_Aadhar.pdf' to Google Drive (ID: 1GhI...)
...
✅ Uploaded 26/26 files to Google Drive
```

---

## 🔧 Troubleshooting

### Error: "Drive folder not configured"

**Problem:** `GOOGLE_DRIVE_FOLDER_ID` not set in `.env`

**Solution:**
1. Follow Step 3 to get your folder ID
2. Add it to `.env` file
3. Restart the server

### Error: "The user does not have sufficient permissions"

**Problem:** Service account doesn't have access to the folder

**Solution:**
1. Open your Google Drive folder
2. Click **Share**
3. Add your service account email with **Editor** permission
4. Try again

### Error: "Access not configured. Drive API has not been used"

**Problem:** Google Drive API not enabled

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Library**
3. Search for "Google Drive API"
4. Click **Enable**
5. Wait 1-2 minutes for activation
6. Try again

### Files Not Uploading

**Check:**
1. ✅ Drive API is enabled
2. ✅ `GOOGLE_DRIVE_FOLDER_ID` is set correctly
3. ✅ Service account has Editor access to folder
4. ✅ `google-api-python-client` is installed
5. ✅ All Google credentials in `.env` are correct

### Base64 Decoding Error

**Problem:** Invalid file data format

**Solution:**
- Ensure frontend sends files as base64 with data URI prefix:
  ```
  data:image/png;base64,iVBORw0KGgoAAAANS...
  ```
- Or plain base64 without prefix

---

## 🎯 What's Changed

### New Code Features

1. **File Upload Functions:**
   - `upload_file_to_drive()` - Uploads single base64 file to Drive
   - `upload_team_files_to_drive()` - Uploads all team files at once

2. **Enhanced save_to_google_sheet():**
   - Now includes Drive API scope
   - Automatically uploads files after saving to Sheets
   - Returns Drive upload results

3. **File Type Support:**
   - Pastor letters
   - Payment receipts
   - Player Aadhar cards
   - Player subscription cards

### New Dependencies

- `google-api-python-client` - Google Drive API client
- Added Drive scope to service account credentials

---

## 📊 Response Format

After a successful registration, the API returns:

```json
{
  "success": true,
  "message": "Registration successful!",
  "team_id": "ICCT26-0001",
  "players_count": 11,
  "drive_upload": {
    "success": true,
    "message": "Uploaded 26/26 files",
    "team_folder_id": "1XyZ...abc",
    "uploads": [
      {
        "type": "pastor_letter",
        "success": true,
        "file_id": "1AbC...",
        "web_view_link": "https://drive.google.com/file/d/1AbC.../view"
      },
      {
        "type": "payment_receipt",
        "success": true,
        "file_id": "1DeF...",
        "web_view_link": "https://drive.google.com/file/d/1DeF.../view"
      },
      {
        "type": "aadhar",
        "player": "John_Doe",
        "success": true,
        "file_id": "1GhI...",
        "web_view_link": "https://drive.google.com/file/d/1GhI.../view"
      }
      // ... more files
    ]
  }
}
```

---

## 🎉 You're All Set!

Once configured, your system will automatically:
- ✅ Save team data to Google Sheets
- ✅ Upload all files to Google Drive (organized by team)
- ✅ Send confirmation emails
- ✅ Provide file links in the response

**Next Step:** Test with a registration to verify everything works!

---

## 📞 Need Help?

- Check server console for detailed error messages
- Verify all `.env` variables are set correctly
- Ensure service account has proper permissions
- Test with a small file first (< 1MB)

**Last Updated:** November 4, 2025
