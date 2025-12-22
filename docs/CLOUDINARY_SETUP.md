# 🚀 CLOUDINARY SETUP GUIDE

## Why You Need Cloudinary

Your registration endpoint is now configured to upload files (pastor letters, payment receipts, group photos, player documents) to **Cloudinary** - a cloud-based file storage service. Without Cloudinary credentials, file uploads will fail.

## Current Status

✅ **Registration endpoint**: Configured to upload to Cloudinary  
❌ **Cloudinary credentials**: NOT configured (using default "demo" values)  
❌ **File uploads**: Will fail until credentials are added

## Quick Setup (5 minutes)

### Step 1: Create Free Cloudinary Account

1. Go to: **https://cloudinary.com/users/register/free**
2. Sign up with your email
3. Verify your email address
4. You get **25GB free storage** + 25GB bandwidth/month (perfect for ICCT26)

### Step 2: Get Your Credentials

1. Login to: **https://console.cloudinary.com**
2. Go to **Dashboard** (you'll see it immediately after login)
3. Look for **"Product Environment Credentials"** section
4. You'll see:
   - **Cloud Name**: `your-unique-cloud-name`
   - **API Key**: `123456789012345` (15 digits)
   - **API Secret**: `abcdefghijklmnopqrstuvwxyz` (hidden, click "Reveal")

### Step 3: Update .env File

Open `d:\ICCT26 BACKEND\.env` and replace these lines:

```env
CLOUDINARY_CLOUD_NAME=your-cloud-name-here
CLOUDINARY_API_KEY=your-api-key-here
CLOUDINARY_API_SECRET=your-api-secret-here
```

**With your actual values:**

```env
CLOUDINARY_CLOUD_NAME=demo  # Replace with your cloud name
CLOUDINARY_API_KEY=123456789012345  # Replace with your API key
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz  # Replace with your API secret
```

### Step 4: Restart Server

```powershell
# Stop the current server (Ctrl+C in terminal)
# Then restart:
cd "d:\ICCT26 BACKEND"
& "D:/ICCT26 BACKEND/venv/Scripts/python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Verification

After updating credentials, check server startup logs for:

```
✅ Cloudinary initialized successfully
```

If you see this, you're ready! New registrations will upload files to Cloudinary.

## What Gets Uploaded

Each team registration uploads files to Cloudinary organized like this:

```
pending/
  ICCT-001/
    ICCT-001_pastor_letter.pdf
    ICCT-001_payment_receipt.pdf
    ICCT-001_group_photo.jpg
    players/
      ICCT-001-P01_aadhar.pdf
      ICCT-001-P01_subscription.pdf
      ICCT-001-P02_aadhar.pdf
      ICCT-001-P02_subscription.pdf
      ... (up to 11 players)
```

After admin confirmation, files move to:

```
confirmed/
  ICCT-001/
    ... (same structure)
```

## URLs Stored in Database

Cloudinary returns secure HTTPS URLs like:

```
https://res.cloudinary.com/your-cloud-name/image/upload/v1234567890/pending/ICCT-001/ICCT-001_pastor_letter.pdf
```

These URLs are stored in your Neon database:
- **teams table**: `pastor_letter`, `payment_receipt`, `group_photo` columns
- **players table**: `aadhar_file`, `subscription_file` columns

## Free Tier Limits

- **Storage**: 25 GB
- **Bandwidth**: 25 GB/month
- **Transformations**: 25 credits/month
- **API requests**: Unlimited

For ICCT26:
- Avg file size: ~100 KB
- 100 teams × 14 files = 1,400 files
- Total storage: ~140 MB (0.5% of free tier)

**You're well within free limits!** 🎉

## Troubleshooting

### Error: "Cloudinary upload failed"

**Check:**
1. `.env` file has correct credentials (no spaces, no quotes)
2. Server was restarted after updating `.env`
3. Cloudinary account is active (check email for verification)

### Error: "Invalid cloud name"

**Fix:** Copy cloud name exactly from Cloudinary dashboard (case-sensitive)

### Error: "Invalid API credentials"

**Fix:** 
1. Click "Reveal" for API Secret in Cloudinary dashboard
2. Copy the full secret (usually 27 characters)
3. Update `.env` file
4. Restart server

## Alternative: Test Without Cloudinary

If you want to test registration **without Cloudinary** (files won't be stored):

1. Open `app/routes/registration_production.py`
2. Find line ~346: `logger.info(f"[{request_id}] Uploading team files to Cloudinary...")`
3. Replace the upload section with dummy URLs (as before)

But this defeats the purpose - your admin won't have access to uploaded documents!

## Next Steps

1. ✅ Set up Cloudinary credentials (5 min)
2. ✅ Test registration with real file uploads
3. ✅ Verify files appear in Cloudinary dashboard
4. ✅ Check database has real Cloudinary URLs

---

**Need help?** Check Cloudinary docs: https://cloudinary.com/documentation
