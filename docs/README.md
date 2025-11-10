# 📚 Documentation Index

Complete guide to all documentation for the ICCT26 Cricket Tournament Registration API.

## Quick Navigation

### 🚀 Getting Started
- **[SETUP.md](guides/SETUP.md)** - Installation and local development setup
  - Prerequisites and step-by-step installation
  - Virtual environment configuration
  - Database initialization
  - Running the server locally
  - IDE configuration (VS Code, PyCharm)
  - Troubleshooting common issues

### 🔐 Security
- **[SECURITY.md](guides/SECURITY.md)** - Credential management and security best practices
  - Environment file management (.env, .env.local, .env.example)
  - Credentials setup guide
  - Best practices for credentials
  - Incident response procedures
  - Pre-commit security checks
  - Production deployment security checklist

### 🌐 Deployment
- **[DEPLOYMENT.md](deployment/DEPLOYMENT.md)** - Production deployment guide
  - Database setup (Neon PostgreSQL)
  - Multiple deployment options (Render, Railway, Docker)
  - Pre-deployment checklist
  - Environment configuration
  - Post-deployment verification
  - Monitoring and maintenance
  - Rollback procedures
  - Common issues and solutions

## Documentation by Category

### Setup & Configuration
| Document | Purpose | Audience |
|----------|---------|----------|
| [SETUP.md](guides/SETUP.md) | Local development setup | Developers |
| [guides/SECURITY.md](guides/SECURITY.md) | Credentials management | All team members |

### Deployment
| Document | Purpose | Audience |
|----------|---------|----------|
| [DEPLOYMENT.md](deployment/DEPLOYMENT.md) | Production deployment | DevOps / Leads |

### API Documentation
| Document | Location | Purpose |
|----------|----------|---------|
| API_DOCS.md | Root directory | Complete API reference |
| Swagger UI | http://localhost:8000/docs | Interactive API docs |

### Project Documentation
| Document | Location | Purpose |
|----------|----------|---------|
| README.md | Root directory | Project overview |
| PROJECT_STRUCTURE.md | Root directory | Directory organization |

## Directory Structure

```
docs/
├── README.md                    # This file
├── guides/
│   ├── SETUP.md                # Installation guide
│   ├── SECURITY.md             # Security & credentials
│   └── [Other guides...]
├── deployment/
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── [Deployment configs]
└── [Other documentation]
```

## By Role

### Developer (First Time Setup)
1. Read: [README.md](../README.md) - Project overview
2. Follow: [SETUP.md](guides/SETUP.md) - Get environment running
3. Read: [API_DOCS.md](../API_DOCS.md) - Understand endpoints
4. Start: Making changes in `app/` directory

### Developer (Daily Work)
- Reference: [API_DOCS.md](../API_DOCS.md) for endpoint details
- Check: [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) for file organization
- Review: Code comments and docstrings
- Use: [Swagger UI](http://localhost:8000/docs) for interactive testing

### DevOps / Infrastructure
1. Read: [DEPLOYMENT.md](deployment/DEPLOYMENT.md) - Deployment options
2. Follow: [SECURITY.md](guides/SECURITY.md) - Credential management
3. Setup: Chosen hosting platform (Render, Railway, etc.)
4. Monitor: Application health and logs

### Security Auditor
1. Review: [SECURITY.md](guides/SECURITY.md) - Credential practices
2. Check: .env.local gitignore protection
3. Verify: No hardcoded secrets in code
4. Audit: Production environment configuration

## Key Files Reference

### Root Level Documentation
```
README.md                # Project overview and quick start
API_DOCS.md             # Complete API endpoint documentation
PROJECT_STRUCTURE.md    # Directory and file organization
requirements.txt        # Python dependencies
.env.example           # Configuration template (safe to commit)
.gitignore             # Git ignore rules
```

### Main Application Files
```
main.py                # Application entry point
database.py            # Database configuration
models.py             # Database models (Team, Player)
```

### Application Modules
```
app/config.py         # Settings and configuration
app/schemas.py        # Pydantic models for validation
app/services.py       # Business logic
app/routes/           # API endpoints
```

### Utility & Test Files
```
scripts/migrate_to_neon.py    # Database migration script
tests/test_endpoints.py       # Endpoint integration tests
tests/test_db.py             # Database connection tests
```

## Important Links

### Local Development
- API Root: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### External Services
- Neon PostgreSQL: https://neon.tech/console
- Render Deployment: https://render.com
- Railway Deployment: https://railway.app
- Gmail App Passwords: https://myaccount.google.com/apppasswords

### Documentation Resources
- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- Pydantic Docs: https://docs.pydantic.dev
- Neon Docs: https://neon.tech/docs

## Common Tasks

### How to... Set up locally?
→ See [SETUP.md](guides/SETUP.md)

### How to... Deploy to production?
→ See [DEPLOYMENT.md](deployment/DEPLOYMENT.md)

### How to... Manage credentials safely?
→ See [SECURITY.md](guides/SECURITY.md)

### How to... Understand API endpoints?
→ See [API_DOCS.md](../API_DOCS.md) or http://localhost:8000/docs

### How to... Run tests?
→ See tests/ directory and [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)

### How to... Report a security issue?
→ See [SECURITY.md](guides/SECURITY.md) - "If Credentials Leak" section

## Updates & Maintenance

### When docs are out of date
1. Update relevant guide in `docs/guides/` or `docs/deployment/`
2. Update date in "Last Updated" section if present
3. Update this README if structure changes
4. Commit with message: "docs: update [guide name]"

### Adding new documentation
1. Create file in appropriate directory:
   - `docs/guides/` - How-to and best practices
   - `docs/deployment/` - Deployment specific
2. Add link to this README
3. Include "Last Updated" section
4. Commit with message: "docs: add [guide name]"

## Questions?

### If you're confused about...
- **Setup** → Read [SETUP.md](guides/SETUP.md) and [README.md](../README.md)
- **Security** → Read [SECURITY.md](guides/SECURITY.md)
- **Deployment** → Read [DEPLOYMENT.md](deployment/DEPLOYMENT.md)
- **Endpoints** → Read [API_DOCS.md](../API_DOCS.md) or http://localhost:8000/docs
- **File organization** → Read [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)

### If issue persists...
1. Check [SETUP.md](guides/SETUP.md) troubleshooting section
2. Review log output carefully for error messages
3. Search GitHub issues for similar problems
4. Ask development team

## Checklist for New Team Members

- [ ] Read [README.md](../README.md)
- [ ] Follow [SETUP.md](guides/SETUP.md) to set up locally
- [ ] Read [SECURITY.md](guides/SECURITY.md)
- [ ] Review [API_DOCS.md](../API_DOCS.md)
- [ ] Explore code in `app/` directory
- [ ] Try running tests: `pytest tests/`
- [ ] Access API docs locally: http://localhost:8000/docs
- [ ] Understand [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)
- [ ] Ask questions in team chat

---

**Last Updated:** 2024
**Maintained By:** Development Team
**Questions?** See "Getting Help" sections in individual guides
