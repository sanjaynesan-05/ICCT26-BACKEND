"""
ICCT26 Cricket Tournament Registration API
Main FastAPI application entry point
"""

import logging
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
# Logging
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
# FastAPI app
# -----------------------
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

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
app.include_router(main_router)


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
