# Render Deployment Configuration

## Build Command
```bash
pip install -r requirements.txt
```

## Start Command
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables (Set in Render Dashboard)

### Required
```
DATABASE_URL=postgresql://user:pass@host/dbname
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
JWT_SECRET_KEY=your-long-random-secret
SECRET_KEY=your-long-random-secret
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM_EMAIL=noreply@icct26.com
API_URL=https://your-app.onrender.com
ENVIRONMENT=production
```

### Optional
```
LOG_LEVEL=INFO
ENABLE_COMPRESSION=true
ENABLE_RATE_LIMITING=true
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Python Version
Add `.python-version` file with:
```
3.11
```

## Deployment Steps

1. **Commit changes**
   ```bash
   git add .
   git commit -m "Fix: Add pydantic-settings and update config"
   git push origin main
   ```

2. **Render Dashboard**
   - Go to https://dashboard.render.com
   - Select your service
   - Go to "Environment" tab
   - Add all required environment variables above
   - Click "Save Changes"

3. **Manual Deploy (if auto-deploy disabled)**
   - Click "Manual Deploy" → "Deploy latest commit"

4. **Check Logs**
   - Go to "Logs" tab
   - Look for: "Application startup complete"
   - Check for errors during startup

5. **Test Deployment**
   ```bash
   curl https://your-app.onrender.com/health
   curl https://your-app.onrender.com/docs
   ```

## Troubleshooting

### If "Module not found" error persists
1. Check requirements.txt includes `pydantic-settings>=2.0.0`
2. Trigger rebuild: Settings → Manual Deploy → Clear build cache

### If app crashes on startup
1. Check environment variables are set correctly
2. Check logs for specific error
3. Verify DATABASE_URL format is correct

### If database connection fails
1. Ensure DATABASE_URL includes `postgresql+asyncpg://` prefix
2. Check database is accessible from Render
3. Verify database credentials

## Health Check Endpoint
```
GET /health
```
Should return 200 OK when app is running correctly.
