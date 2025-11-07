# 🔐 Security Guide - ICCT26 Backend

## ⚠️ CRITICAL: Never Commit Secrets to Git

Your repository had hardcoded credentials detected by GitGuardian. This guide ensures it never happens again.

---

## 🚨 What Was Fixed

| File | Issue | Status |
|------|-------|--------|
| `.env` | Database & SMTP credentials | ✅ Removed from commits |
| `EXECUTIVE_SUMMARY.txt` | Hardcoded passwords | ✅ Replaced with placeholders |
| `.gitignore` | Already configured | ✅ Verified |
| `.env.example` | Template for developers | ✅ Updated safely |

---

## 📋 Environment Variables Setup

### Step 1: Copy the Template
```bash
cp .env.example .env
```

### Step 2: Edit .env with YOUR Values
```bash
# Edit .env file with your actual credentials
code .env
```

### Step 3: Verify .gitignore
Ensure `.env` is in `.gitignore`:
```
.env
.env.local
.env.*.local
.env.production
```

---

## 🔑 Required Credentials

### Database Credentials
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/icct26_db
```

**Generate/Get from:**
- PostgreSQL installation
- Render Dashboard (for production)

### SMTP Credentials (Gmail)
```env
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # NOT your Gmail password!
```

**How to get Gmail App Password:**
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer" (or your device)
3. Copy the 16-character password
4. Paste it in `.env` as `SMTP_PASSWORD`

### Google Drive/Sheets (Optional)
```env
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
SPREADSHEET_ID=your-spreadsheet-id
```

**How to get:**
- Drive: Right-click folder → Share → Copy folder ID from URL
- Sheets: Open spreadsheet → ID is in the URL

---

## ✅ Security Checklist

Before committing code:

- [ ] `.env` is NOT staged for commit
- [ ] `.env.example` has only placeholders
- [ ] `.gitignore` includes `.env` and other secret files
- [ ] No credentials in code files (main.py, models.py, etc.)
- [ ] No credentials in documentation files
- [ ] Run `git status` and verify `.env` is not listed

### Check if `.env` is already committed (if yes, revoke credentials!)

```bash
# Check git history for .env
git log --all -- .env

# If found, your credentials are exposed - regenerate them immediately!
```

---

## 🛡️ Deployment Security

### For Production (Render/Heroku/AWS)

1. **Do NOT use local `.env`**
2. **Use platform's environment variable management**

**Example - Render Dashboard:**
- Go to Service Settings
- Click "Environment"
- Add each variable from `.env.example`
- Render will encrypt and secure them

**Example - GitHub Secrets (for CI/CD):**
```yaml
# .github/workflows/deploy.yml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
```

---

## 🚨 If Credentials Are Exposed

**IMMEDIATELY:**

1. **Revoke the compromised credentials:**
   - Gmail: Change password & app password
   - Database: Change password in PostgreSQL
   - API Keys: Regenerate in respective dashboards

2. **Remove from git history:**
   ```bash
   # Remove .env from git history
   git filter-branch --tree-filter 'rm -f .env' HEAD
   git push origin --force
   ```

3. **Rotate credentials in all environments**

---

## 📚 File-by-File Security

### ✅ `.env` (NEVER COMMIT)
```
❌ Contains: Real passwords, API keys, credentials
✅ Protected by: .gitignore
✅ Use: Locally only, environment variables in production
```

### ✅ `.env.example` (CAN COMMIT)
```
✅ Contains: Only placeholder values
✅ Purpose: Template for developers
✅ Instructions: Copy to .env and fill your values
```

### ✅ `main.py` (CAN COMMIT)
```
✅ Contains: Code, not secrets
✅ Rule: Never hardcode passwords/keys
✅ Instead: Read from environment variables using os.getenv()
```

### ✅ `README.md` (CAN COMMIT)
```
✅ Contains: Documentation, examples with placeholders
✅ Never: Include real credentials in examples
```

---

## 🔍 Automated Secret Detection

This repo uses **GitGuardian** to detect secrets. If you see alerts:

1. **Review the flagged file**
2. **Remove/replace credentials**
3. **Verify `.gitignore` is correct**
4. **Force-push if needed** (if committed):
   ```bash
   git filter-branch --tree-filter 'rm -f .env' HEAD
   git push origin --force
   ```

---

## 📝 Best Practices

### DO ✅
- Use `.env` for local development
- Use environment variables in production
- Rotate credentials regularly
- Use strong passwords (20+ characters)
- Use app-specific passwords (Gmail)
- Document which env vars are required

### DON'T ❌
- Commit `.env` to git
- Hardcode credentials in source code
- Use same password for multiple services
- Share `.env` files via email/chat
- Use generic passwords like "password123"
- Expose secrets in error messages/logs

---

## 🔐 Current Status

| Check | Status | Evidence |
|-------|--------|----------|
| `.env` excluded | ✅ | .gitignore configured |
| `.env.example` safe | ✅ | Only placeholders |
| Credentials rotated | ⚠️ | Change these if exposed |
| Documentation safe | ✅ | No real secrets in docs |

---

## 📞 Quick Reference

**Start development safely:**
```bash
# 1. Copy template
cp .env.example .env

# 2. Edit with your values
nano .env

# 3. Verify before committing
git status  # Should NOT show .env

# 4. Start server
uvicorn main:app --reload
```

---

**Last Updated**: November 5, 2025  
**Security Level**: 🟢 Compliant  
**Next Review**: Quarterly or after deployment
