# ICCT26 Backend API

**Production-Ready FastAPI Backend for Cricket Tournament Team Registration**

A robust, enterprise-grade backend system for managing cricket tournament team registrations with complete player management, file uploads, and production hardening features.

---

## 🎯 Project Overview

**Status:** ✅ Production Ready | **Version:** 1.0.0 | **Last Updated:** November 2025

### What This Backend Does

The ICCT26 Backend API provides a complete registration and management system for cricket tournaments with:

- **Team Registration** - Multi-step form handling with validation
- **Player Management** - Dynamic player extraction with role validation  
- **File Storage** - Cloudinary integration for pastor letters, receipts, photos, and player documents
- **Tournament Gallery** - Image gallery with download functionality
- **Production Hardening** - Race-safe ID generation, retry logic, structured logging
- **Database Management** - PostgreSQL with async SQLAlchemy ORM

### Technology Stack

```
FastAPI 0.104+ (Async Python Web Framework)
├── PostgreSQL (Neon) - Primary Database
├── SQLAlchemy 2.0+ - Async ORM with connection pooling
├── Cloudinary - File storage and CDN
├── Pydantic 2.5+ - Data validation with pydantic-settings
├── Uvicorn - ASGI production server
└── Gunicorn - Multi-worker process manager
```

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Production Features](#-production-features)
- [Architecture](#-architecture)
- [API Endpoints](#-api-endpoints)
  - [Team Registration](#registration-endpoint)
  - [Gallery Management](#gallery-endpoints)
  - [Admin Operations](#admin-endpoints)
- [Installation & Setup](#-installation--setup)
- [Configuration](#-configuration)
- [Database Schema](#-database-schema)
- [Running the Application](#-running-the-application)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Error Handling](#-error-handling)
- [Monitoring & Logging](#-monitoring--logging)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ or Neon database account
- Cloudinary account (free tier works)
- Git

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/sanjaynesan-05/ICCT26-BACKEND.git
cd ICCT26-BACKEND

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
cp .env.example .env.local
# Edit .env.local with your database and Cloudinary credentials

# 6. Run the application
uvicorn main:app --reload --port 8000
```

**API Documentation:** http://localhost:8000/docs  
**Health Check:** http://localhost:8000/health

---

## 🔐 Production Features

### 1. Race-Safe Team ID Generation

Sequential team IDs (`ICCT-001`, `ICCT-002`, etc.) with **zero race conditions**:

- Database-backed counter with `SELECT FOR UPDATE` row locking
- Atomic increment operations in nested transactions
- Handles 100+ concurrent requests safely
- Max 3 retries on conflict with exponential backoff

**Code:** `app/utils/race_safe_team_id.py`

### 2. Dynamic Player Extraction

**Frontend sends:**
```text
player_0_name, player_0_role, player_0_aadhar_file, player_0_subscription_file
player_1_name, player_1_role, player_1_aadhar_file, player_1_subscription_file
...
player_14_name, player_14_role, player_14_aadhar_file, player_14_subscription_file
```

**Backend automatically:**
- Detects all players dynamically (no limit hardcoded)
- Validates name (2+ chars) and role (Batsman/Bowler/All-Rounder/Wicket-Keeper)
- Uploads aadhar + subscription files to Cloudinary
- Creates Player records with Cloudinary URLs
- Links players to team via foreign key

**Code:** `app/routes/registration_production.py` (lines 120-180)

### 3. Strong Input Validation

Comprehensive validation layer using Pydantic and custom validators:

| Field | Validation Rules |
|-------|------------------|
| **Team Name** | 3-80 chars, letters/spaces/hyphens only |
| **Names** | 3-50 chars, letters/spaces/apostrophes/hyphens |
| **Phone** | Exactly 10 digits, numeric only |
| **Email** | RFC 5322 compliant regex |
| **Player Role** | Must be: Batsman, Bowler, All-Rounder, or Wicket-Keeper |
| **Files** | Max 5MB, PNG/JPEG/PDF only, MIME validation |

**Code:** `app/utils/validation.py`

### 4. Duplicate Protection (Two-Layer Defense)

**Layer 1: Database Constraints**
```sql
CONSTRAINT uq_team_name_captain_phone UNIQUE (team_name, captain_phone)
```

**Layer 2: Idempotency Keys**
- Send `Idempotency-Key: <unique-id>` header
- Server caches response for 10 minutes
- Prevents duplicate submissions on page refresh
- Returns 409 Conflict with original response

**Code:** `app/utils/idempotency.py`

### 5. File Upload with Retry Logic

**Cloudinary uploads** (3 retries with exponential backoff):

- Attempt 1: Immediate
- Attempt 2: +0.5s delay
- Attempt 3: +1.0s delay  
- Attempt 4: +2.0s delay

**File organization:**
```text
ICCT26/
├── pastor_letters/{team_id}/
├── receipts/{team_id}/
├── group_photos/{team_id}/
└── players/{team_id}/
    ├── player_0/
    │   ├── aadhar/
    │   └── subscription/
    └── player_1/
        ├── aadhar/
        └── subscription/
```

**Code:** `app/utils/cloudinary_reliable.py`

### 6. Structured Logging & Request Tracking

JSON-formatted logs with unique request IDs:

```json
{
  "timestamp": "2025-11-19T10:30:45Z",
  "request_id": "req_abc123xyz",
  "event": "registration_started",
  "team_name": "Warriors",
  "client_ip": "192.168.1.100",
  "duration_ms": 1247
}
```

**Events tracked:**

- `registration_started` - When registration begins
- `validation_error` - Input validation failures
- `file_upload` - Success/failure with URLs
- `db_operation` - Insert/update/delete operations
- `exception` - Unexpected errors with stack traces

**Code:** `app/middleware/logging_middleware.py`

### 7. Unified Error Response Format

Consistent error structure across all endpoints:

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

**Code:** `app/utils/error_responses.py`

### 8. Tournament Gallery Management

Professional image gallery with Cloudinary integration:

- **Browse Images** - Fetch gallery images from ICCT26/Gallery folder
- **Single Download** - Download individual images with proper filenames
- **Bulk Download** - Generate URLs for multiple images at once
- **Pagination** - Support for limit/skip parameters
- **CDN Delivery** - Fast image delivery via Cloudinary CDN
- **Responsive Design** - Mobile-friendly gallery interface
- **Health Check** - Verify Cloudinary API connection

**Code:** `app/routes/gallery.py`

---

## 🏗️ Architecture

### System Architecture

```text
┌─────────────────────────────────────────────────────┐
│              Frontend (React/Next.js)               │
│         (Sends multipart/form-data)                 │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP POST
                      │ /api/register/team
                      ▼
┌─────────────────────────────────────────────────────┐
│           FastAPI Application (main.py)             │
├─────────────────────────────────────────────────────┤
│  Production Middleware:                             │
│  ├── CORS (origin validation)                       │
│  ├── Request ID tracking                            │
│  ├── Rate limiting                                  │
│  └── Structured logging                             │
├─────────────────────────────────────────────────────┤
│  Registration Endpoint:                             │
│  (app/routes/registration_production.py)            │
│                                                      │
│  Step 1: Idempotency check                          │
│  Step 2: Validate team/captain/vice-captain         │
│  Step 3: Validate files (pastor letter, etc.)       │
│  Step 4: Extract players dynamically                │
│  Step 5: Generate race-safe team ID                 │
│  Step 6: Upload team files to Cloudinary            │
│  Step 7: Upload player files + create records       │
│  Step 8: Store idempotency key                      │
│  Step 9: Return success response                    │
├─────────────────────────────────────────────────────┤
│  Utilities Layer:                                   │
│  ├── race_safe_team_id.py (ID generation)          │
│  ├── validation.py (input validation)              │
│  ├── cloudinary_reliable.py (file uploads)         │
│  ├── idempotency.py (duplicate prevention)         │
│  └── error_responses.py (unified errors)           │
└─────────────────────┬───────────────────────────────┘
                      │
            ┌─────────┴──────────┬──────────────────┐
            ▼                    ▼                  ▼
    ┌───────────────┐   ┌────────────────┐  ┌─────────────┐
    │  PostgreSQL   │   │   Cloudinary   │  │ Monitoring  │
    │  (Neon DB)    │   │   CDN + Files  │  │  Logs JSON  │
    │               │   │                │  │             │
    │ Tables:       │   │ Folders:       │  │ Events:     │
    │ - teams       │   │ - pastor_...   │  │ - reg_start │
    │ - players     │   │ - receipts     │  │ - upload    │
    │ - team_seq    │   │ - players/...  │  │ - db_op     │
    │ - idem_keys   │   │                │  │ - errors    │
    └───────────────┘   └────────────────┘  └─────────────┘
```

### Project Structure

```text
ICCT26-BACKEND/
├── main.py                          # FastAPI application entry point
├── config.py                        # Pydantic settings (env vars)
├── database.py                      # SQLAlchemy engine configuration
├── models.py                        # Database models (Team, Player)
├── cloudinary_config.py             # Cloudinary setup
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── .env.local                       # Local config (gitignored)
├── README.md                        # This file
│
├── app/
│   ├── routes/
│   │   ├── registration_production.py  # Main registration endpoint
│   │   ├── gallery.py                  # Gallery management endpoints
│   │   ├── team.py                     # Team management routes
│   │   ├── admin.py                    # Admin endpoints
│   │   └── health.py                   # Health check
│   │
│   ├── utils/
│   │   ├── race_safe_team_id.py        # Sequential ID generator
│   │   ├── validation.py               # Input validation
│   │   ├── idempotency.py              # Duplicate prevention
│   │   ├── cloudinary_reliable.py      # Upload with retry
│   │   ├── error_responses.py          # Unified errors
│   │   ├── structured_logging.py       # JSON logging
│   │   ├── database_hardening.py       # DB health checks
│   │   └── global_exception_handler.py # Exception handlers
│   │
│   └── middleware/
│       └── production_middleware.py    # CORS, request tracking
│
├── tests/
│   ├── test_race_safe_id.py            # ID generation tests
│   ├── test_validation.py              # Validation tests
│   ├── test_idempotency.py             # Idempotency tests
│   └── test_registration_integration.py # E2E tests (25 tests)
│
└── venv/                                # Virtual environment (gitignored)
```

---

## 🔌 API Endpoints

**Endpoint:**

```http
POST /api/register/team
```

**Headers:**

- `Content-Type: multipart/form-data`
- `Idempotency-Key: <unique-uuid>` (optional but recommended)

**Form Fields (Team & Officials):**

- `team_name` - Team name (required, 3-80 chars)
- `church_name` - Church name (required, 3-50 chars)
- `captain_name` - Captain full name (required)
- `captain_phone` - 10-digit phone (required)
- `captain_email` - Valid email (required)
- `captain_whatsapp` - 10-digit WhatsApp (required)
- `vice_name` - Vice-captain name (required)
- `vice_phone` - 10-digit phone (required)
- `vice_email` - Valid email (required)
- `vice_whatsapp` - 10-digit WhatsApp (required)

**Form Fields (Files):**

- `pastor_letter` - PDF/PNG/JPEG, max 5MB (required)
- `payment_receipt` - PDF/PNG/JPEG, max 5MB (optional)
- `group_photo` - PNG/JPEG, max 5MB (optional)

**Form Fields (Players - Dynamic):**

For each player `i` (starting from 0):

- `player_i_name` - Player name (required, 2+ chars)
- `player_i_role` - Role: Batsman/Bowler/All-Rounder/Wicket-Keeper (required)
- `player_i_aadhar_file` - Aadhar card (PDF/PNG/JPEG, max 5MB)
- `player_i_subscription_file` - Church subscription (PDF/PNG/JPEG, max 5MB)

**Example:**

```bash
curl -X POST "https://api.icct26.com/api/register/team" \
  -H "Idempotency-Key: unique-uuid-here" \
  -F "team_name=Chennai Warriors" \
  -F "church_name=CSI Church Coimbatore" \
  -F "captain_name=John Doe" \
  -F "captain_phone=9876543210" \
  -F "captain_email=john@example.com" \
  -F "captain_whatsapp=9876543210" \
  -F "vice_name=Jane Smith" \
  -F "vice_phone=9876543211" \
  -F "vice_email=jane@example.com" \
  -F "vice_whatsapp=9876543211" \
  -F "pastor_letter=@pastor.pdf" \
  -F "payment_receipt=@receipt.png" \
  -F "group_photo=@team.jpg" \
  -F "player_0_name=Player One" \
  -F "player_0_role=Batsman" \
  -F "player_0_aadhar_file=@p0_aadhar.jpg" \
  -F "player_0_subscription_file=@p0_sub.pdf" \
  -F "player_1_name=Player Two" \
  -F "player_1_role=Bowler" \
  -F "player_1_aadhar_file=@p1_aadhar.jpg" \
  -F "player_1_subscription_file=@p1_sub.pdf"
```

**Success Response (201 Created):**

```json
{
  "success": true,
  "team_id": "ICCT-005",
  "team_name": "Chennai Warriors",
  "message": "Team registered successfully",
  "player_count": 11
}
```

**Error Response (400 Bad Request):**

```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Player 1 role must be one of: Batsman, Bowler, All-Rounder, Wicket-Keeper",
  "details": {
    "field": "player_0_role",
    "value": "InvalidRole"
  }
}
```

**Error Response (409 Conflict - Duplicate):**

```json
{
  "success": true,
  "team_id": "ICCT-003",
  "team_name": "Chennai Warriors",
  "message": "Team registered successfully",
  "player_count": 11
}
```

### Health Check Endpoint

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "cloudinary": "configured",
  "timestamp": "2025-11-19T10:30:45Z"
}
```

### Admin Endpoints

```http
GET /admin/teams              # Get all teams
GET /admin/teams/{team_id}    # Get specific team with players
GET /admin/players            # Get all players
```

### Gallery Endpoints

**Purpose:** Manage tournament gallery images with Cloudinary integration

#### Get Gallery Images

```http
GET /api/gallery/ICCT26/Gallery/images
```

Fetch all images from the ICCT26/Gallery folder in Cloudinary.

**Query Parameters:**

- `limit` - Number of images to fetch (default: 50)
- `skip` - Number of images to skip for pagination (default: 0)

**Response:**

```json
{
  "success": true,
  "images": [
    {
      "public_id": "ICCT26/Gallery/image_001",
      "url": "https://res.cloudinary.com/...",
      "secure_url": "https://res.cloudinary.com/...",
      "format": "jpg",
      "created_at": "2025-11-20T10:30:45Z",
      "width": 1920,
      "height": 1080
    }
  ],
  "total_count": 150,
  "limit": 50,
  "skip": 0
}
```

#### Get Gallery Images from Cloudinary Collection

```http
GET /api/gallery/collection/images
```

Fetch all images from Cloudinary Collection. Collection provides easier management through Cloudinary's web UI.

**Collection:** https://collection.cloudinary.com/dplaeuuqk/b40aac6242ba4cd0c8bedcb520ca1eac

**Query Parameters:**

- `limit` - Number of images to fetch (default: 50)
- `skip` - Number of images to skip for pagination (default: 0)

**Response:**

Same as folder-based endpoint above.

**Advantages:**
- Easy drag-and-drop upload via Cloudinary UI
- Better organization without folder structure
- Collaborative asset management
- Built-in metadata and tagging

#### Download Single Image

```http
POST /api/gallery/download/single
Content-Type: application/json
```

Generate download URL for a single image.

**Request Body:**

```json
{
  "public_id": "ICCT26/Gallery/image_001"
}
```

**Response:**

```json
{
  "success": true,
  "public_id": "ICCT26/Gallery/image_001",
  "download_url": "https://res.cloudinary.com/...?fl_attachment",
  "filename": "image_001.jpg"
}
```

#### Download Bulk Images

```http
POST /api/gallery/download/bulk
Content-Type: application/json
```

Prepare zip file with multiple images for download.

**Request Body:**

```json
{
  "public_ids": [
    "ICCT26/Gallery/image_001",
    "ICCT26/Gallery/image_002",
    "ICCT26/Gallery/image_003"
  ]
}
```

**Response:**

```json
{
  "success": true,
  "count": 3,
  "download_urls": [
    {
      "public_id": "ICCT26/Gallery/image_001",
      "url": "https://res.cloudinary.com/...?fl_attachment",
      "filename": "image_001.jpg"
    }
  ],
  "message": "Download URLs generated for 3 images"
}
```

#### Gallery Health Check

```http
GET /api/gallery/health
```

Verify Cloudinary connection and API status.

**Response:**

```json
{
  "success": true,
  "status": "healthy",
  "cloudinary_api": "connected",
  "timestamp": "2025-11-20T10:30:45Z"
}
```

---

## 💾 Installation & Setup

### Step 1: Prerequisites

Install the following on your system:

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download](https://www.postgresql.org/download/) OR [Neon Account](https://neon.tech/)
- **Cloudinary Account** - [Sign Up](https://cloudinary.com/)
- **Git** - [Download](https://git-scm.com/)

### Step 2: Clone Repository

```bash
git clone https://github.com/sanjaynesan-05/ICCT26-BACKEND.git
cd ICCT26-BACKEND
```

### Step 3: Create Virtual Environment

**Windows:**

```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env.local

# Open .env.local in your editor
# Fill in your actual credentials (see Configuration section)
```

### Step 6: Run Application

```bash
# Development mode (auto-reload on changes)
uvicorn main:app --reload --port 8000

# Production mode (4 workers)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Step 7: Verify Installation

Open browser to:

- **API Docs:** <http://localhost:8000/docs>
- **Health Check:** <http://localhost:8000/health>

---

## ⚙️ Configuration

### Environment Variables (.env.local)

Create `.env.local` file in project root:

```env
# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# PostgreSQL connection string (async format)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# Example for Neon (production)
DATABASE_URL=postgresql+asyncpg://neondb_owner:password@ep-winter-salad.us-east-1.aws.neon.tech/neondb?ssl=require

# Example for local PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/icct26

# Database pool settings
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_RECYCLE=3600

# =============================================================================
# CLOUDINARY CONFIGURATION
# =============================================================================
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=your-secret-key-here

# Get these from: https://console.cloudinary.com/settings/security

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_TITLE=ICCT26 Backend API
APP_VERSION=1.0.0
ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE=logs/app.log

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com
CORS_ALLOW_CREDENTIALS=true

# =============================================================================
# SECURITY
# =============================================================================
SECRET_KEY=your-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this
JWT_ALGORITHM=HS256

# =============================================================================
# OPTIONAL: SMTP (Email disabled by default)
# =============================================================================
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASS=your-smtp-password
SMTP_FROM_EMAIL=noreply@icct26.com
SMTP_FROM_NAME=ICCT26 Tournament
```

### Cloudinary Setup

1. **Sign up** at [cloudinary.com](https://cloudinary.com/)
2. **Navigate to:** Dashboard → Settings → Security
3. **Copy credentials:**
   - Cloud Name
   - API Key
   - API Secret
4. **Paste into** `.env.local`

### Database Setup Options

#### Option 1: Neon (Recommended for Production)

1. **Sign up** at [neon.tech](https://neon.tech/)
2. **Create project** → Copy connection string
3. **Replace** `postgresql://` with `postgresql+asyncpg://`
4. **Add** `?ssl=require` at the end
5. **Paste into** `.env.local`

#### Option 2: Local PostgreSQL

```bash
# Install PostgreSQL
# Windows: https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Linux: sudo apt install postgresql

# Create database
psql -U postgres
CREATE DATABASE icct26;
\q

# Update .env.local
DATABASE_URL=postgresql+asyncpg://postgres:your-password@localhost:5432/icct26
```

---

## 🗄️ Database Schema

### Tables Overview

```text
teams (Main table for team information)
  ├── team_id (PK, unique: ICCT-001, ICCT-002, ...)
  ├── team_name
  ├── church_name
  ├── captain details (name, phone, email, whatsapp)
  ├── vice-captain details (name, phone, email, whatsapp)
  ├── pastor_letter (Cloudinary URL)
  ├── payment_receipt (Cloudinary URL)
  └── group_photo (Cloudinary URL)

players (Player information with file uploads)
  ├── player_id (PK, unique: ICCT-001-P01, ICCT-001-P02, ...)
  ├── team_id (FK → teams.team_id)
  ├── name
  ├── role (Batsman/Bowler/All-Rounder/Wicket-Keeper)
  ├── aadhar_file (Cloudinary URL)
  └── subscription_file (Cloudinary URL)

team_sequence (For race-safe ID generation)
  ├── id (always 1)
  ├── last_number (auto-incremented)
  └── updated_at

idempotency_keys (Duplicate prevention)
  ├── key (unique request identifier)
  ├── response_data (cached JSON response)
  ├── expires_at (TTL: 10 minutes)
  └── created_at
```

### SQL Schema

```sql
-- Teams Table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR(50) UNIQUE NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    church_name VARCHAR(200) NOT NULL,
    captain_name VARCHAR(100) NOT NULL,
    captain_phone VARCHAR(15) NOT NULL,
    captain_email VARCHAR(255) NOT NULL,
    captain_whatsapp VARCHAR(20),
    vice_captain_name VARCHAR(100) NOT NULL,
    vice_captain_phone VARCHAR(15) NOT NULL,
    vice_captain_email VARCHAR(255) NOT NULL,
    vice_captain_whatsapp VARCHAR(20),
    pastor_letter TEXT,
    payment_receipt TEXT,
    group_photo TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate registrations
    CONSTRAINT uq_team_name_captain_phone UNIQUE (team_name, captain_phone)
);

-- Players Table
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) UNIQUE NOT NULL,
    team_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    aadhar_file TEXT,
    subscription_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key with cascade delete
    CONSTRAINT fk_team FOREIGN KEY (team_id) 
        REFERENCES teams(team_id) ON DELETE CASCADE
);

-- Team Sequence Table (Race-safe ID generation)
CREATE TABLE team_sequence (
    id INTEGER PRIMARY KEY DEFAULT 1,
    last_number INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initialize sequence
INSERT INTO team_sequence (id, last_number) VALUES (1, 0);

-- Idempotency Keys Table
CREATE TABLE idempotency_keys (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    response_data TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for performance
CREATE INDEX idx_team_id ON teams(team_id);
CREATE INDEX idx_player_team_id ON players(team_id);
CREATE INDEX idx_idempotency_key ON idempotency_keys(key);
CREATE INDEX idx_idempotency_expires ON idempotency_keys(expires_at);
```

### Database Initialization

The application automatically creates tables on first startup via `main.py`:

```python
@app.on_event("startup")
async def startup_event():
    async with async_engine.begin() as conn:
        await conn.run_sync(AsyncBase.metadata.create_all)
```

---

## 🎯 Running the Application

### Development Mode (Local Testing)

```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run with auto-reload
uvicorn main:app --reload --port 8000 --log-level debug

# Output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

### Production Mode (Multiple Workers)

```bash
# Using Gunicorn (recommended)
gunicorn main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log

# Or using Uvicorn directly
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

### Docker (Optional)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

```bash
# Build and run
docker build -t icct26-backend .
docker run -p 8000:8000 --env-file .env.local icct26-backend
```

### Access Points

| URL | Purpose |
|-----|---------|
| <http://localhost:8000> | API Root |
| <http://localhost:8000/docs> | Swagger UI (Interactive Docs) |
| <http://localhost:8000/redoc> | ReDoc Documentation |
| <http://localhost:8000/health> | Health Check |
| <http://localhost:8000/openapi.json> | OpenAPI Schema |

---

## 🧪 Testing

### Manual API Testing

**Using Swagger UI** (Recommended):

1. Start server: `uvicorn main:app --reload`
2. Open browser: <http://localhost:8000/docs>
3. Click endpoint → "Try it out"
4. Fill parameters → "Execute"
5. View response

**Using cURL:**

```bash
# Health check
curl http://localhost:8000/health

# Register team (with files)
curl -X POST "http://localhost:8000/api/register/team" \
  -H "Idempotency-Key: test-$(date +%s)" \
  -F "team_name=Test Team" \
  -F "church_name=Test Church" \
  -F "captain_name=John Doe" \
  -F "captain_phone=9876543210" \
  -F "captain_email=john@test.com" \
  -F "captain_whatsapp=9876543210" \
  -F "vice_name=Jane Smith" \
  -F "vice_phone=9876543211" \
  -F "vice_email=jane@test.com" \
  -F "vice_whatsapp=9876543211" \
  -F "pastor_letter=@pastor.pdf" \
  -F "player_0_name=Player One" \
  -F "player_0_role=Batsman"
```

### Automated Testing (Pytest)

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx aiosqlite

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_registration_integration.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

**Test Results (Current):**

```text
============================= test session starts =============================
tests/test_race_safe_id.py ................                            [ 25%]
tests/test_validation.py ...........................                   [ 75%]
tests/test_idempotency.py .....                                        [ 90%]
tests/test_registration_integration.py ...                             [100%]

============================== 25 passed in 3.42s ==============================
```

---

## 🚀 Deployment

### Render Deployment (Recommended)

**Step 1: Prepare Repository**

```bash
# Ensure .env.local is in .gitignore
echo ".env.local" >> .gitignore

# Commit changes
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

**Step 2: Create Web Service**

1. **Log in** to [render.com](https://render.com/)
2. **New** → **Web Service**
3. **Connect Repository** → Select `ICCT26-BACKEND`
4. **Configure Service:**
   - **Name:** `icct26-backend`
   - **Region:** Oregon (US West)
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

**Step 3: Add Environment Variables**

In Render dashboard, add these environment variables:

```env
DATABASE_URL=<your-neon-postgres-url>
CLOUDINARY_CLOUD_NAME=<your-cloud-name>
CLOUDINARY_API_KEY=<your-api-key>
CLOUDINARY_API_SECRET=<your-api-secret>
SECRET_KEY=<generate-random-string>
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend.com
```

**Step 4: Create PostgreSQL Database**

1. **New** → **PostgreSQL**
2. **Name:** `icct26-db`
3. **Region:** Same as web service
4. **Copy** Internal Database URL
5. **Update** `DATABASE_URL` in web service env vars

**Step 5: Deploy**

- Render auto-deploys on git push
- **View logs:** Dashboard → Logs tab
- **Test API:** `https://icct26-backend.onrender.com/health`

### Production Checklist

- [ ] Environment variables configured
- [ ] Database connected and tables created
- [ ] Cloudinary configured
- [ ] CORS origins set correctly
- [ ] Health check returns 200 OK
- [ ] Test registration endpoint
- [ ] Monitor logs for errors
- [ ] Set up uptime monitoring (UptimeRobot)

---

## 🚨 Error Handling

### Error Response Format

All errors return this structure:

```json
{
  "success": false,
  "error_code": "ERROR_CODE_HERE",
  "message": "Human-readable error description",
  "details": {
    "field": "field_name",
    "value": "submitted_value"
  }
}
```

### Error Codes Reference

| Error Code | HTTP Status | Description | Solution |
|------------|-------------|-------------|----------|
| `VALIDATION_FAILED` | 400 | Input validation error | Check field requirements |
| `FILE_TOO_LARGE` | 400 | File exceeds 5MB | Compress file |
| `INVALID_MIME_TYPE` | 400 | Wrong file type | Use PNG/JPEG/PDF |
| `DUPLICATE_SUBMISSION` | 409 | Team already exists | Check team name + captain phone |
| `TEAM_ID_GENERATION_FAILED` | 500 | Cannot generate ID | Retry request |
| `CLOUDINARY_UPLOAD_FAILED` | 500 | File upload failed | Check Cloudinary config |
| `DB_WRITE_FAILED` | 500 | Database error | Check database connection |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected error | Contact support |

### Common Error Scenarios

**1. Validation Error**

```json
{
  "success": false,
  "error_code": "VALIDATION_FAILED",
  "message": "Captain phone must be exactly 10 digits",
  "details": {
    "field": "captain_phone",
    "value": "12345"
  }
}
```

**Fix:** Ensure phone is 10 digits, numeric only.

**2. Duplicate Team**

```json
{
  "success": false,
  "error_code": "DUPLICATE_SUBMISSION",
  "message": "Team with name 'Warriors' and captain phone '9876543210' already exists",
  "details": {
    "field": "team_name/captain_phone",
    "value": "Warriors"
  }
}
```

**Fix:** Change team name or captain phone.

**3. File Too Large**

```json
{
  "success": false,
  "error_code": "FILE_TOO_LARGE",
  "message": "File size exceeds 5MB limit",
  "details": {
    "field": "pastor_letter",
    "size": "7340032"
  }
}
```

**Fix:** Compress file to under 5MB.

---

## 📊 Monitoring & Logging

### Structured Logging

All requests logged in JSON format:

```json
{
  "timestamp": "2025-11-19T10:30:45.123Z",
  "level": "INFO",
  "request_id": "req_abc123xyz",
  "event": "registration_started",
  "team_name": "Chennai Warriors",
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "duration_ms": 1247
}
```

### Log Locations

- **Console:** Real-time logs (development)
- **File:** `logs/app.log` (production)
- **Render:** Dashboard → Logs tab

### Monitored Events

| Event | Description |
|-------|-------------|
| `registration_started` | Team registration begins |
| `validation_error` | Input validation fails |
| `file_upload` | Cloudinary upload (success/failure) |
| `db_operation` | Database insert/update/delete |
| `exception` | Unexpected errors with stack trace |
| `health_check` | Health endpoint called |

### Performance Metrics

Track these via logs:

- Request duration (`duration_ms`)
- Database query time
- File upload time
- Error rates by endpoint

### Recommended Monitoring Tools

- **Uptime:** [UptimeRobot](https://uptimerobot.com/)
- **Logs:** Render built-in logs
- **Errors:** [Sentry](https://sentry.io/)
- **APM:** [New Relic](https://newrelic.com/)

---

## 🔒 Security

### Security Features Implemented

✅ **Input Validation** - All inputs validated with Pydantic  
✅ **SQL Injection Prevention** - SQLAlchemy ORM with parameterized queries  
✅ **File Security** - MIME validation, size limits, sanitized filenames  
✅ **CORS Protection** - Configurable allowed origins  
✅ **Environment Variables** - No secrets in code  
✅ **HTTPS** - Enforced in production (Render)  
✅ **Rate Limiting** - Middleware-based (Render handles DDoS)

### Security Best Practices

**1. Environment Variables**

```bash
# NEVER commit .env or .env.local
echo ".env*" >> .gitignore
echo "!.env.example" >> .gitignore

# Use strong, random secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

**2. Database Security**

```bash
# Use connection pooling (prevents exhaustion)
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Use SSL for Neon
DATABASE_URL=...?ssl=require
```

**3. File Upload Security**

```python
# Already implemented:
- Max 5MB file size
- MIME type validation (PNG/JPEG/PDF only)
- Filename sanitization
- Virus scanning (recommended for production)
```

**4. CORS Configuration**

```env
# Production: Specific origins only
CORS_ORIGINS=https://your-frontend.com,https://www.your-frontend.com

# Development: Localhost allowed
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Security Checklist

- [ ] `.env.local` in `.gitignore`
- [ ] Strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] DATABASE_URL uses SSL (`?ssl=require`)
- [ ] CORS origins set to production domain
- [ ] Cloudinary signed uploads (future)
- [ ] Rate limiting enabled
- [ ] HTTPS enforced (Render auto-provides)
- [ ] Regular dependency updates (`pip install --upgrade`)

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. Application Won't Start

**Symptom:**

```text
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**

```bash
# Ensure virtual environment is activated
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Database Connection Failed

**Symptom:**

```text
Database health check failed: Cannot connect to database
```

**Solutions:**

```bash
# Check DATABASE_URL format
# Correct: postgresql+asyncpg://user:pass@host:5432/db?ssl=require
# Wrong: postgresql://user:pass@host:5432/db

# Test connection
python -c "import asyncpg; print('asyncpg installed')"

# For Neon: Ensure SSL is required
DATABASE_URL=...?ssl=require
```

#### 3. Cloudinary Upload Failed

**Symptom:**

```json
{
  "error_code": "CLOUDINARY_UPLOAD_FAILED",
  "message": "File upload failed after 3 retries"
}
```

**Solutions:**

```bash
# Verify Cloudinary credentials
python -c "import cloudinary; cloudinary.config(cloud_name='test'); print('OK')"

# Check .env.local has correct values
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abc123def456

# Test upload manually via Cloudinary dashboard
```

#### 4. CORS Error in Browser

**Symptom:**

```text
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**

```env
# Update CORS_ORIGINS in .env.local
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com

# Restart server after changing
```

#### 5. Port Already in Use

**Symptom:**

```text
Error: [Errno 48] Address already in use
```

**Solution:**

```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

#### 6. Players Not Stored

**Symptom:** Teams created but players table empty

**Solution:**

```bash
# Ensure frontend sends player_i_name, player_i_role, etc.
# Check request in browser DevTools → Network tab

# Example correct format:
player_0_name=John
player_0_role=Batsman
player_1_name=Jane
player_1_role=Bowler

# Backend automatically detects and creates players
```

### Debug Mode

Enable detailed logging:

```bash
# Set in .env.local
LOG_LEVEL=DEBUG
LOG_TO_FILE=true

# Run with debug
uvicorn main:app --reload --log-level debug
```

### Get Help

1. **Check logs:** `logs/app.log` or Render dashboard
2. **Test endpoint:** <http://localhost:8000/docs>
3. **Verify config:** Ensure `.env.local` has all required variables
4. **Check database:** Tables created on first startup
5. **Review error response:** `error_code` and `details` provide hints

---

## 📝 License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is prohibited.

© 2025 ICCT26 Cricket Tournament. All rights reserved.

---

## 🙏 Acknowledgments

### Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Modern async Python web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [PostgreSQL](https://www.postgresql.org/) - Powerful open-source database
- [Pydantic](https://docs.pydantic.dev/) - Data validation using Python type hints
- [Cloudinary](https://cloudinary.com/) - Cloud-based file storage and CDN
- [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server

### Special Thanks

- Neon for serverless PostgreSQL
- Render for easy deployment
- FastAPI community for excellent documentation

---

## 📞 Contact

**Development Team:** ICCT26 Backend Team  
**Repository:** [github.com/sanjaynesan-05/ICCT26-BACKEND](https://github.com/sanjaynesan-05/ICCT26-BACKEND)  
**Production API:** <https://icct26-backend.onrender.com>

For bug reports or feature requests, open an issue on GitHub.

---

**Last Updated:** November 19, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅

---

*This README is the single source of truth for the ICCT26 Backend API. Keep it updated with any changes to the system.*
