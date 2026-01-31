"""
Property scraper for Zillow property listings.
"""

import re
import json
import logging
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode, quote

from .base import BaseScraper, NotFoundException, ScraperException, BlockedException
from .utils import (
    extract_json_from_script,
    extract_apollo_state,
    parse_property_card,
    clean_price,
    clean_number,
    clean_text,
    build_search_url,
)

logger = logging.getLogger(__name__)


class PropertyScraper(BaseScraper):
    """Scraper for Zillow property listings."""
    
    def _build_search_query_state(self, **filters) -> Dict:
        """Build Zillow search query state object."""
        filter_state = {}
        
        # Price filters
        if filters.get('minPrice'):
            filter_state['price'] = filter_state.get('price', {})
            filter_state['price']['min'] = filters['minPrice']
        if filters.get('maxPrice'):
            filter_state['price'] = filter_state.get('price', {})
            filter_state['price']['max'] = filters['maxPrice']
        
        # Beds/Baths
        if filters.get('beds'):
            filter_state['beds'] = {'min': filters['beds']}
        if filters.get('baths'):
            filter_state['baths'] = {'min': filters['baths']}
        
        # Square footage
        if filters.get('minSqft'):
            filter_state['sqft'] = filter_state.get('sqft', {})
            filter_state['sqft']['min'] = filters['minSqft']
        if filters.get('maxSqft'):
            filter_state['sqft'] = filter_state.get('sqft', {})
            filter_state['sqft']['max'] = filters['maxSqft']
        
        # Year built
        if filters.get('minBuilt'):
            filter_state['built'] = filter_state.get('built', {})
            filter_state['built']['min'] = filters['minBuilt']
        if filters.get('maxBuilt'):
            filter_state['built'] = filter_state.get('built', {})
            filter_state['built']['max'] = filters['maxBuilt']
        
        # Lot size
        if filters.get('minLot'):
            filter_state['lotSize'] = filter_state.get('lotSize', {})
            filter_state['lotSize']['min'] = filters['minLot']
        if filters.get('maxLot'):
            filter_state['lotSize'] = filter_state.get('lotSize', {})
            filter_state['lotSize']['max'] = filters['maxLot']
        
        # HOA
        if filters.get('maxHOA'):
            filter_state['hoa'] = {'max': filters['maxHOA']}
        
        # Property types
        if filters.get('isSingleFamily'):
            filter_state['isSingleFamily'] = {'value': True}
        if filters.get('isCondo'):
            filter_state['isCondo'] = {'value': True}
        if filters.get('isTownhouse'):
            filter_state['isTownhouse'] = {'value': True}
        if filters.get('isApartment'):
            filter_state['isApartment'] = {'value': True}
        if filters.get('isMultiFamily'):
            filter_state['isMultiFamily'] = {'value': True}
        if filters.get('isLotLand'):
            filter_state['isLotLand'] = {'value': True}
        if filters.get('isManufactured'):
            filter_state['isManufactured'] = {'value': True}
        
        # Features
        if filters.get('hasPool'):
            filter_state['hasPool'] = {'value': True}
        if filters.get('hasGarage'):
            filter_state['hasGarage'] = {'value': True}
        if filters.get('parkingSpots'):
            filter_state['parkingSpots'] = {'min': filters['parkingSpots']}
        if filters.get('singleStory'):
            filter_state['singleStory'] = {'value': True}
        
        # Views
        if filters.get('isWaterView'):
            filter_state['isWaterfront'] = {'value': True}
        if filters.get('isMountainView'):
            filter_state['isMountainView'] = {'value': True}
        if filters.get('isParkView'):
            filter_state['isParkView'] = {'value': True}
        if filters.get('isCityView'):
            filter_state['isCityView'] = {'value': True}
        
        # Basement
        if filters.get('isBasementFinished'):
            filter_state['isBasementFinished'] = {'value': True}
        if filters.get('isBasementUnfinished'):
            filter_state['isBasementUnfinished'] = {'value': True}
        
        # Status
        if filters.get('isComingSoon'):
            filter_state['isComingSoon'] = {'value': True}
        if filters.get('isForSaleForeclosure'):
            filter_state['isForSaleForeclosure'] = {'value': True}
        if filters.get('isAuction'):
            filter_state['isAuction'] = {'value': True}
        if filters.get('isOpenHousesOnly'):
            filter_state['isOpenHouse'] = {'value': True}
        if filters.get('is3dHome'):
            filter_state['is3dHome'] = {'value': True}
        
        # Days on Zillow
        if filters.get('daysOnZillow'):
            filter_state['daysOnZillow'] = {'value': filters['daysOnZillow']}
        
        return filter_state
    
    def _parse_search_results(self, soup) -> List[Dict]:
        """Parse property search results from page."""
        properties = []
        
        # Try to find JSON data in script tags
        for script in soup.find_all('script'):
            script_text = script.string or ''
            
            # Skip short scripts
            if len(script_text) < 1000:
                continue
            
            # Try to parse as JSON
            if script_text.strip().startswith('{') or '"searchResults"' in script_text or '"listResults"' in script_text:
                try:
                    data = json.loads(script_text)
                    
                    # Try various paths to find property results
                    paths_to_try = [
                        # Next.js pageProps structure
                        lambda d: d.get('props', {}).get('pageProps', {}).get('searchPageState', {}).get('cat1', {}).get('searchResults', {}).get('listResults', []),
                        lambda d: d.get('props', {}).get('pageProps', {}).get('searchResults', {}).get('listResults', []),
                        # Direct paths
                        lambda d: d.get('searchResults', {}).get('listResults', []),
                        lambda d: d.get('cat1', {}).get('searchResults', {}).get('listResults', []),
                        lambda d: d.get('searchPageState', {}).get('cat1', {}).get('searchResults', {}).get('listResults', []),
                        # List at root
                        lambda d: d.get('listResults', []),
                    ]
                    
                    for path_func in paths_to_try:
                        try:
                            results = path_func(data)
                            if results and isinstance(results, list):
                                for result in results:
                                    parsed = parse_property_card(result)
                                    if parsed and (parsed.get('address') or parsed.get('zpid')):
                                        properties.append(parsed)
                                if properties:
                                    logger.info(f"Found {len(properties)} properties from JSON")
                                    return properties
                        except (KeyError, TypeError, AttributeError):
                            continue
                            
                except json.JSONDecodeError:
                    continue
        
        # Also try Apollo state
        if not properties:
            apollo_state = extract_apollo_state(soup)
            if apollo_state:
                for key, value in apollo_state.items():
                    if isinstance(value, dict) and value.get('zpid'):
                        parsed = parse_property_card(value)
                        if parsed:
                            properties.append(parsed)
        
        # Fallback: Parse HTML
        if not properties:
            logger.info("No properties found in scripts, trying HTML parsing...")
            # Try multiple selectors
            selectors = [
                '[data-test="property-card"]',
                '.list-card',
                '.property-card',
                'article[data-test]',
                '[class*="StyledPropertyCard"]',
                'li[class*="ListItem"]',
                'a[href*="/homedetails/"]',
            ]
            
            for selector in selectors:
                cards = soup.select(selector)
                if cards:
                    logger.info(f"Found {len(cards)} elements with selector: {selector}")
                    break
            else:
                cards = []
            
            for card in cards:
                address_elem = card.select_one('[data-test="property-card-addr"], .list-card-addr, address, [class*="address"]')
                price_elem = card.select_one('[data-test="property-card-price"], .list-card-price, [class*="price"]')
                link_elem = card.select_one('a[href*="/homedetails/"], a[href*="zpid"]')
                details_elem = card.select_one('[data-test="property-card-details"], .list-card-details, [class*="details"]')
                
                if address_elem or link_elem:
                    prop = {
                        'zpid': None,
                        'address': clean_text(address_elem.get_text()) if address_elem else '',
                        'url': '',
                        'price': clean_price(price_elem.get_text()) if price_elem else None,
                        'beds': None,
                        'baths': None,
                        'sqft': None,
                    }
                    
                    # Handle if card itself is a link
                    if card.name == 'a' and '/homedetails/' in card.get('href', ''):
                        link_elem = card
                    
                    if link_elem:
                        href = link_elem.get('href', '')
                        prop['url'] = f"{self.BASE_URL}{href}" if href.startswith('/') else href
                        # Extract zpid
                        zpid_match = re.search(r'(\d+)_zpid', href)
                        if zpid_match:
                            prop['zpid'] = int(zpid_match.group(1))
                    
                    # Parse beds/baths/sqft from details
                    if details_elem:
                        details_text = details_elem.get_text()
                        beds_match = re.search(r'(\d+)\s*b[de]', details_text, re.I)
                        baths_match = re.search(r'(\d+)\s*ba', details_text, re.I)
                        sqft_match = re.search(r'([\d,]+)\s*sq', details_text, re.I)
                        
                        if beds_match:
                            prop['beds'] = int(beds_match.group(1))
                        if baths_match:
                            prop['baths'] = int(baths_match.group(1))
                        if sqft_match:
                            prop['sqft'] = int(sqft_match.group(1).replace(',', ''))
                    
                    if prop.get('address') or prop.get('zpid'):
                        properties.append(prop)
        
        return properties
    
    def search_by_location(
        self,
        location: str,
        list_type: str = 'for-sale',
        page: int = 1,
        **filters
    ) -> List[Dict]:
        """
        Search properties by location.
        
        Args:
            location: Location slug (e.g., "seattle-wa")
            list_type: 'for-sale', 'for-rent', or 'sold'
            page: Page number
            **filters: Additional search filters
            
        Returns:
            List of property dictionaries
        """
        # Build URL
        url = build_search_url(location, list_type, page)
        
        try:
            soup = self.get_soup(url)
            properties = self._parse_search_results(soup)
            
            if not properties:
                raise NotFoundException(f"No properties found for location: {location}")
            
            return properties
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to search by location: {e}")
            raise ScraperException(f"Failed to search properties: {e}")
    
    def search_by_coordinates(
        self,
        lat: float,
        lng: float,
        list_type: str = 'for-sale',
        **filters
    ) -> List[Dict]:
        """
        Search properties by coordinates.
        
        Args:
            lat: Latitude
            lng: Longitude
            list_type: 'for-sale', 'for-rent', or 'sold'
            **filters: Additional search filters
            
        Returns:
            List of property dictionaries
        """
        # Create a small bounding box around coordinates
        delta = 0.05  # Approximately 3.5 miles
        
        return self.search_by_map_bounds(
            north=lat + delta,
            south=lat - delta,
            east=lng + delta,
            west=lng - delta,
            list_type=list_type,
            **filters
        )
    
    def search_by_map_bounds(
        self,
        north: float,
        south: float,
        east: float,
        west: float,
        list_type: str = 'for-sale',
        page: int = 1,
        **filters
    ) -> List[Dict]:
        """
        Search properties by map bounds.
        
        Args:
            north: Northern latitude
            south: Southern latitude
            east: Eastern longitude
            west: Western longitude
            list_type: 'for-sale', 'for-rent', or 'sold'
            page: Page number
            **filters: Additional search filters
            
        Returns:
            List of property dictionaries
        """
        # Build search query state
        map_bounds = {
            'north': north,
            'south': south,
            'east': east,
            'west': west,
        }
        
        filter_state = self._build_search_query_state(**filters)
        
        search_query_state = {
            'mapBounds': map_bounds,
            'isMapVisible': True,
            'filterState': filter_state,
            'isListVisible': True,
        }
        
        if page > 1:
            search_query_state['pagination'] = {'currentPage': page}
        
        # URL encode the query state
        query_string = urlencode({
            'searchQueryState': json.dumps(search_query_state)
        })
        
        url = f"{self.BASE_URL}/homes/?{query_string}"
        
        try:
            soup = self.get_soup(url)
            properties = self._parse_search_results(soup)
            
            if not properties:
                raise NotFoundException("No properties found in specified bounds")
            
            return properties
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to search by map bounds: {e}")
            raise ScraperException(f"Failed to search properties: {e}")
    
    def search_by_mls_id(self, mls_id: str, **filters) -> List[Dict]:
        """
        Search properties by MLS ID.
        
        Args:
            mls_id: MLS listing ID
            **filters: Additional search filters
            
        Returns:
            List of property dictionaries
        """
        try:
            # Search for the MLS ID
            search_url = f"{self.BASE_URL}/homes/{mls_id}/"
            soup = self.get_soup(search_url)
            properties = self._parse_search_results(soup)
            
            if not properties:
                raise NotFoundException(f"No properties found for MLS ID: {mls_id}")
            
            return properties
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to search by MLS ID: {e}")
            raise ScraperException(f"Failed to search by MLS ID: {e}")
    
    def search_by_polygon(
        self,
        polygon: str,
        list_type: str = 'for-sale',
        page: int = 1,
        **filters
    ) -> List[Dict]:
        """
        Search properties by polygon coordinates.
        
        Args:
            polygon: Semicolon-separated coordinates (lat,lng;lat,lng;...)
            list_type: 'for-sale', 'for-rent', or 'sold'
            page: Page number
            **filters: Additional search filters
            
        Returns:
            List of property dictionaries
        """
        # Parse polygon coordinates
        coords = []
        for point in polygon.split(';'):
            parts = point.strip().split(',')
            if len(parts) == 2:
                coords.append({
                    'lat': float(parts[0]),
                    'lng': float(parts[1])
                })
        
        if len(coords) < 3:
            raise ValueError("Polygon must have at least 3 points")
        
        # Calculate bounding box from polygon
        lats = [c['lat'] for c in coords]
        lngs = [c['lng'] for c in coords]
        
        return self.search_by_map_bounds(
            north=max(lats),
            south=min(lats),
            east=max(lngs),
            west=min(lngs),
            list_type=list_type,
            page=page,
            **filters
        )
    
    def search_by_url(self, url: str) -> List[Dict]:
        """
        Parse a Zillow URL and return results.
        Handles both search result pages and individual property detail pages.
        
        Args:
            url: Full Zillow URL (search results or property detail)
            
        Returns:
            List of property dictionaries
        """
        try:
            soup = self.get_soup(url)
            
            # Check if page is blocked
            title = soup.find('title')
            title_text = title.get_text().lower() if title else ''
            logger.info(f"Page title: '{title_text}', page size: {len(str(soup))}")
            
            if 'denied' in title_text or 'blocked' in title_text or 'captcha' in title_text:
                logger.warning(f"Block detected! Title: {title_text}")
                raise BlockedException("Request blocked by Zillow - access denied")
            
            # Check if this is a single property detail page (/homedetails/)
            if '/homedetails/' in url:
                property_data = self._parse_property_details(soup, url)
                if property_data:
                    return [property_data]
                raise NotFoundException("No property details found at URL")
            
            # Otherwise, treat as search results page
            properties = self._parse_search_results(soup)
            
            if not properties:
                raise NotFoundException("No properties found at URL")
            
            return properties
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to parse URL: {e}")
            raise ScraperException(f"Failed to parse URL: {e}")
    
    def _parse_property_details(self, soup, url: str) -> Optional[Dict]:
        """Parse a single property detail page."""
        try:
            script_data = extract_json_from_script(soup)
            
            if not script_data:
                return None
            
            property_data = {}
            
            # Try new structure: componentProps.gdpClientCache (JSON string)
            component_props = script_data.get('componentProps', {})
            gdp_cache = component_props.get('gdpClientCache', '')
            
            if isinstance(gdp_cache, str) and gdp_cache:
                try:
                    gdp_data = json.loads(gdp_cache)
                    # Find any key that contains a 'property' object
                    for key, value in gdp_data.items():
                        if isinstance(value, dict) and 'property' in value:
                            property_data = value.get('property', {})
                            if property_data:
                                logger.info(f"Found property data in gdpClientCache")
                                break
                except json.JSONDecodeError:
                    pass
            
            # Fallback to old structure
            if not property_data:
                property_data = (
                    script_data.get('property', {}) or
                    script_data.get('propertyDetails', {}) or
                    script_data.get('listing', {}) or
                    {}
                )
            
            # Extract zpid from URL if not in data
            zpid = property_data.get('zpid')
            if not zpid:
                import re
                match = re.search(r'/(\d+)_zpid', url)
                if match:
                    zpid = int(match.group(1))
            
            # Build address from components
            address_parts = []
            street = property_data.get('streetAddress', '')
            city = property_data.get('city', '')
            state = property_data.get('state', '')
            zipcode = property_data.get('zipcode', '')
            
            if street:
                address_parts.append(street)
            if city:
                address_parts.append(city)
            if state:
                address_parts.append(state)
            if zipcode:
                address_parts.append(zipcode)
            
            address = ', '.join(address_parts) if address_parts else property_data.get('address', '')
            
            # Get photo
            photo_url = ''
            photos = property_data.get('hiResImageLink') or property_data.get('photos', [])
            if isinstance(photos, list) and photos:
                first_photo = photos[0]
                if isinstance(first_photo, dict):
                    photo_url = first_photo.get('mixedSources', {}).get('jpeg', [{}])[0].get('url', '')
                else:
                    photo_url = first_photo
            elif isinstance(photos, str):
                photo_url = photos
                
            return {
                'zpid': zpid,
                'address': address,
                'url': url,
                'photo_url': photo_url,
                'price': clean_price(property_data.get('price') or property_data.get('zestimate')),
                'beds': property_data.get('bedrooms') or property_data.get('beds'),
                'baths': property_data.get('bathrooms') or property_data.get('baths'),
                'sqft': property_data.get('livingArea') or property_data.get('livingAreaValue'),
                'property_type': property_data.get('homeType', ''),
                'status': property_data.get('homeStatus', ''),
                'latitude': property_data.get('latitude'),
                'longitude': property_data.get('longitude'),
                'brokerage': (property_data.get('attributionInfo', {}).get('brokerName') or
                             property_data.get('brokerageName') or 
                             property_data.get('listingProvider', '')),
                'description': clean_text(property_data.get('description', '')),
                'year_built': property_data.get('yearBuilt'),
                'lot_size': property_data.get('lotSize'),
            }
        except Exception as e:
            logger.warning(f"Failed to parse property details: {e}")
            return None
    
    def get_apartment_details(self, url: str) -> Dict:
        """
        Get apartment/building details.
        
        Args:
            url: Apartment listing URL
            
        Returns:
            Apartment details dictionary
        """
        try:
            soup = self.get_soup(url)
            
            details = {
                'url': url,
                'name': '',
                'address': '',
                'description': '',
                'units': [],
                'amenities': [],
                'photos': [],
            }
            
            # Try script data - new structure: componentProps.initialReduxState.gdp.building
            script_data = extract_json_from_script(soup)
            if script_data:
                building = None
                
                # Try new structure
                component_props = script_data.get('componentProps', {})
                redux_state = component_props.get('initialReduxState', {})
                gdp = redux_state.get('gdp', {})
                if gdp:
                    building = gdp.get('building', {})
                
                # Fallback to old structure
                if not building:
                    building = script_data.get('building', {}) or script_data.get('property', {})
                
                if building:
                    # Build full address
                    street = building.get('streetAddress', '')
                    city = building.get('city', '')
                    state = building.get('state', '')
                    zipcode = building.get('zipcode', '')
                    full_address = building.get('fullAddress', '')
                    
                    if not full_address and street:
                        parts = [street]
                        if city:
                            parts.append(city)
                        if state:
                            parts.append(state)
                        if zipcode:
                            parts.append(zipcode)
                        full_address = ', '.join(parts)
                    
                    # Extract amenities from structuredAmenities
                    amenities = []
                    structured = building.get('structuredAmenities') or []
                    if structured:
                        for category in structured:
                            if isinstance(category, dict):
                                items = category.get('items') or []
                                for item in items:
                                    if isinstance(item, dict) and item.get('text'):
                                        amenities.append(item.get('text', ''))
                    
                    # Extract photos
                    photos = []
                    photo_list = building.get('photos') or building.get('galleryPhotos') or []
                    if photo_list:
                        for photo in photo_list:
                            if isinstance(photo, dict):
                                # Try to get URL from mixedSources
                                mixed = photo.get('mixedSources') or {}
                                jpeg = mixed.get('jpeg') or []
                                if jpeg and len(jpeg) > 0:
                                    photos.append(jpeg[-1].get('url', ''))  # Get largest
                                elif photo.get('url'):
                                    photos.append(photo.get('url'))
                    
                    # Extract floor plans / units
                    units = building.get('floorPlans') or building.get('ungroupedUnits') or []
                    
                    details.update({
                        'name': building.get('buildingName', '') or street,
                        'address': full_address,
                        'description': clean_text(building.get('description', '') or ''),
                        'units': units,
                        'amenities': amenities,
                        'photos': photos,
                    })
            
            # Fallback: Parse HTML
            if not details['name']:
                name_elem = soup.select_one('h1, [data-test="building-name"]')
                if name_elem:
                    details['name'] = clean_text(name_elem.get_text())
            
            if not details['address']:
                addr_elem = soup.select_one('[data-test="building-address"], address')
                if addr_elem:
                    details['address'] = clean_text(addr_elem.get_text())
            
            if not details['name']:
                raise NotFoundException(f"Apartment details not found: {url}")
            
            return details
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to get apartment details: {e}")
            raise ScraperException(f"Failed to get apartment details: {e}")
    
    def autocomplete(self, query: str) -> List[Dict]:
        """
        Get location autocomplete suggestions.
        
        Args:
            query: Search query
            
        Returns:
            List of suggestion dictionaries
        """
        # Zillow's autocomplete API - requires specific headers
        url = "https://www.zillow.com/zg-graph"
        
        # GraphQL query for autocomplete
        payload = {
            "query": """
                query getAutoCompleteResults($query: String!) {
                    zgsAutocompleteRequest(query: $query) {
                        results {
                            display
                            resultType
                            metaData {
                                regionId
                                regionType
                                city
                                state
                                county
                            }
                        }
                    }
                }
            """,
            "variables": {"query": query}
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Referer': 'https://www.zillow.com/',
            'Origin': 'https://www.zillow.com',
        }
        
        try:
            import requests
            
            # Make direct request with proper headers
            response = requests.post(
                url,
                json=payload,
                headers={**self._get_headers(), **headers},
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                # Fallback: Use simple search redirect approach
                return self._autocomplete_fallback(query)
            
            data = response.json()
            
            results = data.get('data', {}).get('zgsAutocompleteRequest', {}).get('results', [])
            
            suggestions = []
            for result in results:
                meta = result.get('metaData', {}) or {}
                suggestions.append({
                    'display': result.get('display', ''),
                    'type': result.get('resultType', ''),
                    'id': meta.get('regionId', ''),
                    'city': meta.get('city', ''),
                    'state': meta.get('state', ''),
                })
            
            if not suggestions:
                return self._autocomplete_fallback(query)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"GraphQL autocomplete failed: {e}, trying fallback")
            return self._autocomplete_fallback(query)
    
    def _autocomplete_fallback(self, query: str) -> List[Dict]:
        """Fallback autocomplete using search page parsing."""
        try:
            # Try to search and extract suggestions from the page
            search_url = f"{self.BASE_URL}/homes/{query.replace(' ', '-')}_rb/"
            
            soup = self.get_soup(search_url)
            
            # Return a simple suggestion based on the query
            return [{
                'display': query.title(),
                'type': 'search',
                'id': '',
                'city': query.title(),
                'state': '',
            }]
            
        except Exception as e:
            logger.error(f"Autocomplete fallback failed: {e}")
            raise NotFoundException(f"No suggestions found for: {query}")


# Singleton instance
property_scraper = PropertyScraper()
