# Final Deployment Checklist

## ✅ File Structure
```
ICCT26-BACKEND/
├── main.py                    # FastAPI app entry point
├── config.py                  # Settings with pydantic-settings
├── requirements.txt           # All dependencies including pydantic-settings
├── .python-version            # Python 3.11
├── .env                       # Local env (NOT committed)
├── app/
│   ├── __init__.py
│   ├── routes/
│   ├── models/
│   ├── schemas/
│   ├── utils/
│   └── middleware/
└── tests/
```

## ✅ Pre-Deployment Verification

### 1. Local Test
```bash
# Install dependencies
pip install -r requirements.txt

# Verify pydantic-settings installed
python -c "from pydantic_settings import BaseSettings; print('OK')"

# Test import
python -c "from config import settings; print(settings.APP_TITLE)"

# Run tests
pytest tests/ -v

# Start locally
uvicorn main:app --reload
```

### 2. Commit & Push
```bash
git status
git add .
git commit -m "fix: Add pydantic-settings and update config for Render"
git push origin main
```

## ✅ Render Configuration

### Build Command
```
pip install -r requirements.txt
```

### Start Command
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables (REQUIRED)
Set these in Render Dashboard → Environment tab:

| Variable | Example Value | Required |
|----------|---------------|----------|
| `DATABASE_URL` | `postgresql://user:pass@host/db` | ✅ |
| `CLOUDINARY_CLOUD_NAME` | `your-cloud-name` | ✅ |
| `CLOUDINARY_API_KEY` | `123456789` | ✅ |
| `CLOUDINARY_API_SECRET` | `abcdef123456` | ✅ |
| `JWT_SECRET_KEY` | `random-64-char-string` | ✅ |
| `SECRET_KEY` | `random-64-char-string` | ✅ |
| `SMTP_HOST` | `smtp.gmail.com` | ✅ |
| `SMTP_PORT` | `587` | ✅ |
| `SMTP_USER` | `your-email@gmail.com` | ✅ |
| `SMTP_PASS` | `app-password` | ✅ |
| `SMTP_FROM_EMAIL` | `noreply@icct26.com` | ✅ |
| `API_URL` | `https://your-app.onrender.com` | ✅ |
| `ENVIRONMENT` | `production` | ✅ |
| `CORS_ORIGINS` | `https://yourdomain.com` | Optional |
| `LOG_LEVEL` | `INFO` | Optional |

## ✅ Render Dashboard Steps

### Step 1: Configure Service
1. Go to https://dashboard.render.com
2. Select your web service
3. Go to **Settings** tab
4. Verify:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Python Version: `3.11`

### Step 2: Set Environment Variables
1. Go to **Environment** tab
2. Click **Add Environment Variable**
3. Add ALL required variables from table above
4. Click **Save Changes**

### Step 3: Trigger Deploy
1. Go to **Manual Deploy**
2. Click **Clear build cache & deploy** (first time)
3. Or click **Deploy latest commit**
4. Wait 2-5 minutes

## ✅ Verify Deployment

### Check Logs
1. Go to **Logs** tab
2. Look for success messages:
   ```
   INFO:     Started server process
   INFO:     Application startup complete
   INFO:     Uvicorn running on http://0.0.0.0:10000
   ```

### Test Endpoints
```bash
# Health check
curl https://your-app.onrender.com/health

# API docs
curl https://your-app.onrender.com/docs

# OpenAPI spec
curl https://your-app.onrender.com/openapi.json
```

### Expected Response (health)
```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T..."
}
```

## ✅ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pydantic_settings'"
**Fix:**
1. Verify `requirements.txt` has `pydantic-settings>=2.0.0`
2. In Render: Manual Deploy → **Clear build cache & deploy**

### Error: "Configuration validation failed"
**Fix:**
1. Check all REQUIRED environment variables are set
2. Verify no typos in variable names
3. Check DATABASE_URL format: `postgresql://` or `postgresql+asyncpg://`

### Error: "Connection refused" or "Database error"
**Fix:**
1. Verify DATABASE_URL is correct
2. Check database is accessible from Render
3. Ensure async driver: `postgresql+asyncpg://`

### Error: App crashes after successful build
**Fix:**
1. Check Render logs for specific error
2. Verify all environment variables exist
3. Test config import: Add this to main.py temporarily:
   ```python
   print(f"Config loaded: {settings.ENVIRONMENT}")
   ```

### Error: CORS issues from frontend
**Fix:**
1. Set `CORS_ORIGINS` to your frontend URL
2. Format: `https://yourdomain.com,https://www.yourdomain.com`
3. Or use `*` for testing (not recommended for production)

## ✅ Post-Deployment

### Monitor
- Check logs regularly for errors
- Set up alerts in Render dashboard
- Monitor response times

### Test All Endpoints
```bash
# List all routes
curl https://your-app.onrender.com/openapi.json | jq '.paths | keys'

# Test registration
curl -X POST https://your-app.onrender.com/api/register \
  -H "Content-Type: application/json" \
  -d '{"team_name": "Test Team", ...}'
```

### Database Migrations
```bash
# If using Alembic
alembic upgrade head
```

## ✅ Success Checklist

- [ ] `pydantic-settings>=2.0.0` in requirements.txt
- [ ] `config.py` uses `from pydantic_settings import BaseSettings`
- [ ] All required environment variables set in Render
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Deployment successful (no errors in logs)
- [ ] Health endpoint returns 200 OK
- [ ] API docs accessible at `/docs`
- [ ] Can connect to database
- [ ] Frontend can call backend (CORS working)

---

**Status**: Ready for production deployment
**Last Updated**: November 18, 2025
