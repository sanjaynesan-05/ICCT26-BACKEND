# 🏏 ICCT26 Cricket Tournament Backend API# 🏏 ICCT26 Cricket Tournament Backend API



**FastAPI-based asynchronous team registration system** for the **ICCT26 Cricket Tournament** organized by **CSI St. Peter's Church, Coimbatore**.**FastAPI-based asynchronous team registration system** for the **ICCT26 Cricket Tournament** organized by **CSI St. Peter's Church, Coimbatore**.



## 🎯 Event Details## 🎯 Event Details

- **Event:** ICCT26 Cricket Tournament 2026

- **Event:** ICCT26 Cricket Tournament 2026- **Format:** Red Tennis Ball Cricket

- **Format:** Red Tennis Ball Cricket- **Dates:** January 24-26, 2026

- **Dates:** January 24-26, 2026- **Location:** CSI St. Peter's Church Cricket Ground, Coimbatore, Tamil Nadu

- **Location:** CSI St. Peter's Church Cricket Ground, Coimbatore, Tamil Nadu- **Registration Fee:** ₹2,000 per team

- **Registration Fee:** ₹2,000 per team- **Teams per Church:** 1-2 teams

- **Teams per Church:** 1-2 teams- **Players per Team:** 11-15 players

- **Players per Team:** 11-15 players- **Player Age Range:** 15-60 years

- **Player Age Range:** 15-60 years

---

---

## ⚡ Quick Start

## ⚡ Quick Start

### 1. Installation

### 1. Installation

```bash

```bash# Clone repository

git clone <your-repo-url>git clone <your-repo-url>

cd icct26-backendcd icct26-backend

python -m venv venv

venv\Scripts\activate# Create virtual environment

pip install -r requirements.txtpython -m venv venv

```

# Activate virtual environment

### 2. Configuration# Windows:

venv\Scripts\activate

```bash# macOS/Linux:

cp .env.example .envsource venv/bin/activate

# Edit .env with Google credentials and SMTP settings

```# Install dependencies

pip install -r requirements.txt

### 3. Setup Google Credentials```



See [Google Credentials Setup Guide](./docs/GOOGLE_CREDENTIALS_SETUP.md) for detailed instructions.### 2. Configuration



### 4. Run Server```bash

# Copy environment template

```bashcp .env.example .env

uvicorn main:app --reload --host 127.0.0.1 --port 8000

```# Edit .env with your credentials:

# - Google Cloud service account credentials

### 5. Access API# - SMTP credentials for email

# - Google Sheets spreadsheet ID

- **API Home:** <http://localhost:8000>```

- **Swagger UI:** <http://localhost:8000/docs>

- **ReDoc:** <http://localhost:8000/redoc>### 3. Setup Google Credentials

- **Queue Status:** <http://localhost:8000/queue/status>

See [Google Credentials Setup Guide](./docs/GOOGLE_CREDENTIALS_SETUP.md) for detailed instructions.

---

### 4. Run Server

## 🚀 API Endpoints

```bash

### Register Team# Using Uvicorn (recommended)

uvicorn main:app --reload --host 127.0.0.1 --port 8000

```http

POST /register/team# Production deployment

```uvicorn main:app --host 0.0.0.0 --port 8000

```

Register a cricket team with 11-15 players, captain, vice-captain, and required documents.

### 5. Access API

**Request Body:**

- **API Home:** <http://localhost:8000>

```json- **Swagger UI:** <http://localhost:8000/docs>

{- **ReDoc:** <http://localhost:8000/redoc>

  "churchName": "CSI St. Peter's Church",- **Queue Status:** <http://localhost:8000/queue/status>

  "teamName": "Thunder Strikers",

  "pastorLetter": "data:image/png;base64,...",---

  "captain": {

    "name": "John Doe",## 🚀 API Endpoints

    "phone": "+919876543210",

    "whatsapp": "919876543210",### Register Team

    "email": "john.doe@example.com"

  },```http

  "viceCaptain": {POST /register/team

    "name": "Jane Smith",```

    "phone": "+919123456789",

    "whatsapp": "919123456789",Register a cricket team with 11-15 players, captain, vice-captain, and required documents.

    "email": "jane.smith@example.com"

  },**Request Body:**

  "players": [

    {```json

      "name": "Player One",{

      "age": 25,  "churchName": "CSI St. Peter's Church",

      "phone": "+919876543211",  "teamName": "Thunder Strikers",

      "role": "Batsman",  "pastorLetter": "data:image/png;base64,...",

      "aadharFile": "data:image/png;base64,...",  "captain": {

      "subscriptionFile": "data:image/png;base64,..."    "name": "John Doe",

    }    "phone": "+919876543210",

  ],    "whatsapp": "919876543210",

  "paymentReceipt": "data:image/png;base64,..."    "email": "john.doe@example.com"

}  },

```  "viceCaptain": {

    "name": "Jane Smith",

**Response (Success):**    "phone": "+919123456789",

    "whatsapp": "919123456789",

```json    "email": "jane.smith@example.com"

{  },

  "success": true,  "players": [

  "message": "Team registration queued successfully",    {

  "status": "processing",      "name": "Player One",

  "data": {      "age": 25,

    "teamName": "Thunder Strikers",      "phone": "+919876543211",

    "churchName": "CSI St. Peter's Church",      "role": "Batsman",

    "captainName": "John Doe",      "aadharFile": "data:image/png;base64,...",

    "playerCount": 11,      "subscriptionFile": "data:image/png;base64,..."

    "queuedAt": "2026-01-15T10:30:45Z"    }

  }  ],

}  "paymentReceipt": "data:image/png;base64,..."

```}

```

### Get Queue Status

**Response (Success):**

```http

GET /queue/status```json

```{

  "success": true,

Check current registration queue processing status.  "message": "Team registration queued successfully",

  "status": "processing",

**Response:**  "data": {

    "teamName": "Thunder Strikers",

```json    "churchName": "CSI St. Peter's Church",

{    "captainName": "John Doe",

  "queue_size": 3,    "playerCount": 11,

  "worker_active": true,    "queuedAt": "2026-01-15T10:30:45Z"

  "timestamp": "2026-01-15T10:40:15Z"  }

}}

``````



---### Get Queue Status



## ✨ Key Features```http

GET /queue/status

| Feature | Description |```

|---------|-------------|

| 🚀 **Async Processing** | Queue-based system handles high volume |Check current registration queue processing status.

| ✅ **Team Validation** | 11-15 players, age 15-60, auto-validation |

| 📊 **Google Sheets Sync** | Real-time data synchronization |**Response:**

| 📄 **File Support** | Base64 encoded documents and images |

| 📧 **Email Notifications** | Automated HTML confirmation emails |```json

| 🔄 **Duplicate Detection** | Prevents duplicate team registrations |{

| 🏗️ **Nested Structure** | Captain/Vice-Captain as objects |  "queue_size": 3,

| 🔒 **Thread-Safe Queue** | No data loss during concurrent requests |  "worker_active": true,

| 🌐 **CORS Enabled** | Cross-origin requests supported |  "timestamp": "2026-01-15T10:40:15Z"

| 📚 **Auto Documentation** | Swagger UI and ReDoc available |}

```

---

---

## 📊 Data Models

## ✨ Key Features

### PlayerDetails

| Feature | Description |

```python|---------|-------------|

- name: str (required, 2-100 chars)| 🚀 **Asynchronous Processing** | Queue-based registration handles high volume without blocking |

- age: int (required, 15-60)| ✅ **Team Validation** | Enforces 11-15 players with age restrictions (15-60 years) |

- phone: str (required, 10 digits)| 📊 **Google Sheets Sync** | Auto-populate Teams, Players, and Files sheets in real-time |

- role: str (Batsman, Bowler, All-rounder, Wicket-keeper)| 📄 **File Support** | Base64 encoded documents (pastor letters, receipts, Aadhar, subscriptions) |

- aadharFile: str (required, base64)| 📧 **Email Notifications** | Automated HTML confirmation emails after registration |

- subscriptionFile: str (required, base64)| 🔄 **Duplicate Detection** | Prevents team name + payment receipt duplicates |

```| 🏗️ **Nested Structure** | Captain/Vice-Captain as objects, players as array |

| 🔒 **Thread-Safe Queue** | No data loss during concurrent registrations |

### CaptainInfo / ViceCaptainInfo| 🌐 **CORS Enabled** | Cross-origin requests fully supported |

| 📚 **Auto Docs** | Swagger UI and ReDoc for interactive testing |

```python

- name: str (required, 2-100 chars)---

- phone: str (required, 10 digits)

- whatsapp: str (required, 10 digits)## 📊 Data Models

- email: str (required, valid format)

```### PlayerDetails



### TeamRegistration```python

- name: str (required, 2-100 characters)

```python- age: int (required, 15-60)

- churchName: str (required, 2-200 chars)- phone: str (required, 10 digits)

- teamName: str (required, 2-100 chars, unique)- role: str (required, one of: Batsman, Bowler, All-rounder, Wicket-keeper)

- pastorLetter: str (required, base64)- aadharFile: str (required, base64 image)

- captain: CaptainInfo (required)- subscriptionFile: str (required, base64 image)

- viceCaptain: ViceCaptainInfo (required)```

- players: List[PlayerDetails] (required, 11-15)

- paymentReceipt: str (required, base64)### CaptainInfo / ViceCaptainInfo

```

```python

---- name: str (required, 2-100 characters)

- phone: str (required, 10 digits)

## 📚 Documentation- whatsapp: str (required, 10 digits)

- email: str (required, valid email format)

All documentation is organized in the `docs/` folder:```



| Document | Purpose |### TeamRegistration

|----------|---------|

| [docs/README.md](./docs/README.md) | Main overview |```python

| [docs/MODELS_DOCUMENTATION.md](./docs/MODELS_DOCUMENTATION.md) | Complete API reference |- churchName: str (required, 2-200 characters)

| [docs/GOOGLE_CREDENTIALS_SETUP.md](./docs/GOOGLE_CREDENTIALS_SETUP.md) | Google Cloud setup |- teamName: str (required, 2-100 characters, unique per church)

| [docs/REGISTRATION_REFACTOR.md](./docs/REGISTRATION_REFACTOR.md) | React frontend guide |- pastorLetter: str (required, base64 image)

- captain: CaptainInfo (required)

---- viceCaptain: ViceCaptainInfo (required)

- players: List[PlayerDetails] (required, 11-15 items)

## 📁 Project Structure- paymentReceipt: str (required, base64 image)

```

```

icct26-backend/---

├── docs/                          # 📚 Documentation

│   ├── README.md## 📚 Documentation

│   ├── MODELS_DOCUMENTATION.md

│   ├── GOOGLE_CREDENTIALS_SETUP.mdAll documentation is organized in the `docs/` folder:

│   ├── REGISTRATION_REFACTOR.md

│   └── .markdownlint.json| Document | Purpose |

├── main.py                        # 🚀 FastAPI app|----------|---------|

├── requirements.txt               # 📦 Dependencies| **[docs/README.md](./docs/README.md)** | Main project overview (this file) |

├── pyproject.toml                 # 🐍 Config| **[docs/MODELS_DOCUMENTATION.md](./docs/MODELS_DOCUMENTATION.md)** | Complete API reference with request/response examples |

├── test_email.py                  # ✉️ Email tester| **[docs/GOOGLE_CREDENTIALS_SETUP.md](./docs/GOOGLE_CREDENTIALS_SETUP.md)** | Step-by-step Google Cloud setup guide |

├── .env                           # ⚙️ Variables| **[docs/REGISTRATION_REFACTOR.md](./docs/REGISTRATION_REFACTOR.md)** | Frontend React integration guide |

├── .env.example                   # 📋 Template

├── .gitignore                     # 🔒 Git rules---

└── icct26-3d6153f8ac99.json       # 🔑 Credentials (not committed)

```## � Project Structure



---```

icct26-backend/

## ⚙️ Environment Configuration├── docs/                          # 📚 Documentation folder

│   ├── README.md                  # Main project documentation

### Required Variables│   ├── MODELS_DOCUMENTATION.md    # Complete API reference

│   ├── GOOGLE_CREDENTIALS_SETUP.md # Google Cloud setup

```bash│   ├── REGISTRATION_REFACTOR.md   # Frontend integration guide

# Google Cloud Service Account (from service account JSON)│   └── .markdownlint.json         # Markdown linting rules

GOOGLE_CREDENTIALS_TYPE=service_account│

GOOGLE_PROJECT_ID=your-project-id├── main.py                        # 🚀 FastAPI application (core)

GOOGLE_PRIVATE_KEY_ID=your-key-id├── requirements.txt               # 📦 Python dependencies

GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"├── pyproject.toml                 # 🐍 Python project config

GOOGLE_CLIENT_EMAIL=icct26@project.iam.gserviceaccount.com├── test_email.py                  # ✉️ Email testing utility

GOOGLE_CLIENT_ID=your-client-id│

GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth├── .env                          # ⚙️ Environment variables (not committed)

GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token├── .env.example                  # 📋 Environment template

GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs├── .gitignore                    # 🔒 Git ignore rules

GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...├── icct26-3d6153f8ac99.json      # 🔑 Google credentials (not committed)

GOOGLE_UNIVERSE_DOMAIN=googleapis.com│

└── .python-version               # 🐍 Python version specification

# Google Sheets```

SPREADSHEET_ID=your-spreadsheet-id-here

---

# SMTP Email

SMTP_SERVER=smtp.gmail.com## ⚙️ Environment Configuration

SMTP_PORT=587

SMTP_USERNAME=your-email@gmail.com### Required Environment Variables

SMTP_PASSWORD=your-app-password

SMTP_FROM_EMAIL=your-email@gmail.com```bash

SMTP_FROM_NAME=ICCT26 Registration Team# Google Cloud Service Account

GOOGLE_CREDENTIALS_TYPE=service_account

# ServerGOOGLE_PROJECT_ID=your-project-id

PORT=8000GOOGLE_PRIVATE_KEY_ID=your-key-id

ENVIRONMENT=developmentGOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

```GOOGLE_CLIENT_EMAIL=icct26@project.iam.gserviceaccount.com

GOOGLE_CLIENT_ID=your-client-id

### Setup StepsGOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth

GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token

1. **Create `.env` from template:**GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs

GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...

```bashGOOGLE_UNIVERSE_DOMAIN=googleapis.com

cp .env.example .env

```# Google Sheets Configuration

SPREADSHEET_ID=your-spreadsheet-id-here

2. **Add Google credentials** (see [Google Setup Guide](./docs/GOOGLE_CREDENTIALS_SETUP.md))

3. **Create Google Sheet** and share with service account# SMTP Email Configuration

4. **Configure SMTP** (use Gmail app passwords)SMTP_SERVER=smtp.gmail.com

SMTP_PORT=587

---SMTP_USERNAME=your-email@gmail.com

SMTP_PASSWORD=your-app-password

## 🧪 TestingSMTP_FROM_EMAIL=your-email@gmail.com

SMTP_FROM_NAME=ICCT26 Registration Team

### Test Email Configuration

# Server Configuration

```bashPORT=8000

python test_email.pyENVIRONMENT=development

``````



### API Testing with cURL### Setup Steps



```bash1. **Create `.env` file from template:**

curl http://localhost:8000   ```bash

curl http://localhost:8000/queue/status   cp .env.example .env

```   ```



### Interactive Testing2. **Add Google credentials** (see [Google Setup Guide](./docs/GOOGLE_CREDENTIALS_SETUP.md))



- **Swagger UI:** <http://localhost:8000/docs>3. **Create Google Sheet** and share with service account email

- **ReDoc:** <http://localhost:8000/redoc>

4. **Configure SMTP** (Gmail recommended - use app passwords)

---

---

## 🚀 Deployment

## 🧪 Testing

### Local Development

### Test Email Configuration

```bash```bash

pip install -r requirements.txtpython test_email.py

uvicorn main:app --reload --host 127.0.0.1 --port 8000```

```

### API Testing with cURL

### Production with Gunicorn```bash

# Check API health

```bashcurl http://localhost:8000

pip install gunicorn

gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000# Get queue status

```curl http://localhost:8000/queue/status



### Docker Deployment# Register a team (example)

curl -X POST http://localhost:8000/register/team \

```dockerfile  -H "Content-Type: application/json" \

FROM python:3.11-slim  -d @team-registration.json

WORKDIR /app```

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt### Interactive Testing

COPY . .- **Swagger UI:** http://localhost:8000/docs

EXPOSE 8000- **ReDoc:** http://localhost:8000/redoc

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

```---



Build and run:## 🚀 Deployment



```bash### Local Development

docker build -t icct26-backend .```bash

docker run -p 8000:8000 --env-file .env icct26-backend# Install dependencies

```pip install -r requirements.txt



### Production Checklist# Run with auto-reload

uvicorn main:app --reload --host 127.0.0.1 --port 8000

- [ ] Set `ENVIRONMENT=production` in `.env````

- [ ] Use production SMTP credentials

- [ ] Configure Google Sheets access### Production Deployment

- [ ] Set up HTTPS with reverse proxy (nginx/Caddy)

- [ ] Enable firewall restrictions#### Option 1: Uvicorn with Gunicorn

- [ ] Configure monitoring and logging```bash

- [ ] Set up backup strategypip install gunicorn

gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

---```



## 🏗️ Architecture#### Option 2: Docker Deployment

```dockerfile

```FROM python:3.11-slim

Frontend (React)

       ↓WORKDIR /app

FastAPI Server → Validation + CORS

       ↓COPY requirements.txt .

Queue System → Background WorkerRUN pip install --no-cache-dir -r requirements.txt

       ↓

Google Sheets + Email ServiceCOPY . .

```

EXPOSE 8000

---

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

## 📦 Dependencies```



- **FastAPI** 0.104+ - Modern async web frameworkBuild and run:

- **Uvicorn** - ASGI server```bash

- **Pydantic** 2.5.0+ - Data validationdocker build -t icct26-backend .

- **gspread** - Google Sheets APIdocker run -p 8000:8000 --env-file .env icct26-backend

- **google-auth** - Authentication```

- **aiofiles** - Async file operations

- **python-dotenv** - Environment management#### Configuration Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`

See `requirements.txt` for complete list.- [ ] Use production SMTP credentials

- [ ] Configure Google Sheets with proper access

---- [ ] Set up HTTPS with reverse proxy (nginx/Caddy)

- [ ] Enable firewall restrictions

## 🔒 Security Best Practices- [ ] Set up monitoring and logging

- [ ] Configure backup strategy

✅ **Environment Variables** - Credentials in `.env` (not committed)

✅ **Git Ignore** - Sensitive files excluded:---

   - `icct26-3d6153f8ac99.json` - Google credentials

   - `.env` - Environment variables## 🏗️ Architecture

   - `__pycache__/` - Python cache

```

✅ **HTTPS** - Use HTTPS in production┌─────────────────────────────────────────────────────────┐

✅ **CORS** - Configured for frontend│                    Frontend (React)                      │

✅ **Input Validation** - Pydantic models│           POST /register/team with Base64 files          │

✅ **File Validation** - Base64 size limits└────────────────────────┬────────────────────────────────┘

✅ **Duplicate Prevention** - Team + receipt validation                         │

┌────────────────────────▼────────────────────────────────┐

---│                   FastAPI Server                        │

│  ├─ Validation (Pydantic models)                        │

## 📧 Email Configuration│  ├─ CORS Handling                                       │

│  └─ Instant JSON Response                              │

### Gmail Setup (Recommended)└────────────────────────┬────────────────────────────────┘

                         │

1. Go to [Google Account Security](https://myaccount.google.com/security)                    Queue System

2. Enable 2-Step Verification                         │

3. Generate [App Password](https://myaccount.google.com/apppasswords)┌────────────────────────▼────────────────────────────────┐

4. Add to `.env`:│              Background Worker Thread                   │

│  ├─ Extract & Validate Data                            │

```bash│  ├─ Decode Base64 Files                                │

SMTP_USERNAME=your-email@gmail.com│  ├─ Check Duplicates                                   │

SMTP_PASSWORD=your-app-password│  └─ Google Sheets Integration                          │

```└────────────────────────┬────────────────────────────────┘

                         │

### Test Email Setup        ┌────────────────┴────────────────┐

        │                                  │

```bash   ┌────▼────────────┐         ┌──────────▼───────┐

python test_email.py   │ Google Sheets   │         │ Email Service    │

```   │ - Teams sheet   │         │ - Confirmations  │

   │ - Players sheet │         │ - Notifications  │

---   │ - Files sheet   │         │ - HTML templates │

   └─────────────────┘         └──────────────────┘

## 🤝 Contributing```



1. Fork the repository---

2. Create a feature branch

3. Commit your changes## � Dependencies

4. Push to the branch

5. Open a Pull Request- **FastAPI** 0.104+ - Modern async web framework

- **Uvicorn** - ASGI server

---- **Pydantic** 2.5.0+ - Data validation

- **gspread** - Google Sheets API client

## 📞 Support & Troubleshooting- **google-auth** - Google authentication

- **aiofiles** - Async file operations

### Common Issues- **python-dotenv** - Environment variable management



**"ModuleNotFoundError: No module named 'fastapi'"**See `requirements.txt` for complete list with versions.



```bash---

pip install -r requirements.txt

```## 🔒 Security Best Practices



**"Google Sheets API error"**✅ **Environment Variables** - Credentials stored in `.env`, never in code

- Check `SPREADSHEET_ID` in `.env`✅ **Git Ignore** - Sensitive files excluded via `.gitignore`:

- Verify service account has Editor access   - `icct26-3d6153f8ac99.json` - Google credentials

- See [Google Setup Guide](./docs/GOOGLE_CREDENTIALS_SETUP.md)   - `.env` - Environment variables

   - `__pycache__/` - Python cache

**"SMTP authentication failed"**   - `.python-version` - Local version spec

- Use app password, not account password

- Check credentials in `.env`✅ **HTTPS** - Use HTTPS in production with reverse proxy

- Run `python test_email.py`✅ **CORS** - Configured for frontend origin

✅ **Input Validation** - Pydantic models validate all inputs

**"Port 8000 already in use"**✅ **File Size Limits** - Base64 files validated before processing

✅ **Duplicate Prevention** - Team + payment receipt validation

```bash

uvicorn main:app --port 8001---

```

## 📧 Email Configuration

### Documentation

### Gmail Setup (Recommended)

- 📖 [Full API Reference](./docs/MODELS_DOCUMENTATION.md)

- 🔧 [Google Cloud Setup](./docs/GOOGLE_CREDENTIALS_SETUP.md)1. Go to [Google Account Security](https://myaccount.google.com/security)

- ⚛️ [React Frontend Guide](./docs/REGISTRATION_REFACTOR.md)2. Enable 2-Step Verification

- 🌐 [Interactive API Docs](http://localhost:8000/docs)3. Generate [App Password](https://myaccount.google.com/apppasswords)

4. Use app password in `.env`:

---   ```bash

   SMTP_USERNAME=your-email@gmail.com

**Made with ❤️ for ICCT26 Cricket Tournament | 2026**   SMTP_PASSWORD=your-app-password

   ```

### Test Email Setup
```bash
python test_email.py
```

Expected output:
```
Email configuration test
SMTP Server: smtp.gmail.com:587
From: your-email@gmail.com
Status: ✅ Connection successful
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License & Credits

- **Event:** ICCT26 Cricket Tournament 2026
- **Organized by:** CSI St. Peter's Church, Coimbatore
- **Built with:** FastAPI, Pydantic, Google Sheets API, SMTP
- **Tech Stack:** Python 3.11+, async/await, background workers

---

## 📞 Support & Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'fastapi'"**
```bash
pip install -r requirements.txt
```

**"Google Sheets API error"**
- Check `SPREADSHEET_ID` in `.env`
- Verify service account has Editor access to sheet
- See [Google Setup Guide](./docs/GOOGLE_CREDENTIALS_SETUP.md)

**"SMTP authentication failed"**
- Use app password, not account password
- Check SMTP credentials in `.env`
- Run `python test_email.py` to verify

**"Port 8000 already in use"**
```bash
# Use different port
uvicorn main:app --port 8001
```

### Documentation Links
- 📖 [Full API Reference](./docs/MODELS_DOCUMENTATION.md)
- 🔧 [Google Cloud Setup](./docs/GOOGLE_CREDENTIALS_SETUP.md)
- ⚛️ [React Frontend Guide](./docs/REGISTRATION_REFACTOR.md)
- 🌐 [Interactive API Docs](http://localhost:8000/docs)

---

**Made with ❤️ for ICCT26 Cricket Tournament | 2026**
