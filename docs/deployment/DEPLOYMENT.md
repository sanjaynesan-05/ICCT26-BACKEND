# 🚀 Deployment Guide

Complete guide for deploying the ICCT26 backend to production.

## Database Setup (Neon PostgreSQL)

### Prerequisites
- Neon account (free tier available at neon.tech)
- PostgreSQL knowledge
- Connection string format

### Steps

1. **Create Neon project:**
   - Go to [neon.tech/console](https://neon.tech/console)
   - Click "New Project"
   - Select "PostgreSQL"
   - Note your connection string

2. **Get connection details:**
   ```
   Connection String:
   postgresql://user:password@ep-xxxxxxxx-pooler.us-east-1.aws.neon.tech/dbname
   ```

3. **Initialize database:**
   ```bash
   python migrate_to_neon.py
   ```
   
   This will:
   - Create `teams` table (16 columns)
   - Create `players` table (12 columns)
   - Set up proper indexes
   - Verify connection

4. **Connection settings for Neon:**
   - **SSL Mode:** `require` (mandatory)
   - **Pool Size:** 5 (Neon limitation)
   - **Max Overflow:** 0 (Neon limitation)
   - **Pool Recycle:** 300 seconds (connection refresh)

## Backend Deployment Options

### Option 1: Render.com (Recommended)

**Pros:** Simple, free tier, auto-deploy from git

**Steps:**

1. **Create account:** [render.com](https://render.com)

2. **Connect GitHub:**
   - Click "New +"
   - Select "Web Service"
   - Select your repository
   - Authorize access

3. **Configure service:**
   ```
   Name: icct26-cricket-api
   Runtime: Python 3
   Region: Singapore (or nearest)
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Set environment variables:**
   - Go to "Environment"
   - Add each from .env.example
   - Use real values (not placeholders)

5. **Deploy:**
   - Click "Create Web Service"
   - Render auto-deploys on git push

**Monitoring:**
```bash
# View logs
tail -f render.log

# Restart if needed
# Use dashboard
```

### Option 2: Railway.app

**Pros:** Fast, good documentation, GitHub integration

**Steps:**

1. **Create project:** [railway.app](https://railway.app)

2. **Connect repository:**
   - Click "New"
   - Select "GitHub Repo"
   - Choose your repository

3. **Add PostgreSQL:**
   - Click "Add Service"
   - Select "PostgreSQL"
   - Configure

4. **Configure backend:**
   - Add environment variables
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port 8000`

5. **Deploy:**
   - Click "Deploy"
   - View logs in dashboard

### Option 3: Docker + Any Host

**Works with:** AWS, DigitalOcean, Azure, Heroku, custom VPS

**Dockerfile:**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SMTP_USERNAME: ${SMTP_USERNAME}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
    restart: unless-stopped
```

**Deploy:**
```bash
docker build -t icct26-api .
docker run -p 8000:8000 --env-file .env.local icct26-api
```

## Pre-deployment Checklist

### Code Quality
- [ ] No hardcoded credentials
- [ ] All imports resolved
- [ ] No unused imports
- [ ] Proper error handling
- [ ] All endpoints tested

### Security
- [ ] SSL/TLS enabled
- [ ] Credentials in environment
- [ ] .env.local gitignored
- [ ] .gitignore updated
- [ ] No secrets in logs
- [ ] CORS configured properly

### Configuration
- [ ] DATABASE_URL set correctly
- [ ] SMTP credentials configured
- [ ] API keys set
- [ ] Logging level appropriate
- [ ] Timeouts configured

### Database
- [ ] Neon project created
- [ ] Database initialized (migrate_to_neon.py run)
- [ ] Tables verified
- [ ] Backup enabled
- [ ] Connection tested

### Testing
- [ ] All 5 endpoints return 200
- [ ] Root endpoint responsive
- [ ] Health check working
- [ ] Database queries working
- [ ] Error handling tested

### Documentation
- [ ] README updated
- [ ] API docs current
- [ ] Setup guide available
- [ ] Security guide reviewed
- [ ] Deployment steps clear

## Production Environment Variables

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@neon.tech/db?ssl=require
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
SPREADSHEET_ID=your_spreadsheet_id

# Optional
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-domain.com
```

## Post-deployment Verification

1. **Check service health:**
   ```bash
   curl https://your-api.com/health
   # Should return: {"status":"healthy","service":"ICCT26 Registration API"}
   ```

2. **Verify database:**
   ```bash
   curl https://your-api.com/status
   # Should show: "database":"connected"
   ```

3. **Test API:**
   ```bash
   curl https://your-api.com/
   # Should return API info
   ```

4. **Monitor logs:**
   - Check platform logs for errors
   - Monitor response times
   - Watch error rates

## Monitoring & Maintenance

### Daily Tasks
- Check application logs
- Monitor error rates
- Verify database connectivity

### Weekly Tasks
- Review usage statistics
- Check security alerts
- Backup verification

### Monthly Tasks
- Rotate credentials
- Update dependencies
- Review performance metrics
- Security audit

## Rollback Plan

If deployment fails:

1. **Quick rollback:**
   ```bash
   git revert <commit-hash>
   git push
   # Platform auto-redeploys
   ```

2. **Emergency stop:**
   - Disable the service in dashboard
   - Route traffic to previous version
   - Investigate issue

3. **Restore database:**
   - Neon has automatic backups
   - Contact support for specific restore

## Common Issues & Solutions

### Connection Timeout
- **Cause:** Neon connection string wrong
- **Fix:** Verify in Neon dashboard, update DATABASE_URL

### SSL Error
- **Cause:** SSL mode not set to `require`
- **Fix:** Check DATABASE_URL has `ssl=require` or `sslmode=require`

### 502 Bad Gateway
- **Cause:** Service crashed
- **Fix:** Check logs, restart service, check environment variables

### High Response Times
- **Cause:** Connection pool exhausted
- **Fix:** Increase pool size (if possible), optimize queries

### Memory Issues
- **Cause:** Memory leaks
- **Fix:** Restart service, check logs for issues

## Documentation

- See `docs/guides/SECURITY.md` for credential management
- See `API_DOCS.md` for endpoint documentation
- See `README.md` for project overview

## Support

For deployment help:
1. Check this guide
2. Review logs
3. Test locally first
4. Contact platform support
5. Review GitHub issues

---

**Last Updated:** [Current Date]
**Maintained By:** Development Team
