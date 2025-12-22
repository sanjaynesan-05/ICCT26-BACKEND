"""
Test configuration and pytest fixtures
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_db():
    """Create async database session for tests"""
    from app.config import get_async_database_url, get_async_engine
    
    # Use the production async engine
    async_engine = get_async_engine()
    
    # Create session factory
    AsyncSessionLocal = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Create session
    async with AsyncSessionLocal() as session:
        yield session
