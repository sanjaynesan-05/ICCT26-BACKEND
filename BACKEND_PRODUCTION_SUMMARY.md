# BACKEND_PRODUCTION_SUMMARY.md

## ICCT26 Backend - Production Deployment Summary

**Last Updated**: November 18, 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Production Hardening](#production-hardening)
3. [Deployment Checklist](#deployment-checklist)
4. [Environment Configuration](#environment-configuration)
5. [API Endpoints](#api-endpoints)
6. [Troubleshooting](#troubleshooting)
7. [Rollback Procedure](#rollback-procedure)

---

## System Architecture

### Core Components

```
┌─────────────────────────────────────────────┐
│         FastAPI Application                  │
│  ┌────────────────────────────────────────┐  │
│  │    Production Middleware Suite          │  │
│  │  - Request Timeout (60s)                │  │
│  │  - Body Size Limit (10MB)               │  │
│  │  - Rate Limiting (30 req/min/IP)        │  │
│  │  - GZIP Compression                     │  │
│  │  - CORS Management                      │  │
│  └────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────┐  │
│  │    Global Exception Handlers             │  │
│  │  - ValidationError                      │  │
│  │  - HTTPException                        │  │
│  │  - RuntimeError                         │  │
│  │  - Generic Exception                    │  │
│  └────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────┐  │
│  │    Registration Endpoint                │  │
│  │  - Input Validation                     │  │
│  │  - Duplicate Prevention (Idempotency)   │  │
│  │  - File Upload (Cloudinary + Retry)     │  │
│  │  - Email Notification (SMTP + Retry)    │  │
│  │  - Structured Logging                   │  │
│  └────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────┐  │
│  │    Supporting Utilities                 │  │
│  │  - Race-Safe ID Generation              │  │
│  │  - Circuit Breaker Pattern               │  │
│  │  - Database Health Checks                │  │
│  │  - Structured JSON Logging               │  │
│  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
        ↓              ↓              ↓
   PostgreSQL    Cloudinary      SMTP Server
```

### Technology Stack

- **Framework**: FastAPI with Uvicorn
- **Database**: PostgreSQL with SQLAlchemy (async)
- **File Storage**: Cloudinary
- **Email**: SMTP (configurable)
- **Logging**: JSON-structured logging to file
- **Auth**: API key validation
- **Monitoring**: Request duration tracking, error logging

---

## Production Hardening

### 1. Request Processing

| Feature | Implementation | Threshold |
|---------|-----------------|-----------|
| **Timeout** | Async timeout middleware | 60 seconds |
| **Body Size** | Body size validation | 10 MB max |
| **Rate Limit** | IP-based rate limiting | 30 req/min |
| **Compression** | GZIP/Deflate | Auto for >1KB |

### 2. Validation & Security

- **Input Validation**: Strict schema validation (Pydantic v2)
- **Duplicate Prevention**: Idempotency key tracking (10-min TTL)
- **File Validation**: MIME type + size checking
- **Race Condition Prevention**: SELECT FOR UPDATE locking
- **Error Sanitization**: No internal details exposed

### 3. Reliability

- **Database Connection Pooling**: 20 pool size, 10 overflow
- **Transient Error Retry**: Exponential backoff (up to 3 retries)
- **Circuit Breaker**: Failure rate monitoring, graceful degradation
- **Health Checks**: Startup DB connectivity test

### 4. Observability

- **Structured Logging**: JSON format to `logs/app.log`
- **Request Tracking**: Unique request IDs for correlation
- **Duration Metrics**: All requests timed
- **Error Tracking**: Full exception details logged

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (unit, integration, type check)
- [ ] Lint check passed (no warnings)
- [ ] Database migrations current
- [ ] Environment variables configured
- [ ] SSL/TLS certificates valid
- [ ] Backup of current database created
- [ ] Rollback plan documented

### Deployment Steps

```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run database migrations
alembic upgrade head

# 4. Run tests
pytest tests/ -v

# 5. Start application
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

# 6. Verify health
curl http://localhost:8000/health
```

### Post-Deployment

- [ ] Health endpoint returns 200
- [ ] Logs created successfully
- [ ] Sample registration works end-to-end
- [ ] Monitor logs for errors
- [ ] Test rate limiting (send 31 requests/min from IP)
- [ ] Test timeout (make slow request)
- [ ] Verify email notifications sent
- [ ] Monitor database connection pool

---

## Environment Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/icct26
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_RECYCLE=3600

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Email/SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@icct26.com

# API Configuration
API_URL=https://api.icct26.com
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security
SECRET_KEY=your-secret-key-min-32-chars
MAX_REQUEST_SIZE=10485760
REQUEST_TIMEOUT=60
RATE_LIMIT_REQUESTS=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_TO_FILE=true

# CORS
CORS_ORIGINS=https://icct26.com,https://www.icct26.com

# Environment
ENVIRONMENT=production
DEBUG=false
```

### Configuration Loading

```python
from config import settings

# All variables validated at startup
print(settings.DATABASE_URL)
print(settings.CORS_ORIGINS)
```

---

## API Endpoints

### Registration

```http
POST /api/registration
Content-Type: multipart/form-data
X-Idempotency-Key: unique-key-per-request

Form Data:
- team_name: string (3-80 chars)
- church_name: string (3-80 chars)
- captain_name: string (3-50 chars)
- captain_phone: string (10 digits)
- captain_email: string (valid email)
- captain_whatsapp: string (10 digits)
- coach_name: string (3-50 chars)
- logo: file (PNG/JPEG, <5MB)
- players: JSON array of {name, role, phone}
```

### Response Format

**Success (200)**:
```json
{
  "success": true,
  "team_id": "ICCT-001",
  "message": "Team registered successfully"
}
```

**Error (4xx/5xx)**:
```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Input validation failed",
  "details": {
    "field_errors": {
      "captain_email": "Invalid email format"
    }
  }
}
```

### Utility Endpoints

```
GET /health          # Health check
GET /status          # Server status
GET /admin/teams     # List all teams (admin only)
GET /docs            # Swagger API docs
```

---

## Troubleshooting

### Issue: Database Connection Failed

**Symptoms**: Startup fails with "Database connection failed"

**Solution**:
1. Check `DATABASE_URL` is correct
2. Verify PostgreSQL server is running
3. Test connection: `psql -c "SELECT 1"`
4. Check firewall rules
5. Review logs for specific error

### Issue: High Failure Rate Warnings

**Symptoms**: Logs show "High failure rate for cloudinary_upload"

**Solution**:
1. Check Cloudinary API credentials
2. Check network connectivity
3. Verify file sizes don't exceed limits
4. Review Cloudinary console for API errors
5. Check rate limit: max 500 requests/min

### Issue: Rate Limit Rejections

**Symptoms**: "Too many requests" (429) errors

**Solution**:
1. Wait 1 minute before retrying
2. Implement exponential backoff on client
3. Verify single IP isn't making >30 req/min
4. Check for bot traffic
5. If legitimate traffic, increase `RATE_LIMIT_REQUESTS`

### Issue: Timeout Errors

**Symptoms**: "Request timeout exceeded" (408) errors

**Solution**:
1. Check database performance
2. Profile slow endpoints with logging
3. Verify Cloudinary/SMTP not timing out
4. Increase `REQUEST_TIMEOUT` if needed (config change)
5. Check server load and CPU/memory

### Issue: Email Not Sent

**Symptoms**: Registration succeeds but email not received

**Solution**:
1. Check SMTP credentials in logs
2. Verify firewall allows port 587 outbound
3. Check spam folder
4. Review logs for SMTP errors
5. Test manually: `python -c "import smtplib; s = smtplib.SMTP('...')"`

---

## Rollback Procedure

### Full Rollback (1-2 minutes)

```bash
# 1. Stop current application
pkill -f "uvicorn main:app"

# 2. Revert code to previous tag
git checkout v1.0.0  # Previous stable version

# 3. Reinstall dependencies
pip install -r requirements.txt

# 4. Restart application
uvicorn main:app --workers 4

# 5. Verify health
curl http://localhost:8000/health

# 6. Monitor logs for errors
tail -f logs/app.log
```

### Database Rollback

```bash
# If migrations caused issues
alembic downgrade -1  # Revert last migration
alembic upgrade head  # Reapply after fix
```

### Data Recovery

```bash
# If database corrupted
psql -d icct26 < backup.sql  # Restore from backup
```

---

## Monitoring

### Key Metrics to Monitor

1. **Request Metrics**
   - Average response time
   - p95/p99 latency
   - Error rate (4xx, 5xx)
   - Rate limit hits

2. **Database Metrics**
   - Connection pool usage
   - Query duration
   - Transaction rollbacks

3. **External Service Metrics**
   - Cloudinary upload success rate
   - Email delivery success rate
   - Circuit breaker state

4. **Application Metrics**
   - Memory usage
   - CPU usage
   - Log volume
   - Disk space

### Log Locations

```
logs/app.log  # Main application log (JSON format)
```

### Health Check

```bash
curl -X GET http://localhost:8000/health
# Response: {"status": "healthy"}
```

---

## Support & Escalation

**Technical Issues**: Check logs first, then reference troubleshooting

**Database Issues**: Contact DevOps team, provide error logs

**Cloudinary Issues**: Check API console, verify credentials

**Email Issues**: Check SMTP logs, verify credentials

---

**Document Version**: 1.0.0  
**Last Updated**: November 18, 2025  
**Maintained By**: Backend Team
