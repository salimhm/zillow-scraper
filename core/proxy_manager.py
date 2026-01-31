"""
Proxy Manager for providing proxy configuration.

Note: If using a rotating proxy provider (like Bright Data, Oxylabs, etc.),
the provider handles IP rotation automatically on each request.
"""

import logging
from typing import Optional, Dict
from django.conf import settings

logger = logging.getLogger(__name__)


class ProxyManager:
    """
    Provides proxy configuration for web scraping requests.
    
    This is a simplified version that assumes the proxy provider
    handles rotation automatically. No blacklisting or rotation needed.
    """
    
    def __init__(self):
        self.proxy_url = self._load_proxy()
        
    def _load_proxy(self) -> Optional[str]:
        """Load proxy from settings."""
        proxies = settings.SCRAPER_SETTINGS.get('PROXIES', [])
        if isinstance(proxies, str):
            proxies = [p.strip() for p in proxies.split(',') if p.strip()]
        
        if proxies:
            # Use the first proxy URL (provider handles rotation)
            return proxies[0] if proxies else None
        return None
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get the configured proxy.
        
        Returns:
            Dictionary with 'http' and 'https' keys, or None if no proxy configured.
        """
        if not self.proxy_url:
            logger.debug("No proxy configured. Requests will be made directly.")
            return None
        
        logger.debug(f"Using proxy: {self.proxy_url[:30]}...")
        return {
            'http': self.proxy_url,
            'https': self.proxy_url,
        }
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Alias for get_proxy() for backward compatibility."""
        return self.get_proxy()
    
    def mark_proxy_failed(self, proxy_url: str):
        """No-op: Provider handles rotation, so no need to blacklist."""
        logger.debug(f"Proxy request failed (provider will rotate): {proxy_url[:30]}...")
    
    def mark_proxy_success(self, proxy_url: str):
        """No-op: Provider handles rotation."""
        pass
    
    def get_proxy_count(self) -> int:
        """Return 1 if proxy configured, 0 otherwise."""
        return 1 if self.proxy_url else 0
    
    def get_available_proxy_count(self) -> int:
        """Return 1 if proxy configured, 0 otherwise."""
        return self.get_proxy_count()


# Singleton instance
proxy_manager = ProxyManager()
