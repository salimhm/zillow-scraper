"""
Rate Limiter for controlling request rates per user/IP.
"""

import time
import logging
from typing import Optional
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple rate limiter using Redis for distributed rate limiting.
    
    Implements a sliding window rate limiting algorithm.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 500,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
    
    def _get_cache_key(self, identifier: str, window: str) -> str:
        """Generate cache key for rate limiting."""
        return f"rate_limit:{identifier}:{window}"
    
    def is_allowed(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check if a request is allowed for the given identifier.
        
        Args:
            identifier: Usually user ID or IP address.
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        current_minute = int(time.time() // 60)
        current_hour = int(time.time() // 3600)
        
        # Check minute limit
        minute_key = self._get_cache_key(identifier, f"minute:{current_minute}")
        minute_count = cache.get(minute_key, 0)
        
        if minute_count >= self.requests_per_minute:
            seconds_until_next_minute = 60 - int(time.time() % 60)
            logger.warning(f"Rate limit exceeded (minute) for {identifier}")
            return False, seconds_until_next_minute
        
        # Check hour limit
        hour_key = self._get_cache_key(identifier, f"hour:{current_hour}")
        hour_count = cache.get(hour_key, 0)
        
        if hour_count >= self.requests_per_hour:
            seconds_until_next_hour = 3600 - int(time.time() % 3600)
            logger.warning(f"Rate limit exceeded (hour) for {identifier}")
            return False, seconds_until_next_hour
        
        # Increment counters
        cache.set(minute_key, minute_count + 1, timeout=60)
        cache.set(hour_key, hour_count + 1, timeout=3600)
        
        return True, None
    
    def get_remaining_requests(self, identifier: str) -> dict:
        """
        Get remaining requests for the given identifier.
        
        Args:
            identifier: Usually user ID or IP address.
            
        Returns:
            Dictionary with remaining minute and hour counts.
        """
        current_minute = int(time.time() // 60)
        current_hour = int(time.time() // 3600)
        
        minute_key = self._get_cache_key(identifier, f"minute:{current_minute}")
        hour_key = self._get_cache_key(identifier, f"hour:{current_hour}")
        
        minute_count = cache.get(minute_key, 0)
        hour_count = cache.get(hour_key, 0)
        
        return {
            'remaining_per_minute': max(0, self.requests_per_minute - minute_count),
            'remaining_per_hour': max(0, self.requests_per_hour - hour_count),
            'limit_per_minute': self.requests_per_minute,
            'limit_per_hour': self.requests_per_hour,
        }
    
    def reset(self, identifier: str):
        """Reset rate limits for the given identifier."""
        current_minute = int(time.time() // 60)
        current_hour = int(time.time() // 3600)
        
        minute_key = self._get_cache_key(identifier, f"minute:{current_minute}")
        hour_key = self._get_cache_key(identifier, f"hour:{current_hour}")
        
        cache.delete(minute_key)
        cache.delete(hour_key)
        logger.info(f"Rate limits reset for {identifier}")


# Default rate limiter instance
rate_limiter = RateLimiter(
    requests_per_minute=int(settings.SCRAPER_SETTINGS.get('RATE_LIMIT_PER_MINUTE', 60) if hasattr(settings, 'SCRAPER_SETTINGS') else 60),
    requests_per_hour=int(settings.SCRAPER_SETTINGS.get('RATE_LIMIT_PER_HOUR', 500) if hasattr(settings, 'SCRAPER_SETTINGS') else 500),
)
