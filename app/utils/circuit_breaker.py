"""
Circuit Breaker Pattern
=======================
Failure rate monitoring for email and Cloudinary operations.
Prevents cascading failures.
"""

import logging
import time
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any, Coroutine
from collections import defaultdict

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures detected, failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation for resilience.
    Monitors failure rates and stops calling failing services.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,  # Failures before opening circuit
        recovery_timeout: int = 60,  # Seconds before attempting recovery
        time_window: int = 60,  # Time window for failure counting
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.time_window = time_window
        
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.failure_times = []
        self.failure_count = 0
        self.success_count = 0
    
    def _cleanup_old_failures(self):
        """Remove failures outside the time window"""
        now = time.time()
        self.failure_times = [
            failure_time for failure_time in self.failure_times
            if now - failure_time < self.time_window
        ]
        self.failure_count = len(self.failure_times)
    
    def record_success(self):
        """Record successful call"""
        self._cleanup_old_failures()
        
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit {self.name} recovered, closing circuit")
            self.state = CircuitState.CLOSED
            self.failure_times = []
            self.failure_count = 0
            self.success_count = 0
    
    def record_failure(self):
        """Record failed call"""
        self.last_failure_time = time.time()
        self.failure_times.append(self.last_failure_time)
        self.failure_count = len(self.failure_times)
        
        if self.failure_count >= self.failure_threshold:
            logger.warning(
                f"Circuit {self.name} opening due to failure rate",
                extra={
                    "failures": self.failure_count,
                    "threshold": self.failure_threshold
                }
            )
            self.state = CircuitState.OPEN
    
    def can_execute(self) -> bool:
        """Check if call should be allowed"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                time_since_last_failure = time.time() - self.last_failure_time
                if time_since_last_failure >= self.recovery_timeout:
                    logger.info(
                        f"Circuit {self.name} attempting recovery",
                        extra={"time_since_failure": round(time_since_last_failure, 1)}
                    )
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    return True
            return False
        
        # HALF_OPEN: allow one attempt
        return True
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        """
        if not self.can_execute():
            raise RuntimeError(
                f"Circuit {self.name} is open. Service unavailable."
            )
        
        try:
            result = await func(*args, **kwargs) if hasattr(func, '__await__') else func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise


class CircuitBreakerManager:
    """Manage multiple circuit breakers"""
    
    def __init__(self):
        self.breakers: dict[str, CircuitBreaker] = {}
    
    def get_or_create(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create circuit breaker"""
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(name, **kwargs)
        return self.breakers[name]
    
    def get_status(self) -> dict[str, dict]:
        """Get status of all circuit breakers"""
        return {
            name: {
                "state": breaker.state.value,
                "failures": breaker.failure_count,
                "threshold": breaker.failure_threshold
            }
            for name, breaker in self.breakers.items()
        }


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()


class FailureRateMonitor:
    """Monitor failure rates for operations"""
    
    def __init__(self, window_minutes: int = 1, threshold_failures: int = 3):
        self.window_minutes = window_minutes
        self.threshold_failures = threshold_failures
        self.failures = defaultdict(list)
    
    def record_failure(self, operation: str):
        """Record failure for operation"""
        now = datetime.now()
        self.failures[operation].append(now)
        
        # Cleanup old failures
        cutoff = now - timedelta(minutes=self.window_minutes)
        self.failures[operation] = [
            failure_time for failure_time in self.failures[operation]
            if failure_time > cutoff
        ]
    
    def get_failure_rate(self, operation: str) -> int:
        """Get failure count in current window"""
        return len(self.failures.get(operation, []))
    
    def should_warn(self, operation: str) -> bool:
        """Check if failure rate exceeds threshold"""
        return self.get_failure_rate(operation) >= self.threshold_failures
    
    def log_warnings(self):
        """Log warning for operations with high failure rates"""
        for operation, failures in self.failures.items():
            if len(failures) >= self.threshold_failures:
                logger.warning(
                    f"High failure rate for {operation}",
                    extra={
                        "operation": operation,
                        "failures": len(failures),
                        "window_minutes": self.window_minutes,
                        "threshold": self.threshold_failures
                    }
                )


# Global failure rate monitor
failure_rate_monitor = FailureRateMonitor(
    window_minutes=1,
    threshold_failures=3
)


async def execute_with_circuit_breaker(
    operation_name: str,
    func: Callable,
    *args,
    **kwargs
) -> Any:
    """
    Execute function with circuit breaker protection.
    Handles failure rate monitoring and graceful degradation.
    """
    breaker = circuit_breaker_manager.get_or_create(
        operation_name,
        failure_threshold=5,
        recovery_timeout=60
    )
    
    try:
        result = await breaker.execute(func, *args, **kwargs)
        return result
    except Exception as e:
        failure_rate_monitor.record_failure(operation_name)
        
        if failure_rate_monitor.should_warn(operation_name):
            logger.error(
                f"Operation {operation_name} exceeding failure threshold",
                extra={
                    "failures": failure_rate_monitor.get_failure_rate(operation_name),
                    "threshold": failure_rate_monitor.threshold_failures
                }
            )
        
        raise
