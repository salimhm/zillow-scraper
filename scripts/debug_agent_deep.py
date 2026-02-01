import logging
import sys
import os
import django
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zillow_scraper.settings')
django.setup()

from scrapers.agent_scraper import AgentScraper

logging.basicConfig(level=logging.INFO)

def debug_deep():
    scraper = AgentScraper()
    agent_name = "Pardee-Properties"
    zuid = "X1-ZUz0nmomozy2o9_9bpwk"
    
    print(f"Checking pagination for {agent_name} ({zuid})")
    
    # Page 1
    print("\n--- Page 1 ---")
    data1 = scraper._fetch_agent_listings_api(zuid, 'sold', page=1)
    if not data1: print("Failed Page 1"); return
    
    list1 = data1.get('past_sales', [])
    print(f"Count: {len(list1)}")
    if list1:
        print(f"First Item: {list1[0].get('address', {}).get('line1')}")
        
    # Page 2
    print("\n--- Page 2 ---")
    data2 = scraper._fetch_agent_listings_api(zuid, 'sold', page=2)
    if not data2: print("Failed Page 2"); return
    
    list2 = data2.get('past_sales', [])
    print(f"Count: {len(list2)}")
    if list2:
        print(f"First Item: {list2[0].get('address', {}).get('line1')}")
        
    if list1 and list2:
        if list1[0]['zpid'] == list2[0]['zpid']:
            print("\nRESULT: DUPLICATE (Pagination Ignored)")
        else:
            print("\nRESULT: DIFFERENT (Pagination Working, but small page size)")

if __name__ == "__main__":
    debug_deep()
