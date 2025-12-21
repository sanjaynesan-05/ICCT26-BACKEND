# 🗂️ ICCT26 Backend - Directory Structure

**Clean, Organized, Production-Ready**

---

## 📁 Root Directory

```
ICCT26 BACKEND/
├── .env.example              # Example environment variables
├── .env.local                # 🔒 SECURE - Your environment config
├── .gitignore                # Git ignore rules
├── .python-version           # Python version specification
├── database.py               # Database configuration
├── main.py                   # ⚡ FastAPI application entry point
├── models.py                 # SQLAlchemy database models
├── pyproject.toml            # Project configuration
├── README.md                 # Main project documentation
├── requirements.txt          # Python dependencies
├── run_server.bat            # 🚀 Quick server launcher
└── FRONTEND_UPDATE_PROMPT.md # Frontend integration guide
```

---

## 📂 Application Code (`app/`)

```
app/
├── __init__.py               # Package initialization
├── config.py                 # Application configuration
├── db_utils.py               # Database utilities
├── services.py               # Business logic services
├── schemas.py                # Pydantic schemas (general)
├── schemas_multipart.py      # Multipart form schemas
├── schemas_schedule.py       # Schedule schemas
├── schemas_team.py           # Team schemas
│
├── middleware/               # Request/response middleware
│   ├── logging_middleware.py
│   └── production_middleware.py
│
├── routes/                   # API endpoints
│   ├── __init__.py
│   ├── admin.py              # Admin operations
│   ├── gallery.py            # Photo gallery
│   ├── health.py             # Health checks
│   ├── registration_production.py  # Team registration
│   ├── schedule.py           # Match scheduling
│   └── team.py               # Team management
│
└── utils/                    # Utility functions
    ├── circuit_breaker.py    # Circuit breaker pattern
    ├── cloudinary_reliable.py # Cloudinary reliability
    ├── cloudinary_upload.py  # Cloud file uploads
    ├── database_hardening.py # Database security
    ├── db_retry.py           # Database retry logic
    ├── email_reliable.py     # Email reliability
    ├── error_handlers.py     # Error handling
    ├── error_responses.py    # Error responses
    ├── file_utils.py         # File operations
    ├── file_validation.py    # File validation
    ├── global_exception_handler.py
    ├── idempotency.py        # Idempotency key handling
    ├── race_safe_team_id.py  # Race-safe ID generation
    ├── structured_logging.py # Structured logging
    ├── team_id_generator.py  # Team ID generation
    └── validation.py         # Input validation
```

---

## 🧪 Tests (`tests/`)

**48 Tests - All Passing ✅**

```
tests/
├── __init__.py
├── conftest.py                      # Pytest configuration
├── test_admin_api.py                # Admin API tests
├── test_admin_endpoints.py          # Admin endpoint tests
├── test_db.py                       # Database tests
├── test_endpoints.py                # General endpoint tests
├── test_idempotency.py              # Idempotency tests
├── test_race_safe_id.py             # Race-safe ID tests
├── test_registration_integration.py # Registration flow tests
└── test_validation.py               # Validation tests
```

**Run tests:**
```bash
pytest tests/
```

---

## 📜 Scripts (`scripts/`)

**Database Setup & Management**

```
scripts/
├── README.md                 # Scripts documentation
├── setup_database.py         # Database initialization
├── setup_postgres.bat        # PostgreSQL setup (Windows)
├── setup_postgres.sh         # PostgreSQL setup (Linux/Mac)
└── __init__.py
```

---

## 📚 Documentation (`docs/`)

```
docs/
├── CLEANUP_SUMMARY.md
├── EMAIL_CONFIRMATION_FEATURE.md
├── FRONTEND_QUICK_START.md
├── MATCH_SCHEDULE_API.md
├── PROJECT_STRUCTURE.md
├── REGISTRATION_CONFIRMATION_FEATURE.md
│
├── api-reference/            # API documentation
│   ├── COMPLETE_API_ENDPOINTS.md
│   ├── QUICK_REFERENCE.md
│   └── README.md
│
├── deployment/               # Deployment guides
│   ├── DEPLOYMENT.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── POSTGRESQL_SETUP.md
│   ├── PRODUCTION_DEPLOYMENT_GUIDE.md
│   └── RUNS_WICKETS_FIX.md
│
├── frontend/                 # Frontend integration
│   ├── FRONTEND_INTEGRATION.md
│   ├── FRONTEND_QUICK_REFERENCE.md
│   ├── FRONTEND_READY.md
│   ├── FRONTEND_SUMMARY.txt
│   ├── INTEGRATION_CHECKLIST.md
│   └── INTEGRATION_DIAGRAM.md
│
├── guides/                   # Setup & security guides
│   ├── SECURITY.md
│   └── SETUP.md
│
├── security/                 # Security documentation
│   ├── CREDENTIALS_FIXED.md
│   ├── SECURITY_FIX_REPORT.md
│   └── SECURITY.md
│
└── setup/                    # Setup guides
    ├── 00_START_HERE.md
    ├── DOCUMENTATION_INDEX.md
    └── SETUP_GUIDE.md
```

---

## 📊 Logs (`logs/`)

Runtime application logs are stored here.

---

## 🐍 Virtual Environment

- `venv/` - Main Python virtual environment
- `.venv/` - Alternative virtual environment

**Activate:**
```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env.local` and add your credentials.

### 3. Setup Database
```bash
python scripts/setup_database.py
```

### 4. Run Server
```bash
# Option 1: Batch file
run_server.bat

# Option 2: Direct command
uvicorn main:app --reload --port 8000
```

### 5. Access API
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

---

## ✅ Production Ready

- ✅ **48/48 tests passing**
- ✅ **Clean database** (0 test data)
- ✅ **Organized code structure**
- ✅ **Complete documentation**
- ✅ **Cloud-first file storage**
- ✅ **Email confirmation system**
- ✅ **Security hardening**
- ✅ **Error handling**
- ✅ **Idempotency support**
- ✅ **Frontend integration guide**

---

## 📦 Key Technologies

- **Framework:** FastAPI
- **Database:** PostgreSQL (Neon)
- **Storage:** Cloudinary
- **Email:** Gmail SMTP
- **Testing:** Pytest
- **Validation:** Pydantic

---

## 🔐 Security Notes

- Keep `.env.local` secure (NEVER commit to Git)
- Use environment variables for all secrets
- Enable HTTPS in production
- Review `docs/guides/SECURITY.md`

---

**Last Updated:** December 21, 2025  
**Status:** ✅ Production Ready
