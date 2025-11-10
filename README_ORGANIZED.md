# 🏏 ICCT26 Cricket Tournament Registration API

Backend API for managing cricket tournament registration, team management, and player information for ICCT26.

## ⚡ Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL (Neon cloud database)
- Virtual environment

### 5-Minute Setup

```bash
# 1. Clone and enter directory
git clone <repo-url>
cd ICCT26_backend

# 2. Create and activate environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env.local
# Edit .env.local with your credentials

# 5. Initialize database
python scripts/migrate_to_neon.py

# 6. Run server
python -m uvicorn main:app --reload
```

**API running at:** http://localhost:8000/docs

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [docs/README.md](docs/README.md) | Documentation index |
| [docs/guides/SETUP.md](docs/guides/SETUP.md) | Detailed setup instructions |
| [docs/guides/SECURITY.md](docs/guides/SECURITY.md) | Security & credentials |
| [docs/deployment/DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md) | Production deployment |
| [API_DOCS.md](API_DOCS.md) | API endpoint reference |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Directory organization |

## 🗂️ Project Structure

```
ICCT26_backend/
├── main.py                 # Application entry point
├── database.py             # Database configuration
├── models.py              # Database models
│
├── app/                   # Application package
│   ├── config.py         # Settings
│   ├── schemas.py        # Pydantic models
│   ├── services.py       # Business logic
│   └── routes/           # API endpoints
│
├── docs/                 # Documentation
│   ├── guides/          # How-to guides
│   └── deployment/      # Deployment guides
│
├── tests/               # Test suite
│   ├── test_endpoints.py
│   └── test_db.py
│
├── scripts/             # Utility scripts
│   └── migrate_to_neon.py
│
└── requirements.txt     # Python dependencies
```

## 🔧 Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| FastAPI | 0.121.1 | Web framework |
| SQLAlchemy | 2.0.44 | ORM |
| Pydantic | 2.12.4 | Data validation |
| Uvicorn | 0.38.0 | ASGI server |
| PostgreSQL (Neon) | Latest | Database |
| asyncpg | 0.30.0 | Async PostgreSQL driver |
| psycopg2 | 2.9.11 | Sync PostgreSQL driver |

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root - info and status |
| GET | `/health` | Health check |
| GET | `/status` | Server status with DB info |
| GET | `/admin/teams` | List all teams |
| GET | `/docs` | Swagger API documentation |
| GET | `/redoc` | ReDoc API documentation |

Full documentation: [API_DOCS.md](API_DOCS.md) or http://localhost:8000/docs

## 🚀 Development

### Running the Server

```bash
# Activate environment
venv\Scripts\activate

# Run with auto-reload
python -m uvicorn main:app --reload

# Run on specific port
python -m uvicorn main:app --port 8001
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_endpoints.py::test_root_endpoint

# With coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black app/ main.py database.py

# Linting
flake8 app/ main.py database.py

# Type checking
mypy app/ main.py database.py
```

## 🔐 Security

⚠️ **IMPORTANT:** Never commit credentials to git!

- Store credentials in `.env.local` (gitignored)
- Use `.env.example` as template
- Review [docs/guides/SECURITY.md](docs/guides/SECURITY.md) for best practices

## 📦 Database

### Setup
```bash
python scripts/migrate_to_neon.py
```

### Schema
- **teams** table: Team information (16 columns)
- **players** table: Player information (12 columns)

### Connection
- Provider: Neon PostgreSQL
- Connection pooling: Optimized for serverless
- SSL: Required for security

## 🚢 Deployment

### Quick Deploy
1. Choose platform: [Render](https://render.com) or [Railway](https://railway.app)
2. Connect GitHub repository
3. Set environment variables
4. Deploy

Full guide: [docs/deployment/DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md)

### Environment Variables Required
```
DATABASE_URL              # PostgreSQL connection string
SMTP_USERNAME            # Gmail address for emails
SMTP_PASSWORD            # Gmail app-specific password
GOOGLE_DRIVE_FOLDER_ID   # Google Drive folder ID
SPREADSHEET_ID           # Google Sheets ID
```

## ✅ Verification

Test your setup:

```bash
# 1. Check endpoints
curl http://localhost:8000/health

# 2. Access API docs
# Open http://localhost:8000/docs in browser

# 3. Run test suite
pytest tests/

# 4. Check database
python scripts/migrate_to_neon.py
```

## 📱 Common Tasks

### Set up locally?
→ Follow [docs/guides/SETUP.md](docs/guides/SETUP.md)

### Deploy to production?
→ See [docs/deployment/DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md)

### Manage credentials safely?
→ Read [docs/guides/SECURITY.md](docs/guides/SECURITY.md)

### Understand endpoints?
→ Check [API_DOCS.md](API_DOCS.md) or http://localhost:8000/docs

### Report a bug?
→ Check existing issues or create new one

## 📞 Getting Help

1. **Setup issues?** Check [docs/guides/SETUP.md](docs/guides/SETUP.md) troubleshooting
2. **API questions?** Review [API_DOCS.md](API_DOCS.md) and http://localhost:8000/docs
3. **Security concerns?** See [docs/guides/SECURITY.md](docs/guides/SECURITY.md)
4. **Deployment help?** Follow [docs/deployment/DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md)
5. **Still stuck?** Check [docs/README.md](docs/README.md) for complete documentation index

## 🧪 Testing

### Automated Tests
```bash
# Run all tests
pytest tests/

# Test endpoints
python tests/test_endpoints.py

# Test database
python tests/test_db.py
```

### Manual Testing
```bash
# Test API locally
curl http://localhost:8000/health

# Use Swagger UI
open http://localhost:8000/docs
```

## 📝 Environment Files

| File | Purpose | Commit? |
|------|---------|---------|
| `.env.example` | Template with placeholders | ✅ YES |
| `.env.local` | Real credentials (local) | ❌ NO |
| `.env` | Environment variables (production) | ❌ NO |

**.gitignore** protects `.env.local` and `.env`

## 🔄 Workflow

### Development
```
1. Activate venv
2. Run server with --reload
3. Make code changes
4. Test via http://localhost:8000/docs
5. Run test suite: pytest tests/
6. Commit changes
```

### Deployment
```
1. Test locally (pytest)
2. Push to GitHub
3. Platform auto-deploys
4. Verify in production
5. Monitor logs
```

## 📚 Resources

### Internal Documentation
- [docs/](docs/) - All documentation
- [API_DOCS.md](API_DOCS.md) - API reference
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - File organization

### External Resources
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [Neon Docs](https://neon.tech/docs)
- [Pydantic Docs](https://docs.pydantic.dev)

## 🐛 Known Issues

None currently. See GitHub Issues for details.

## 📋 Checklist for New Developers

- [ ] Clone repository
- [ ] Follow [SETUP.md](docs/guides/SETUP.md)
- [ ] Read [SECURITY.md](docs/guides/SECURITY.md)
- [ ] Review [API_DOCS.md](API_DOCS.md)
- [ ] Run `pytest tests/` successfully
- [ ] Access http://localhost:8000/docs
- [ ] Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [ ] Understand codebase in `app/`

## 📄 License

[Your License Here]

## 👥 Team

- Development Team

## 🎯 Status

- ✅ Database: Connected (Neon PostgreSQL)
- ✅ API: Running (FastAPI + Uvicorn)
- ✅ Tests: Passing (5/5 endpoints)
- ✅ Security: Credentials secured (environment variables)
- ✅ Documentation: Complete

---

**Last Updated:** 2024  
**Maintained By:** Development Team  
**Questions?** See [docs/README.md](docs/README.md)
