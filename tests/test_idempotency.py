"""
Tests for idempotency key management
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.utils.idempotency import (
    check_idempotency_key,
    store_idempotency_key,
    cleanup_expired_keys,
    IdempotencyKey,
    Base
)


@pytest_asyncio.fixture
async def test_db():
    """Create an in-memory test database"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_store_and_check_idempotency_key(test_db):
    """Test storing and retrieving idempotency keys"""
    key = "test-key-123"
    response = '{"success": true, "team_id": "ICCT-001"}'
    
    # Store key
    await store_idempotency_key(test_db, key, response)
    
    # Check key exists
    retrieved = await check_idempotency_key(test_db, key)
    assert retrieved == response


@pytest.mark.asyncio
async def test_duplicate_key_returns_cached_response(test_db):
    """Test that duplicate keys return the cached response"""
    key = "duplicate-key"
    response = '{"success": true}'
    
    await store_idempotency_key(test_db, key, response)
    
    # Second check should return the same response
    cached = await check_idempotency_key(test_db, key)
    assert cached == response


@pytest.mark.asyncio
async def test_nonexistent_key_returns_none(test_db):
    """Test that checking a non-existent key returns None"""
    result = await check_idempotency_key(test_db, "nonexistent-key")
    assert result is None


@pytest.mark.asyncio
async def test_cleanup_expired_keys(test_db):
    """Test that expired keys are cleaned up"""
    # Create an expired key
    expired_key = IdempotencyKey(
        key="expired-key",
        response_data='{"old": true}',
        expires_at=datetime.utcnow() - timedelta(minutes=20)
    )
    test_db.add(expired_key)
    
    # Create a valid key
    valid_key = IdempotencyKey(
        key="valid-key",
        response_data='{"valid": true}',
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    test_db.add(valid_key)
    await test_db.commit()
    
    # Run cleanup
    deleted_count = await cleanup_expired_keys(test_db)
    assert deleted_count == 1
    
    # Valid key should still exist
    valid_response = await check_idempotency_key(test_db, "valid-key")
    assert valid_response == '{"valid": true}'
    
    # Expired key should be gone
    expired_response = await check_idempotency_key(test_db, "expired-key")
    assert expired_response is None


@pytest.mark.asyncio
async def test_idempotency_ttl(test_db):
    """Test that keys expire after TTL"""
    # This test verifies the default 10-minute TTL
    key = "ttl-test-key"
    response = '{"test": true}'
    
    await store_idempotency_key(test_db, key, response)
    
    # Manually set expiry to past
    from sqlalchemy import update
    stmt = update(IdempotencyKey).where(
        IdempotencyKey.key == key
    ).values(expires_at=datetime.utcnow() - timedelta(seconds=1))
    await test_db.execute(stmt)
    await test_db.commit()
    
    # Cleanup should remove it
    await cleanup_expired_keys(test_db)
    
    result = await check_idempotency_key(test_db, key)
    assert result is None
