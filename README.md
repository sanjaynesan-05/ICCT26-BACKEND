# ICCT26 Backend API

A modern, **production-hardened** FastAPI backend for managing teams, players, and administrative operations with comprehensive security features, reliability enhancements, and monitoring capabilities.

**Status:** ✅ Production Ready (Hardened) | **Python:** 3.8+ | **Framework:** FastAPI | **Database:** PostgreSQL

---

## 🔐 Production Security Features

This backend has been fully hardened for production use with:

✅ **Race-Safe Team IDs** - Database-backed sequential IDs with zero race conditions  
✅ **Strong Input Validation** - Regex-based validation for all inputs  
✅ **Duplicate Protection** - Database constraints + idempotency keys  
✅ **File Security** - 5MB limit, MIME type validation, sanitized filenames  
✅ **Retry Logic** - Exponential backoff for uploads (3x) and emails (2x)  
✅ **Structured Logging** - Request ID tracking, JSON logs for monitoring  
✅ **Unified Errors** - Consistent error codes and response format  

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Production Features](#production-features)
- [API Endpoints](#api-endpoints)
- [Security & Validation](#security--validation)
- [Error Codes](#error-codes)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Deployment](#deployment)
- [Documentation](#documentation)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Cloudinary account (for file uploads)
- SMTP credentials (for emails)
- pip (Python package manager)

### Installation (5 minutes)

```bash
# 1. Clone the repository
git clone <repository-url>
cd ICCT26_BACKEND

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
# Copy .env.example to .env and fill in your values
cp .env.example .env  # or copy .env.example .env on Windows

# 6. Set up database
# See Database Setup section below

# 7. Run the application
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

**Swagger Documentation:** `http://localhost:8000/docs`  
**ReDoc Documentation:** `http://localhost:8000/redoc`

---

## 📖 Project Overview

### What This Project Does

ICCT26 Backend is a comprehensive REST API that manages:

✅ **Teams Management** - Create, read, update, and manage teams  
✅ **Player Management** - Track players, their statistics, and assignments  
✅ **Admin Panel** - Comprehensive admin endpoints for system management  
✅ **Email Notifications** - Automated email system with template support  
✅ **Security** - Role-based access control, secure credential handling  

### Key Features

---

## 🔐 Production Features

### 1. Race-Safe Team ID Generation

Sequential team IDs (`ICCT-001`, `ICCT-002`, etc.) with **zero race conditions**:

- Database-backed counter with `SELECT FOR UPDATE` row locking
- Atomic increment operations in nested transactions
- Handles concurrent requests safely
- Max 3 retries on conflict with exponential backoff

**Implementation:** `app/utils/race_safe_team_id.py`

### 2. Strong Input Validation

Comprehensive validation layer for all inputs:

| Field | Rules |
|-------|-------|
| **Names** | 3-50 chars, letters/spaces/hyphens/apostrophes only |
| **Phone** | Exactly 10 digits, numeric |
| **Email** | RFC 5322 compliant regex |
| **Team Name** | 3-80 chars |
| **Files** | Max 5MB, MIME validation (PNG/JPEG/PDF only) |

**Implementation:** `app/utils/validation.py`

### 3. Duplicate Submission Protection

Two-layer defense against duplicates:

1. **Database Constraints**: `UNIQUE(team_name, captain_phone)`
2. **Idempotency Keys**: 10-minute TTL, cached responses

Usage: Send `Idempotency-Key: <unique-id>` header

**Implementation:** `app/utils/idempotency.py`

### 4. File Security

Multi-layer file validation:

- **Size Limit**: 5MB hard limit
- **MIME Detection**: Uses `python-magic` for true file type detection
- **Filename Sanitization**: Prevents path traversal attacks
- **Allowed Types**: PNG, JPEG, PDF only

**Implementation:** `app/utils/validation.py`

### 5. Retry Logic with Exponential Backoff

Never crash on transient failures:

**Cloudinary Uploads** (3 retries):
- Attempt 1: Immediate
- Attempt 2: +0.5s
- Attempt 3: +1.0s
- Attempt 4: +2.0s

**Email Sending** (2 retries):
- Attempt 1: Immediate
- Attempt 2: +1.0s
- Attempt 3: +2.0s

**Implementations:**
- `app/utils/cloudinary_reliable.py`
- `app/utils/email_reliable.py`

### 6. Structured Logging & Monitoring

JSON-formatted logs with request tracking:

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "request_id": "req_abc123",
  "event": "registration_started",
  "team_name": "Warriors",
  "client_ip": "192.168.1.1",
  "duration_ms": 1250
}
```

**Events Logged:**
- `registration_started`
- `validation_error`
- `file_upload` (success/failed)
- `db_operation` (insert/update)
- `email_sent` (success/failed)
- `exception` (with stack traces)

**Implementation:** `app/middleware/logging_middleware.py`

### 7. Unified Error Response Format

Consistent error structure across all endpoints:

```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Human-readable description",
  "details": {
    "field": "captain_phone",
    "value": "123"
  }
}
```

**Implementation:** `app/utils/error_responses.py`

---

## 🚨 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_FAILED` | 400 | Input validation error |
| `DUPLICATE_SUBMISSION` | 409 | Team/idempotency key already exists |
| `FILE_TOO_LARGE` | 400 | File exceeds 5MB limit |
| `INVALID_MIME_TYPE` | 400 | Invalid file type (not PNG/JPEG/PDF) |
| `DB_WRITE_FAILED` | 500 | Database operation failed |
| `CLOUDINARY_UPLOAD_FAILED` | 500 | File upload failed after retries |
| `EMAIL_FAILED` | 500 | Email send failed (non-fatal) |
| `TEAM_ID_GENERATION_FAILED` | 500 | Could not generate team ID |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error |

---

## 🏗️ Architecture

### Tech Stack

```
┌─────────────────────────────────────────┐
│     FastAPI Web Framework               │
│  (Async Python, Production-Hardened)    │
├─────────────────────────────────────────┤
│  Security & Validation Layer            │
│  (Race-safe IDs, Input Validation)      │
├─────────────────────────────────────────┤
│  Reliability Layer                      │
│  (Retry Logic, Idempotency)             │
├─────────────────────────────────────────┤
│  Monitoring & Logging                   │
│  (Structured Logs, Request Tracking)    │
├─────────────────────────────────────────┤
│     SQLAlchemy ORM                      │
│  (Async, Transaction-Safe)              │
├─────────────────────────────────────────┤
│     PostgreSQL Database                 │
│  (With Constraints & Indices)           │
├─────────────────────────────────────────┤
│  External Services                      │
│  (Cloudinary, SMTP)                     │
└─────────────────────────────────────────┘
```

### Project Structure

```
ICCT26_BACKEND/
├── main.py                          # Main FastAPI application
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project configuration
├── .env.example                     # Environment variables template
├── README.md                        # This file
│
├── app/
│   ├── routes/
│   │   └── registration_production.py  # Production-hardened endpoint
│   │
│   ├── utils/
│   │   ├── race_safe_team_id.py    # Sequential ID generator
│   │   ├── validation.py           # Input validation
│   │   ├── idempotency.py          # Duplicate prevention
│   │   ├── cloudinary_reliable.py  # Upload with retry
│   │   ├── email_reliable.py       # Email with retry
│   │   └── error_responses.py      # Unified errors
│   │
│   └── middleware/
│       └── logging_middleware.py    # Structured logging
│
├── tests/
│   ├── test_race_safe_id.py        # ID generation tests
│   ├── test_validation.py          # Validation tests
│   ├── test_idempotency.py         # Idempotency tests
│   └── test_registration_integration.py  # E2E tests
│
└── venv/                            # Virtual environment (git-ignored)
```

### Database Schema

```sql
-- Teams Table (with unique constraint)
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR(50) UNIQUE NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    church_name VARCHAR(200) NOT NULL,
    captain_name VARCHAR(100),
    captain_phone VARCHAR(20),
    captain_email VARCHAR(255),
    captain_whatsapp VARCHAR(20),
    vice_captain_name VARCHAR(100),
    vice_captain_phone VARCHAR(20),
    vice_captain_email VARCHAR(255),
    vice_captain_whatsapp VARCHAR(20),
    pastor_letter TEXT,
    payment_receipt TEXT,
    group_photo TEXT,
    registration_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate registrations
    CONSTRAINT uq_team_name_captain_phone UNIQUE (team_name, captain_phone)
);

-- Team Sequence Table (for race-safe IDs)
CREATE TABLE team_sequence (
    id INTEGER PRIMARY KEY DEFAULT 1,
    last_number INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Idempotency Keys Table (10-minute TTL)
CREATE TABLE idempotency_keys (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    response_data TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players Table
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50),
    team_id VARCHAR(50) REFERENCES teams(team_id),
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    aadhar_file TEXT,
    subscription_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for performance
CREATE INDEX idx_idempotency_key ON idempotency_keys(key);
```

---

## 🔌 API Endpoints

### Registration Endpoint (Production-Hardened)

```
POST /api/register/team
```

**Headers:**
- `Content-Type: multipart/form-data`
- `Idempotency-Key: <unique-id>` (optional, recommended)

**Form Fields:**
- `team_name` (required): Team name (3-80 chars)
- `church_name` (required): Church name (3-50 chars)
- `captain_name` (required): Captain full name (3-50 chars)
- `captain_phone` (required): 10-digit phone number
- `captain_email` (required): Valid email address
- `captain_whatsapp` (required): 10-digit WhatsApp number
- `vice_name` (required): Vice-captain full name
- `vice_phone` (required): 10-digit phone number
- `vice_email` (required): Valid email address
- `vice_whatsapp` (required): 10-digit WhatsApp number
- `players_json` (optional): JSON array of players
- `pastor_letter` (required): File (PNG/JPEG/PDF, max 5MB)
- `payment_receipt` (optional): File (PNG/JPEG/PDF, max 5MB)
- `group_photo` (optional): File (PNG/JPEG/PDF, max 5MB)

**Success Response (201):**
```json
{
  "success": true,
  "team_id": "ICCT-001",
  "team_name": "Warriors",
  "message": "Team registered successfully",
  "email_sent": true,
  "player_count": 15
}
```

**Error Response (400/409/500):**
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

### Authentication Endpoints

```
GET  /health                - Health check with DB status
GET  /status                - API status
```

### Team Endpoints

| Feature | Description |
|---------|-------------|
| **FastAPI** | Modern async Python web framework with automatic OpenAPI docs |
| **SQLAlchemy ORM** | Type-safe database operations with async support |
| **PostgreSQL** | Robust, scalable relational database |
| **Async/Await** | Non-blocking I/O for high performance |
| **Email Integration** | SMTP-based email notifications with templates |
| **Admin Panel** | Dedicated endpoints for administrative operations |
| **Error Handling** | Comprehensive exception handling with meaningful responses |
| **Type Hints** | Full type annotations for IDE support and code clarity |

---

## 🏗️ Architecture

### Tech Stack

```
┌─────────────────────────────────────────┐
│     FastAPI Web Framework               │
│  (Async Python, Starlette-based)        │
├─────────────────────────────────────────┤
│     SQLAlchemy ORM + Alembic            │
│  (Database abstraction, migrations)     │
├─────────────────────────────────────────┤
│     PostgreSQL Database                 │
│  (Persistent data storage)              │
├─────────────────────────────────────────┤
│     Pydantic Models                     │
│  (Request/Response validation)          │
├─────────────────────────────────────────┤
│     SMTP Email Service                  │
│  (Email notifications)                  │
└─────────────────────────────────────────┘
```

### Project Structure

```
ICCT26_BACKEND/
├── main.py                          # Main FastAPI application
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project configuration
├── .env.example                     # Environment variables template
├── README.md                        # This file
│
├── venv/                            # Virtual environment (git-ignored)
│
└── docs/                            # Documentation
    ├── INDEX.md                     # Documentation master index
    ├── admin-panel/                 # Admin panel docs (8 files)
    ├── api-reference/               # API reference docs (2 files)
    ├── deployment/                  # Deployment guides (4 files)
    ├── frontend/                    # Frontend integration (6 files)
    ├── security/                    # Security guidelines (3 files)
    └── setup/                       # Setup guides (3 files)
```

### Database Schema

```sql
-- Teams Table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    coach VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players Table
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    position VARCHAR(100),
    jersey_number INT,
    team_id INT REFERENCES teams(id) ON DELETE CASCADE,
    email VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for performance
CREATE INDEX idx_players_team_id ON players(team_id);
CREATE INDEX idx_players_email ON players(email);
```

---

## 🔌 API Endpoints

### Authentication Endpoints

```
GET  /auth/health           - Health check / API status
```

### Team Endpoints

```
GET    /teams               - Get all teams
POST   /teams               - Create new team
GET    /teams/{team_id}     - Get specific team
PUT    /teams/{team_id}     - Update team
DELETE /teams/{team_id}     - Delete team
```

### Player Endpoints

```
GET    /players             - Get all players
POST   /players             - Create new player
GET    /players/{player_id} - Get specific player
PUT    /players/{player_id} - Update player
DELETE /players/{player_id} - Delete player
```

### Admin Endpoints

```
GET    /admin/teams         - Get all teams with detailed info (admin)
GET    /admin/teams/{team_id}        - Get team with all players
GET    /admin/players/{player_id}    - Get player with full details
```

### Email Endpoints

```
POST   /send-test-email     - Send test email
POST   /send-email          - Send custom email
```

**Full API Documentation:** See `docs/api-reference/` and `docs/INDEX.md`

---

## 📥 Installation & Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd ICCT26_BACKEND
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your configuration
# See Configuration section below
```

### Step 5: Set Up Database

```bash
# See Database Setup section below
```

### Step 6: Run Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/icct26_db

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Application Settings
APP_NAME=ICCT26 Backend API
DEBUG=True
SECRET_KEY=your-secret-key-here-keep-it-secure
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Admin Settings
ADMIN_EMAIL=admin@example.com
```

### Email Configuration

#### Gmail Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select Mail and Windows Computer
   - Copy the generated password
3. Use the password in `SMTP_PASSWORD`

#### Alternative Email Providers

- **SendGrid:** Update `SMTP_HOST` to `smtp.sendgrid.net`, `SMTP_PORT` to `587`
- **Mailgun:** Update `SMTP_HOST` to `smtp.mailgun.org`, `SMTP_PORT` to `587`
- **AWS SES:** Update `SMTP_HOST` to `email-smtp.region.amazonaws.com`

### Database Configuration

```env
# PostgreSQL Connection String Format
DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]

# Example for local development
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/icct26_db

# Example for Render (production)
DATABASE_URL=postgresql+asyncpg://user:password@dpg-xxxxx-xxxx.oregon-postgres.render.com:5432/icct26_db
```

---

## ▶️ Running the Application

### Development Mode

```bash
# With auto-reload
uvicorn main:app --reload --port 8000

# Output:
# Uvicorn running on http://127.0.0.1:8000
# Press CTRL+C to quit
```

### Production Mode

```bash
# With multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Or with gunicorn (recommended)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Access Points

| URL | Purpose |
|-----|---------|
| `http://localhost:8000` | API Root |
| `http://localhost:8000/docs` | Swagger UI (Interactive API Docs) |
| `http://localhost:8000/redoc` | ReDoc (API Documentation) |
| `http://localhost:8000/openapi.json` | OpenAPI Schema |

---

## 🔐 Admin Panel

The Admin Panel provides comprehensive management endpoints:

### Admin Features

✅ **Team Management** - View all teams with complete details  
✅ **Player Management** - View player information across all teams  
✅ **Data Export** - Get structured data for reporting  
✅ **Performance** - Optimized queries with minimal database hits  

### Admin Endpoints

```bash
# Get all teams (with player count, coach info, etc.)
GET /admin/teams

# Get specific team with all players
GET /admin/teams/{team_id}

# Get player full details
GET /admin/players/{player_id}
```

### Usage Example

```bash
curl -X GET "http://localhost:8000/admin/teams"

curl -X GET "http://localhost:8000/admin/teams/1"

curl -X GET "http://localhost:8000/admin/players/5"
```

**Full Admin Documentation:** See `docs/admin-panel/ADMIN_PANEL_ENDPOINTS.md`

---

## 📧 Email Notifications

### Test Email Endpoint

```bash
# Send a test email
curl -X POST "http://localhost:8000/send-test-email" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "test@example.com"
  }'
```

### Send Custom Email

```bash
curl -X POST "http://localhost:8000/send-email" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Test Subject",
    "body": "Email content here",
    "html_body": "<h1>HTML Content</h1>"
  }'
```

### Email Features

✅ **SMTP Integration** - Works with Gmail, SendGrid, Mailgun, AWS SES  
✅ **HTML Templates** - Support for rich HTML emails  
✅ **Async Sending** - Non-blocking email dispatch  
✅ **Error Handling** - Comprehensive error messages  

**Full Email Documentation:** See test_email.py for examples

---

## 🗄️ Database Setup

### PostgreSQL Installation

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# Run installer and follow prompts
# Remember the password you set for 'postgres' user
```

**macOS:**
```bash
# Using Homebrew
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE icct26_db;

# Create user (optional, for security)
CREATE USER icct26_user WITH PASSWORD 'secure_password';
ALTER ROLE icct26_user SET client_encoding TO 'utf8';
ALTER ROLE icct26_user SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE icct26_db TO icct26_user;

# Exit psql
\q
```

### Initialize Database Connection

Update `.env` with your database credentials:

```env
DATABASE_URL=postgresql+asyncpg://icct26_user:secure_password@localhost:5432/icct26_db
```

### Verify Connection

```bash
# Run the application, it will test the connection
uvicorn main:app --reload

# Check for "Connected to PostgreSQL" message in console
```

---

## 🚀 Deployment

### Deployment Platforms

The application can be deployed to:

- **Render** (Recommended for PostgreSQL + FastAPI)
- **Railway**
- **Fly.io**
- **Heroku**
- **AWS EC2** / **Lightsail**
- **DigitalOcean**

### Quick Deployment to Render

1. **Push to GitHub** - Ensure code is in a GitHub repository
2. **Connect Render** - Go to https://render.com and connect your GitHub account
3. **Create Web Service** - Select this repository
4. **Configure:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables from `.env`
5. **Add PostgreSQL Database** - Create PostgreSQL instance on Render
6. **Update DATABASE_URL** - Use Render database URL

**Full Deployment Guide:** See `docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md`

---

## 📚 Documentation

Complete documentation is organized in the `docs/` folder:

### Documentation Structure

```
docs/
├── INDEX.md                           # Master documentation index
├── admin-panel/                       # Admin Panel (8 files)
│   ├── ADMIN_PANEL_ENDPOINTS.md
│   ├── ADMIN_TESTING_GUIDE.md
│   └── ...
├── api-reference/                     # API Reference (2 files)
│   └── SIMPLE_API_README.md
├── deployment/                        # Deployment Guides (4 files)
│   ├── PRODUCTION_DEPLOYMENT_GUIDE.md
│   ├── RENDER_SETUP_SUMMARY.md
│   └── ...
├── frontend/                          # Frontend Integration (6 files)
│   ├── FRONTEND_INTEGRATION.md
│   ├── INTEGRATION_CHECKLIST.md
│   └── ...
├── security/                          # Security (3 files)
│   ├── SECURITY.md
│   └── ...
└── setup/                             # Setup Guides (3 files)
    ├── SETUP_GUIDE.md
    └── ...
```

### Quick Links

| Document | Purpose |
|----------|---------|
| `docs/INDEX.md` | **START HERE** - Master index of all documentation |
| `docs/admin-panel/ADMIN_PANEL_ENDPOINTS.md` | Admin API endpoints reference |
| `docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md` | Production deployment steps |
| `docs/frontend/FRONTEND_INTEGRATION.md` | Frontend integration guide |
| `docs/security/SECURITY.md` | Security guidelines and best practices |
| `docs/setup/SETUP_GUIDE.md` | Complete setup instructions |

**Access Documentation:** Open `docs/INDEX.md` in your editor

---

## 🧪 Testing

### Run Test Email

```bash
# Using Python directly
python test_email.py

# Expected output:
# Testing email functionality...
# Email sent successfully!
```

### API Testing

```bash
# Test health check
curl -X GET "http://localhost:8000/auth/health"

# Test create team
curl -X POST "http://localhost:8000/teams" \
  -H "Content-Type: application/json" \
  -d '{"name":"Team A","description":"Test team"}'

# Test get teams
curl -X GET "http://localhost:8000/teams"
```

### Automated Testing

Use the Swagger UI for interactive testing:
1. Go to `http://localhost:8000/docs`
2. Click on an endpoint
3. Click "Try it out"
4. Enter parameters and click "Execute"

---

## 🔒 Security

### Key Security Features

✅ **Environment Variables** - Sensitive data not hardcoded  
✅ **Type Validation** - Pydantic models validate all inputs  
✅ **Error Handling** - No sensitive data in error messages  
✅ **CORS Configuration** - Restrict cross-origin requests  
✅ **Async Operations** - Protection against blocking attacks  

### Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use strong passwords** - For database and email
3. **Rotate secrets** - Especially `SECRET_KEY`
4. **Keep dependencies updated** - Run `pip install --upgrade -r requirements.txt`
5. **Use HTTPS in production** - Configure SSL certificates
6. **Monitor logs** - Check for suspicious activity

**Full Security Guide:** See `docs/security/SECURITY.md`

---

## 📦 Dependencies

### Core Dependencies

```
fastapi==0.104.1          # Web framework
uvicorn==0.24.0           # ASGI server
sqlalchemy==2.0.23        # ORM
asyncpg==0.29.0           # PostgreSQL async driver
pydantic==2.5.0           # Data validation
python-dotenv==1.0.0      # Environment variables
aiosmtplib==3.0.0         # Async SMTP
```

### Installation

```bash
pip install -r requirements.txt
```

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

---

## 🤝 Contributing

### Contribution Workflow

1. **Create a branch** - `git checkout -b feature/your-feature`
2. **Make changes** - Implement your feature
3. **Test thoroughly** - Run tests and verify functionality
4. **Commit changes** - `git commit -m "Add feature"`
5. **Push to GitHub** - `git push origin feature/your-feature`
6. **Create Pull Request** - Describe your changes
7. **Code Review** - Wait for review and feedback
8. **Merge** - Once approved, merge to main

### Code Standards

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for complex functions
- Test new features thoroughly
- Update documentation

---

## ❓ FAQ

### Q: How do I reset the database?
**A:** Delete all records:
```sql
DELETE FROM players;
DELETE FROM teams;
```

### Q: How do I backup my database?
**A:** Use pg_dump:
```bash
pg_dump -U postgres icct26_db > backup.sql
```

### Q: How do I restore from backup?
**A:** Use psql:
```bash
psql -U postgres icct26_db < backup.sql
```

### Q: How do I check if the API is running?
**A:** Test the health endpoint:
```bash
curl -X GET "http://localhost:8000/auth/health"
```

### Q: How do I debug API errors?
**A:** Check console output and error messages in responses. Use Swagger UI for detailed error info.

### Q: How do I enable CORS for a frontend?
**A:** Update `.env` and add your frontend URL to `ALLOWED_ORIGINS`:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## 🆘 Support

### Getting Help

1. **Check Documentation** - See `docs/INDEX.md`
2. **Read Error Messages** - They often indicate the solution
3. **Check API Docs** - Visit `http://localhost:8000/docs`
4. **Review Examples** - Check test_email.py and documentation files

### Common Issues

| Issue | Solution |
|-------|----------|
| **Database Connection Error** | Check DATABASE_URL in .env and PostgreSQL is running |
| **Email Not Sending** | Verify SMTP settings, check Gmail app password |
| **Port Already in Use** | Change port: `uvicorn main:app --port 8001` |
| **Virtual Environment Issues** | Delete venv and recreate: `python -m venv venv` |

### Troubleshooting

**Application won't start:**
```bash
# Check if dependencies are installed
pip list | findstr fastapi

# Reinstall if needed
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8 or higher
```

**Database connection fails:**
```bash
# Test PostgreSQL connection
psql -U postgres -d icct26_db -c "SELECT 1"

# Verify DATABASE_URL format in .env
```

**Email not working:**
```bash
# Run test email script
python test_email.py

# Check SMTP settings in .env
```

---

## 📝 License

This project is proprietary and confidential. Unauthorized copying or distribution is prohibited.

---

## 📧 Contact

For questions or support, contact the development team.

---

## 🎯 Roadmap

### Planned Features

- [ ] Authentication and Authorization (JWT)
- [ ] Rate limiting
- [ ] Caching layer (Redis)
- [ ] Database migrations (Alembic)
- [ ] Advanced filtering and search
- [ ] Data export to CSV/Excel
- [ ] Real-time notifications (WebSocket)
- [ ] Mobile API endpoints
- [ ] Analytics dashboard

---

## 📊 Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| **API Core** | ✅ Ready | FastAPI application running |
| **Database** | ✅ Ready | PostgreSQL configured |
| **Admin Panel** | ✅ Ready | 3 endpoints implemented |
| **Email System** | ✅ Ready | SMTP integration working |
| **Documentation** | ✅ Complete | 26 comprehensive docs |
| **Deployment** | ✅ Ready | Render ready |

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Pydantic](https://docs.pydantic.dev/)

---

**Last Updated:** November 2025  
**Version:** 1.0.0  
**Maintainer:** Development Team

For detailed documentation, see `docs/INDEX.md` 📚
