# 📋 Setup Guide

Step-by-step guide to set up the ICCT26 Cricket Tournament Registration API locally.

## Prerequisites

- Python 3.13 or higher
- PostgreSQL client (optional, for local testing)
- Git
- Virtual environment tool (venv - included with Python)
- Text editor or IDE

## Installation Steps

### 1. Clone Repository

```bash
cd /path/to/projects
git clone https://github.com/yourusername/ICCT26_backend.git
cd ICCT26_backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy template
cp .env.example .env.local

# Edit with your credentials
# Open .env.local and fill in real values
```

**Required values:**

| Variable | Where to Get |
|----------|-------------|
| `DATABASE_URL` | Neon Dashboard → Connection String |
| `SMTP_USERNAME` | Your Gmail address |
| `SMTP_PASSWORD` | Gmail App Passwords (not your regular password) |
| `GOOGLE_DRIVE_FOLDER_ID` | Google Drive folder ID |
| `SPREADSHEET_ID` | Google Sheets ID |

### 5. Initialize Database

```bash
# Run migration
python scripts/migrate_to_neon.py

# You should see:
# ✅ Database tables initialized
# ✅ Teams table created
# ✅ Players table created
```

### 6. Verify Installation

```bash
# Test imports
python -c "import fastapi; import sqlalchemy; print('All imports OK')"

# Should print: All imports OK
```

## Running the Server

### Development Mode

```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows

# Start server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Output should show:**
```
Uvicorn running on http://0.0.0.0:8000
✅ Database tables initialized (async)
✅ Database tables initialized (sync)
Application startup complete
```

### Testing the API

In a new terminal:

```bash
# Test root endpoint
curl http://localhost:8000

# Test health
curl http://localhost:8000/health

# View API docs
# Open http://localhost:8000/docs in browser
```

## Project Structure

```
ICCT26_backend/
├── main.py                 # Entry point
├── database.py             # Database config
├── models.py              # Database models
├── requirements.txt       # Dependencies
├── .env.example          # Template (commit)
├── .env.local            # Real credentials (gitignored)
│
├── app/
│   ├── __init__.py
│   ├── config.py         # Settings
│   ├── schemas.py        # Pydantic models
│   ├── services.py       # Business logic
│   └── routes/           # API endpoints
│       ├── __init__.py
│       ├── registration.py
│       └── admin.py
│
├── docs/
│   ├── guides/           # Documentation
│   │   ├── SECURITY.md
│   │   └── SETUP.md (this file)
│   └── deployment/
│       └── DEPLOYMENT.md
│
├── tests/                # Test files
│   ├── test_endpoints.py
│   └── test_db.py
│
└── scripts/              # Utility scripts
    └── migrate_to_neon.py
```

## Common Setup Issues

### Issue: Virtual Environment Not Activating

**Solution:**
```bash
# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate

# Windows CMD
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate
```

### Issue: Dependencies Won't Install

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements again
pip install -r requirements.txt

# If still fails, check Python version
python --version  # Should be 3.13+
```

### Issue: Database Connection Error

**Solution:**
1. Verify DATABASE_URL in .env.local
2. Check Neon project is active
3. Verify internet connection
4. Try connecting directly:
   ```bash
   psql "your-connection-string"
   ```

### Issue: SSL Error Connecting to Database

**Solution:**
- Verify DATABASE_URL includes `ssl=require` or `sslmode=require`
- Neon requires SSL, don't disable it

### Issue: Port 8000 Already in Use

**Solution:**
```bash
# Use different port
python -m uvicorn main:app --port 8001

# Or kill process on port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

## Development Workflow

### Daily Development

1. **Activate virtual environment:**
   ```bash
   venv\Scripts\activate
   ```

2. **Start server:**
   ```bash
   python -m uvicorn main:app --reload
   ```

3. **Make changes** to code

4. **Reload automatically** (with --reload flag)

5. **Test changes:**
   ```bash
   curl http://localhost:8000/endpoint
   ```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_endpoints.py::test_health

# Run with coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black app/ main.py database.py

# Check style
flake8 app/ main.py database.py

# Type checking
mypy app/ main.py database.py
```

## IDE Setup

### VS Code

1. **Install Extensions:**
   - Python
   - Pylance
   - FastAPI
   - Thunder Client (for API testing)

2. **Configure settings:**
   - File → Preferences → Settings
   - Search: "Python: Default Interpreter Path"
   - Set to: `.venv/bin/python` (macOS/Linux) or `venv\Scripts\python.exe` (Windows)

3. **Run in VS Code:**
   - Terminal → New Terminal
   - Run: `python -m uvicorn main:app --reload`

### PyCharm

1. **Configure interpreter:**
   - File → Settings → Project → Python Interpreter
   - Add interpreter from `venv/bin/python`

2. **Run configuration:**
   - Add configuration → Python
   - Script path: main.py
   - Parameters: --reload

## Useful Commands

```bash
# Activate environment
venv\Scripts\activate

# Check Python version
python --version

# List installed packages
pip list

# Freeze dependencies
pip freeze > requirements.txt

# Install in development mode
pip install -e .

# Run server
python -m uvicorn main:app --reload

# Run tests
pytest tests/

# Deactivate environment
deactivate
```

## Next Steps

1. ✅ Installation complete
2. ⬜ Review docs/guides/SECURITY.md for credential management
3. ⬜ Read API_DOCS.md for API endpoint documentation
4. ⬜ Check docs/deployment/DEPLOYMENT.md for production setup
5. ⬜ Start development!

## Getting Help

- Check specific documentation: `docs/guides/` and `docs/deployment/`
- Review API documentation: `API_DOCS.md` and `http://localhost:8000/docs`
- Check code comments in `app/` directory
- See GitHub Issues for common problems

## Troubleshooting Commands

```bash
# Verify database connection
python -c "from app.config import settings; print(settings.database_url)"

# Test asyncpg connection
python -c "import asyncio; from database import async_engine; asyncio.run(async_engine.connect())"

# Check installed packages
pip show fastapi uvicorn sqlalchemy

# Update all packages
pip install --upgrade -r requirements.txt
```

---

**Need Help?** Check the docs/ folder for more guides.
