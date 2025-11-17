# 🚀 ICCT26 Backend - Setup & Deployment Guide

## 📋 Current Setup Status

✅ **Your setup is READY for production!**

### Current Configuration:
- **Framework**: FastAPI (Async)
- **Database**: Render PostgreSQL Cloud
- **ORM**: SQLAlchemy 2.0 (Async)
- **Driver**: asyncpg
- **Server**: Uvicorn
- **Email**: Gmail SMTP
- **Status**: ✅ Production-Ready

---

## 🔧 Configuration Options

### Option 1: Use Render Cloud Database (RECOMMENDED FOR PRODUCTION)

Your `.env` is already configured for Render:
```env
DATABASE_URL=postgresql+asyncpg://your-db-user:your-db-password@your-render-host.oregon-postgres.render.com/icct26_db
```

**✅ This is the recommended setup for production deployment!**

#### How to deploy to production:
1. Push your code to GitHub
2. Connect your repo to Render
3. Render will auto-deploy when you push
4. Your database is already created on Render

---

### Option 2: Use Local PostgreSQL (FOR DEVELOPMENT)

If you want to develop locally with your local database, uncomment this in `.env`:

```env
# Local Development (uncomment to use local PostgreSQL instead of Render)
DATABASE_URL=postgresql+asyncpg://postgres:your-db-password@localhost:5432/icct26_db
```

Then comment out the Render URL:
```env
# DATABASE_URL=postgresql+asyncpg://your-db-user:your-db-password@your-render-host.oregon-postgres.render.com/icct26_db
```

---

## 📦 Dependencies Required

All dependencies are in `requirements.txt`:

```
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
python-dotenv>=1.0.0
email-validator>=2.3.0
asyncpg>=0.29.0
sqlalchemy>=2.0.0
alembic>=1.12.0
```

✅ **Already installed in your venv**

---

## 🚀 Running the Server

### Local Development:
```powershell
cd "d:\ICCT26 BACKEND"
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### With Render Database (Production):
```powershell
cd "d:\ICCT26 BACKEND"
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

⚠️ **Note**: The command is the same! The database URL is read from `.env`

---

## 🔍 Check Database Connection

### Method 1: API Endpoint
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/teams" -Method GET | Select-Object -ExpandProperty Content
```

### Method 2: Inspection Script
```powershell
python inspect_db.py
```

### Method 3: Terminal (pgAdmin)
```powershell
# Open pgAdmin at: http://localhost:5050
# Connection: Render PostgreSQL (if using Render)
```

---

## 🌐 Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/status` | GET | API status & config |
| `/teams` | GET | List all registered teams |
| `/queue/status` | GET | Queue status |
| `/register/team` | POST | Register new team |
| `/docs` | GET | Swagger API docs |
| `/redoc` | GET | ReDoc API docs |

---

## 📊 Database Schema

Your database has 4 tables:

```
team_registrations
├── id (INT, PK)
├── team_id (STRING, UNIQUE)
├── church_name (STRING)
├── team_name (STRING)
├── pastor_letter (TEXT, nullable)
├── payment_receipt (TEXT, nullable)
├── created_at (DATETIME)
└── updated_at (DATETIME)

captains
├── id (INT, PK)
├── registration_id (INT, FK)
├── name (STRING)
├── phone (STRING)
├── whatsapp (STRING)
├── email (STRING)

vice_captains
├── id (INT, PK)
├── registration_id (INT, FK)
├── name (STRING)
├── phone (STRING)
├── whatsapp (STRING)
├── email (STRING)

players
├── id (INT, PK)
├── registration_id (INT, FK)
├── name (STRING)
├── age (INT)
├── phone (STRING)
├── role (STRING)
├── aadhar_file (TEXT)
└── subscription_file (TEXT)
```

---

## 🔐 Security Notes

### Credentials in `.env` (SENSITIVE)
- **Database User**: your-db-user
- **Database Password**: your-secure-db-password
- **Gmail App Password**: your-app-specific-password
- **Gmail Username**: your-email@gmail.com

⚠️ **IMPORTANT**: 
- Never commit `.env` to git!
- Change these credentials periodically
- Use environment variables in production
- Add `.env` to `.gitignore`

### `.gitignore` should include:
```
.env
venv/
__pycache__/
*.pyc
.DS_Store
```

---

## 📱 Connecting Frontend

Your backend is ready to accept requests from any frontend!

### Example Frontend Call:
```javascript
// JavaScript/React
const registerTeam = async (teamData) => {
  const response = await fetch('http://127.0.0.1:8000/register/team', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(teamData)
  });
  return response.json();
};
```

### Required Request Body:
```json
{
  "teamName": "Team Name",
  "churchName": "Church Name",
  "captain": {
    "name": "Captain Name",
    "phone": "+91...",
    "whatsapp": "9876...",
    "email": "captain@example.com"
  },
  "viceCaptain": {
    "name": "Vice Captain Name",
    "phone": "+91...",
    "whatsapp": "9876...",
    "email": "vicecaptain@example.com"
  },
  "players": [
    {
      "name": "Player 1",
      "age": 25,
      "phone": "+91...",
      "role": "Batsman",
      "aadharFile": "base64_encoded_pdf",
      "subscriptionFile": "base64_encoded_pdf"
    }
    // ... 10 more players (11 total)
  ]
}
```

---

## 🚢 Deployment to Render

### Step 1: Push to GitHub
```bash
git add .
git commit -m "ICCT26 Backend - Production Ready"
git push origin main
```

### Step 2: Create Render Service
1. Go to https://render.com
2. Click "New +"
3. Select "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: icct26-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - **Environment Variables**: Add all from `.env`

### Step 3: Deploy
- Render will auto-deploy on every push
- Your API will be live at: `https://icct26-backend.onrender.com`

---

## 🐛 Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver
```
**Solution**: Ensure `DATABASE_URL` has `postgresql+asyncpg://` prefix

### Port Already in Use
```powershell
# Change port
uvicorn main:app --reload --port 8001
```

### CORS Errors
Frontend and backend are on different domains?
- Backend is already configured with CORS
- Check `main.py` around line 400

### Email Not Sending
- Check Gmail credentials in `.env`
- Generate App Password at: https://myaccount.google.com/apppasswords
- Ensure 2FA is enabled on Gmail

---

## 📝 Environment Variables Quick Reference

| Variable | Value | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | postgres://... | Database connection |
| `SMTP_SERVER` | smtp.gmail.com | Email service |
| `SMTP_USERNAME` | your-email@gmail.com | Email login |
| `SMTP_PASSWORD` | your-app-specific-password | Email password |
| `PORT` | 8000 | Server port |
| `ENVIRONMENT` | production | App environment |

---

## ✅ Checklist Before Production

- [ ] `.env` file properly configured
- [ ] `.gitignore` includes `.env`
- [ ] All tests passing
- [ ] Database tables created
- [ ] Sample data in database
- [ ] Frontend can connect to API
- [ ] Email notifications working
- [ ] CORS configured correctly
- [ ] Logging configured
- [ ] Error handling implemented
- [ ] Rate limiting configured
- [ ] API documentation updated

---

## 🎯 Next Steps

1. **Test the API** using Swagger docs at `http://127.0.0.1:8000/docs`
2. **Connect your frontend** to the backend
3. **Deploy to Render** when ready for production
4. **Monitor logs** on Render dashboard
5. **Set up CI/CD** for automated testing

---

## 📞 Quick Links

- **Render Dashboard**: https://dashboard.render.com
- **Render PostgreSQL**: oregon-postgres.render.com
- **Gmail App Passwords**: https://myaccount.google.com/apppasswords
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org

---

**Last Updated**: November 5, 2025  
**Status**: ✅ Production Ready  
**Database**: ✅ Render PostgreSQL Connected
