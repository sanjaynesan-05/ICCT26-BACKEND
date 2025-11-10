# 🔒 SECURITY BEST PRACTICES - Credentials Management

## ⚠️ CRITICAL: Never Commit Credentials to Git

This document explains how to properly manage sensitive credentials for the ICCT26 backend.

## What Should NEVER Be Committed

❌ **DO NOT commit these files:**
- `.env` (any environment files)
- `.env.local`
- `.env.production`
- Credentials files
- API keys
- Database passwords
- SMTP passwords
- Google credentials

## ✅ What IS Safe to Commit

✅ **SAFE to commit:**
- `.env.example` (with placeholder values)
- `.gitignore` (with sensitive files listed)
- Configuration code (no hardcoded secrets)
- Documentation about setup

## File Structure & Security

### 1. `.env.example` ✅
**Location:** Committed to git  
**Purpose:** Template for developers  
**Content:** Placeholder values only  
**Example:**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?ssl=require
SMTP_PASSWORD=your-app-specific-password
```

### 2. `.env.local` ❌
**Location:** Local machine only (in .gitignore)  
**Purpose:** Actual credentials for local development  
**Content:** Real credentials  
**Example:**
```bash
DATABASE_URL=postgresql+asyncpg://neondb_owner:actual_password@neon-host.tech/neondb?ssl=require
SMTP_PASSWORD=actual-password
```

### 3. Environment Variables in Deployment
**Location:** Hosting platform's environment configuration  
**Purpose:** Production credentials  
**Method:** Set via:
- Render: Dashboard → Environment
- Railway: Dashboard → Variables
- Heroku: Config Vars
- Docker: ENV in Dockerfile or docker-compose.yml
- Kubernetes: Secrets

## Setup Instructions

### For Local Development

1. **Copy the example file:**
   ```bash
   cp .env.example .env.local
   ```

2. **Edit .env.local with your credentials:**
   ```bash
   # Use your actual Neon credentials
   DATABASE_URL=postgresql+asyncpg://your_user:your_pass@...
   
   # Use your actual SMTP credentials
   SMTP_PASSWORD=your-app-specific-password
   ```

3. **Verify .env.local is in .gitignore:**
   ```bash
   cat .gitignore | grep ".env.local"
   # Should see: .env.local
   ```

4. **Start development:**
   ```bash
   .\venv\Scripts\Activate.ps1
   python -m uvicorn main:app --reload
   ```

### For Production Deployment

#### Option 1: Render

1. Go to Render Dashboard
2. Select your service
3. Go to **Environment**
4. Add variables:
   ```
   DATABASE_URL = postgresql+asyncpg://user:pass@neon-host/db?ssl=require
   SMTP_PASSWORD = your-app-password
   PORT = 8000
   ENVIRONMENT = production
   ```

#### Option 2: Railway

1. Go to Variables section
2. Add each environment variable
3. Deploy automatically

#### Option 3: Docker/Local Server

Create a `.env.prod` file (not committed):
```bash
DATABASE_URL=postgresql+asyncpg://...
SMTP_PASSWORD=...
```

Run with:
```bash
docker run --env-file .env.prod my-app
```

## GitHub Security

### Revoking Compromised Credentials

If credentials are exposed on GitHub:

1. **Immediately revoke in source system:**
   - Neon: Change password in dashboard
   - Gmail: Revoke app password
   - API tokens: Regenerate

2. **Remove from git history:**
   ```bash
   # Using git-filter-branch (careful!)
   git filter-branch --tree-filter 'rm -f .env.local' HEAD
   
   # Or use BFG (simpler):
   bfg --delete-files .env.local
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push --force
   ```

3. **Verify removal:**
   ```bash
   git log --all --full-history -- .env.local
   # Should show no recent commits
   ```

4. **Notify team:**
   - Check if credentials were used elsewhere
   - Rotate all related credentials

## Pre-commit Security Check

### Install git-secrets

**Windows (Git Bash):**
```bash
cd "C:\Program Files\Git\mingw64\libexec\git-core"
wget https://raw.githubusercontent.com/awslabs/git-secrets/master/git-secrets
chmod +x git-secrets
```

**macOS:**
```bash
brew install git-secrets
```

### Configure git-secrets

```bash
cd D:\ICCT26\ BACKEND
git secrets --install
git secrets --register-aws
```

### Add custom patterns

```bash
git secrets --add --local 'npg_[A-Za-z0-9]{20,}'  # Neon password pattern
git secrets --add --local 'password.*=.*'         # Explicit password lines
```

### Test it

```bash
# This should fail
echo "DATABASE_URL=postgresql://user:npg_abc123def456@host/db" > test.txt
git add test.txt
# Error: found exposed secret

# Remove and commit
rm test.txt
git reset
```

## Environment Variable Source Priority

The application loads credentials in this order:

1. ✅ `.env.local` (Local development)
2. ✅ `.env` (Fallback)
3. ✅ System environment variables
4. ✅ Hosting platform defaults

## Credentials Used by ICCT26 Backend

### Database Credentials
- **Variable:** `DATABASE_URL`
- **Format:** `postgresql+asyncpg://user:pass@host/db?ssl=require`
- **Sensitivity:** 🔴 CRITICAL
- **Rotation:** After any breach

### Email Credentials
- **Variables:** `SMTP_USERNAME`, `SMTP_PASSWORD`
- **Type:** Gmail App Password (not regular password)
- **Sensitivity:** 🔴 CRITICAL
- **Location:** `.env.local`, not in code

### Google Credentials (Optional)
- **Variables:** `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- **Type:** OAuth credentials
- **Sensitivity:** 🟡 HIGH
- **Storage:** Credentials file (not in `.env`)

## Checking Current Code

✅ **Already Secured:**
- Database configuration uses `os.environ.get()`
- SMTP password from environment
- No hardcoded credentials in source

⚠️ **To Verify:**
```bash
# Search for exposed secrets
grep -r "password" --include="*.py" app/
grep -r "npg_" --include="*.py" .
grep -r "@" --include="*.py" migrations/

# Should only find environment variable references
```

## Team Guidelines

### ✅ DO:
- Use `.env.local` for development
- Use `.env.example` as template
- Rotate credentials regularly
- Use app-specific passwords (Gmail)
- Enable 2FA on accounts
- Review git history before pushing
- Use secrets manager in production

### ❌ DON'T:
- Hardcode credentials in Python files
- Commit `.env.local` to git
- Share `.env.local` via email
- Use same password everywhere
- Put credentials in documentation
- Store credentials in comments
- Commit service account JSON files

## Resources

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Git Secrets](https://github.com/awslabs/git-secrets)
- [Neon Security](https://neon.tech/docs/security)
- [Gmail App Passwords](https://myaccount.google.com/apppasswords)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

## Questions?

If you accidentally commit credentials:
1. Stop and revoke immediately
2. Rewrite git history
3. Rotate all affected credentials
4. Notify the team

---

**Last Updated:** November 10, 2025  
**Status:** Security Hardened ✅
