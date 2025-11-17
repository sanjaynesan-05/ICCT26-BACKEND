# DEPLOYMENT_CHECKLIST.md

## ICCT26 Backend - Deployment Checklist

**Version**: 1.0.0  
**Last Updated**: November 18, 2025  
**Estimated Time**: 30-45 minutes

---

## Pre-Deployment Validation

### Code Quality

- [ ] All unit tests passing: `pytest tests/ -v`
- [ ] All integration tests passing: `pytest tests/ -v --integration`
- [ ] Lint check passed: `pylint app/ --disable=R,C`
- [ ] Type check passed: `mypy app/`
- [ ] No security issues: `bandit -r app/`
- [ ] Code coverage >80%: `pytest --cov=app --cov-report=term`

### Configuration

- [ ] Environment variables documented in `.env.example`
- [ ] All required env vars present
- [ ] Production secrets not in code
- [ ] Database connection string valid
- [ ] Cloudinary credentials correct
- [ ] SMTP credentials correct
- [ ] CORS origins configured correctly
- [ ] API_URL matches deployment domain

### Database

- [ ] Database server is running and accessible
- [ ] PostgreSQL version compatible (12+)
- [ ] Database backup created: `pg_dump -U user icct26 > backup.sql`
- [ ] Migrations up to date: `alembic current`
- [ ] All migration scripts tested
- [ ] Rollback script prepared

### External Services

- [ ] Cloudinary account accessible
- [ ] Cloudinary API key valid: `curl https://api.cloudinary.com/v1_1/{cloud}/ping -u {key}:{secret}`
- [ ] SMTP server accessible: `telnet smtp.server.com 587`
- [ ] Email test sent successfully
- [ ] Rate limits confirmed with providers

### Infrastructure

- [ ] Server resources adequate (CPU, RAM, disk)
- [ ] Load balancer configured (if applicable)
- [ ] SSL/TLS certificates valid (not expired)
- [ ] Firewall rules allow API traffic (port 8000)
- [ ] Outbound firewall rules allow SMTP (port 587)
- [ ] Outbound firewall rules allow Cloudinary API
- [ ] Log directory exists and is writable: `mkdir -p logs && touch logs/app.log`
- [ ] Log rotation configured

### Documentation

- [ ] BACKEND_PRODUCTION_SUMMARY.md reviewed
- [ ] API_REFERENCE.md reviewed
- [ ] KNOWN_ERROR_CODES.md reviewed
- [ ] This checklist reviewed
- [ ] Rollback procedure documented
- [ ] On-call contact list updated

---

## Deployment Steps

### 1. Pre-Deployment Safety (5 min)

```bash
# Stop monitoring alerts (temporarily)
# Alert your team about deployment
# Set maintenance mode (if applicable)

# Create timestamped backup
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
pg_dump -U postgres icct26 > $BACKUP_FILE
echo "Backup created: $BACKUP_FILE"

# Verify backup
psql -U postgres < $BACKUP_FILE --dry-run
```

- [ ] Backup created and verified
- [ ] Team notified
- [ ] Maintenance mode active (if applicable)

### 2. Code Deployment (5 min)

```bash
# Pull latest code
cd /path/to/icct26-backend
git pull origin main
git log --oneline -1

# Verify code integrity
git verify-commit HEAD  # If using signed commits

# Install/update dependencies
pip install -r requirements.txt

# Verify dependencies installed
python -c "import fastapi; import sqlalchemy; print('OK')"
```

- [ ] Latest code pulled
- [ ] Dependencies updated
- [ ] Code verified
- [ ] No merge conflicts

### 3. Configuration Verification (2 min)

```bash
# Load and validate configuration
python -c "from config import settings; print(settings.ENVIRONMENT)"

# Test database connection
python -c "
from database import engine
import asyncio
async def test():
    from app.utils.database_hardening import DatabaseHealthCheck
    result = await DatabaseHealthCheck.check_connection(engine)
    print('Database OK' if result else 'Database FAILED')
asyncio.run(test())
"

# Create logs directory
mkdir -p logs
chmod 755 logs
```

- [ ] Configuration validated
- [ ] Database connection tested
- [ ] Log directory created

### 4. Database Migration (5-10 min)

```bash
# Check current migration status
alembic current

# Run migrations (if any)
alembic upgrade head

# Verify migration success
alembic current
```

- [ ] Migrations reviewed
- [ ] Migrations executed
- [ ] Database schema verified

### 5. Application Start (3 min)

```bash
# Option A: Direct Uvicorn (development only)
# uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option B: Gunicorn + Uvicorn (production recommended)
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info

# Option C: Systemd service (if configured)
systemctl restart icct26-backend
```

- [ ] Application process started
- [ ] Process listening on port 8000
- [ ] No startup errors in logs

### 6. Health Verification (5 min)

```bash
# Wait for application to fully start
sleep 5

# Health check
curl -X GET http://localhost:8000/health
# Expected: {"status": "healthy"}

# Status endpoint
curl -X GET http://localhost:8000/status
# Expected: {"status": "running", "database": "connected"}

# Check logs for errors
tail -50 logs/app.log | grep -i error

# Monitor metrics
watch -n 1 'curl -s http://localhost:8000/status | jq .'
```

- [ ] Health endpoint returns 200
- [ ] Status endpoint shows all services connected
- [ ] No errors in logs
- [ ] Response times <500ms

### 7. Smoke Tests (10 min)

```bash
# 1. Test rate limiting (expect 429 after 30 requests)
for i in {1..35}; do
  curl -s http://localhost:8000/api/registration \
    -H "X-API-Key: test-key" \
    -H "X-Idempotency-Key: test-$i" \
    -F "team_name=Test" \
    -w "\nStatus: %{http_code}\n"
done

# 2. Test timeout (send request expected to timeout)
curl --max-time 5 \
  -X POST http://localhost:8000/api/registration \
  -H "X-API-Key: test-key" \
  -F "team_name=Test" &
sleep 65 && kill $!

# 3. Test duplicate detection
IDEMPOTENCY_KEY=$(uuidgen)
curl -X POST http://localhost:8000/api/registration \
  -H "X-API-Key: test-key" \
  -H "X-Idempotency-Key: $IDEMPOTENCY_KEY" \
  -F "team_name=Test Team" \
  ...

# Retry immediately (should get 409)
curl -X POST http://localhost:8000/api/registration \
  -H "X-API-Key: test-key" \
  -H "X-Idempotency-Key: $IDEMPOTENCY_KEY" \
  -F "team_name=Different Team" \
  ...
```

- [ ] Rate limiting working (429 after 30 requests)
- [ ] Timeout handling working (408 on timeout)
- [ ] Duplicate detection working (409 on duplicate)
- [ ] Error responses formatted correctly

### 8. Integration Tests (5 min)

```bash
# Run full integration test suite
pytest tests/test_registration_integration.py -v

# Test with real Cloudinary (if configured)
pytest tests/ -v -k "cloudinary"

# Test email sending (if configured)
pytest tests/ -v -k "email"
```

- [ ] All integration tests passing
- [ ] File upload working
- [ ] Email notifications working

### 9. Monitoring & Alerting (3 min)

```bash
# Enable monitoring
# - Start metrics collection
# - Enable log aggregation
# - Set up error alerts
# - Configure PagerDuty/alerting (if applicable)

# Monitor logs in real-time
tail -f logs/app.log | jq .
```

- [ ] Monitoring enabled
- [ ] Alerting configured
- [ ] Log aggregation working

### 10. Post-Deployment Verification (5 min)

```bash
# Full end-to-end test
python tests/e2e_smoke_test.py

# Database query audit
psql -U postgres icct26 -c "SELECT COUNT(*) FROM teams;"

# Check disk usage
du -sh logs/
df -h /

# Memory/CPU check
ps aux | grep uvicorn
```

- [ ] E2E smoke test passed
- [ ] Database accessible and queryable
- [ ] Disk space adequate
- [ ] Application running stable

---

## Post-Deployment Tasks

### Monitoring (Continuous)

```bash
# Watch for errors
tail -f logs/app.log | grep -i error

# Monitor performance
watch -n 5 'ps aux | grep uvicorn'

# Check database connections
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

- [ ] Monitor logs for 15 minutes
- [ ] Check performance metrics stable
- [ ] Database connections healthy

### Communication

- [ ] Team notified of successful deployment
- [ ] Stakeholders notified of go-live
- [ ] Status page updated (if applicable)
- [ ] Maintenance mode disabled

### Documentation

- [ ] Deployment timestamp logged
- [ ] Deployed version documented
- [ ] Any deviations from plan noted
- [ ] Post-deployment observations recorded

---

## Rollback Procedures

### Quick Rollback (5 minutes)

```bash
# 1. Stop current application
pkill -f "uvicorn main:app"
# or
systemctl stop icct26-backend

# 2. Revert code to previous version
git checkout v1.0.0  # or previous tag
pip install -r requirements.txt

# 3. Downgrade database if migrations changed
alembic downgrade -1

# 4. Restart application
gunicorn main:app --workers 4 --bind 0.0.0.0:8000 &

# 5. Verify health
sleep 5
curl http://localhost:8000/health
```

- [ ] Application stopped
- [ ] Code reverted
- [ ] Database rolled back
- [ ] Application restarted
- [ ] Health verified

### Database Rollback (if needed)

```bash
# Restore from backup if database corrupted
psql -U postgres icct26 < backup_YYYYMMDD_HHMMSS.sql

# Verify restoration
psql -U postgres icct26 -c "SELECT COUNT(*) FROM teams;"
```

- [ ] Backup restored
- [ ] Data integrity verified

### Full Environment Rollback

```bash
# If deployment broke system
# Contact DevOps/Infrastructure team
# Use infrastructure-as-code to redeploy previous version
# Terraform: terraform apply -var="version=v1.0.0"
```

---

## Validation Checklist (Post-Deployment)

### Functionality

- [ ] Team registration endpoint working
- [ ] File uploads successful
- [ ] Email notifications sent
- [ ] Admin endpoints accessible
- [ ] API docs accessible at /docs

### Performance

- [ ] Response time <500ms (average)
- [ ] p99 latency <2000ms
- [ ] Error rate <0.1%
- [ ] Database query time <100ms (avg)

### Reliability

- [ ] No unhandled exceptions in logs
- [ ] Retries working for transient errors
- [ ] Circuit breaker protecting against cascading failures
- [ ] Health checks passing

### Security

- [ ] API key validation working
- [ ] Rate limiting enforced
- [ ] CORS policies working
- [ ] No debug information exposed
- [ ] SSL/TLS enabled

### Monitoring

- [ ] Logs being written to file
- [ ] Structured JSON logs readable
- [ ] Error alerts configured
- [ ] Performance metrics captured

---

## Contacts & Escalation

| Role | Name | Phone | Email |
|------|------|-------|-------|
| Deployment Lead | [Name] | [Phone] | [Email] |
| Backend Team | [Name] | [Phone] | [Email] |
| DevOps | [Name] | [Phone] | [Email] |
| Database Admin | [Name] | [Phone] | [Email] |
| On-Call | [Name] | [Phone] | [Email] |

---

## Sign-Off

| Role | Name | Date | Time | Status |
|------|------|------|------|--------|
| Deployer | _______ | _______ | _______ | [ ] |
| QA Lead | _______ | _______ | _______ | [ ] |
| Ops Lead | _______ | _______ | _______ | [ ] |

---

## Deployment Notes

```
Use this space to record any issues encountered or deviations from this plan:

_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

**Deployment Checklist Version**: 1.0.0  
**Last Updated**: November 18, 2025  
**Created By**: Backend Team
