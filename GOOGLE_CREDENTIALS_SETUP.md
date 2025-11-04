# Google Cloud Service Account Setup Guide

## Step-by-Step Instructions to Get Your Credentials

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter your project name (e.g., "icct26-registration")
5. Click "Create"

### Step 2: Enable Required APIs
1. In your project, go to "APIs & Services" → "Library"
2. Search for and enable:
   - **Google Sheets API**
   - **Google Drive API** (needed for Sheets access)

### Step 3: Create a Service Account
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in:
   - **Service account name**: `icct26-service-account`
   - **Service account ID**: `icct26-service-account` (auto-filled)
   - **Description**: `Service account for ICCT26 registration system`
4. Click "Create and Continue"
5. Skip the role assignment for now (we'll add it later)
6. Click "Done"

### Step 4: Create and Download JSON Key
1. In the "Credentials" page, find your new service account
2. Click on the service account name
3. Go to the "Keys" tab
4. Click "Add Key" → "Create new key"
5. Choose "JSON" format
6. Click "Create"

**⚠️ IMPORTANT:** A JSON file will download automatically. **Keep this file secure!**

### Step 5: Grant Permissions to Service Account
1. In the service account details, go to the "Permissions" tab
2. Click "Grant Access"
3. Add your own Google account as a principal (for testing)
4. Grant these roles:
   - **Editor** (for Google Sheets access)
   - **Service Account Token Creator** (optional, for advanced use)

### Step 6: Create Google Sheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it "ICCT26 Team Registrations"
4. Create these worksheets (tabs):
   - **Teams** - Main registration data
   - **Players** - Player details
   - **Files** - File upload tracking

### Step 7: Share Sheet with Service Account
1. In your Google Sheet, click "Share"
2. Paste your service account email (from the JSON file: `client_email`)
3. Give it "Editor" access
4. Click "Send"

### Step 8: Extract Values from JSON File

Open the downloaded JSON file and copy these values:

```json
{
  "type": "service_account",  // → GOOGLE_CREDENTIALS_TYPE
  "project_id": "your-project-id",  // → GOOGLE_PROJECT_ID
  "private_key_id": "abc123...",  // → GOOGLE_PRIVATE_KEY_ID
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",  // → GOOGLE_PRIVATE_KEY
  "client_email": "account@project.iam.gserviceaccount.com",  // → GOOGLE_CLIENT_EMAIL
  "client_id": "123456789",  // → GOOGLE_CLIENT_ID
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",  // → GOOGLE_AUTH_URI
  "token_uri": "https://oauth2.googleapis.com/token",  // → GOOGLE_TOKEN_URI
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",  // → GOOGLE_AUTH_PROVIDER_X509_CERT_URL
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/...",  // → GOOGLE_CLIENT_X509_CERT_URL
  "universe_domain": "googleapis.com"  // → GOOGLE_UNIVERSE_DOMAIN
}
```

### Step 9: Create Your .env File

1. Copy `.env.example` to `.env`
2. Replace the placeholder values with your actual JSON values
3. Get your spreadsheet ID from the URL: `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`

### Step 10: Test the Connection

Run your backend and check the logs. You should see:
```
✓ Google Sheets integration ready
```

## Troubleshooting

### "Access denied" errors:
- Make sure the service account has "Editor" access to the Google Sheet
- Verify the JSON credentials are correct
- Check that Google Sheets API is enabled

### "Invalid credentials" errors:
- Regenerate the JSON key if corrupted
- Ensure no extra spaces or characters in .env values
- Check that the private key includes the `\n` line breaks

### "API not enabled" errors:
- Go back to Google Cloud Console and enable the required APIs
- Wait 5-10 minutes for APIs to activate

## Security Notes

- **Never commit the .env file** to version control
- **Keep the JSON key file secure** - anyone with it can access your Google services
- **Use environment-specific service accounts** for production vs development
- **Rotate keys regularly** for security

## Cost Information

Google Cloud service accounts are **free**. The Google Sheets API has generous free quotas:
- 100 requests per 100 seconds
- 1000 requests per day (free tier)

Your usage will be well within free limits for a tournament registration system.