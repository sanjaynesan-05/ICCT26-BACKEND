"""
ICCT26 Cricket Tournament Registration API
Main FastAPI application entry point

Professional modular structure:
- app/config.py - Configuration and settings
- app/schemas.py - Pydantic models for request/response validation
- app/services.py - Business logic (email, database, registration)
- app/routes/ - API endpoints organized by feature
  - routes/health.py - Health check and status endpoints
  - routes/registration.py - Team registration endpoints
  - routes/admin.py - Admin panel endpoints
- database.py - Database configuration and session management
- models.py - SQLAlchemy ORM models
- main.py - Main FastAPI application (this file)
"""

import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker as async_sessionmaker

from app.config import settings, get_async_database_url
from app.routes import main_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# Async Database Configuration
# ============================================================

DATABASE_URL_ASYNC = get_async_database_url()
async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=settings.DATABASE_ECHO)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
AsyncBase = declarative_base()


# ============================================================
# Async Database Models (for legacy async endpoints)
# ============================================================

class TeamRegistrationAsyncDB(AsyncBase):
    """Team registration model for async operations"""
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
    """Captain model for async operations"""
    __tablename__ = "captains"
    
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    phone = Column(String(20))
    whatsapp = Column(String(20))
    email = Column(String(255))


class ViceCaptainAsyncDB(AsyncBase):
    """Vice-captain model for async operations"""
    __tablename__ = "vice_captains"
    
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    phone = Column(String(20))
    whatsapp = Column(String(20))
    email = Column(String(255))


class PlayerAsyncDB(AsyncBase):
    """Player model for async operations"""
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("team_registrations.id"))
    name = Column(String(100))
    age = Column(Integer)
    phone = Column(String(20))
    role = Column(String(20))
    aadhar_file = Column(Text, nullable=True)
    subscription_file = Column(Text, nullable=True)


# ============================================================
# FastAPI Application Setup
# ============================================================

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ============================================================
# CORS Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# ============================================================
# Event Handlers
# ============================================================


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await init_db()
        logger.info("✅ Database tables initialized (async)")

        # Also ensure tables exist for sync operations using raw SQL
        from database import sync_engine
        with sync_engine.connect() as conn:
            # Create tables if they don't exist
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

    except Exception as e:
        logger.warning(f"[WARNING] Database initialization warning: {e}")
        logger.warning("   Make sure PostgreSQL is running and DATABASE_URL is correct")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application...")


# ============================================================
# Database Functions
# ============================================================

async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(AsyncBase.metadata.create_all)


async def get_db_async():
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ============================================================
# Routes Registration
# ============================================================

# Include all routes from modular route files
app.include_router(main_router)

# ============================================================
# Debug Endpoints
# ============================================================


@app.get("/debug/db")
def debug_database():
    """Debug database connection"""
    try:
        from database import get_db
        db = next(get_db())
        result = db.execute(text("SELECT COUNT(*) FROM team_registrations"))
        count = result.fetchone()[0]
        return {"status": "success", "team_count": count}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/debug/create-tables")
def create_tables():
    """Create database tables manually"""
    try:
        from app.services import DatabaseService
        from database import sync_engine
        
        with sync_engine.connect() as conn:
            session_obj = type('Session', (), {
                'execute': lambda self, query: conn.execute(query),
                'commit': lambda self: conn.commit(),
                'rollback': lambda self: conn.rollback()
            })()
            
            DatabaseService.create_tables(session_obj)
        
        return {"status": "success", "message": "Tables created"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================
# Exception Handlers
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "status_code": exc.status_code
        }
    )


# ============================================================
# Main Entry Point
# ============================================================

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
