"""
Celery tasks for asynchronous scraping operations.
"""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def scrape_agents_by_location(self, location: str):
    """
    Async task to scrape agents by location.
    
    Args:
        location: Location slug
        
    Returns:
        List of agent dictionaries
    """
    from scrapers.agent_scraper import agent_scraper
    
    try:
        logger.info(f"Starting agent scrape for location: {location}")
        agents = agent_scraper.get_agents_by_location(location)
        logger.info(f"Found {len(agents)} agents for {location}")
        return agents
    except Exception as e:
        logger.error(f"Agent scrape failed: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def scrape_properties_by_location(self, location: str, list_type: str = 'for-sale', **filters):
    """
    Async task to scrape properties by location.
    
    Args:
        location: Location slug
        list_type: Listing type
        **filters: Additional search filters
        
    Returns:
        List of property dictionaries
    """
    from scrapers.property_scraper import property_scraper
    
    try:
        logger.info(f"Starting property scrape for location: {location}")
        properties = property_scraper.search_by_location(
            location=location, list_type=list_type, **filters
        )
        logger.info(f"Found {len(properties)} properties for {location}")
        return properties
    except Exception as e:
        logger.error(f"Property scrape failed: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def health_check():
    """Simple health check task."""
    logger.info("Celery health check: OK")
    return "OK"
