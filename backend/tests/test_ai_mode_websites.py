"""
Test AI Mode with Different Website URLs
Tests website info fetching and AI responses for various website types
"""
import sys
sys.path.insert(0, '.')

from services.universal_website_fetcher import UniversalWebsiteFetcher
from services.ai_service import ai_reply

print("=" * 70)
print("Testing AI Mode with Different Website URLs")
print("=" * 70)

# Test websites - different types
test_websites = [
    {
        "name": "WooCommerce Site",
        "url": "https://hiveworks-me.com",
        "business_type": "product"
    },
    {
        "name": "WordPress Site",
        "url": "https://wordpress.org",
        "business_type": "service"
    },
    {
        "name": "Simple Business Site",
        "url": "https://example.com",
        "business_type": "service"
    }
]

def test_website_fetch(url, business_type):
    """Test fetching website info"""
    print(f"\n{'='*50}")
    print(f"Testing: {url}")
    print(f"{'='*50}")

    # 1. Platform Detection
    print("\n1. Platform Detection:")
    platform = UniversalWebsiteFetcher.detect_platform(url)
    print(f"   Platform: {platform['platform']}")
    print(f"   Is WordPress: {platform['is_wordpress']}")
    print(f"   Is WooCommerce: {platform['is_woocommerce']}")
    print(f"   Is Shopify: {platform['is_shopify']}")

    # 2. Site Info Fetch
    print("\n2. Site Info Fetch:")
    site_info = UniversalWebsiteFetcher.fetch_site_info(url)
    print(f"   Site Name: {site_info.get('site_name', 'N/A')}")
    print(f"   Site Description: {site_info.get('site_description', 'N/A')[:100]}...")
    print(f"   About: {site_info.get('about', 'N/A')[:100]}...")
    print(f"   Services Count: {len(site_info.get('services', []))}")
    if site_info.get('services'):
        print(f"   Services: {site_info['services'][:5]}")

    # Contact Info
    contact = site_info.get('contact', {})
    print(f"\n3. Contact Info:")
    print(f"   Phone: {contact.get('phone', 'N/A')}")
    print(f"   Email: {contact.get('email', 'N/A')}")
    print(f"   Address: {contact.get('address', 'N/A')}")
    print(f"   Hours: {contact.get('hours', 'N/A')}")

    # Product scraping (for product sites)
    if business_type == "product":
        print("\n4. Product Scraping:")
        products = UniversalWebsiteFetcher.scrape_products_from_website(url)
        print(f"   Success: {products.get('success', False)}")
        print(f"   Products Found: {products.get('total_products', 0)}")
        if products.get('products'):
            print(f"   Sample Products: {products['products'][:3]}")

    return site_info

def test_ai_response(site_info, business_type, user_plan="starter"):
    """Test AI response with fetched website info"""
    print(f"\n{'='*50}")
    print("Testing AI Response Generation")
    print(f"{'='*50}")
    print(f"Business Type: {business_type}")
    print(f"User Plan: {user_plan}")

    # Simulate AI reply (without actual API call - just check prompt building)
    site_name = site_info.get('site_name', 'our business')
    site_desc = site_info.get('site_description', '')
    about = site_info.get('about', '')
    services = site_info.get('services', [])
    contact = site_info.get('contact', {})

    print(f"\nSite Name passed to AI: {site_name}")
    print(f"Services passed to AI: {len(services)} services")
    print(f"Contact Info passed to AI: {bool(contact)}")

    # Check what the AI would see
    show_products = (user_plan == "growth" and business_type == "product")
    print(f"\nAI Feature Access:")
    print(f"   Show Products: {show_products}")
    print(f"   User Plan: {user_plan}")

    return True

# Run tests
results = {}

for test_site in test_websites:
    print(f"\n\n{'#'*70}")
    print(f"# TESTING: {test_site['name']}")
    print(f"# URL: {test_site['url']}")
    print(f"{'#'*70}")

    try:
        # Fetch website info
        site_info = test_website_fetch(
            test_site['url'],
            test_site['business_type']
        )

        # Test AI response generation (starter plan)
        ai_result_starter = test_ai_response(
            site_info,
            test_site['business_type'],
            user_plan="starter"
        )

        # Test AI response generation (growth plan)
        ai_result_growth = test_ai_response(
            site_info,
            test_site['business_type'],
            user_plan="growth"
        )

        results[test_site['name']] = {
            "success": True,
            "site_name": site_info.get('site_name', 'N/A'),
            "services_count": len(site_info.get('services', [])),
            "has_contact": bool(site_info.get('contact')),
        }

    except Exception as e:
        print(f"ERROR: {e}")
        results[test_site['name']] = {
            "success": False,
            "error": str(e)
        }

# Summary
print(f"\n\n{'='*70}")
print("TEST SUMMARY")
print("="*70)
for name, result in results.items():
    status = "PASS" if result.get('success') else "FAIL"
    print(f"\n{name}: {status}")
    if result.get('success'):
        print(f"  - Site Name: {result.get('site_name', 'N/A')}")
        print(f"  - Services Found: {result.get('services_count', 0)}")
        print(f"  - Contact Info: {'Found' if result.get('has_contact') else 'Missing'}")
    else:
        print(f"  - Error: {result.get('error', 'Unknown')}")

print("\n" + "="*70)
print("Testing Complete!")
print("="*70)
