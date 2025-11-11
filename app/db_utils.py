"""
Database utilities for handling Neon connection retries and resilience.
"""

import asyncio
import logging
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # seconds


async def retry_on_timeout(
    func: Callable[..., Awaitable[Any]],
    *args,
    max_retries: int = MAX_RETRIES,
    delay_base: float = RETRY_DELAY_BASE,
    **kwargs
) -> Any:
    """
    Retry a coroutine function on timeout/connection errors.
    
    Uses exponential backoff: 2s, 4s, 8s...
    
    Args:
        func: Async function to execute
        max_retries: Number of retry attempts
        delay_base: Base delay for exponential backoff
        *args, **kwargs: Arguments to pass to func
    
    Returns:
        Result from func if successful
    
    Raises:
        Last exception if all retries fail
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempting DB operation (attempt {attempt + 1}/{max_retries})")
            result = await func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(f"✅ DB operation succeeded after {attempt} retries")
            
            return result
            
        except (asyncio.TimeoutError, asyncio.CancelledError) as e:
            last_error = e
            logger.warning(
                f"Timeout on attempt {attempt + 1}/{max_retries}: {str(e)}"
            )
            
            if attempt < max_retries - 1:
                delay = delay_base * (2 ** attempt)  # Exponential backoff
                logger.info(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)
        
        except Exception as e:
            last_error = e
            logger.warning(
                f"Error on attempt {attempt + 1}/{max_retries}: {str(e)}"
            )
            
            # Don't retry on non-timeout errors (e.g., validation errors)
            raise
    
    # All retries exhausted
    logger.error(f"❌ DB operation failed after {max_retries} attempts")
    raise last_error


async def safe_commit(session, max_retries: int = MAX_RETRIES) -> None:
    """
    Safely commit a session with retry logic.
    
    Handles Neon timeouts gracefully with exponential backoff.
    
    Args:
        session: SQLAlchemy async session
        max_retries: Number of retry attempts
    
    Raises:
        Exception if all retries fail
    """
    await retry_on_timeout(session.commit, max_retries=max_retries)


async def safe_flush(session, max_retries: int = MAX_RETRIES) -> None:
    """
    Safely flush a session with retry logic.
    
    Args:
        session: SQLAlchemy async session
        max_retries: Number of retry attempts
    
    Raises:
        Exception if all retries fail
    """
    await retry_on_timeout(session.flush, max_retries=max_retries)
