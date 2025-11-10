# 🔒 Security & Credentials Management

This guide covers best practices for managing sensitive credentials in the ICCT26 backend.

## ⚠️ CRITICAL RULE

**NEVER commit credentials to git!**

All sensitive information (passwords, API keys, tokens) must be stored in `.env.local` which is gitignored.

## Environment Files

### `.env.example` ✅ Safe to Commit
- **Location:** Root directory
- **Content:** Placeholder values only
- **Purpose:** Template for developers
- **Committed:** YES

```bash
DATABASE_URL=postgresql+asyncpg://user:password@host/db?ssl=require
SMTP_PASSWORD=your-app-specific-password
```

### `.env.local` ❌ NEVER Commit
- **Location:** Local machine only
- **Content:** Real credentials
- **Purpose:** Development environment
- **Committed:** NO (in .gitignore)

```bash
DATABASE_URL=postgresql+asyncpg://actual_user:actual_pass@neon.tech/db?ssl=require
SMTP_PASSWORD=actual-gmail-password
```

## Setup Guide

### For Development

1. **Copy template:**
   ```bash
   cp .env.example .env.local
   ```

2. **Edit with real credentials:**
   ```bash
   # .env.local
   DATABASE_URL=postgresql+asyncpg://your_user:your_pass@...
   SMTP_PASSWORD=your-gmail-app-password
   ```

3. **Verify it's ignored:**
   ```bash
   git status | grep .env.local
   # Should show nothing (good!)
   ```

### For Production

1. **Get credentials from:**
   - Neon Dashboard: Connection string
   - Gmail: App-specific password (not your regular password)
   - Hosting provider: Document where to set these

2. **Set in hosting platform:**
   - **Render:** Dashboard → Environment variables
   - **Railway:** Dashboard → Variables
   - **Docker:** ENV in docker-compose.yml
   - **Kubernetes:** Secrets

3. **Never hardcode** in:
   - Source code
   - Docker images
   - Configuration files committed to git

## Credentials to Manage

| Variable | Type | Source | Risk |
|----------|------|--------|------|
| DATABASE_URL | PostgreSQL | Neon Dashboard | 🔴 CRITICAL |
| SMTP_USERNAME | Email | Gmail | 🔴 CRITICAL |
| SMTP_PASSWORD | Password | Gmail App Passwords | 🔴 CRITICAL |
| GOOGLE_DRIVE_FOLDER_ID | API | Google Drive | 🟡 HIGH |
| SPREADSHEET_ID | API | Google Sheets | 🟡 HIGH |

## Best Practices

### ✅ DO
- Use strong, unique passwords
- Rotate credentials regularly
- Use app-specific passwords (Gmail)
- Store credentials in environment variables
- Use .env files locally only
- Document which credentials are needed
- Check .gitignore before committing

### ❌ DON'T
- Hardcode credentials in Python
- Put credentials in documentation
- Share .env.local via email
- Use same password everywhere
- Commit .env files to git
- Store credentials in comments
- Put credentials in commit messages

## If Credentials Leak

**IMMEDIATE ACTIONS:**

1. Revoke in source system
   - Neon: Change database password
   - Gmail: Revoke app password
   - Other APIs: Regenerate tokens

2. Remove from git history
   ```bash
   # Using BFG (simpler than git filter-branch)
   bfg --delete-files .env.local
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push --force
   ```

3. Notify team
   - Security incident occurred
   - Old credentials compromised
   - New credentials set
   - Repository force-pushed

4. Document incident
   - What leaked
   - When discovered
   - Actions taken
   - Prevention measures

## Pre-commit Security Check

### Manual Check

```bash
# Before committing, check for secrets
grep -r "password" --include="*.py" .
grep -r "npg_" --include="*.py" .
grep -r "SMTP" --include="*.py" app/ | grep -v "SMTP_"

# Should return only environment variable references
```

### Automated with Pre-commit Hooks

1. **Install tools:**
   ```bash
   pip install detect-secrets
   pip install pre-commit
   ```

2. **Initialize:**
   ```bash
   pre-commit install
   ```

3. **Test:**
   ```bash
   # This should fail
   echo "password=secret123" > test.txt
   git add test.txt
   # Error: secret detected
   ```

## Production Deployment Checklist

Before deploying to production:

- [ ] All credentials stored in environment variables
- [ ] .env.local never committed
- [ ] .env.example is template only
- [ ] credentials are rotated (new ones generated)
- [ ] No secrets in logs
- [ ] API documentation doesn't expose credentials
- [ ] SSL/TLS enabled for all connections
- [ ] Database password changed from default
- [ ] SMTP password is app-specific (Gmail)

## Resources

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Neon Database Security](https://neon.tech/docs/security)
- [Gmail App Passwords](https://myaccount.google.com/apppasswords)
- [detect-secrets Python](https://github.com/Yelp/detect-secrets)
- [Pre-commit Framework](https://pre-commit.com/)

## Questions?

If you're unsure about credential management:
1. Read this guide again
2. Check docs/guides/SETUP.md for setup help
3. Review docs/deployment/DEPLOYMENT.md for production
4. Ask the security team

---

**Remember:** A single exposed credential can compromise your entire application!
