"""
User-Agent Manager for rotating user agents to mimic different browsers.
"""

import random
import logging
from typing import Optional, List
from django.conf import settings

logger = logging.getLogger(__name__)

# Fallback user agents if fake-useragent fails or no custom agents configured
DEFAULT_USER_AGENTS = [
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    # Chrome on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # Firefox on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    # Firefox on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    # Safari on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    # Edge on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
]


class UserAgentManager:
    """
    Manages user-agent rotation for web scraping requests.
    
    Features:
    - Uses fake-useragent library when available
    - Falls back to custom user agents from settings
    - Uses default user agents as last resort
    """
    
    def __init__(self):
        self.user_agents = self._load_user_agents()
        self._fake_ua = self._init_fake_useragent()
    
    def _load_user_agents(self) -> List[str]:
        """Load custom user agents from settings."""
        user_agents = settings.SCRAPER_SETTINGS.get('USER_AGENTS', [])
        if isinstance(user_agents, str):
            user_agents = [ua.strip() for ua in user_agents.split(',') if ua.strip()]
        return [ua for ua in user_agents if ua]
    
    def _init_fake_useragent(self) -> Optional[object]:
        """Initialize fake-useragent library."""
        try:
            from fake_useragent import UserAgent
            ua = UserAgent()
            # Test that it works
            _ = ua.random
            logger.info("fake-useragent initialized successfully")
            return ua
        except Exception as e:
            logger.warning(f"Failed to initialize fake-useragent: {e}")
            return None
    
    def get_random_user_agent(self) -> str:
        """
        Get a random user agent string.
        
        Priority:
        1. Custom user agents from settings
        2. fake-useragent library
        3. Default fallback list
        
        Returns:
            A random user agent string.
        """
        # Priority 1: Custom user agents from settings
        if self.user_agents:
            ua = random.choice(self.user_agents)
            logger.debug(f"Using custom user agent: {ua[:50]}...")
            return ua
        
        # Priority 2: fake-useragent library
        if self._fake_ua:
            try:
                ua = self._fake_ua.random
                logger.debug(f"Using fake-useragent: {ua[:50]}...")
                return ua
            except Exception as e:
                logger.warning(f"fake-useragent failed: {e}")
        
        # Priority 3: Default fallback
        ua = random.choice(DEFAULT_USER_AGENTS)
        logger.debug(f"Using default user agent: {ua[:50]}...")
        return ua
    
    def get_chrome_user_agent(self) -> str:
        """Get a Chrome-specific user agent."""
        if self._fake_ua:
            try:
                return self._fake_ua.chrome
            except Exception:
                pass
        
        chrome_agents = [ua for ua in DEFAULT_USER_AGENTS if 'Chrome' in ua and 'Edg' not in ua]
        return random.choice(chrome_agents) if chrome_agents else DEFAULT_USER_AGENTS[0]
    
    def get_firefox_user_agent(self) -> str:
        """Get a Firefox-specific user agent."""
        if self._fake_ua:
            try:
                return self._fake_ua.firefox
            except Exception:
                pass
        
        firefox_agents = [ua for ua in DEFAULT_USER_AGENTS if 'Firefox' in ua]
        return random.choice(firefox_agents) if firefox_agents else DEFAULT_USER_AGENTS[3]
    
    def get_safari_user_agent(self) -> str:
        """Get a Safari-specific user agent."""
        if self._fake_ua:
            try:
                return self._fake_ua.safari
            except Exception:
                pass
        
        safari_agents = [ua for ua in DEFAULT_USER_AGENTS if 'Safari' in ua and 'Chrome' not in ua]
        return random.choice(safari_agents) if safari_agents else DEFAULT_USER_AGENTS[5]


# Singleton instance
user_agent_manager = UserAgentManager()
