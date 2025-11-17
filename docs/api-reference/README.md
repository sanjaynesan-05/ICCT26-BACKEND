# 🏏 ICCT26 Cricket Tournament Backend API

A professional, production-ready FastAPI backend for the **ICCT26 Cricket Tournament** registration system with PostgreSQL database integration, SMTP email notifications, and comprehensive API documentation.

**Organized by**: CSI St. Peter's Church, Coimbatore

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## 🎯 Overview

The ICCT26 Backend provides a complete REST API for cricket tournament team registration. Teams can register with 11-15 players, and the system automatically:
- Validates all input data using Pydantic models
- Stores registrations in PostgreSQL database
- Sends confirmation emails to team captains
- Generates unique team IDs for tracking

### Event Details
- **Event**: ICCT26 Cricket Tournament 2026
- **Format**: Red Tennis Ball Cricket  
- **Dates**: January 24-26, 2026
- **Venue**: CSI St. Peter's Church, Coimbatore

---

## ✨ Features

### Core Functionality
- ✅ **Complete Team Registration** - Register teams with 11-15 players
- ✅ **Multi-Role Player System** - Support for Batsman, Bowler, All-Rounder, Wicket Keeper
- ✅ **Document Management** - Base64 encoded PDF file uploads (Aadhar, Subscription, Pastor Letter, Payment Receipt)
- ✅ **Email Notifications** - Automatic confirmation emails to team captains
- ✅ **Unique Team IDs** - Auto-generated identifiers for tracking

### Technical Features
- ✅ **PostgreSQL Integration** - Persistent, relational data storage
- ✅ **SQLAlchemy ORM** - Object-relational mapping with async support
- ✅ **Pydantic Validation** - Strict input/output validation
- ✅ **CORS Support** - Frontend integration ready
- ✅ **API Documentation** - Auto-generated Swagger UI and ReDoc
- ✅ **Error Handling** - Comprehensive exception handling
- ✅ **Async Operations** - Non-blocking database operations with asyncpg
- ✅ **SMTP Email** - Gmail and custom SMTP provider support

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.104+ |
| **Server** | Uvicorn | 0.24+ |
| **Database** | PostgreSQL | 17+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Async Driver** | asyncpg | 0.29+ |
| **Validation** | Pydantic | 2.5+ |
| **Python** | Python | 3.11+ |

---

## 📂 Project Structure

```
ICCT26-BACKEND/
│
├── 📄 Core Application Files
│   ├── main.py                    # FastAPI application (production)
│   ├── simple_main.py             # Simple FastAPI app (testing)
│   ├── database.py                # SQLAlchemy configuration
│   ├── models.py                  # SQLAlchemy ORM models
│   └── init_db.py                 # Database initialization
│
├── 📁 scripts/                    # Utility scripts
│   ├── test_registration_simple.py     # Full API test
│   ├── test_simple_api.py              # Simple API test
│   ├── setup_database.py               # Database setup
│   ├── setup_postgres.bat              # Windows PostgreSQL setup
│   └── setup_postgres.sh               # Linux/macOS setup
│
├── 📁 docs/                       # Documentation
│   └── POSTGRESQL_SETUP.md        # PostgreSQL installation guide
│
├── 🔧 Configuration Files
│   ├── requirements.txt           # Python dependencies
│   ├── pyproject.toml             # Project metadata
│   ├── .env                       # Environment variables (git ignored)
│   └── .env.example               # Environment template
│
├── 📖 Documentation
│   ├── README.md                  # This file
│   └── SIMPLE_API_README.md       # Simple API documentation
│
└── 📦 Virtual Environment
    ├── venv/                      # Python virtual environment
    └── .git/                      # Git repository
```

---

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.11 or higher
- **PostgreSQL**: Version 17 or higher
- **pip**: Python package manager
- **Git**: For version control

### 1-Minute Setup

```bash
# Clone repository
git clone <repo-url> && cd ICCT26-BACKEND

# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start server
uvicorn main:app --reload
```

Open browser: **http://localhost:8000/docs**

---

## 📦 Installation

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd ICCT26-BACKEND
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- fastapi - Web framework
- uvicorn - ASGI server
- sqlalchemy - ORM
- psycopg2-binary - PostgreSQL driver
- asyncpg - Async PostgreSQL driver
- pydantic - Data validation
- python-dotenv - Environment variables
- email-validator - Email validation

### Step 4: PostgreSQL Setup

**Complete Guide**: See [`POSTGRESQL_SETUP.md`](./POSTGRESQL_SETUP.md)

Quick setup:
```bash
# Windows
scripts\setup_postgres.bat

# Linux/macOS
chmod +x scripts/setup_postgres.sh
./scripts/setup_postgres.sh
```

### Step 5: Environment Configuration

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:icctpg@localhost/icct26_db

# SMTP (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=ICCT26 TEAM

# Server
PORT=8000
ENVIRONMENT=development
```

### Step 6: Initialize Database

```bash
python init_db.py
```

Expected output:
```
⏳ Creating database tables...
✅ All tables created successfully!
```

### Step 7: Start Server

```bash
# Production API
uvicorn main:app --reload --port 8000

# Simple API (for testing)
uvicorn simple_main:app --reload --port 8001
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | string | - | PostgreSQL connection URL |
| `SMTP_SERVER` | string | `smtp.gmail.com` | SMTP server address |
| `SMTP_PORT` | int | `587` | SMTP port |
| `SMTP_USERNAME` | string | - | SMTP username/email |
| `SMTP_PASSWORD` | string | - | SMTP password/app-password |
| `SMTP_FROM_EMAIL` | string | - | Sender email address |
| `SMTP_FROM_NAME` | string | `ICCT26 TEAM` | Sender display name |
| `PORT` | int | `8000` | Server port |
| `ENVIRONMENT` | string | `development` | Environment (development/production) |

### Database Configuration

**File**: `database.py`

```python
DATABASE_URL = "postgresql+asyncpg://postgres:icctpg@localhost:5432/icct26_db"
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession)
```

### SMTP Configuration

**For Gmail:**
1. Enable 2-factor authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use App Password in `.env` (not your main password)

**Example:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
```

---

## 📊 Database Schema

### team_registrations
Main registration table

```sql
CREATE TABLE team_registrations (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR(50) UNIQUE NOT NULL,
    church_name VARCHAR(200),
    team_name VARCHAR(100),
    pastor_letter TEXT,
    payment_receipt TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### captains
Team captain information

```sql
CREATE TABLE captains (
    id SERIAL PRIMARY KEY,
    registration_id INTEGER REFERENCES team_registrations(id),
    name VARCHAR(100),
    phone VARCHAR(15),
    whatsapp VARCHAR(10),
    email VARCHAR(255)
);
```

### vice_captains
Vice-captain information

```sql
CREATE TABLE vice_captains (
    id SERIAL PRIMARY KEY,
    registration_id INTEGER REFERENCES team_registrations(id),
    name VARCHAR(100),
    phone VARCHAR(15),
    whatsapp VARCHAR(10),
    email VARCHAR(255)
);
```

### players
Player roster (11-15 per team)

```sql
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    registration_id INTEGER REFERENCES team_registrations(id),
    name VARCHAR(100),
    age INTEGER,
    phone VARCHAR(15),
    role VARCHAR(20),
    aadhar_file TEXT,
    subscription_file TEXT
);
```

### teams (Simple API Only)
Simple teams table for basic testing

```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    captain VARCHAR(100),
    registered_on TIMESTAMP DEFAULT NOW()
);
```

---

## 🔌 API Endpoints

### Main API (Production)

#### POST `/register/team`
Register a cricket team with player details

**Content-Type**: `application/json`

**Request Body:**
```json
{
  "churchName": "CSI St. Peter's Church",
  "teamName": "Warriors",
  "pastorLetter": "data:application/pdf;base64,JVBERi0xLjQ...",
  "captain": {
    "name": "John Doe",
    "phone": "+919876543210",
    "whatsapp": "9876543210",
    "email": "captain@example.com"
  },
  "viceCaptain": {
    "name": "Jane Smith",
    "phone": "+919876543211",
    "whatsapp": "9876543211",
    "email": "vice@example.com"
  },
  "players": [
    {
      "name": "Player One",
      "age": 25,
      "phone": "+919876543212",
      "role": "Batsman",
      "aadharFile": "data:application/pdf;base64,JVBERi0xLjQ...",
      "subscriptionFile": "data:application/pdf;base64,JVBERi0xLjQ..."
    },
    {
      "name": "Player Two",
      "age": 26,
      "phone": "+919876543213",
      "role": "Bowler",
      "aadharFile": null,
      "subscriptionFile": null
    }
  ],
  "paymentReceipt": "data:application/pdf;base64,JVBERi0xLjQ..."
}
```

**Response (Success 200):**
```json
{
  "success": true,
  "message": "Team registration successful",
  "data": {
    "team_id": "ICCT26-20251105143934",
    "team_name": "Warriors",
    "captain_name": "John Doe",
    "players_count": 11,
    "registered_at": "2025-11-05T14:39:34.123456",
    "email_sent": true,
    "database_saved": true
  }
}
```

**Response (Validation Error 422):**
```json
{
  "detail": [
    {
      "loc": ["body", "players"],
      "msg": "Team must have 11-15 players",
      "type": "value_error"
    }
  ]
}
```

### Simple API (Testing)

#### GET `/`
Health check

**Response:**
```json
{
  "message": "ICCT26 Backend connected to PostgreSQL successfully"
}
```

#### POST `/register/team?name=Warriors&captain=John+Doe`
Simple team registration

**Response:**
```json
{
  "id": 1,
  "name": "Warriors",
  "captain": "John Doe"
}
```

---

## 🧪 Testing

### Swagger UI (Interactive Documentation)

**Main API**: http://localhost:8000/docs
**Simple API**: http://localhost:8001/docs

Interactive API testing with request/response examples.

### Automated Test Scripts

```bash
# Test main API with full registration
python scripts/test_registration_simple.py

# Test simple API
python scripts/test_simple_api.py
```

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/

# Register team (simple API)
curl -X POST "http://localhost:8001/register/team?name=Warriors&captain=John%20Doe"

# Register team with full details (main API)
curl -X POST "http://localhost:8000/register/team" \
  -H "Content-Type: application/json" \
  -d @registration_data.json
```

### Database Verification

```bash
# Connect to PostgreSQL
psql -U postgres -d icct26_db

# View teams
SELECT * FROM team_registrations;

# View captains
SELECT c.name, c.email, t.team_name 
FROM captains c 
JOIN team_registrations t ON c.registration_id = t.id;

# View players count
SELECT t.team_name, COUNT(p.id) as player_count
FROM team_registrations t
LEFT JOIN players p ON t.id = p.registration_id
GROUP BY t.team_name;

# Count registrations
SELECT COUNT(*) as total_registrations FROM team_registrations;
```

---

## 🐛 Troubleshooting

### Database Connection Issues

**Error**: `password authentication failed for user "postgres"`

**Solution**:
```bash
# Reset PostgreSQL password
psql -U postgres -c "ALTER USER postgres PASSWORD 'icctpg';"

# Update .env with correct password
DATABASE_URL=postgresql+asyncpg://postgres:icctpg@localhost/icct26_db
```

### Database Does Not Exist

**Error**: `database "icct26_db" does not exist`

**Solution**:
```bash
# Initialize database
python init_db.py

# Or manually create
createdb -U postgres icct26_db
```

### SMTP Connection Failed

**Error**: `smtplib.SMTPAuthenticationError: (535, b'5.7.8 Username and password not accepted')`

**Solution**:
1. Verify email and password in `.env`
2. For Gmail, use App Password (not main password)
3. Ensure 2-factor authentication is enabled
4. Check SMTP settings are correct

### Port Already in Use

**Error**: `Address already in use: ('0.0.0.0', 8000)`

**Solution**:
```bash
# Use different port
uvicorn main:app --port 8001

# Or kill process using port
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Production Deployment

### Environment Setup

```env
# Production .env
DATABASE_URL=postgresql+asyncpg://prod_user:strong_password@prod-db-server/icct26_db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=team@icct26.com
SMTP_PASSWORD=secure_app_password
SMTP_FROM_EMAIL=team@icct26.com
SMTP_FROM_NAME=ICCT26 Tournament Team

PORT=8000
ENVIRONMENT=production
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run database initialization
RUN python init_db.py

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run:**
```bash
docker build -t icct26-backend .
docker run -p 8000:8000 --env-file .env icct26-backend
```

### PostgreSQL Production Setup

```sql
-- Create dedicated user
CREATE USER icct26_user WITH PASSWORD 'secure_password';

-- Create database
CREATE DATABASE icct26_db OWNER icct26_user;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE icct26_db TO icct26_user;
\c icct26_db
GRANT ALL ON SCHEMA public TO icct26_user;
```

### Security Checklist

- [ ] Use strong database passwords (12+ characters, mixed case, numbers, symbols)
- [ ] Enable HTTPS/SSL in production
- [ ] Use environment variables for all secrets
- [ ] Never commit `.env` to version control
- [ ] Implement rate limiting on API endpoints
- [ ] Use Gmail App Passwords (not main password)
- [ ] Enable database backups
- [ ] Monitor application logs
- [ ] Set up firewall rules
- [ ] Use VPN for database connections

---

## 📚 Documentation

- **PostgreSQL Setup Guide**: [`POSTGRESQL_SETUP.md`](./POSTGRESQL_SETUP.md)
- **Simple API Documentation**: [`SIMPLE_API_README.md`](./SIMPLE_API_README.md)
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -m "Add feature"`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a Pull Request

---

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review [`POSTGRESQL_SETUP.md`](./POSTGRESQL_SETUP.md)
3. Check API documentation at `/docs`
4. Review test scripts for usage examples
5. Open an issue on GitHub

---

## 📄 License

ICCT26 Cricket Tournament - CSI St. Peter's Church, Coimbatore

---

## ✅ Project Status

- ✅ FastAPI framework setup
- ✅ PostgreSQL integration (async)
- ✅ SQLAlchemy ORM models
- ✅ Pydantic data validation
- ✅ SMTP email notifications
- ✅ REST API endpoints
- ✅ Test scripts and automation
- ✅ Comprehensive documentation
- ✅ Error handling and logging
- ✅ Database schema and migrations
- ✅ Production-ready configuration
- ✅ Docker support

---

**Last Updated**: November 5, 2025
**Version**: 1.0.0
**Status**: ✅ Production Ready
**Python**: 3.11+
**PostgreSQL**: 17+
**FastAPI**: 0.104+
