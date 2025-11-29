# ICCT26 Cricket Tournament Backend

**Status:** ✅ Production Ready | **Version:** 1.0.1 | **Updated:** November 29, 2025

A complete enterprise-grade FastAPI backend for cricket tournament management featuring team registration, player management, match scheduling with runs/wickets separation, file uploads, and production-hardening.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Overview](#project-overview)
3. [Core Features](#core-features)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Installation](#installation)
7. [Configuration](#configuration)
8. [Running the Application](#running-the-application)
9. [API Endpoints](#api-endpoints)
10. [Match Management System](#match-management-system)
11. [Database Schema](#database-schema)
12. [Deployment](#deployment)
13. [Testing](#testing)
14. [Security](#security)
15. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 5-Minute Setup

```bash
# Clone repository
git clone https://github.com/sanjaynesan-05/ICCT26-BACKEND.git
cd ICCT26-BACKEND

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run application
python main.py
```

Access at http://localhost:8000/docs (Swagger UI)

---

## Project Overview

### What This Backend Does

The ICCT26 Backend provides a complete tournament management system:

- **Team Registration** - Multi-step form handling with file uploads
- **Player Management** - Dynamic player extraction and validation
- **Match Scheduling** - 4-stage workflow with runs/wickets separation
- **File Storage** - Cloudinary integration for documents, photos, and videos
- **Gallery Management** - Tournament image gallery with downloads
- **Admin Functions** - Team/player/match management
- **Production Hardening** - Race-safe IDs, retry logic, structured logging

### Technology Stack

```
FastAPI 0.104+           (Async Python web framework)
PostgreSQL + Neon        (Serverless database)
SQLAlchemy 2.0+          (Async ORM)
Pydantic 2.5+            (Data validation)
Cloudinary               (File storage & CDN)
Uvicorn/Gunicorn         (ASGI server)
```

---

## Core Features

### 1. Race-Safe Team ID Generation

Sequential team IDs (ICCT-001, ICCT-002, etc.) with zero race conditions:

- Database-backed counter with `SELECT FOR UPDATE` row locking
- Atomic increment in nested transactions
- Handles 100+ concurrent requests safely
- 3 retries with exponential backoff

**File:** `app/utils/race_safe_team_id.py`

### 2. Dynamic Player Extraction

Frontend sends `player_0_name`, `player_0_role`, `player_0_aadhar_file`, `player_0_subscription_file`, `player_1_name`, etc.

Backend automatically:
- Detects all players dynamically
- Validates name (2+ chars) and role (Batsman/Bowler/All-Rounder/Wicket-Keeper)
- Uploads files to Cloudinary
- Creates Player records with URLs
- Links players to team

**File:** `app/routes/registration_production.py`

### 3. Runs & Wickets Separation

**New Schema (November 2025):**
- `team1_first_innings_runs` (Integer: 0-999)
- `team1_first_innings_wickets` (Integer: 0-10)
- `team2_first_innings_runs` (Integer: 0-999)
- `team2_first_innings_wickets` (Integer: 0-10)

**Display Format:** `165/8` (runs/wickets)

### 4. 4-Stage Match Workflow

```
Stage 1: CREATE        → POST /api/schedule/matches
         ↓
Stage 2: START         → PUT /api/schedule/matches/{id}/start (toss info)
         ↓
Stage 3: RECORD INNINGS → PUT /api/schedule/matches/{id}/first-innings-score
                        → PUT /api/schedule/matches/{id}/second-innings-score
         ↓
Stage 4: FINISH        → PUT /api/schedule/matches/{id}/finish (result)
```

### 5. Input Validation

| Field | Rules |
|-------|-------|
| Team Name | 3-80 chars, letters/spaces/hyphens |
| Names | 3-50 chars, letters/spaces/apostrophes |
| Phone | 10 digits, numeric |
| Email | RFC 5322 compliant |
| Player Role | Batsman/Bowler/All-Rounder/Wicket-Keeper |
| Files | Max 5MB, PNG/JPEG/PDF |

### 6. Duplicate Protection

- Database unique constraint: `(team_name, captain_phone)`
- Idempotency keys (10-minute cache)
- Returns 409 Conflict with original response on duplicate

**File:** `app/utils/idempotency.py`

### 7. File Upload with Retry Logic

Cloudinary uploads with 3 retries + exponential backoff:

```
Attempt 1: Immediate
Attempt 2: +0.5s delay
Attempt 3: +1.0s delay
Attempt 4: +2.0s delay
```

**File Structure:**
```
ICCT26/
├── pastor_letters/{team_id}/
├── receipts/{team_id}/
├── group_photos/{team_id}/
└── players/{team_id}/player_0/aadhar/, subscription/
```

### 8. Structured Logging

JSON-formatted logs with request tracking:

```json
{
  "timestamp": "2025-11-19T10:30:45Z",
  "request_id": "req_abc123xyz",
  "event": "registration_started",
  "team_name": "Warriors",
  "duration_ms": 1247
}
```

**Events:** registration_started, validation_error, file_upload, db_operation, exception

### 9. Unified Error Responses

Consistent error format across all endpoints:

```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Captain phone must be exactly 10 digits",
  "details": {
    "field": "captain_phone",
    "value": "123"
  }
}
```

### 10. Production Hardening

- Circuit breaker pattern for external services
- Database retry logic with exponential backoff
- Connection pooling (20 connections + 10 overflow)
- Race condition prevention
- Request/response logging middleware
- Global exception handling

---

## Project Structure

```
ICCT26 BACKEND/
├── app/                           (Production code)
│   ├── __init__.py
│   ├── config.py                 (Configuration)
│   ├── db_utils.py               (Database utilities)
│   ├── schemas.py                (Pydantic schemas)
│   ├── schemas_multipart.py      (Multipart schemas)
│   ├── schemas_team.py           (Team schemas)
│   ├── services.py               (Business logic)
│   │
│   ├── routes/                   (API endpoints)
│   │   ├── __init__.py
│   │   ├── registration_production.py  (Team registration)
│   │   ├── team.py               (Team management)
│   │   ├── admin.py              (Admin functions)
│   │   └── health.py             (Health checks)
│   │
│   ├── middleware/               (Request processing)
│   │   ├── logging_middleware.py
│   │   └── production_middleware.py
│   │
│   └── utils/                    (Utility functions)
│       ├── circuit_breaker.py
│       ├── cloudinary_reliable.py
│       ├── cloudinary_upload.py
│       ├── database_hardening.py
│       ├── db_retry.py
│       ├── email_reliable.py
│       ├── error_handlers.py
│       ├── error_responses.py
│       ├── file_utils.py
│       ├── file_validation.py
│       ├── global_exception_handler.py
│       ├── idempotency.py
│       ├── race_safe_team_id.py
│       ├── structured_logging.py
│       ├── team_id_generator.py
│       └── validation.py
│
├── docs/                          (Comprehensive documentation)
│   ├── PROJECT_STRUCTURE.md
│   ├── MATCH_SCHEDULE_API.md
│   ├── FRONTEND_QUICK_START.md
│   ├── CLEANUP_SUMMARY.md
│   ├── api-reference/
│   ├── deployment/
│   ├── frontend/
│   ├── guides/
│   ├── security/
│   └── setup/
│
├── scripts/                       (Database setup)
│   ├── setup_database.py
│   ├── setup_postgres.bat/.sh
│   ├── create_matches_table.py
│   ├── migrate_match_details.py
│   └── README.md
│
├── tests/                         (Unit & integration tests)
│   ├── conftest.py
│   ├── test_admin_api.py
│   ├── test_admin_endpoints.py
│   ├── test_db.py
│   ├── test_endpoints.py
│   ├── test_idempotency.py
│   ├── test_race_safe_id.py
│   ├── test_registration_integration.py
│   ├── test_validation.py
│   └── __init__.py
│
├── testing/                       (Test utilities)
├── logs/                          (Application logs)
├── venv/                          (Virtual environment)
│
├── main.py                        (FastAPI entry point)
├── models.py                      (SQLAlchemy models)
├── database.py                    (DB connection)
├── config.py                      (Configuration)
├── cloudinary_config.py           (Cloudinary setup)
├── requirements.txt               (Dependencies)
├── pyproject.toml                 (Project metadata)
├── README.md                      (This file)
├── run_server.bat                 (Windows startup)
├── run_test.bat                   (Windows tests)
├── .env                           (Credentials - not in git)
├── .env.example                   (Config template)
└── .gitignore                     (Git exclusions)
```

---

## Installation

### Prerequisites

- Python 3.13+ (tested with 3.13.9)
- PostgreSQL 12+ or Neon account
- Cloudinary account
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/sanjaynesan-05/ICCT26-BACKEND.git
cd ICCT26-BACKEND
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Setup Database

```bash
python scripts/setup_database.py
```

### Step 5: Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### Step 6: Run Application

```bash
python main.py
# Server runs on http://localhost:8000
```

---

## Configuration

### Environment Variables (.env)

```env
# DATABASE
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/icct26?ssl=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_RECYCLE=3600

# CLOUDINARY
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-secret

# APP
APP_TITLE=ICCT26 Backend
APP_VERSION=1.0.1
ENVIRONMENT=production
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com

# SECURITY
SECRET_KEY=generate-random-string-here
JWT_SECRET_KEY=generate-random-jwt-key-here
```

### Database Setup Options

**Option 1: Neon (Recommended)**
1. Sign up at neon.tech
2. Create project
3. Copy connection string
4. Replace `postgresql://` with `postgresql+asyncpg://`
5. Add `?ssl=require` at the end

**Option 2: Local PostgreSQL**
```bash
# Create database
createdb icct26

# Update .env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/icct26
```

---

## Running the Application

### Development Mode

```bash
uvicorn main:app --reload --port 8000
```

Access:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

### Production Mode

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

---

## API Endpoints

### Team Registration

**Endpoint:**
```
POST /api/register/team
```

**Request:** multipart/form-data

**Form Fields:**

Team & Officials:
- `team_name` (required, 3-80 chars)
- `church_name` (required)
- `captain_name`, `captain_phone`, `captain_email`, `captain_whatsapp` (required)
- `vice_name`, `vice_phone`, `vice_email`, `vice_whatsapp` (required)

Files:
- `pastor_letter` (required, max 5MB)
- `payment_receipt` (optional)
- `group_photo` (optional)

Players (dynamic):
- `player_0_name`, `player_0_role`, `player_0_aadhar_file`, `player_0_subscription_file`
- `player_1_name`, `player_1_role`, `player_1_aadhar_file`, `player_1_subscription_file`
- ... (any number of players)

**Success Response (201):**
```json
{
  "success": true,
  "team_id": "ICCT-005",
  "team_name": "Chennai Warriors",
  "message": "Team registered successfully",
  "player_count": 11
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Player role must be one of: Batsman, Bowler, All-Rounder, Wicket-Keeper",
  "details": {
    "field": "player_0_role",
    "value": "InvalidRole"
  }
}
```

### Match Management Endpoints

**Create Match:**
```
POST /api/schedule/matches
Content-Type: application/json

{
  "round": "Round 1",
  "round_number": 1,
  "match_number": 1,
  "team1": "Team A",
  "team2": "Team B",
  "scheduled_start_time": "2025-11-28T10:00:00"
}
```

**Start Match:**
```
PUT /api/schedule/matches/{id}/start

{
  "toss_winner": "Team A",
  "toss_choice": "bat",
  "actual_start_time": "2025-11-28T10:15:00"
}
```

**Record First Innings:**
```
PUT /api/schedule/matches/{id}/first-innings-score

{
  "batting_team": "Team A",
  "runs": 165,
  "wickets": 8
}
```

**Record Second Innings:**
```
PUT /api/schedule/matches/{id}/second-innings-score

{
  "batting_team": "Team B",
  "runs": 152,
  "wickets": 5
}
```

**Finish Match:**
```
PUT /api/schedule/matches/{id}/finish

{
  "winner": "Team A",
  "margin": 13,
  "margin_type": "runs",
  "match_end_time": "2025-11-28T13:45:00"
}
```

**Get All Matches:**
```
GET /api/schedule/matches

Response:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "team1": "Team A",
      "team2": "Team B",
      "status": "done",
      "team1_first_innings_runs": 165,
      "team1_first_innings_wickets": 8,
      "team2_first_innings_runs": 152,
      "team2_first_innings_wickets": 5,
      "result": {
        "winner": "Team A",
        "margin": 13,
        "marginType": "runs",
        "wonByBattingFirst": true
      }
    }
  ]
}
```

### Team Management

```
GET /api/teams                           # List all teams
GET /api/teams/{team_id}                # Get team details
POST /api/teams/{team_id}/players       # Add player to team
DELETE /api/teams/{team_id}/players/{player_id}  # Remove player
```

### Admin Functions

```
GET /api/admin/teams                    # All teams
GET /api/admin/teams/{team_id}          # Team with players
GET /api/admin/players                  # All players
GET /api/health                         # Health check
```

### Gallery Management

```
GET /api/gallery/ICCT26/Gallery/images  # Get gallery images
POST /api/gallery/download/single       # Download single image
POST /api/gallery/download/bulk         # Download multiple images
GET /api/gallery/health                 # Gallery health check
```

---

## Match Management System

### Match Statuses

- `scheduled` - Match created, not started
- `live` - Match started, innings in progress
- `done` - Match completed with result

### Match Fields

```
id, round, round_number, match_number
team1, team2
toss_winner, toss_choice
scheduled_start_time, actual_start_time, match_end_time
team1_first_innings_runs, team1_first_innings_wickets
team2_first_innings_runs, team2_first_innings_wickets
match_score_url
result: {winner, margin, margin_type, won_by_batting_first}
created_at, updated_at
```

### Match Response Format

```json
{
  "id": 45,
  "round": "Round 1",
  "match_number": 1,
  "team1": "Team A",
  "team2": "Team B",
  "status": "done",
  "toss_winner": "Team A",
  "toss_choice": "bat",
  "team1_first_innings_runs": 165,
  "team1_first_innings_wickets": 8,
  "team2_first_innings_runs": 152,
  "team2_first_innings_wickets": 5,
  "result": {
    "winner": "Team A",
    "margin": 13,
    "marginType": "runs",
    "wonByBattingFirst": true
  },
  "created_at": "2025-11-28T10:00:00",
  "updated_at": "2025-11-28T13:45:00"
}
```

---

## Database Schema

### Tables

**teams**
- id, team_id (unique), team_name, church_name
- captain: name, phone, email, whatsapp
- vice_captain: name, phone, email, whatsapp
- pastor_letter, payment_receipt, group_photo (Cloudinary URLs)
- Constraint: UNIQUE(team_name, captain_phone)

**players**
- id, player_id (unique), team_id (FK)
- name, role
- aadhar_file, subscription_file (Cloudinary URLs)

**matches**
- id, round, round_number, match_number
- team1, team2, status
- toss_winner, toss_choice
- scheduled_start_time, actual_start_time, match_end_time
- team1_first_innings_runs, team1_first_innings_wickets
- team2_first_innings_runs, team2_first_innings_wickets
- match_score_url
- winner, margin, margin_type, won_by_batting_first

**team_sequence** (race-safe ID generation)
- id (always 1), last_number, updated_at

**idempotency_keys** (duplicate prevention)
- id, key (unique), response_data, expires_at

### Indices

```sql
CREATE INDEX idx_team_id ON teams(team_id);
CREATE INDEX idx_player_team_id ON players(team_id);
CREATE INDEX idx_match_team ON matches(team1, team2);
CREATE INDEX idx_idempotency_key ON idempotency_keys(key);
CREATE INDEX idx_idempotency_expires ON idempotency_keys(expires_at);
```

---

## Deployment

### Render (Recommended)

**1. Prepare Repository**
```bash
git push origin main
```

**2. Create Web Service**
- Log in to render.com
- New → Web Service
- Connect ICCT26-BACKEND repository
- Build: `pip install -r requirements.txt`
- Start: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

**3. Add Environment Variables**
```
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?ssl=require
CLOUDINARY_CLOUD_NAME=your-name
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
SECRET_KEY=random-secret
CORS_ORIGINS=https://your-frontend.com
ENVIRONMENT=production
```

**4. Create Database (PostgreSQL on Render)**
- New → PostgreSQL
- Copy connection string
- Update DATABASE_URL

**5. Deploy**
- Auto-deploys on git push
- Check status on Render dashboard

### Heroku Alternative

```bash
heroku create icct26-backend
heroku addons:create heroku-postgresql:standard-0
git push heroku main
heroku config:set CLOUDINARY_CLOUD_NAME=...
heroku logs --tail
```

### Manual Deployment

```bash
# On your server
git clone repo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.production

# Configure .env.production with production values

# Run with systemd/supervisor
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```

---

## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_registration_integration.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

- `test_race_safe_id.py` - ID generation tests
- `test_validation.py` - Input validation
- `test_idempotency.py` - Duplicate prevention
- `test_registration_integration.py` - End-to-end workflows
- `test_endpoints.py` - API endpoint tests
- `test_admin_api.py` - Admin functionality

### Manual Testing

**Using cURL:**
```bash
curl -X POST http://localhost:8000/api/schedule/matches \
  -H "Content-Type: application/json" \
  -d '{
    "team1": "Team A",
    "team2": "Team B",
    "round": "Round 1",
    "match_number": 1
  }'
```

**Using Swagger UI:**
1. Visit http://localhost:8000/docs
2. Click endpoint
3. Click "Try it out"
4. Execute

---

## Security

### Features Implemented

- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)
- CORS protection
- File security (MIME validation, size limits)
- Rate limiting (via Render/reverse proxy)
- HTTPS enforced (production)
- Environment variables for secrets
- No hardcoded credentials
- Connection pooling
- Structured logging

### Security Checklist

- [x] .env.local in .gitignore
- [x] Strong SECRET_KEY (random)
- [x] Database SSL enabled
- [x] CORS origins restricted
- [x] File upload validation
- [x] Input validation
- [x] Error sanitization
- [x] Logging configured

### Best Practices

1. **Environment Variables**
   ```bash
   # Never commit .env
   echo ".env*" >> .gitignore
   echo "!.env.example" >> .gitignore
   ```

2. **Database Security**
   ```env
   # Use SSL
   DATABASE_URL=...?ssl=require
   # Use connection pooling
   DATABASE_POOL_SIZE=20
   ```

3. **File Upload Security**
   - Max 5MB
   - PNG/JPEG/PDF only
   - MIME validation
   - Sanitized filenames

4. **CORS Configuration**
   ```env
   # Production
   CORS_ORIGINS=https://your-frontend.com
   # Development
   CORS_ORIGINS=http://localhost:3000
   ```

---

## Troubleshooting

### Database Connection Failed

```bash
# Check connection string
# Correct: postgresql+asyncpg://user:pass@host:5432/db?ssl=require
# Wrong: postgresql://user:pass@host:5432/db

# Test connection
python -c "import asyncpg; print('OK')"

# For Neon: Check SSL
DATABASE_URL=...?ssl=require
```

### Cloudinary Upload Failed

```bash
# Verify credentials
CLOUDINARY_CLOUD_NAME=your-name
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret

# Check logs
tail -f logs/app.log
```

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

### CORS Error

```env
# Update CORS_ORIGINS
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com

# Restart server
```

### Module Not Found

```bash
# Check virtual environment is activated
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

---

## API Reference Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/register/team | Register team |
| GET | /api/schedule/matches | List matches |
| POST | /api/schedule/matches | Create match |
| GET | /api/schedule/matches/{id} | Get match |
| PUT | /api/schedule/matches/{id}/start | Start match |
| PUT | /api/schedule/matches/{id}/first-innings-score | Record 1st innings |
| PUT | /api/schedule/matches/{id}/second-innings-score | Record 2nd innings |
| PUT | /api/schedule/matches/{id}/finish | Finish match |
| GET | /api/teams | List teams |
| GET | /api/admin/teams | Admin teams list |
| GET | /api/gallery/ICCT26/Gallery/images | Get gallery |
| GET | /health | Health check |

---

## Performance Metrics

- **Response Time:** < 500ms (typical)
- **Database Pool:** 20 connections
- **Max Overflow:** 10 connections
- **Concurrent Users:** 100+ (tested)
- **Uptime:** 99.9% (Render SLA)

---

## Monitoring & Logging

### Log Levels

- DEBUG - Detailed diagnostic information
- INFO - Confirmation that things working as expected
- WARNING - Something unexpected or problematic
- ERROR - Serious problem, something failed
- CRITICAL - Very serious, program itself failing

### Log Files

- Console: Real-time output
- File: `logs/app.log` (if enabled)
- Render: Dashboard → Logs tab

### Monitored Events

- `registration_started` - Team registration begins
- `validation_error` - Input validation fails
- `file_upload` - Cloudinary upload (success/failure)
- `db_operation` - Database operations
- `exception` - Unexpected errors

---

## Environment Comparison

| Item | Development | Production |
|------|-------------|------------|
| Host | localhost:8000 | api.icct26.com |
| Workers | 1 | 4 |
| Log Level | DEBUG | INFO |
| Database | Local/Neon | Neon |
| CORS | localhost:3000 | your-frontend.com |
| Reload | Yes | No |

---

## Dependencies

**Core:**
- fastapi 0.104+
- uvicorn 0.24+
- sqlalchemy 2.0+
- pydantic 2.5+
- asyncpg 0.29+

**Storage:**
- cloudinary 1.35+

**Utilities:**
- python-multipart 0.0.6+
- aiofiles 23.2+

**Testing:**
- pytest 7.4+
- pytest-asyncio 0.21+
- httpx 0.25+

See `requirements.txt` for complete list.

---

## Versioning

**Current Version:** 1.0.1

**Version History:**
- 1.0.1 (Nov 29, 2025) - Cleanup, organization, frontend integration docs
- 1.0.0 (Nov 28, 2025) - Initial release, all features complete

---

## Documentation

Complete documentation available in `docs/` folder:
- `PROJECT_STRUCTURE.md` - Architecture overview
- `MATCH_SCHEDULE_API.md` - Match API details
- `FRONTEND_QUICK_START.md` - Frontend integration guide
- `deployment/` - Deployment guides
- `api-reference/` - Complete API reference
- `security/` - Security documentation

---

## Support

**Repository:** https://github.com/sanjaynesan-05/ICCT26-BACKEND

**Issues:** Open GitHub issue

**Contact:** ICCT26 Development Team

---

## License

© 2025 ICCT26 Cricket Tournament. Proprietary and confidential.

---

**Status:** ✅ Production Ready | **Last Updated:** November 29, 2025 | **Version:** 1.0.1
