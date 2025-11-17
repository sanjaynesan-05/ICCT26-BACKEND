"""
ICCT26 Cricket Tournament Registration API
Main FastAPI application entry point
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker as async_sessionmaker

from app.config import settings, get_async_database_url, get_async_engine
from app.routes import main_router

# Initialize Cloudinary
try:
    import cloudinary_config
    cloudinary_config.verify_cloudinary_config()
    logger = logging.getLogger(__name__)
    logger.info("☁️ Cloudinary initialized successfully")
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Cloudinary initialization failed: {str(e)}")
    logger.warning("⚠️ File uploads will use Base64 fallback mode")

# -----------------------
# Logging Configuration
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# -----------------------
# FastAPI app initialization
# -----------------------
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

logger.info(f"🚀 Initializing FastAPI application ({ENVIRONMENT})")

# -----------------------
# CORS Middleware - MUST be added BEFORE any routes
# -----------------------
origins = [
    # Production domains
    "https://icct26.netlify.app",
    "https://www.icct26.netlify.app",
    "https://icct26-admin.vercel.app",          # Admin panel production
    "https://production-domain.com",             # Main production domain
    
    # Development/Local
    "http://localhost:3000",                     # React dev server
    "http://localhost:5173",                     # Vite dev server
    "http://127.0.0.1:3000",                     # React dev server (127.0.0.1)
    "http://127.0.0.1:5173",                     # Vite dev server (127.0.0.1)
]

logger.info("=" * 70)
logger.info("📡 CORS CONFIGURATION")
logger.info("=" * 70)
logger.info(f"✅ Allowed Origins ({len(origins)}):")
for origin in sorted(origins):
    logger.info(f"   • {origin}")
logger.info(f"✅ Allowed Methods: * (GET, POST, PUT, DELETE, OPTIONS, etc.)")
logger.info(f"✅ Allowed Headers: * (all headers)")
logger.info(f"✅ Expose Headers: * (all headers)")
logger.info(f"✅ Credentials: True")
logger.info("=" * 70)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

logger.info("✅ CORS Middleware configured and loaded")

# -----------------------
# Request Logging Middleware (for debugging)
# -----------------------
@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    """Log incoming requests and responses (useful for debugging CORS)"""
    start_time = time.time()

    request_id = request.headers.get("x-request-id", "N/A")
    origin = request.headers.get("origin", "N/A")
    method = request.method
    path = request.url.path

    logger.info(f"📨 Incoming: [{request_id}] {method} {path}")
    if origin != "N/A":
        logger.info(f"   Origin: {origin}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        status_code = response.status_code
        status_emoji = "✅" if 200 <= status_code < 300 else "⚠️" if 300 <= status_code < 400 else "❌"
        logger.info(f"📤 Response: [{request_id}] {status_emoji} {status_code} (took {process_time:.3f}s)")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ Error: [{request_id}] {str(e)} (took {process_time:.3f}s)")
        raise

# -----------------------
# Async DB config (Neon-optimized)
# -----------------------
DATABASE_URL_ASYNC = get_async_database_url()
async_engine = get_async_engine()  # 🔥 Uses optimized engine with timeouts, SSL, and pool settings
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
AsyncBase = declarative_base()

# -----------------------
# Async models (compatibility)
# NOTE: use same table names as rest of project -> "teams", "players"
# -----------------------
class TeamAsyncDB(AsyncBase):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(50), unique=True, index=True)
    church_name = Column(String(200))
    team_name = Column(String(100))
    pastor_letter = Column(Text, nullable=True)
    payment_receipt = Column(Text, nullable=True)
    registration_date = Column(DateTime)
    created_at = Column(DateTime)


class CaptainAsyncDB(AsyncBase):
    __tablename__ = "captains"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(50), ForeignKey("teams.team_id"))
    name = Column(String(100))
    phone = Column(String(20))
    whatsapp = Column(String(20))
    email = Column(String(255))


class ViceCaptainAsyncDB(AsyncBase):
    __tablename__ = "vice_captains"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(50), ForeignKey("teams.team_id"))
    name = Column(String(100))
    phone = Column(String(20))
    whatsapp = Column(String(20))
    email = Column(String(255))


class PlayerAsyncDB(AsyncBase):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(50), ForeignKey("teams.team_id"))
    name = Column(String(100))
    age = Column(Integer)
    phone = Column(String(20))
    role = Column(String(50))
    aadhar_file = Column(Text, nullable=True)
    subscription_file = Column(Text, nullable=True)

# -----------------------
# Helpers to import sync engine (defensive)
# -----------------------
def _get_sync_engine():
    try:
        from database import sync_engine as se
        logger.debug("Using database.sync_engine")
        return se
    except Exception:
        try:
            from database import engine as e
            logger.debug("Using database.engine")
            return e
        except Exception:
            logger.warning("No sync engine available in database.py (sync table creation will be skipped).")
            return None


# -----------------------
# Neon DB Keep-Alive Task
# -----------------------
async def keep_neon_awake():
    """
    Background task that pings Neon database every 10 minutes.
    Prevents Neon from idling and causing cold-start delays.
    This task starts on app startup and runs indefinitely.
    """
    ping_interval = 600  # 10 minutes
    logger.info("🌙 Starting Neon keep-alive background task (pings every 10 min)")
    
    while True:
        try:
            await asyncio.sleep(ping_interval)
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("🌙 Neon DB pinged to stay awake")
        except Exception as e:
            logger.warning(f"⚠️ Neon keep-alive ping failed: {e}")
            # Don't crash the app, just log and continue

# -----------------------
# Startup & Shutdown events
# -----------------------
@app.on_event("startup")
async def startup_event():
    """Initialize async metadata, ensure sync tables exist, and warm up Neon DB"""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(AsyncBase.metadata.create_all)
        logger.info("✅ Database tables initialized (async)")
        
        # 🔥 Warm up Neon by pinging it early
        try:
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("🌡️ Neon database warmed up successfully (connection established)")
        except Exception as warmup_err:
            logger.warning(f"⚠️ Neon warmup ping failed: {warmup_err}")

        sync_engine = _get_sync_engine()
        if sync_engine is not None:
            try:
                with sync_engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS teams (
                            id SERIAL PRIMARY KEY,
                            team_id VARCHAR(50) UNIQUE NOT NULL,
                            team_name VARCHAR(100) NOT NULL,
                            church_name VARCHAR(200) NOT NULL,
                            captain_name VARCHAR(100),
                            captain_phone VARCHAR(20),
                            captain_email VARCHAR(255),
                            captain_whatsapp VARCHAR(20),
                            vice_captain_name VARCHAR(100),
                            vice_captain_phone VARCHAR(20),
                            vice_captain_email VARCHAR(255),
                            vice_captain_whatsapp VARCHAR(20),
                            payment_receipt TEXT,
                            pastor_letter TEXT,
                            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS players (
                            id SERIAL PRIMARY KEY,
                            team_id VARCHAR(50) REFERENCES teams(team_id),
                            player_id VARCHAR(50),
                            name VARCHAR(100) NOT NULL,
                            age INTEGER NOT NULL,
                            phone VARCHAR(20) NOT NULL,
                            role VARCHAR(50) NOT NULL,
                            aadhar_file TEXT,
                            subscription_file TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    conn.commit()
                logger.info("✅ Database tables initialized (sync)")
            except Exception as sync_err:
                logger.warning(f"[WARNING] Sync table creation failed: {sync_err}")
                logger.warning("   Make sure the sync DB is configured correctly if you rely on these tables.")
        else:
            logger.info("Skipping sync table creation because no sync engine was found in database.py")
    except Exception as e:
        logger.warning(f"[WARNING] Database initialization warning: {e}")
        logger.warning("   Make sure PostgreSQL is running and DATABASE_URL is correct")
    
    # 🌙 Start background task to keep Neon awake
    asyncio.create_task(keep_neon_awake())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")

# -----------------------
# Async DB dependency (for routes that rely on this module)
# -----------------------
async def get_db_async():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# -----------------------
# Include routers
# -----------------------
logger.info("📍 Including application routers...")
app.include_router(main_router)

# Include new multipart upload router
from app.routes import registration_multipart
app.include_router(registration_multipart.router, prefix="/api", tags=["Registration-Multipart"])
logger.info("✅ Multipart upload router included")

logger.info("✅ All routers included successfully")

# -----------------------
# Root endpoint
# -----------------------
@app.get("/", tags=["Root"])
async def root():
    logger.info("📍 GET / - Root endpoint called")
    return {
        "success": True,
        "message": "ICCT26 Cricket Tournament Registration API",
        "version": settings.APP_VERSION,
        "environment": ENVIRONMENT,
        "status": "operational",
        "available_endpoints": {
            "health": "/health",
            "status": "/status",
            "register_team": "POST /api/register/team",
            "teams": "GET /api/teams",
            "admin_teams": "GET /admin/teams",
            "documentation": "/docs",
            "docs_alt": "/redoc",
        },
        "cors_enabled": True,
        "frontend_url": "https://icct26.netlify.app",
        "timestamp": datetime.now().isoformat(),
    }

# -----------------------
# Health and Status endpoints (additional to router ones)
# -----------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check that pings Neon DB to prevent idle sleep.
    Returns database connection status.
    """
    logger.info("🏥 GET /health - Health check called")
    
    db_status = "unknown"
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.warning(f"Database ping failed: {e}")
        db_status = "error"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database_status": db_status,
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
    }

@app.get("/status", tags=["Status"])
async def status():
    logger.info("📊 GET /status - Status check called")
    try:
        sync_engine = _get_sync_engine()
        db_status = "connected" if sync_engine is not None else "async_only"
    except Exception as e:
        logger.warning(f"Database status check failed: {e}")
        db_status = "error"

    return {
        "success": True,
        "api_status": "operational",
        "database_status": db_status,
        "cors_enabled": True,
        "environment": ENVIRONMENT,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
    }

@app.get("/queue/status", tags=["Status"])
async def queue_status():
    logger.info("📊 GET /queue/status - Queue status check called")
    return {
        "success": True,
        "queue_status": "operational",
        "registrations_in_queue": 0,
        "average_processing_time": "< 5s",
        "timestamp": datetime.now().isoformat(),
    }

# -----------------------
# Debug endpoints (single definitions only)
# -----------------------
@app.get("/debug/db", tags=["Debug"])
def debug_database():
    logger.info("🐛 GET /debug/db - Debug database called")
    try:
        from database import get_db as _get_db
        db_gen = _get_db()
        db = next(db_gen)
        result = db.execute(text("SELECT COUNT(*) FROM teams"))
        count = result.fetchone()[0]
        try:
            next(db_gen)
        except StopIteration:
            pass
        logger.info(f"✅ Database query successful - {count} teams")
        return {
            "status": "success",
            "message": "Database is operational",
            "team_count": count,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception:
        sync_engine = _get_sync_engine()
        if sync_engine is None:
            logger.warning("No sync DB available to query")
            return {
                "status": "warning",
                "error": "No sync DB available to query",
                "message": "Using async DB only",
            }
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM teams"))
            count = result.fetchone()[0]
        logger.info(f"✅ Database query successful (sync) - {count} teams")
        return {
            "status": "success",
            "message": "Database is operational (sync)",
            "team_count": count,
            "timestamp": datetime.now().isoformat(),
        }

@app.post("/debug/create-tables", tags=["Debug"])
def create_tables():
    logger.info("🐛 POST /debug/create-tables - Create tables called")
    try:
        from app.services import DatabaseService
        sync_engine = _get_sync_engine()
        if sync_engine is None:
            logger.error("No sync engine available")
            return {"status": "error", "error": "No sync engine available", "timestamp": datetime.now().isoformat()}
        with sync_engine.connect() as conn:
            session_obj = type('Session', (), {
                'execute': lambda self, query: conn.execute(query),
                'commit': lambda self: conn.commit(),
                'rollback': lambda self: conn.rollback()
            })()
            DatabaseService.create_tables(session_obj)
        logger.info("✅ Tables created successfully")
        return {"status": "success", "message": "Tables created", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.exception("❌ create_tables failed")
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

# -----------------------
# Exception handlers (return JSONResponse)
# -----------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    payload = {
        "success": False,
        "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        "status_code": exc.status_code
    }
    return JSONResponse(status_code=exc.status_code, content=payload)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field_path = " -> ".join(str(loc) for loc in first_error.get("loc", []))
    error_msg = first_error.get("msg", "Validation error")
    error_type = first_error.get("type", "value_error")
    logger.error(f"Validation error on {request.url.path}: {errors}")

    def sanitize_error(err):
        clean = {}
        for key, value in err.items():
            if key == "ctx" and isinstance(value, dict):
                clean[key] = {k: str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v 
                              for k, v in value.items()}
            elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
                clean[key] = value
            elif isinstance(value, tuple):
                clean[key] = list(value)
            else:
                clean[key] = str(value)
        return clean

    sanitized_errors = [sanitize_error(err) for err in errors]

    payload = {
        "success": False,
        "message": f"Validation failed: {error_msg}",
        "field": field_path,
        "error_type": error_type,
        "details": sanitized_errors if len(sanitized_errors) <= 5 else sanitized_errors[:5],
        "status_code": 422
    }

    return JSONResponse(status_code=422, content=payload)

# -----------------------
# Main entry
# -----------------------
if __name__ == "__main__":
    import uvicorn
    port = settings.PORT
    logger.info(f"\n{'='*60}")
    logger.info(f"[STARTING] {settings.APP_TITLE}")
    logger.info(f"   Version: {settings.APP_VERSION}")
    logger.info(f"   Starting on {settings.HOST}:{port}...")
    logger.info(f"   Docs: http://{settings.HOST}:{port}/docs")
    logger.info(f"   ReDoc: http://{settings.HOST}:{port}/redoc")
    logger.info(f"{'='*60}\n")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=port,
        reload=settings.RELOAD,
        log_level="info"
    )
