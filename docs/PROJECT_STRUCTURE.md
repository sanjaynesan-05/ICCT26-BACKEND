# ICCT26 Backend - Project Structure

**Last Updated:** November 29, 2025  
**Status:** Production Ready ✅

---

## 📁 Directory Structure

```
ICCT26 BACKEND/
├── app/                              # FastAPI Application
│   ├── __init__.py
│   ├── config.py                    # App configuration
│   ├── db_utils.py                  # Database utilities
│   ├── schemas.py                   # Core schemas (Team, Player)
│   ├── schemas_multipart.py         # Multipart file upload schemas
│   ├── schemas_team.py              # Team management schemas
│   ├── services.py                  # Business logic services
│   ├── middleware/                  # Middleware components
│   │   ├── logging_middleware.py    # Request/response logging
│   │   └── production_middleware.py # Production hardening
│   ├── routes/                      # API route handlers
│   │   ├── admin.py                 # Admin endpoints
│   │   ├── health.py                # Health check endpoints
│   │   ├── registration_production.py # Player registration
│   │   └── team.py                  # Team management endpoints
│   └── utils/                       # Utility functions
│       ├── circuit_breaker.py       # Circuit breaker pattern
│       ├── cloudinary_reliable.py   # Cloudinary wrapper
│       ├── cloudinary_upload.py     # File upload handler
│       ├── database_hardening.py    # DB security measures
│       ├── db_retry.py              # Database retry logic
│       ├── email_reliable.py        # Email service wrapper
│       ├── error_handlers.py        # Global error handling
│       ├── error_responses.py       # Error response formats
│       ├── file_utils.py            # File utilities
│       ├── file_validation.py       # File validation rules
│       ├── global_exception_handler.py # Exception handling
│       ├── idempotency.py           # Idempotency keys
│       ├── race_safe_team_id.py     # Race condition prevention
│       ├── structured_logging.py    # Structured logging
│       ├── team_id_generator.py     # Team ID generation
│       └── validation.py            # Input validation
│
├── docs/                            # Documentation
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── MATCH_SCHEDULE_API.md        # Match schedule API reference
│   ├── api-reference/               # API documentation
│   │   ├── COMPLETE_API_ENDPOINTS.md
│   │   ├── QUICK_REFERENCE.md
│   │   └── README.md
│   ├── deployment/                  # Deployment guides
│   │   ├── DEPLOYMENT.md
│   │   ├── POSTGRESQL_SETUP.md
│   │   ├── PRODUCTION_DEPLOYMENT_GUIDE.md
│   │   └── RUNS_WICKETS_FIX.md
│   ├── frontend/                    # Frontend integration docs
│   ├── guides/                      # Additional guides
│   ├── security/                    # Security documentation
│   └── setup/                       # Setup instructions
│
├── scripts/                         # Database setup scripts
│   ├── setup_database.py            # Database initialization
│   ├── setup_postgres.bat           # Windows PostgreSQL setup
│   ├── setup_postgres.sh            # Unix PostgreSQL setup
│   ├── create_matches_table.py      # Create matches table
│   ├── migrate_match_details.py     # Match details migration
│   └── README.md                    # Scripts documentation
│
├── tests/                           # Unit & Integration Tests
│   ├── conftest.py                  # Test fixtures
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
├── testing/                         # Testing utilities
│   └── README.md
│
├── logs/                            # Application logs
│
├── venv/                            # Python virtual environment
│
├── main.py                          # FastAPI application entry point
├── models.py                        # SQLAlchemy ORM models
├── database.py                      # Database connection setup
├── config.py                        # Configuration management
├── cloudinary_config.py             # Cloudinary configuration
│
├── README.md                        # Main project documentation
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project metadata
│
├── run_server.bat                   # Windows server startup script
├── run_test.bat                     # Windows test script
│
├── .env                             # Environment variables (not in git)
├── .env.example                     # Example environment variables
├── .env.local                       # Local environment overrides
├── .gitignore                       # Git ignore rules
├── .python-version                  # Python version specification
│
└── .git/                            # Git repository metadata
```

---

## 🔧 Core Components

### Main Application (`main.py`)
- FastAPI application initialization
- CORS configuration
- Middleware setup (logging, production hardening)
- Health check endpoint
- Exception handlers

### Database (`database.py`)
- Dual engine setup (sync + async)
- PostgreSQL connection pooling
- Session management

### ORM Models (`models.py`)
- **Team**: Tournament team information
- **Player**: Player registration data
- **Match**: Cricket match details with 4-stage workflow

### API Routes
| Module | Purpose |
|--------|---------|
| `registration_production.py` | Player registration & profile management |
| `team.py` | Team management & operations |
| `admin.py` | Administrative functions |
| `health.py` | System health checks |

---

## 📊 Match Management System

### 4-Stage Workflow
```
1. CREATE MATCH        → Status: scheduled
2. START MATCH         → Status: live (toss info recorded)
3. RECORD INNINGS      → Status: live (scores recorded)
4. FINISH MATCH        → Status: done (result determined)
```

### Match Fields (in `models.Match`)
- **Basic Info**: id, round, round_number, match_number
- **Teams**: team1, team2 (team names)
- **Toss Info**: toss_winner, toss_choice
- **Timing**: scheduled_start_time, actual_start_time, match_end_time
- **Scores** (Separated runs & wickets):
  - `team1_first_innings_runs` (Integer)
  - `team1_first_innings_wickets` (Integer: 0-10)
  - `team2_first_innings_runs` (Integer)
  - `team2_first_innings_wickets` (Integer: 0-10)
- **Result**: winner, margin, margin_type, won_by_batting_first
- **URL**: match_score_url (external scorecard)

---

## 🔑 Key Features

✅ **Player Registration**
- Team assignment
- File uploads (documents, photos)
- Email verification via Brevo
- Cloudinary file storage

✅ **Team Management**
- Team creation and player assignment
- Player roster management
- Team information updates

✅ **Match Scheduling**
- Complete 4-stage match workflow
- Runs and wickets tracking (separate fields)
- Match result recording
- Toss information management

✅ **Production Hardening**
- Circuit breaker pattern for external services
- Database retry logic with exponential backoff
- Idempotency key support
- Race condition prevention
- Structured logging
- Request/response logging middleware
- Global exception handling

✅ **File Management**
- Cloudinary integration
- File validation
- Multipart form handling
- Base64 encoding/decoding

---

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- PostgreSQL (local or Neon)
- Cloudinary account
- Brevo email service account

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database
python scripts/setup_database.py

# Run server
python main.py
# or
./run_server.bat
```

### Environment Setup
Copy `.env.example` to `.env` and fill in:
```
DATABASE_URL=postgresql://user:password@localhost/icct26
CLOUDINARY_CLOUD_NAME=xxxxx
CLOUDINARY_API_KEY=xxxxx
CLOUDINARY_API_SECRET=xxxxx
BREVO_API_KEY=xxxxx
```

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| `README.md` | Main project overview |
| `MATCH_SCHEDULE_API.md` | Match schedule API guide |
| `docs/api-reference/` | Complete API documentation |
| `docs/deployment/` | Deployment & setup guides |
| `docs/frontend/` | Frontend integration guides |
| `docs/security/` | Security documentation |

---

## ✅ Production Checklist

- [x] Database migrations applied
- [x] ORM models updated
- [x] API schemas validated
- [x] All endpoints functional
- [x] Error handling implemented
- [x] Logging configured
- [x] Documentation complete
- [x] File structure organized
- [ ] Frontend integration (in progress)
- [ ] Deployment to production

---

## 📝 Recent Changes

**November 29, 2025:**
- ✅ Separated runs and wickets into distinct fields
- ✅ Updated Match ORM model
- ✅ Updated API schemas
- ✅ Updated all route handlers
- ✅ Migrated existing data
- ✅ Verified all endpoints
- ✅ Cleaned up file structure
- ✅ Organized documentation

---

## 🔗 Related Files

- **Models**: `models.py` (Match, Team, Player)
- **Routes**: `app/routes/` (API endpoints)
- **Schemas**: `app/schemas*.py` (Request/response validation)
- **Database**: `database.py` (Connection & session management)
- **Config**: `config.py`, `app/config.py` (Settings)
