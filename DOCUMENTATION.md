# ICCT26 Cricket Tournament - Backend API

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** November 7, 2025

---

## 📚 Documentation

All documentation has been organized in the `docs/` folder for easy navigation.

### Quick Links

- **📖 [Full Documentation Index](./docs/INDEX.md)** - Start here!
- **🚀 [Quick Start Guide](./docs/setup/00_START_HERE.md)** - Get up and running
- **⚙️ [Setup Guide](./docs/setup/SETUP_GUIDE.md)** - Installation and configuration
- **🔌 [Admin Panel Docs](./docs/admin-panel/)** - New admin endpoints
- **🎨 [Frontend Integration](./docs/frontend/)** - Integrate with React/Vue
- **🚀 [Deployment Guide](./docs/deployment/)** - Deploy to production
- **🔒 [Security Guide](./docs/security/)** - Security best practices

---

## 📁 Documentation Structure

```
docs/
├── admin-panel/          # Admin Panel API endpoints (8 files)
├── api-reference/        # API documentation (2 files)
├── deployment/           # Deployment guides (4 files)
├── frontend/             # Frontend integration (6 files)
├── security/             # Security guidelines (3 files)
├── setup/                # Setup and installation (3 files)
└── INDEX.md              # Main documentation index
```

---

## 🎯 Getting Started

### For New Developers

1. Read: [docs/setup/00_START_HERE.md](./docs/setup/00_START_HERE.md)
2. Follow: [docs/setup/SETUP_GUIDE.md](./docs/setup/SETUP_GUIDE.md)
3. Review: [docs/api-reference/README.md](./docs/api-reference/README.md)

### For Admin Panel Development

1. Start: [docs/admin-panel/README_ADMIN_PANEL.md](./docs/admin-panel/README_ADMIN_PANEL.md)
2. Reference: [docs/admin-panel/ADMIN_PANEL_ENDPOINTS.md](./docs/admin-panel/ADMIN_PANEL_ENDPOINTS.md)
3. Test: [docs/admin-panel/ADMIN_TESTING_GUIDE.md](./docs/admin-panel/ADMIN_TESTING_GUIDE.md)

### For Frontend Integration

1. Read: [docs/frontend/FRONTEND_INTEGRATION.md](./docs/frontend/FRONTEND_INTEGRATION.md)
2. Checklist: [docs/frontend/INTEGRATION_CHECKLIST.md](./docs/frontend/INTEGRATION_CHECKLIST.md)
3. Reference: [docs/frontend/FRONTEND_QUICK_REFERENCE.md](./docs/frontend/FRONTEND_QUICK_REFERENCE.md)

### For Deployment

1. Review: [docs/deployment/DEPLOYMENT_CHECKLIST.md](./docs/deployment/DEPLOYMENT_CHECKLIST.md)
2. Guide: [docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md](./docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)

---

## 🚀 Quick Start

### Install Dependencies

```bash
cd d:\ICCT26 BACKEND
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Start the Server

```bash
uvicorn main:app --reload --port 8000
```

### Access Documentation

- **Interactive API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## ✨ Features

✅ **Team Registration** - Complete team registration system  
✅ **Player Management** - Manage team rosters  
✅ **Admin Panel** - 3 new endpoints for team/player management  
✅ **Frontend Integration** - React and Vue.js examples  
✅ **Security** - Best practices implemented  
✅ **Deployment Ready** - Deploy to Render, Heroku, or AWS  

---

## 🔌 API Endpoints

### Registration Endpoints

- **POST** `/register/team` - Register a new team
- **GET** `/teams` - Get all teams
- **GET** `/health` - Health check
- **GET** `/status` - API status
- **GET** `/queue/status` - Queue status

### Admin Panel Endpoints (NEW)

- **GET** `/admin/teams` - List all teams
- **GET** `/admin/teams/{teamId}` - Get team details
- **GET** `/admin/players/{playerId}` - Get player details

---

## 📊 Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| Backend API | ✅ Complete | All endpoints working |
| Database | ✅ Connected | PostgreSQL configured |
| Admin Panel | ✅ Complete | 3 endpoints implemented |
| Frontend Integration | ✅ Ready | React/Vue examples |
| Security | ✅ Implemented | Best practices applied |
| Deployment | ✅ Ready | Guides provided |
| Documentation | ✅ Complete | 26 files organized |

---

## 🔐 Environment Setup

Create `.env.local` file (for local development):

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/icct26_db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
PORT=8000
```

For production, see: [docs/deployment/RENDER_SETUP_SUMMARY.md](./docs/deployment/RENDER_SETUP_SUMMARY.md)

---

## 📞 Support

For detailed information:

- **Setup issues?** → [docs/setup/SETUP_GUIDE.md](./docs/setup/SETUP_GUIDE.md)
- **API questions?** → [docs/api-reference/README.md](./docs/api-reference/README.md)
- **Integration help?** → [docs/frontend/FRONTEND_INTEGRATION.md](./docs/frontend/FRONTEND_INTEGRATION.md)
- **Deployment?** → [docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md](./docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)
- **Security?** → [docs/security/SECURITY.md](./docs/security/SECURITY.md)

---

## 🎓 Technology Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL 17
- **Driver:** asyncpg (async)
- **ORM:** SQLAlchemy 2.0+
- **Validation:** Pydantic v2
- **Server:** Uvicorn
- **Language:** Python 3.10+

---

## 📝 Documentation

All documentation is organized in the `docs/` folder:

| Folder | Files | Purpose |
|--------|-------|---------|
| **admin-panel** | 8 | Admin Panel API (new endpoints) |
| **api-reference** | 2 | General API documentation |
| **deployment** | 4 | Production deployment |
| **frontend** | 6 | Frontend integration |
| **security** | 3 | Security guidelines |
| **setup** | 3 | Setup and installation |

**View the complete index:** [docs/INDEX.md](./docs/INDEX.md)

---

## ✅ What's New (November 7, 2025)

✨ **Admin Panel Endpoints** - Three powerful endpoints for team/player management  
✨ **Comprehensive Documentation** - 26 organized documentation files  
✨ **Testing Suite** - Complete test coverage for all endpoints  
✨ **Integration Examples** - React and Vue.js code examples  
✨ **Deployment Guides** - Ready for production deployment  

---

## 🚀 Next Steps

1. **Read the documentation** - Start with [docs/INDEX.md](./docs/INDEX.md)
2. **Set up the environment** - Follow [docs/setup/SETUP_GUIDE.md](./docs/setup/SETUP_GUIDE.md)
3. **Start the server** - Run `uvicorn main:app --reload --port 8000`
4. **Integrate with frontend** - See [docs/frontend/FRONTEND_INTEGRATION.md](./docs/frontend/FRONTEND_INTEGRATION.md)
5. **Deploy to production** - Follow [docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md](./docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)

---

## 📄 Project Information

- **Repository:** ICCT26-BACKEND
- **Owner:** sanjaynesan-05
- **Branch:** main
- **Status:** ✅ Production Ready
- **Version:** 1.0.0
- **Last Updated:** November 7, 2025

---

**For complete documentation, see: [docs/INDEX.md](./docs/INDEX.md)**
