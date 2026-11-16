"""
ICCT26 Cricket Tournament Registration API
Main FastAPI application entry point
Production-hardened with complete feature set
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

# Production configuration and imports
from config import settings
from app.utils.structured_logging import setup_logging, get_logger
from app.utils.global_exception_handler import setup_global_exception_handlers
from app.middleware.production_middleware import setup_middleware
from app.utils.database_hardening import setup_database_healthcheck, teardown_database, DatabasePooling
from app.config import get_async_database_url, get_async_engine
from app.routes import main_router

# Initialize structured logging
logger = setup_logging(
    "icct26_backend",
    log_file=settings.LOG_FILE if settings.LOG_TO_FILE else None,
    log_level=settings.LOG_LEVEL
)

# Get environment
ENVIRONMENT = settings.ENVIRONMENT
IS_PRODUCTION = ENVIRONMENT == "production"

logger.debug("Initializing ICCT26 Backend (env=%s)", ENVIRONMENT)

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

logger.debug("FastAPI application initialized (v%s)", settings.APP_VERSION)

# -----------------------
# Setup Global Exception Handlers (MUST be first)
# -----------------------
setup_global_exception_handlers(app)
logger.debug("Global exception handlers configured")

# -----------------------
# Setup Production Middleware Suite
# -----------------------
setup_middleware(app)
logger.debug("Production middleware suite configured")

# -----------------------
# CORS Configuration (from settings)
# -----------------------
logger.debug("CORS origins: %s", settings.CORS_ORIGINS)

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
    team_name = Column(String(100))
    church_name = Column(String(200))
    
    # Captain information
    captain_name = Column(String(100))
    captain_phone = Column(String(15))
    captain_email = Column(String(255))
    captain_whatsapp = Column(String(20), nullable=True)
    
    # Vice-Captain information
    vice_captain_name = Column(String(100))
    vice_captain_phone = Column(String(15))
    vice_captain_email = Column(String(255))
    vice_captain_whatsapp = Column(String(20), nullable=True)
    
    # File uploads
    pastor_letter = Column(Text, nullable=True)
    payment_receipt = Column(Text, nullable=True)
    group_photo = Column(Text, nullable=True)  # 🔥 CRITICAL: Added missing column!
    
    # Timestamps
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
    player_id = Column(String(50), unique=True, nullable=False, index=True)  # 🔥 CRITICAL: Added missing column!
    team_id = Column(String(50), ForeignKey("teams.team_id"))
    name = Column(String(100))
    role = Column(String(50))
    aadhar_file = Column(Text, nullable=True)
    subscription_file = Column(Text, nullable=True)
    created_at = Column(DateTime)  # 🔥 CRITICAL: Added missing column!

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
    logger.debug("Neon keep-alive task started (every %ss)", ping_interval)
    
    while True:
        try:
            await asyncio.sleep(ping_interval)
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.debug("Neon keep-alive ping ok")
        except Exception as e:
            logger.warning(f"Neon keep-alive ping failed: {e}")
            # Don't crash the app, just log and continue

# -----------------------
# Startup & Shutdown events
# -----------------------
startup_log = logging.getLogger("startup")

_LEVEL_FOR_STATUS = {"OK": logging.INFO, "SKIP": logging.INFO, "WARN": logging.WARNING, "FAIL": logging.ERROR}


class StartupReport:
    """Runs startup steps, logging ONE line per step with status + duration."""

    def __init__(self):
        self.t0 = time.perf_counter()
        self.rows = []  # (status, step, detail)

    def record(self, step: str, status: str, detail: str = "", secs: float = 0.0):
        self.rows.append((status, step, detail))
        startup_log.log(_LEVEL_FOR_STATUS.get(status, logging.INFO),
                        f"{step:<13} {status:<4} {detail}" + (f" ({secs:.1f}s)" if secs >= 0.05 else ""))
        return status

    async def run(self, step: str, fn):
        """fn is an async callable returning (status, detail). Exceptions are recorded as FAIL."""
        start = time.perf_counter()
        try:
            status, detail = await fn()
        except Exception as e:
            status, detail = "FAIL", f"{type(e).__name__}: {e}"
        return self.record(step, status, detail, time.perf_counter() - start)

    def count(self, status: str) -> int:
        return sum(1 for r in self.rows if r[0] == status)


async def _ensure_hardening_tables():
    async with async_engine.begin() as conn:
        # team_sequence for race-safe IDs
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS team_sequence (
                id INTEGER PRIMARY KEY,
                last_number INTEGER NOT NULL DEFAULT 0
            )
        """))
        await conn.execute(text("""
            INSERT INTO team_sequence (id, last_number)
            VALUES (1, 0)
            ON CONFLICT (id) DO NOTHING
        """))
        # idempotency_keys for duplicate prevention
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS idempotency_keys (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                response_data TEXT,
                expires_at TIMESTAMP NULL,
                endpoint VARCHAR(100) NOT NULL DEFAULT '/api/register/team',
                request_fingerprint VARCHAR(64),
                state VARCHAR(20) NOT NULL DEFAULT 'processing',
                team_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        # teams.church_name_normalized, its UNIQUE index and registration_status
        # are managed by scripts/migrate_2027.py, not at startup.
        await conn.execute(text("""
            ALTER TABLE idempotency_keys ADD COLUMN IF NOT EXISTS endpoint VARCHAR(100) NOT NULL DEFAULT '/api/register/team'
        """))
        await conn.execute(text("""
            ALTER TABLE idempotency_keys ADD COLUMN IF NOT EXISTS request_fingerprint VARCHAR(64)
        """))
        await conn.execute(text("""
            ALTER TABLE idempotency_keys ADD COLUMN IF NOT EXISTS state VARCHAR(20) NOT NULL DEFAULT 'processing'
        """))
        await conn.execute(text("""
            ALTER TABLE idempotency_keys ADD COLUMN IF NOT EXISTS team_id VARCHAR(50)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_idempotency_key ON idempotency_keys(key)
        """))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'uq_team_name_captain_phone'
                ) THEN
                    ALTER TABLE teams
                    ADD CONSTRAINT uq_team_name_captain_phone
                    UNIQUE (team_name, captain_phone);
                END IF;
            END $$;
        """))


def _ensure_sync_tables(sync_engine):
    with sync_engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS teams (
                id SERIAL PRIMARY KEY,
                team_id VARCHAR(50) UNIQUE NOT NULL,
                team_name VARCHAR(100) NOT NULL,
                church_name VARCHAR(200) NOT NULL,
                church_name_normalized VARCHAR(200),
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
                group_photo TEXT,
                registration_status VARCHAR(20) NOT NULL DEFAULT 'pending',
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                player_id VARCHAR(50) UNIQUE NOT NULL,
                team_id VARCHAR(50) REFERENCES teams(team_id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                role VARCHAR(50),
                aadhar_file TEXT,
                subscription_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()


@app.on_event("startup")
async def startup_event():
    """Run startup steps; each logs one line, followed by a single READY summary."""
    try:
        from database import get_masked_db_target
        db_target = get_masked_db_target()
    except Exception:
        db_target = "?"

    startup_log.info(f"Starting {settings.APP_TITLE} v{settings.APP_VERSION} (env={ENVIRONMENT}, db={db_target})")
    report = StartupReport()

    # 1. Cloudinary
    async def _cloudinary():
        if settings.init_cloudinary():
            return "OK", "enabled"
        return "WARN", "disabled - using Base64 fallback"
    await report.run("cloudinary", _cloudinary)

    # 2. Database connectivity (gate for every DB step below)
    async def _db_health():
        await setup_database_healthcheck(async_engine)
        return "OK", "connected"
    db_ok = await report.run("db-health", _db_health) == "OK"

    db_steps = ["db-tables", "db-hardening", "schema", "team-seq", "sync-tables"]
    if not db_ok:
        for step in db_steps:
            report.record(step, "SKIP", "database unreachable")
    else:
        # 3. ORM tables
        async def _db_tables():
            async with async_engine.begin() as conn:
                await conn.run_sync(AsyncBase.metadata.create_all)
            return "OK", "async create_all"
        await report.run("db-tables", _db_tables)

        # 4. Hardening tables (team_sequence, idempotency_keys, constraints)
        async def _db_hardening():
            await _ensure_hardening_tables()
            return "OK", "team_sequence, idempotency_keys"
        await report.run("db-hardening", _db_hardening)

        # 5. Schema validation (individual errors/warnings are logged by the validator)
        async def _schema():
            from app.utils.startup_validation import validate_database_schema
            async with AsyncSessionLocal() as db:
                r = await validate_database_schema(db)
            n_checks, n_err, n_warn = len(r["checks"]), len(r["errors"]), len(r["warnings"])
            if n_err:
                return "FAIL", f"{n_err} error(s), {n_warn} warning(s) - see above"
            if n_warn:
                return "WARN", f"{n_checks} checks, {n_warn} warning(s) - see above"
            return "OK", f"{n_checks} checks passed"
        await report.run("schema", _schema)

        # 6. Team ID sequence sync
        async def _team_seq():
            from app.utils.race_safe_team_id import sync_sequence_with_teams, get_current_sequence_number
            async with AsyncSessionLocal() as db:
                if not await sync_sequence_with_teams(db):
                    return "WARN", "sync failed - continuing with current state"
                seq = await get_current_sequence_number(db)
            return "OK", f"current={seq}, next=ICCT-{seq + 1:03d}"
        await report.run("team-seq", _team_seq)

        # 7. Legacy sync-engine tables
        async def _sync_tables():
            sync_engine = _get_sync_engine()
            if sync_engine is None:
                return "SKIP", "no sync engine in database.py"
            try:
                await asyncio.to_thread(_ensure_sync_tables, sync_engine)
            except Exception as e:
                return "WARN", f"{type(e).__name__}: {e}"
            return "OK", "teams, players"
        await report.run("sync-tables", _sync_tables)

    # 8. DatabaseService contract (no DB needed)
    async def _services():
        from app.utils.startup_validation import validate_database_service_methods
        r = validate_database_service_methods()
        if not r["valid"]:
            return "FAIL", "; ".join(r["errors"])
        return "OK", f"{len(r['methods'])} methods available"
    await report.run("services", _services)

    # Keep Neon awake
    asyncio.create_task(keep_neon_awake())

    # ---- Single summary block ----
    total = time.perf_counter() - report.t0
    n_ok, n_warn, n_fail, n_skip = (report.count(s) for s in ("OK", "WARN", "FAIL", "SKIP"))
    state = "READY" if n_fail == 0 else "STARTED WITH ERRORS"
    level = logging.INFO if n_fail == 0 else logging.ERROR
    bar = "-" * 64
    startup_log.log(level, bar)
    startup_log.log(level, f"{state} in {total:.1f}s | ok={n_ok} warn={n_warn} fail={n_fail} skip={n_skip}")
    problems = [f"{step}: {detail}" for status, step, detail in report.rows if status in ("WARN", "FAIL")]
    for p in problems:
        startup_log.log(level, f"  ! {p}")
    startup_log.log(level, bar)


@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown: close database connections and cleanup resources"""
    try:
        await teardown_database(async_engine)
        logger.info("Shutdown complete (database connections closed)")
    except Exception as shutdown_err:
        logger.error(f"Error during shutdown: {shutdown_err}")

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
logger.debug("Including application routers...")
app.include_router(main_router)

logger.debug("All routers included")

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
        "frontend_url": "https://icct27.netlify.app",
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
    logger.info(f"Launching uvicorn on http://{settings.HOST}:{port} (docs: /docs, reload={settings.RELOAD})")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=port,
        reload=settings.RELOAD,
        log_level="info"
    )
