# 📁 ICCT26 Backend Project Structure

## Directory Organization

```
ICCT26_BACKEND/
├── 📄 Main Application Files
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLAlchemy ORM models
│   ├── requirements.txt         # Python dependencies
│   ├── pyproject.toml          # Project metadata
│   └── .env.example            # Environment template (safe to commit)
│
├── 📁 app/                     # Application package
│   ├── __init__.py
│   ├── config.py               # Configuration settings
│   ├── schemas.py              # Pydantic models
│   ├── services.py             # Business logic
│   └── routes/                 # API route handlers
│       ├── health.py           # Health check endpoints
│       ├── registration.py     # Team registration
│       └── admin.py            # Admin operations
│
├── 📁 docs/                    # 📚 Documentation
│   ├── README.md               # Project overview
│   ├── QUICK_START.md          # Getting started guide
│   ├── API.md                  # API documentation
│   │
│   ├── 📁 guides/              # Setup & configuration guides
│   │   ├── SECURITY.md         # Security & credentials best practices
│   │   ├── SETUP.md            # Development environment setup
│   │   └── TROUBLESHOOTING.md  # Common issues & solutions
│   │
│   └── 📁 deployment/          # Deployment & migration docs
│       ├── NEON_MIGRATION.md   # Neon PostgreSQL migration
│       ├── DEPLOYMENT.md       # Deployment instructions
│       └── INFRASTRUCTURE.md   # Infrastructure setup
│
├── 📁 tests/                   # 🧪 Test files
│   ├── __init__.py
│   ├── test_endpoints.py       # Endpoint tests
│   └── test_neon_db.py         # Database connection tests
│
├── 📁 scripts/                 # 🔧 Utility scripts
│   ├── migrate_to_neon.py      # Database migration script
│   ├── test_endpoints.py       # Endpoint testing script
│   └── README.md               # Scripts documentation
│
├── 📁 venv/                    # Virtual environment (gitignored)
│
├── 🔒 .env.local               # Local credentials (gitignored)
├── .env.example                # Template (safe to commit)
├── .gitignore                  # Git ignore rules
├── API_DOCS.md                 # Root API documentation
└── README.md                   # Main project README

```

---

## Documentation Organization

### Root Level (Main Entry Points)
- **README.md** - Project overview and quick start
- **API_DOCS.md** - Main API documentation
- **.env.example** - Environment configuration template

### docs/ Directory (Detailed Documentation)

#### Main Documentation
- **docs/README.md** - Documentation index
- **docs/QUICK_START.md** - 5-minute quick start guide
- **docs/API.md** - Detailed API endpoints reference

#### docs/guides/ (How-to Guides)
- **docs/guides/SECURITY.md** - Security best practices & credentials management
- **docs/guides/SETUP.md** - Development environment setup
- **docs/guides/TROUBLESHOOTING.md** - Common issues & solutions

#### docs/deployment/ (Production & Infrastructure)
- **docs/deployment/NEON_MIGRATION.md** - Neon PostgreSQL setup & migration
- **docs/deployment/DEPLOYMENT.md** - Deployment to production (Render, Railway, Docker)
- **docs/deployment/INFRASTRUCTURE.md** - Infrastructure architecture & scaling

---

## Tests Organization

### tests/ Directory
```
tests/
├── __init__.py                 # Makes tests a package
├── test_endpoints.py           # Endpoint unit & integration tests
├── test_neon_db.py            # Database connection tests
└── conftest.py                 # Pytest configuration (optional)
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_endpoints.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app
```

---

## Scripts Organization

### scripts/ Directory
```
scripts/
├── README.md                   # Scripts documentation
├── migrate_to_neon.py         # Database migration to Neon
└── test_endpoints.py          # Manual endpoint testing
```

### Running Scripts
```bash
# Migrate database to Neon
python scripts/migrate_to_neon.py

# Test endpoints
python scripts/test_endpoints.py
```

---

## File Categories

### 🔴 DO NOT COMMIT (in .gitignore)
```
.env.local           # Local credentials
.env.prod            # Production credentials
venv/                # Virtual environment
__pycache__/         # Python cache
*.pyc                # Compiled Python
.pytest_cache/       # Test cache
*.log                # Log files
```

### ✅ SAFE TO COMMIT
```
README.md            # Documentation
.env.example         # Template
.gitignore           # Rules
app/                 # Source code
docs/                # Documentation
tests/               # Tests
scripts/             # Scripts
requirements.txt     # Dependencies
*.py                 # Python files
```

---

## Workflow

### Development
```bash
# 1. Setup
cp .env.example .env.local
# Edit .env.local with credentials

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python -m uvicorn main:app --reload

# 4. Test
pytest tests/

# 5. Document changes
# Edit relevant docs/guides/ file
```

### Before Committing
```bash
# 1. Check no secrets exposed
grep -r "npg_" --include="*.py" .
grep -r "password" --include="*.py" . | grep -v "SMTP_PASSWORD"

# 2. Run tests
pytest tests/

# 3. Verify .env.local not included
git status | grep .env.local

# 4. Commit
git add .
git commit -m "meaningful message"
git push
```

### Deployment
```bash
# 1. Read deployment docs
# docs/deployment/DEPLOYMENT.md

# 2. Review infrastructure
# docs/deployment/INFRASTRUCTURE.md

# 3. Set environment variables
# On your hosting platform (Render, Railway, etc)

# 4. Deploy
# Follow platform-specific instructions
```

---

## Documentation Quick Reference

| Need | File | Location |
|------|------|----------|
| Quick start | QUICK_START.md | docs/ |
| API endpoints | API.md | docs/ |
| Setup help | SETUP.md | docs/guides/ |
| Security/Credentials | SECURITY.md | docs/guides/ |
| Troubleshooting | TROUBLESHOOTING.md | docs/guides/ |
| Neon setup | NEON_MIGRATION.md | docs/deployment/ |
| Deploy to production | DEPLOYMENT.md | docs/deployment/ |
| Infrastructure | INFRASTRUCTURE.md | docs/deployment/ |
| Running tests | README.md | tests/ |
| Running scripts | README.md | scripts/ |

---

## Benefits of This Structure

✅ **Clear Organization** - Everything has its place  
✅ **Easy Navigation** - Developers know where to look  
✅ **Scalable** - Easy to add new docs/tests/scripts  
✅ **Professional** - Industry-standard structure  
✅ **Secure** - Credentials properly separated  
✅ **Maintainable** - Updates are localized  

---

## Next Steps

1. Review this structure
2. Move documentation files to appropriate folders
3. Move test files to tests/ folder
4. Move utility scripts to scripts/ folder
5. Update any import paths
6. Create missing documentation files
7. Commit all changes

---

**Status:** 📁 Clean, organized, and production-ready!
