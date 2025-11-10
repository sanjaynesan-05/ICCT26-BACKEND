# 🚀 Backend Quick Start Guide

## Prerequisites
- Python 3.13.9 installed
- PostgreSQL running with database `icct26_db`
- Environment variables set in `.env` file

## ✅ Verified Working

This backend has been **tested and verified working** with:
- ✅ Virtual environment activated
- ✅ All dependencies installed
- ✅ Database connected and tables initialized
- ✅ All endpoints responding correctly
- ✅ 4 teams loaded from database

## 🎯 Quick Start

### Step 1: Activate Virtual Environment
```powershell
cd 'd:\ICCT26 BACKEND'
.\venv\Scripts\Activate.ps1
```

### Step 2: Start the Backend Server
```bash
# Option 1: Using main.py directly
python main.py

# Option 2: Using uvicorn
uvicorn main:app --host 127.0.0.1 --port 8000

# Option 3: Production mode (no reload)
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Step 3: Access the API
- **API Root:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 📊 API Endpoints

### Health & Status
```
GET /              → Root endpoint
GET /health        → Health check
GET /status        → API status
```

### Admin Endpoints
```
GET /admin/teams           → List all teams
GET /admin/teams/{id}      → Get team details
GET /admin/players/{id}    → Get player details
```

### Registration
```
POST /register/team        → Register a new team
```

## 📁 Project Structure

```
main.py                    ← Main entry point (308 lines)
database.py                ← Database config (100 lines)
models.py                  ← ORM models
requirements.txt           ← Dependencies
pyproject.toml             ← Project config
.env                       ← Environment variables

app/                       ← Application package
├── __init__.py
├── config.py              ← Settings (153 lines)
├── schemas.py             ← Pydantic models (304 lines)
├── services.py            ← Business logic (473 lines)
└── routes/                ← API endpoints
    ├── __init__.py
    ├── health.py          ← Health endpoints (58 lines)
    ├── registration.py    ← Registration (278 lines)
    └── admin.py           ← Admin endpoints (68 lines)
```

## 🔧 Configuration

### Database
- **Type:** PostgreSQL
- **Host:** localhost
- **Port:** 5432
- **Database:** icct26_db
- **User:** postgres
- **Password:** icctpg (from .env)

### Email Service
- **SMTP Server:** Configured via .env
- **SMTP Port:** Configured via .env
- **Email Service:** Integrated via aiosmtplib

## 📝 Environment Variables

Required in `.env`:
```
DATABASE_URL=postgresql://postgres:icctpg@localhost:5432/icct26_db
SMTP_SERVER=your-smtp-server
SMTP_PORT=587
SENDER_EMAIL=your-email@domain.com
SENDER_PASSWORD=your-password
```

## ✅ Server Status Indicators

When the server starts, you should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✅ Database tables initialized (async)
✅ Database tables initialized (sync)
INFO:     Application startup complete.
```

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Kill process on port 8000
taskkill /PID <pid> /F

# Or use a different port
uvicorn main:app --host 127.0.0.1 --port 8001
```

### Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Confirm database `icct26_db` exists

### Module Import Error
```powershell
# Reinstall dependencies
python -m pip install -r requirements.txt --upgrade
```

## 📚 Testing

### Quick API Test
```powershell
# Test health endpoint
Invoke-WebRequest -Uri "http://localhost:8000/health" | Select-Object -ExpandProperty Content

# Test admin teams
Invoke-WebRequest -Uri "http://localhost:8000/admin/teams" | Select-Object -ExpandProperty Content
```

## 🎓 Development Tips

- **Reload Mode:** Add `--reload` to uvicorn command during development
- **Debug Mode:** Check app/config.py for DEBUG setting
- **Logs:** Monitor console output for INFO/ERROR messages
- **API Docs:** Use Swagger UI at /docs to test endpoints interactively

## 📞 Support

For issues or errors:
1. Check the console output for error messages
2. Review logs in the terminal
3. Verify database connection
4. Check environment variables in .env

---

**Backend Last Tested:** November 10, 2025  
**Status:** ✅ **Fully Operational**  
**Team Records:** 4 teams in database  
**Database:** PostgreSQL connected
