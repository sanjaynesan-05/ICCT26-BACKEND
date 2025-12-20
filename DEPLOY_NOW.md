# 🚀 Quick Deployment Guide - ICCT26 Backend

## ✅ Pre-Deployment Checklist

- [x] All tests passing (48/48) ✅
- [x] Server running locally ✅
- [x] Database connected (Neon PostgreSQL) ✅
- [x] Payment approval endpoints working ✅
- [ ] Production environment variables configured
- [ ] Cloudinary configured for file uploads
- [ ] Email SMTP configured
- [ ] Domain/URL decided

---

## 🎯 Recommended: Deploy to Render.com (FREE)

**Why Render?**
- ✅ Free tier (750 hours/month)
- ✅ Auto-deploy from GitHub
- ✅ Built-in PostgreSQL database
- ✅ SSL certificates included
- ✅ Easy environment variables
- ✅ Automatic health checks

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare Your Repository

```bash
# Make sure all deployment files are committed
git add Procfile render.yaml runtime.txt .env.production
git commit -m "Add deployment configuration"
git push origin main
```

### Step 2: Create Render Account

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with **GitHub**
4. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Select your **ICCT26 BACKEND** repository
3. Click **"Connect"**

### Step 4: Configure Service

**Basic Settings:**
```
Name: icct26-backend
Region: Singapore (or closest to your users)
Branch: main
Runtime: Python 3
```

**Build & Deploy:**
```
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Instance Type:**
```
Free (512 MB RAM, shared CPU)
```

### Step 5: Add Environment Variables

Click **"Environment"** and add these:

#### Required Variables:

```bash
# Application
ENVIRONMENT=production
DEBUG=false
APP_TITLE=ICCT26 Cricket Tournament Registration API

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://neondb_owner:YOUR_PASSWORD@YOUR_HOST.neon.tech/neondb?sslmode=require
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=0
DATABASE_POOL_RECYCLE=300

# Cloudinary (Get from console.cloudinary.com)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Email (Gmail App Password)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@icct26.com

# Security (Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))")
SECRET_KEY=your-generated-secret-key-here

# API
API_URL=https://icct26-backend.onrender.com
API_HOST=0.0.0.0
API_PORT=8000

# CORS (Your frontend URL)
CORS_ORIGINS=["https://your-frontend.vercel.app","http://localhost:3000"]

# Features
ENABLE_COMPRESSION=true
ENABLE_RATE_LIMITING=true
LOG_LEVEL=INFO
```

### Step 6: Deploy!

1. Click **"Create Web Service"**
2. Wait for deployment (3-5 minutes)
3. Your API will be live at: `https://icct26-backend.onrender.com`

### Step 7: Verify Deployment

**Test your endpoints:**
```bash
# Health check
curl https://icct26-backend.onrender.com/health

# API docs
# Open in browser: https://icct26-backend.onrender.com/docs

# Admin teams endpoint
curl https://icct26-backend.onrender.com/admin/teams
```

---

## 🗄️ Database Setup (Neon PostgreSQL)

### Option 1: Use Existing Neon Database

Your current `.env` already has Neon configured. Just copy that `DATABASE_URL` to Render environment variables.

### Option 2: Create New Neon Database

1. Go to **https://console.neon.tech**
2. Create new project: **"icct26-production"**
3. Copy connection string
4. Run migration:
   ```bash
   # Update DATABASE_URL in .env to production
   python -c "from database import Base, engine; Base.metadata.create_all(engine)"
   ```

---

## 📧 Email Configuration

### Gmail Setup (Recommended for Testing)

1. Go to **https://myaccount.google.com/apppasswords**
2. Create new app password for "ICCT26 Backend"
3. Copy the 16-character password
4. Add to Render environment variables:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop  # 16-char app password
   ```

### SendGrid Setup (Production)

1. Sign up at **https://sendgrid.com** (Free tier: 100 emails/day)
2. Create API key
3. Configure:
   ```
   SMTP_SERVER=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USERNAME=apikey
   SMTP_PASSWORD=YOUR_SENDGRID_API_KEY
   ```

---

## 🖼️ Cloudinary Configuration

1. Go to **https://console.cloudinary.com**
2. Sign up / Log in
3. Copy from dashboard:
   ```
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=123456789012345
   CLOUDINARY_API_SECRET=abcdefghijklmnopqrs
   ```
4. Add to Render environment variables

---

## 🔐 Security

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy output and add as `SECRET_KEY` in Render.

---

## 🌐 Custom Domain (Optional)

1. In Render dashboard → **Settings** → **Custom Domains**
2. Add: `api.icct26.com`
3. Update DNS:
   ```
   Type: CNAME
   Name: api
   Value: icct26-backend.onrender.com
   ```

---

## 📊 Monitoring & Logs

### View Logs
- Render Dashboard → **Logs** tab
- Real-time log streaming
- Search and filter

### Health Checks
- Automatic health checks every 30 seconds
- Endpoint: `/health`
- Auto-restart on failures

### Metrics
- CPU usage
- Memory usage
- Request count
- Response times

---

## 🔄 Auto-Deploy Setup

**Already configured!** Every `git push` to `main` triggers deployment:

```bash
# Make changes
git add .
git commit -m "Update payment approval logic"
git push origin main

# Render automatically deploys in 2-3 minutes
```

---

## 🚨 Troubleshooting

### Deployment Failed

**Check build logs:**
1. Render Dashboard → Logs
2. Look for errors in build phase
3. Common issues:
   - Missing dependencies in `requirements.txt`
   - Python version mismatch
   - Environment variables missing

### Database Connection Error

**Fix:**
1. Verify `DATABASE_URL` format includes `?sslmode=require`
2. Check Neon database is active (not suspended)
3. Verify connection string is correct

### 500 Internal Server Error

**Debug:**
1. Check Render logs for Python errors
2. Verify all environment variables are set
3. Test endpoints locally first
4. Check Cloudinary credentials

### Application Won't Start

**Common causes:**
1. Missing `PORT` environment variable (Render sets this automatically)
2. Wrong start command (should be: `uvicorn main:app --host 0.0.0.0 --port $PORT`)
3. Import errors in Python code

---

## ✅ Post-Deployment Checklist

- [ ] Backend URL working: `https://your-app.onrender.com`
- [ ] Health endpoint returns 200: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Admin teams endpoint working: `/admin/teams`
- [ ] Payment approval endpoints working
- [ ] Database connected (no connection errors in logs)
- [ ] Cloudinary uploads working
- [ ] Email notifications sending
- [ ] CORS configured for frontend
- [ ] SSL certificate active (https://)

---

## 🔗 Update Frontend

After deployment, update frontend `.env`:

```env
VITE_API_BASE_URL=https://icct26-backend.onrender.com
```

Then redeploy frontend.

---

## 💰 Cost Estimate

**Render Free Tier:**
- ✅ Backend: FREE (750 hours/month)
- ✅ SSL: FREE
- ✅ Auto-deploy: FREE

**Neon PostgreSQL:**
- ✅ Database: FREE (3 projects, 0.5 GB storage)

**Cloudinary:**
- ✅ Image hosting: FREE (25 GB storage, 25 GB bandwidth)

**Total Monthly Cost: $0** 🎉

---

## 📞 Support

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com

**Neon Support:**
- Docs: https://neon.tech/docs
- Discord: https://discord.gg/neon

---

## 🎯 Next Steps

1. **Deploy Backend** (follow steps above)
2. **Test Endpoints** (use `/docs` Swagger UI)
3. **Update Frontend** with production URL
4. **Deploy Frontend** (Vercel/Netlify)
5. **Test Complete Flow** (registration → payment → approval)
6. **Monitor Logs** for any issues

---

**Your backend is production-ready!** 🚀

All 48 tests passed, payment approval system working, database connected.  
Just follow the steps above to go live in ~10 minutes!
