# PostgreSQL Setup Guide for ICCT26 Backend

## Overview

This guide provides comprehensive instructions for installing, configuring, and integrating PostgreSQL with the ICCT26 Cricket Tournament backend. The backend uses asyncpg and SQLAlchemy for database operations.

## Table of Contents

1. [Installation](#installation)
2. [Initial Configuration](#initial-configuration)
3. [Database Setup](#database-setup)
4. [Backend Integration](#backend-integration)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [Production Considerations](#production-considerations)

## Installation

### Windows Installation

#### Option 1: Official PostgreSQL Installer (Recommended)

1. **Download PostgreSQL 17.x**
   - Visit: https://www.postgresql.org/download/windows/
   - Download the latest 17.x version (currently 17.2)
   - Choose "Windows x86-64" for 64-bit systems

2. **Run the Installer**
   - Execute the downloaded `.exe` file
   - Select components:
     - ✅ PostgreSQL Server
     - ✅ pgAdmin 4 (optional but recommended)
     - ✅ Command Line Tools
     - ✅ Stack Builder (optional)

3. **Installation Wizard**
   - Choose installation directory (default is fine)
   - Set password for `postgres` superuser (remember this!)
   - Choose port (default 5432 is fine)
   - Select locale (default is fine)

4. **Verify Installation**
   ```powershell
   # Check version
   psql --version

   # Check service status
   Get-Service postgresql*
   ```

#### Option 2: Chocolatey Package Manager

```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install PostgreSQL
choco install postgresql17
```

### Linux Installation

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Check status
sudo systemctl status postgresql

# Start service
sudo systemctl start postgresql

# Enable auto-start
sudo systemctl enable postgresql
```

#### CentOS/RHEL/Fedora

```bash
# Install PostgreSQL repository
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/F-38-x86_64/pgdg-fedora-repo-latest.noarch.rpm

# Install PostgreSQL
sudo dnf install -y postgresql17-server postgresql17-contrib

# Initialize database
sudo postgresql-17-setup initdb

# Start service
sudo systemctl start postgresql-17

# Enable auto-start
sudo systemctl enable postgresql-17
```

### macOS Installation

#### Using Homebrew (Recommended)

```bash
# Install Homebrew (if not installed)
# Visit: https://brew.sh/ for installation instructions

# Install PostgreSQL
brew install postgresql@17

# Start service
brew services start postgresql@17

# Verify installation
brew services list
```

#### Using EnterpriseDB Installer

1. Download from: https://www.postgresql.org/download/macosx/
2. Run the installer package
3. Follow the installation wizard

## Initial Configuration

### Setting Up the PostgreSQL User

#### Windows

```powershell
# Open PowerShell as Administrator
# Set password for postgres user
psql -U postgres -c "ALTER USER postgres PASSWORD 'your_secure_password';"

# Create icct26_db database
createdb -U postgres icct26_db
```

#### Linux/macOS

```bash
# Switch to postgres user
sudo -u postgres psql

# In psql shell:
ALTER USER postgres PASSWORD 'your_secure_password';
\q

# Create database
sudo -u postgres createdb icct26_db
```

### Automated Setup Script

Run the provided setup script:

```bash
# Windows
scripts\setup_postgres.bat

# Linux/macOS
chmod +x scripts/setup_postgres.sh
./scripts/setup_postgres.sh
```

## Database Setup

### Environment Configuration

Update your `.env` file with database credentials:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:your_secure_password@localhost/icct26_db

# SMTP Configuration (update with your email settings)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=ICCT26 Cricket Tournament
```

### Database Schema

The backend automatically creates the following tables:

1. **team_registrations**
   - `id` (Primary Key)
   - `team_id` (Unique identifier)
   - `church_name`
   - `team_name`
   - `pastor_letter` (Base64 PDF)
   - `payment_receipt` (Base64 PDF)
   - `created_at`, `updated_at`

2. **captains**
   - `id` (Primary Key)
   - `registration_id` (Foreign Key)
   - `name`, `phone`, `whatsapp`, `email`

3. **vice_captains**
   - `id` (Primary Key)
   - `registration_id` (Foreign Key)
   - `name`, `phone`, `whatsapp`, `email`

4. **players**
   - `id` (Primary Key)
   - `registration_id` (Foreign Key)
   - `name`, `age`, `phone`, `role`
   - `aadhar_file`, `subscription_file` (Base64 PDFs)

### Manual Database Creation

If you prefer to create the database manually:

```sql
-- Connect to PostgreSQL
psql -U postgres -d postgres

-- Create database
CREATE DATABASE icct26_db;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE icct26_db TO postgres;

-- Connect to the new database
\c icct26_db

-- The tables will be created automatically by the backend
```

## Backend Integration

### Dependencies Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install specific packages
pip install asyncpg sqlalchemy alembic
```

### Starting the Backend

```bash
# Activate virtual environment (if using one)
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Start the FastAPI server
python main.py
```

The server will:
- ✅ Connect to PostgreSQL
- ✅ Create tables automatically (if they don't exist)
- ✅ Start on `http://localhost:8000`

### API Endpoints

#### POST `/register/team`

Register a cricket team with validation and database storage.

**Request Example:**
```json
{
  "churchName": "CSI St. Peter's Church",
  "teamName": "Warriors",
  "pastorLetter": "base64-encoded-pdf-data",
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
      "aadharFile": "base64-encoded-pdf",
      "subscriptionFile": "base64-encoded-pdf"
    }
  ],
  "paymentReceipt": "base64-encoded-pdf"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Team registration successful",
  "data": {
    "team_id": "ICCT26-20251105120000",
    "team_name": "Warriors",
    "captain_name": "John Doe",
    "players_count": 11,
    "registered_at": "2025-11-05T12:00:00",
    "email_sent": true,
    "database_saved": true
  }
}
```

## Testing

### Database Connection Test

```bash
# Run database setup script
python scripts/setup_database.py
```

### API Testing

```bash
# Test registration endpoint
python scripts/test_registration_simple.py
```

### Manual Testing with curl

```bash
# Test health check
curl http://localhost:8000/docs

# Test registration (replace with actual JSON data)
curl -X POST "http://localhost:8000/register/team" \
     -H "Content-Type: application/json" \
     -d @test_data.json
```

### Database Verification

```sql
-- Connect to database
psql -U postgres -d icct26_db

-- Check tables
\dt

-- View registrations
SELECT * FROM team_registrations;

-- View captains
SELECT * FROM captains;

-- View players
SELECT * FROM players;
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused

**Error:** `password authentication failed for user "postgres"`

**Solutions:**
```bash
# Reset postgres password
psql -U postgres -c "ALTER USER postgres PASSWORD 'new_password';"

# Update .env file
DATABASE_URL=postgresql+asyncpg://postgres:new_password@localhost/icct26_db
```

#### 2. Database Does Not Exist

**Error:** `database "icct26_db" does not exist`

**Solutions:**
```bash
# Create database
createdb -U postgres icct26_db

# Or run setup script
python scripts/setup_database.py
```

#### 3. Port Already in Use

**Error:** `port 5432 is already in use`

**Solutions:**
```bash
# Check what's using the port
netstat -ano | findstr :5432

# Change PostgreSQL port in postgresql.conf
# Or use a different port in DATABASE_URL
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/icct26_db
```

#### 4. Permission Denied

**Error:** `permission denied for database`

**Solutions:**
```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE icct26_db TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
```

#### 5. Service Not Running

**Windows:**
```powershell
# Start PostgreSQL service
net start postgresql-x64-17

# Check status
Get-Service postgresql*
```

**Linux:**
```bash
# Start service
sudo systemctl start postgresql

# Check status
sudo systemctl status postgresql
```

**macOS:**
```bash
# Start service
brew services start postgresql@17

# Check status
brew services list
```

### Log Files

#### PostgreSQL Logs

**Windows:** `C:\Program Files\PostgreSQL\17\data\log\`

**Linux:** `/var/log/postgresql/`

**macOS:** `/usr/local/var/log/postgres.log`

#### Backend Logs

The FastAPI application logs database connection issues to the console.

### Performance Tuning

For production deployments, consider these PostgreSQL configurations:

```sql
-- Increase connection limits
ALTER SYSTEM SET max_connections = '200';

-- Configure memory
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';

-- Reload configuration
SELECT pg_reload_conf();
```

## Production Considerations

### Security

1. **Strong Passwords:** Use complex passwords for database users
2. **Network Security:** Configure PostgreSQL to only accept connections from trusted IPs
3. **SSL/TLS:** Enable SSL for encrypted connections
4. **User Roles:** Create separate database users with minimal privileges

### Backup Strategy

```bash
# Create backup
pg_dump -U postgres -d icct26_db > icct26_backup.sql

# Restore backup
psql -U postgres -d icct26_db < icct26_backup.sql

# Automated backups (add to cron/scheduled task)
pg_dump -U postgres -d icct26_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Monitoring

1. **pgAdmin:** Use the web interface for monitoring
2. **System Tools:** Monitor disk space, memory, and CPU usage
3. **Query Performance:** Use `EXPLAIN ANALYZE` for slow queries

### Scaling

1. **Connection Pooling:** Consider using pgBouncer for high-traffic applications
2. **Read Replicas:** Set up replication for read-heavy workloads
3. **Partitioning:** Partition large tables by date for better performance

## Support

For additional help:

- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **pgAdmin Documentation:** https://www.pgadmin.org/docs/
- **SQLAlchemy Documentation:** https://sqlalchemy.org/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/

## Quick Start Checklist

- [ ] Download and install PostgreSQL 17.x
- [ ] Set postgres user password
- [ ] Create icct26_db database
- [ ] Update .env with DATABASE_URL
- [ ] Install Python dependencies
- [ ] Run database setup script
- [ ] Start backend server
- [ ] Test registration endpoint
- [ ] Verify data in database

---

**Last Updated:** November 5, 2025
**PostgreSQL Version:** 17.x (Recommended)
**Backend Version:** ICCT26 v1.0.0