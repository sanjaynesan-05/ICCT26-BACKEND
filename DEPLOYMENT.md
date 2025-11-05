# 🚀 ICCT26 Backend - Deployment Guide

## Overview

This guide covers deploying the ICCT26 Cricket Tournament Registration API to **Render** (or any cloud platform).

---

## Table of Contents

1. [Render Deployment](#render-deployment)
2. [Environment Configuration](#environment-configuration)
3. [Health Monitoring](#health-monitoring)
4. [Troubleshooting](#troubleshooting)
5. [Post-Deployment Checklist](#post-deployment-checklist)

---

## Render Deployment

### Prerequisites

- GitHub repository pushed and synced
- Render account created at [render.com](https://render.com)
- Google Cloud credentials configured
- SMTP credentials (optional, for email confirmations)

### Step 1: Create a New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository (`ICCT26-BACKEND`)
4. Select the `main` branch
5. Configure settings:
   - **Name:** `icct26-backend`
   - **Runtime:** `Python 3.11` (upgrade from 3.10 if available)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free or Starter (depends on traffic)

### Step 2: Configure Environment Variables

In Render dashboard, go to **Environment** and add all variables from `.env.example`:

```
GOOGLE_CREDENTIALS_TYPE=service_account
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=your-key-id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=your-service-account@project-id.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40project-id.iam.gserviceaccount.com
GOOGLE_UNIVERSE_DOMAIN=googleapis.com

SPREADSHEET_ID=your-spreadsheet-id
GOOGLE_DRIVE_FOLDER_ID=your-folder-id

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=ICCT26 Cricket Tournament
```

**Important:** 
- Use **Gmail App Password** (not regular password) for SMTP
- Keep `GOOGLE_PRIVATE_KEY` format exactly as shown (with `\n` newlines)

### Step 3: Deploy

Click **"Create Web Service"** → Render will automatically build and deploy.

Monitor logs in real-time on the Render dashboard.

---

## Environment Configuration

### Google Cloud Setup

If not already done:

1. **Create Google Cloud Project** (see [docs/GOOGLE_CREDENTIALS_SETUP.md](./docs/GOOGLE_CREDENTIALS_SETUP.md))
2. **Enable APIs:**
   - Google Sheets API
   - Google Drive API
3. **Create Service Account** with JSON key
4. **Share Spreadsheet** with service account email
5. **Create Google Drive Folder** and share with service account

### .env File (Local Development)

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with actual values (never commit this file).

### Render Environment Variables

Paste the same values into Render's Environment section. Use the format provided in the dashboard.

---

## Health Monitoring

### Health Check Endpoint

The API includes a dedicated health check endpoint for monitoring:

```
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "service": "ICCT26 Cricket Tournament Registration API",
    "version": "2.0.0",
    "timestamp": "2025-11-05 12:00:00"
}
```

### Configure Render Health Checks

1. In Render dashboard, go to your service
2. Scroll to **"Health Check Path"**
3. Set it to `/health`
4. Set **"Check Interval"** to 300 seconds (default)
5. Save

This prevents unnecessary restarts and helps Render manage instance lifecycle properly.

### Monitoring Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /` | Service info & features | JSON with features list |
| `GET /health` | Health status | Status, version, timestamp |
| `GET /queue/status` | Queue stats | Queue size, worker status |
| `POST /register/team` | Register team | Queued response |

---

## Troubleshooting

### "Bad Gateway" Error

**Cause:** Backend not binding to correct port.

**Fix:**
- ✅ Already fixed in `main.py` (uses `os.environ.get("PORT", 8000)`)
- Verify Render's PORT is assigned (check logs)
- Restart service in Render dashboard

### HEAD Requests Return 405 Method Not Allowed

**Cause:** Render health checks send HEAD requests; only GET is defined.

**Fix:**
- ✅ Already fixed with `/health` endpoint (FastAPI auto-supports HEAD for GET endpoints)
- These are safe to ignore if you see them in logs

### SMTP Emails Not Sending

**Cause:** SMTP credentials not configured.

**Fix:**
1. Generate Gmail App Password: https://myaccount.google.com/apppasswords
2. Add to Render environment:
   ```
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```
3. Restart service
4. Check logs for "SMTP service configured"

### Google Sheets/Drive Not Updating

**Cause:** Service account doesn't have access.

**Fix:**
1. Share Google Sheets with service account email (from JSON key)
2. Share Google Drive folder with service account email
3. Verify `SPREADSHEET_ID` and `GOOGLE_DRIVE_FOLDER_ID` are correct
4. Check Render logs for auth errors

### High Memory Usage

**Cause:** Python 3.10 deprecated; consider upgrading.

**Fix:**
1. In Render, change **Runtime** to Python 3.11 or 3.12
2. Redeploy

---

## Post-Deployment Checklist

- [ ] **Service is running** – Visit `https://your-render-url.onrender.com/` and see API info
- [ ] **Health endpoint works** – Check `https://your-render-url.onrender.com/health`
- [ ] **Queue processor active** – Check logs for "Background worker thread started"
- [ ] **Google integration ready** – Logs show "Google Sheets integration ready"
- [ ] **CORS enabled** – Frontend can call API from different domain
- [ ] **SSL/HTTPS enabled** – Render provides free SSL by default
- [ ] **Monitoring configured** – Health check path set to `/health`
- [ ] **Error logs reviewed** – No critical errors in Render dashboard logs

### Test Registration

Send a test registration to verify end-to-end:

```bash
curl -X POST https://your-render-url.onrender.com/register/team \
  -H "Content-Type: application/json" \
  -d '{"churchName":"Test Church","teamName":"Test Team",...}'
```

---

## Auto-Deploy Configuration

Render automatically redeploys when you push to `main` branch.

**To disable auto-deploy:**
1. Go to service **Settings** → **Deploy**
2. Turn off **"Auto-Deploy"**

---

## Logs & Debugging

### View Real-Time Logs

Render dashboard → Service → **"Logs"** tab

### Common Log Patterns

| Pattern | Meaning |
|---------|---------|
| `[OK] Google Sheets integration ready` | Service initialized successfully |
| `Started team registration queue processor` | Background worker running |
| `⚠ SMTP not configured` | Emails disabled (add SMTP_USERNAME to enable) |
| `FutureWarning: Python 3.10` | Upgrade to Python 3.11+ |
| `POST /register/team HTTP/1.1" 200 OK` | Registration received successfully |

---

## Performance Tips

1. **Use Free Tier for Development** – Render spins down after 15 minutes of inactivity
2. **Monitor Queue Size** – Check `/queue/status` to detect bottlenecks
3. **Enable HTTP/2** – Render supports it by default
4. **CDN for Static Files** – If you add a frontend, use Netlify or Vercel
5. **Database (Optional)** – For analytics, add PostgreSQL on Render

---

## Support & Next Steps

- **Frontend Integration** – Ensure frontend sends requests to deployed backend URL
- **Custom Domain** – Add your domain in Render settings
- **SSL Certificate** – Already included with Render hosting
- **Team Collaboration** – Share Render dashboard access with team members

For issues, check:
1. Render logs (dashboard)
2. `.env` variables are correct and complete
3. Google Cloud credentials have proper permissions
4. GitHub repository is up-to-date

---

## Related Documentation

- [Google Credentials Setup](./docs/GOOGLE_CREDENTIALS_SETUP.md)
- [Google Drive Setup](./docs/GOOGLE_DRIVE_SETUP.md)
- [Main README](./README.md)
- [API Documentation](./docs/MODELS_DOCUMENTATION.md)

---

**Last Updated:** November 5, 2025  
**Version:** 2.0.0

