import logging
import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zillow_scraper.settings')
django.setup()

from scrapers.agent_scraper import AgentScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('scrapers.agent_scraper')
logger.setLevel(logging.INFO)

def debug_agent():
    scraper = AgentScraper()
    agent_name = "Pardee-Properties"
    print(f"Fetching agent: {agent_name}")
    
    try:
        # We manually call internal methods to debug
        url = f"https://www.zillow.com/profile/{agent_name}/"
        soup = scraper.get_soup(url)
        print("Got soup")
        
        from scrapers.utils import extract_json_from_script
        script_data = extract_json_from_script(soup)
        print(f"Script data keys: {list(script_data.keys()) if script_data else 'None'}")
        
        zuid = scraper._extract_zuid(script_data, soup)
        print(f"Extracted ZUID: {zuid}")
        
        if zuid:
            api_data = scraper._fetch_agent_listings_api(zuid, 'sold', page=2)
            if api_data:
                print(f"API Data Keys: {list(api_data.keys())}")
                listings = api_data.get('listings') or api_data.get('past_sales') or []
                print(f"Listings count: {len(listings)}")
            else:
                print("API Data empty")
        else:
            print("No ZUID found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_agent()
