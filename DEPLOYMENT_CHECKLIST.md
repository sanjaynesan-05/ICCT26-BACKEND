# 🚀 Pre-Deployment Security Checklist

## Before Committing to Git

- [ ] Run `git status` and verify `.env` is NOT in the changes
- [ ] Verify `.gitignore` includes `.env`
- [ ] Run `git diff --staged` to check for any credentials
- [ ] Verify `README.md` has no real passwords/emails
- [ ] Verify `EXECUTIVE_SUMMARY.txt` has no real passwords
- [ ] Verify all documentation uses placeholders like `[SET_IN_ENV]`

## Before Pushing to Remote (GitHub)

- [ ] Check git log: `git log --all -- .env` (should be empty)
- [ ] Review recent commits for any exposed secrets
- [ ] If found, use `git filter-branch` to remove
- [ ] Force push only if necessary: `git push origin --force`

## Before Deploying to Production

### Environment Variables
- [ ] All credentials are set in platform (Render/Heroku/AWS)
- [ ] Database URL uses production URL
- [ ] SMTP credentials are updated if needed
- [ ] API keys are from production, not development
- [ ] Passwords are strong (20+ characters)

### Code Review
- [ ] No `print()` statements logging sensitive data
- [ ] Error messages don't expose database structure
- [ ] No default credentials in code
- [ ] All database connections use environment variables

### Testing
- [ ] Test all API endpoints with production database
- [ ] Verify email notifications work
- [ ] Test with production credentials
- [ ] Check logs don't contain sensitive info

### Documentation
- [ ] Update `.env.example` if new variables are added
- [ ] No production credentials in code comments
- [ ] No production URLs hardcoded
- [ ] README has setup instructions for developers

## Ongoing Security

### Weekly
- [ ] Check for security advisories in dependencies
- [ ] Review recent commits for accidental secrets
- [ ] Monitor error logs for suspicious activity

### Monthly
- [ ] Rotate credentials if there's been any exposure
- [ ] Update dependencies to patch versions
- [ ] Review API logs for unusual patterns

### Quarterly
- [ ] Full security audit
- [ ] Penetration testing if possible
- [ ] Review access logs and user activity
- [ ] Update this checklist

## Emergency: If Credentials Are Exposed

**Within 5 minutes:**
- [ ] Revoke the exposed credentials immediately
- [ ] Change passwords in all related services
- [ ] Regenerate API keys

**Within 1 hour:**
- [ ] Remove from git history if committed
- [ ] Force push if history was rewritten
- [ ] Notify team of the incident

**Within 24 hours:**
- [ ] Conduct security review
- [ ] Update incident report
- [ ] Implement preventative measures

## Tools to Help

### Git Pre-commit Hook (Prevent accidental commits)
```bash
# Create .git/hooks/pre-commit
#!/bin/bash
if git diff --cached | grep -qE '(password|secret|token|key).*=' | grep -v '.example'; then
    echo "❌ ERROR: Potential secrets detected in commit"
    exit 1
fi
```

### Credential Scanning
```bash
# Scan local files
git grep -n "password\|secret\|token" -- '*.py' '*.md' | grep -v '.example' | grep -v '# '

# Scan git history
git log -p | grep -E '(password|secret|token).*=' | head -20
```

---

**Status**: ✅ Compliant  
**Last Audit**: November 5, 2025
