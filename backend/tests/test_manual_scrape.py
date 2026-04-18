import sys
import os
import json

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.universal_website_fetcher import UniversalWebsiteFetcher

def test_scrape():
    url = "https://brandlessdigital.com/"
    print(f"Testing scrape for: {url}")
    
    # 1. Detect platform
    plat = UniversalWebsiteFetcher.detect_platform(url)
    print(f"Platform: {json.dumps(plat, indent=2)}")
    
    # 2. Fetch site info
    info = UniversalWebsiteFetcher.fetch_site_info(url)
    print(f"Site Info: {json.dumps(info, indent=2)}")
    
    # 3. Scrape products
    res = UniversalWebsiteFetcher.scrape_products_from_website(url)
    print(f"Scrape Result Success: {res.get('success')}")
    print(f"Products Found: {len(res.get('products', []))}")
    if res.get('products'):
        print(f"First product: {res.get('products')[0]}")

if __name__ == "__main__":
    test_scrape()
