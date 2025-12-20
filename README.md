# ICCT26 Cricket Tournament - Backend API

**Production-Ready FastAPI Backend** | Registration System with Payment Approval

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env.local
# Edit .env.local with your credentials

# Run server
uvicorn main:app --reload --port 8000

# Run tests
pytest tests/ -v
```

**Access:** http://localhost:8000 | **Docs:** http://localhost:8000/docs

---

## 📁 Structure

```
app/          # Application code (routes, utils, middleware)
tests/        # Test suite (48 tests)
docs/         # Documentation
scripts/      # Database scripts
main.py       # Entry point
models.py     # Database models
database.py   # DB configuration
```

---

## 🔧 Environment (.env.local)

```env
DATABASE_URL=postgresql+asyncpg://...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SECRET_KEY=GENERATE_SECURE_KEY
CORS_ORIGINS=["https://icct26.netlify.app"]
```

---

## 📊 API Endpoints

### Public
- `POST /api/register` - Register team
- `GET /health` - Health check

### Admin (NEW)
- `GET /admin/teams` - List teams
- `GET /admin/teams/{id}` - Team details
- `POST /admin/payment/approve/{id}` - Approve ⭐
- `POST /admin/payment/reject/{id}` - Reject ⭐

---

## 💰 Payment Flow

1. Team registers → `PENDING_PAYMENT`
2. User pays ₹1,500 via UPI
3. Admin reviews → `APPROVED` / `REJECTED`
4. Email notification sent

---

## 🧪 Testing

✅ **48/48 tests passing**

```bash
pytest tests/ -v
```

---

## 🚀 Deploy

**Render.com (Free):**
1. Push to GitHub
2. Create Web Service on Render
3. Add environment variables
4. Deploy!

See [DEPLOY_NOW.md](DEPLOY_NOW.md) for details.

---

## ✅ Status

- 🟢 All tests passing
- 🟢 Database connected (Neon)
- 🟢 Payment approval working
- 🟢 Production ready

**Frontend:** https://icct26.netlify.app  
**Integration Guide:** [FRONTEND_INTEGRATION_COMPLETE.md](FRONTEND_INTEGRATION_COMPLETE.md)
