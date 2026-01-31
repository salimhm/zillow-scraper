"""
Proxy Manager for rotating proxies to avoid detection and blocking.
"""

import random
import logging
from typing import Optional, Dict, List
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ProxyManager:
    """
    Manages proxy rotation for web scraping requests.
    
    Features:
    - Round-robin proxy rotation
    - Proxy health tracking
    - Automatic proxy blacklisting for failed proxies
    """
    
    CACHE_KEY_INDEX = 'proxy_manager:current_index'
    CACHE_KEY_BLACKLIST = 'proxy_manager:blacklist'
    BLACKLIST_DURATION = 300  # 5 minutes
    
    def __init__(self):
        self.proxies = self._load_proxies()
        
    def _load_proxies(self) -> List[str]:
        """Load proxies from settings."""
        proxies = settings.SCRAPER_SETTINGS.get('PROXIES', [])
        if isinstance(proxies, str):
            proxies = [p.strip() for p in proxies.split(',') if p.strip()]
        return [p for p in proxies if p]
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get the next proxy in rotation.
        
        Returns:
            Dictionary with 'http' and 'https' keys, or None if no proxies available.
        """
        if not self.proxies:
            logger.warning("No proxies configured. Requests will be made without proxy.")
            return None
        
        # Get blacklisted proxies
        blacklist = cache.get(self.CACHE_KEY_BLACKLIST, set())
        available_proxies = [p for p in self.proxies if p not in blacklist]
        
        if not available_proxies:
            logger.warning("All proxies are blacklisted. Using random proxy from pool.")
            available_proxies = self.proxies
        
        # Get current index and rotate
        current_index = cache.get(self.CACHE_KEY_INDEX, 0)
        proxy = available_proxies[current_index % len(available_proxies)]
        
        # Update index for next request
        cache.set(self.CACHE_KEY_INDEX, (current_index + 1) % len(available_proxies), timeout=None)
        
        logger.debug(f"Using proxy: {proxy[:20]}...")
        return {
            'http': proxy,
            'https': proxy,
        }
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy from the pool."""
        if not self.proxies:
            return None
        
        proxy = random.choice(self.proxies)
        return {
            'http': proxy,
            'https': proxy,
        }
    
    def mark_proxy_failed(self, proxy_url: str):
        """
        Mark a proxy as failed and add to blacklist.
        
        Args:
            proxy_url: The proxy URL that failed.
        """
        blacklist = cache.get(self.CACHE_KEY_BLACKLIST, set())
        blacklist.add(proxy_url)
        cache.set(self.CACHE_KEY_BLACKLIST, blacklist, timeout=self.BLACKLIST_DURATION)
        logger.warning(f"Proxy blacklisted for {self.BLACKLIST_DURATION}s: {proxy_url[:20]}...")
    
    def mark_proxy_success(self, proxy_url: str):
        """
        Mark a proxy as successful and remove from blacklist if present.
        
        Args:
            proxy_url: The proxy URL that succeeded.
        """
        blacklist = cache.get(self.CACHE_KEY_BLACKLIST, set())
        if proxy_url in blacklist:
            blacklist.discard(proxy_url)
            cache.set(self.CACHE_KEY_BLACKLIST, blacklist, timeout=self.BLACKLIST_DURATION)
            logger.info(f"Proxy removed from blacklist: {proxy_url[:20]}...")
    
    def get_proxy_count(self) -> int:
        """Return the total number of configured proxies."""
        return len(self.proxies)
    
    def get_available_proxy_count(self) -> int:
        """Return the number of non-blacklisted proxies."""
        blacklist = cache.get(self.CACHE_KEY_BLACKLIST, set())
        return len([p for p in self.proxies if p not in blacklist])


# Singleton instance
proxy_manager = ProxyManager()
