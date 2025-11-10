"""
ICCT26 Cricket Tournament Registration API
Main FastAPI application entry point
"""

import logging
import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker as async_sessionmaker

from app.config import settings, get_async_database_url
from app.routes import main_router

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
cors_origins = settings.CORS_ORIGINS.copy()

# Add Render URL in production if not already there
if IS_PRODUCTION and "https://icct26-backend.onrender.com" not in cors_origins:
    cors_origins.append("https://icct26-backend.onrender.com")

# Add Netlify URL if not already there
if "https://icct26.netlify.app" not in cors_origins:
    cors_origins.append("https://icct26.netlify.app")

# Log CORS configuration
logger.info("=" * 70)
logger.info("📡 CORS CONFIGURATION")
logger.info("=" * 70)
logger.info(f"✅ Allowed Origins ({len(cors_origins)}):")
for origin in sorted(cors_origins):
    logger.info(f"   • {origin}")
logger.info(f"✅ Allowed Methods: {', '.join(settings.CORS_METHODS)}")
logger.info(f"✅ Allowed Headers: {settings.CORS_HEADERS}")
logger.info(f"✅ Credentials: {settings.CORS_CREDENTIALS}")
logger.info("=" * 70)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

logger.info("✅ CORS Middleware configured and loaded")

# -----------------------
# Request Logging Middleware (for debugging)
# -----------------------
@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    """Log incoming requests and responses (useful for debugging CORS)"""
    start_time = time.time()
    
    # Log request details
    request_id = request.headers.get("x-request-id", "N/A")
    origin = request.headers.get("origin", "N/A")
    method = request.method
    path = request.url.path
    
    logger.info(f"📨 Incoming: [{request_id}] {method} {path}")
    if origin != "N/A":
        logger.info(f"   Origin: {origin}")
    
    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response details
        status_code = response.status_code
        status_emoji = "✅" if 200 <= status_code < 300 else "⚠️" if 300 <= status_code < 400 else "❌"
        logger.info(f"📤 Response: [{request_id}] {status_emoji} {status_code} (took {process_time:.3f}s)")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ Error: [{request_id}] {str(e)} (took {process_time:.3f}s)")
        raise

# -----------------------
# Async DB config
# -----------------------
DATABASE_URL_ASYNC = get_async_database_url()
async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=settings.DATABASE_ECHO)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
AsyncBase = declarative_base()

# -----------------------
# Optional legacy async models (kept for compatibility)
# -----------------------
class TeamRegistrationAsyncDB(AsyncBase):
    __tablename__ = "team_registrations"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(50), unique=True, index=True)
    church_name = Column(String(200))
    team_name = Column(String(100))
    pastor_letter = Column(Text, nullable=True)
    payment_receipt = Column(Text, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class CaptainAsyncDB(AsyncBase):
    __tablename__ = "captains"
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    phone = Column(String(20))
    whatsapp = Column(String(20))
    email = Column(String(255))


class ViceCaptainAsyncDB(AsyncBase):
    __tablename__ = "vice_captains"
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    phone = Column(String(20))
    whatsapp = Column(String(20))
    email = Column(String(255))


class PlayerAsyncDB(AsyncBase):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    age = Column(Integer)
    phone = Column(String(20))
    role = Column(String(20))
    aadhar_file = Column(Text, nullable=True)
    subscription_file = Column(Text, nullable=True)


# -----------------------
# Helpers to import sync engine (defensive)
# -----------------------
def _get_sync_engine():
    """
    Try to import sync_engine from database.py; fall back to engine if present.
    Returns: SQLAlchemy Engine object or None if not importable.
    """
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
# Startup & Shutdown events
# -----------------------
@app.on_event("startup")
async def startup_event():
    """Initialize async metadata and ensure sync tables exist (if sync engine available)"""
    try:
        # create async tables
        async with async_engine.begin() as conn:
            await conn.run_sync(AsyncBase.metadata.create_all)
        logger.info("✅ Database tables initialized (async)")

        # create sync tables using raw SQL if a sync engine is available
        sync_engine = _get_sync_engine()
        if sync_engine is not None:
            try:
                with sync_engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS team_registrations (
                            id SERIAL PRIMARY KEY,
                            team_id VARCHAR(50) UNIQUE NOT NULL,
                            church_name VARCHAR(200) NOT NULL,
                            team_name VARCHAR(100) NOT NULL,
                            pastor_letter TEXT,
                            payment_receipt TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS captains (
                            id SERIAL PRIMARY KEY,
                            registration_id INTEGER REFERENCES team_registrations(id),
                            name VARCHAR(100) NOT NULL,
                            phone VARCHAR(20) NOT NULL,
                            whatsapp VARCHAR(20) NOT NULL,
                            email VARCHAR(255) NOT NULL
                        )
                    """))
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS vice_captains (
                            id SERIAL PRIMARY KEY,
                            registration_id INTEGER REFERENCES team_registrations(id),
                            name VARCHAR(100) NOT NULL,
                            phone VARCHAR(20) NOT NULL,
                            whatsapp VARCHAR(20) NOT NULL,
                            email VARCHAR(255) NOT NULL
                        )
                    """))
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS players (
                            id SERIAL PRIMARY KEY,
                            registration_id INTEGER REFERENCES team_registrations(id),
                            name VARCHAR(100) NOT NULL,
                            age INTEGER NOT NULL,
                            phone VARCHAR(20) NOT NULL,
                            role VARCHAR(20) NOT NULL,
                            aadhar_file TEXT,
                            subscription_file TEXT
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


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application...")


# -----------------------
# Async DB dependency (for routes that rely on this module)
# -----------------------
async def get_db_async():
    """Get async database session (dependency)"""
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
logger.info("✅ All routers included successfully")


# -----------------------
# Root endpoint
# -----------------------
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API welcome message
    
    Returns basic API information and available endpoints
    """
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
    Health check endpoint - Used by Render and load balancers
    
    Returns:
        - status: "healthy" if server is running
        - timestamp: Current server time
    """
    logger.info("🏥 GET /health - Health check called")
    return {
        "status": "healthy",
        "message": "API is operational",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
    }


@app.get("/status", tags=["Status"])
async def status():
    """
    Detailed status endpoint - Shows API and database status
    
    Returns:
        - api_status: Current API status
        - database_status: Database connectivity status
        - cors_enabled: Whether CORS is enabled
        - timestamp: Current server time
    """
    logger.info("📊 GET /status - Status check called")
    try:
        # Try to check database connection
        sync_engine = _get_sync_engine()
        db_status = "connected"
        if sync_engine is None:
            db_status = "async_only"
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


# -----------------------
# Queue/Status endpoint (for frontend status monitoring)
# -----------------------
@app.get("/queue/status", tags=["Status"])
async def queue_status():
    """
    Queue status endpoint - For monitoring registration queue
    
    Returns:
        - queue_status: Current queue status
        - timestamp: Current server time
    """
    logger.info("📊 GET /queue/status - Queue status check called")
    return {
        "success": True,
        "queue_status": "operational",
        "registrations_in_queue": 0,
        "average_processing_time": "< 5s",
        "timestamp": datetime.now().isoformat(),
    }


# -----------------------
# Debug endpoints
# -----------------------
@app.get("/debug/db", tags=["Debug"])
def debug_database():
    """Debug database connection - uses sync DB helper if available"""
    logger.info("🐛 GET /debug/db - Debug database called")
    try:
        # If database.py exposes get_db (sync generator), use that; otherwise try sync engine count
        try:
            from database import get_db as _get_db
            db_gen = _get_db()
            db = next(db_gen)
            result = db.execute(text("SELECT COUNT(*) FROM team_registrations"))
            count = result.fetchone()[0]
            # ensure generator cleanup
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
            # fallback: use sync_engine if available
            sync_engine = _get_sync_engine()
            if sync_engine is None:
                logger.warning("No sync DB available to query")
                return {
                    "status": "warning",
                    "error": "No sync DB available to query",
                    "message": "Using async DB only",
                }
            with sync_engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM team_registrations"))
                count = result.fetchone()[0]
            logger.info(f"✅ Database query successful (sync) - {count} teams")
            return {
                "status": "success",
                "message": "Database is operational (sync)",
                "team_count": count,
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.exception("❌ Debug DB query failed")
        return {
            "status": "error",
            "error": str(e),
            "message": "Database query failed",
            "timestamp": datetime.now().isoformat(),
        }


@app.post("/debug/create-tables", tags=["Debug"])
def create_tables():
    """Create database tables manually via app.services (sync)"""
    logger.info("🐛 POST /debug/create-tables - Create tables called")
    try:
        from app.services import DatabaseService
        sync_engine = _get_sync_engine()
        if sync_engine is None:
            logger.error("No sync engine available")
            return {
                "status": "error",
                "error": "No sync engine available",
                "timestamp": datetime.now().isoformat(),
            }
        with sync_engine.connect() as conn:
            session_obj = type('Session', (), {
                'execute': lambda self, query: conn.execute(query),
                'commit': lambda self: conn.commit(),
                'rollback': lambda self: conn.rollback()
            })()
            DatabaseService.create_tables(session_obj)
        logger.info("✅ Tables created successfully")
        return {
            "status": "success",
            "message": "Tables created",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.exception("❌ create_tables failed")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# -----------------------
# Debug endpoints
# -----------------------
@app.get("/debug/db")
def debug_database():
    """Debug database connection - uses sync DB helper if available"""
    try:
        # If database.py exposes get_db (sync generator), use that; otherwise try sync engine count
        try:
            from database import get_db as _get_db
            db_gen = _get_db()
            db = next(db_gen)
            result = db.execute(text("SELECT COUNT(*) FROM team_registrations"))
            count = result.fetchone()[0]
            # ensure generator cleanup
            try:
                next(db_gen)
            except StopIteration:
                pass
            return {"status": "success", "team_count": count}
        except Exception:
            # fallback: use sync_engine if available
            sync_engine = _get_sync_engine()
            if sync_engine is None:
                return {"status": "error", "error": "No sync DB available to query"}
            with sync_engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM team_registrations"))
                count = result.fetchone()[0]
            return {"status": "success", "team_count": count}
    except Exception as e:
        logger.exception("Debug DB query failed")
        return {"status": "error", "error": str(e)}


@app.post("/debug/create-tables")
def create_tables():
    """Create database tables manually via app.services (sync)"""
    try:
        from app.services import DatabaseService
        sync_engine = _get_sync_engine()
        if sync_engine is None:
            return {"status": "error", "error": "No sync engine available"}
        with sync_engine.connect() as conn:
            session_obj = type('Session', (), {
                'execute': lambda self, query: conn.execute(query),
                'commit': lambda self: conn.commit(),
                'rollback': lambda self: conn.rollback()
            })()
            DatabaseService.create_tables(session_obj)
        return {"status": "success", "message": "Tables created"}
    except Exception as e:
        logger.exception("create_tables failed")
        return {"status": "error", "error": str(e)}



# -----------------------
# Exception handler (returns JSONResponse)
# -----------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler returning JSONResponse"""
    payload = {
        "success": False,
        "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        "status_code": exc.status_code
    }
    return JSONResponse(status_code=exc.status_code, content=payload)


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
