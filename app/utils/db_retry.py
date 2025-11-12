"""
Database retry decorator for resilient async operations.

Provides decorator-based retry mechanism with exponential backoff for
database operations. Handles Neon connection timeouts gracefully.

Usage:
    @retry_db_operation(retries=3, delay=2)
    async def register_team(registration: TeamRegistrationRequest, db: AsyncSession):
        # Long-running DB operations here
        pass
"""

import asyncio
import logging
from functools import wraps
from typing import Callable, Any, TypeVar, Coroutine

from sqlalchemy.exc import OperationalError, TimeoutError as SQLAlchemyTimeoutError

logger = logging.getLogger(__name__)

# Type variable for generic decorator
F = TypeVar('F', bound=Callable[..., Coroutine[Any, Any, Any]])


def retry_db_operation(retries: int = 3, delay: float = 2, backoff: float = 2.0):
    """
    Decorator for retrying async database operations with exponential backoff.
    
    Catches database connection errors and retries the operation with increasing delays.
    
    Args:
        retries (int): Number of retry attempts (default: 3)
        delay (float): Initial delay between retries in seconds (default: 2)
        backoff (float): Exponential backoff multiplier (default: 2.0)
        
    Returns:
        Decorator function
        
    Raises:
        Exception: Re-raises the last exception if all retries fail
        
    Example:
        @retry_db_operation(retries=3, delay=2)
        async def register_team(registration, db):
            # DB operations
            await db.commit()
            
        # Usage
        await register_team(registration_data, db_session)
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_error = None
            
            for attempt in range(1, retries + 1):
                try:
                    logger.info(
                        f"🔄 Executing {func.__name__} "
                        f"(attempt {attempt}/{retries})"
                    )
                    
                    result = await func(*args, **kwargs)
                    
                    if attempt > 1:
                        logger.info(
                            f"✅ {func.__name__} succeeded "
                            f"after {attempt - 1} retries"
                        )
                    
                    return result
                
                except (
                    OperationalError,
                    SQLAlchemyTimeoutError,
                    asyncio.TimeoutError,
                    asyncio.CancelledError,
                    ConnectionError,
                    ConnectionResetError,
                    ConnectionAbortedError,
                    BrokenPipeError,
                ) as e:
                    # Store error for potential re-raise
                    last_error = e
                    error_type = type(e).__name__
                    
                    logger.warning(
                        f"⚠️ {func.__name__} failed with {error_type} "
                        f"(attempt {attempt}/{retries}): {str(e)}"
                    )
                    
                    # Don't retry if we've exhausted attempts
                    if attempt >= retries:
                        logger.error(
                            f"❌ {func.__name__} failed after {retries} attempts. "
                            f"Last error: {error_type}: {str(e)}"
                        )
                        raise
                    
                    # Calculate exponential backoff delay
                    current_delay = delay * (backoff ** (attempt - 1))
                    logger.info(
                        f"⏳ Retrying {func.__name__} in {current_delay}s... "
                        f"({attempt}/{retries})"
                    )
                    
                    await asyncio.sleep(current_delay)
                
                except Exception as e:
                    # Don't retry on validation/business logic errors
                    logger.error(
                        f"❌ {func.__name__} failed with non-retryable error "
                        f"{type(e).__name__}: {str(e)}"
                    )
                    raise
            
            # Failsafe: raise last error if loop exits without return
            if last_error:
                raise last_error
        
        return wrapper  # type: ignore
    
    return decorator


def retry_db_operation_with_logging(
    retries: int = 3,
    delay: float = 2,
    backoff: float = 2.0,
    operation_name: str = "DB Operation"
):
    """
    Enhanced retry decorator with detailed logging for debugging.
    
    Logs detailed information about each retry attempt including
    stack traces and connection states.
    
    Args:
        retries (int): Number of retry attempts
        delay (float): Initial delay between retries in seconds
        backoff (float): Exponential backoff multiplier
        operation_name (str): Friendly name for logging
        
    Returns:
        Decorator function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            logger.info(
                f"📌 Starting {operation_name} "
                f"(max {retries} attempts)"
            )
            
            for attempt in range(1, retries + 1):
                try:
                    logger.debug(
                        f"Attempt {attempt}/{retries} for {operation_name}"
                    )
                    
                    result = await func(*args, **kwargs)
                    
                    logger.info(
                        f"✅ {operation_name} completed successfully "
                        f"on attempt {attempt}"
                    )
                    
                    return result
                
                except (
                    OperationalError,
                    SQLAlchemyTimeoutError,
                    asyncio.TimeoutError,
                ) as e:
                    logger.warning(
                        f"⚠️ {operation_name} encountered connection error "
                        f"on attempt {attempt}/{retries}",
                        exc_info=True
                    )
                    
                    if attempt >= retries:
                        logger.error(
                            f"❌ {operation_name} failed after {retries} attempts"
                        )
                        raise
                    
                    current_delay = delay * (backoff ** (attempt - 1))
                    logger.info(
                        f"⏳ {operation_name}: Waiting {current_delay}s "
                        f"before retry {attempt + 1}/{retries}"
                    )
                    
                    await asyncio.sleep(current_delay)
        
        return wrapper  # type: ignore
    
    return decorator
