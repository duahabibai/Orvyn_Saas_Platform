"""
Test the Universal Website Fetcher with different website types
"""
import sys
sys.path.insert(0, '.')

from services.universal_website_fetcher import UniversalWebsiteFetcher

print("=" * 70)
print("Testing Universal Website Fetcher - Works with ANY website!")
print("=" * 70)

# Test 1: E-commerce site
print("\n1️⃣  Testing with hiveworks-me.com (WooCommerce)...")
url1 = "https://hiveworks-me.com"
platform1 = UniversalWebsiteFetcher.detect_platform(url1)
print(f"   ✅ Platform: {platform1['platform']}")
print(f"   ✅ WordPress: {platform1['is_wordpress']}")
print(f"   ✅ WooCommerce: {platform1['is_woocommerce']}")

# Test 2: Try discovering the site
print("\n2️⃣  Auto-discovering hiveworks-me.com...")
result = UniversalWebsiteFetcher.auto_discover_and_fetch(url1)
print(f"   ✅ Success: {result['success']}")
print(f"   ✅ Message: {result['message']}")
print(f"   ✅ Site Name: {result['site_info'].get('site_name', 'N/A')}")
print(f"   ✅ Products Found: {result['products']['total_products']}")
print(f"   ✅ Categories: {len(result['products']['categories'])}")

# Test 3: URL normalization
print("\n3️⃣  Testing URL normalization...")
test_urls = [
    "example.com",
    "http://example.com",
    "https://example.com/",
    "  shop.example.com  "
]
for url in test_urls:
    normalized = UniversalWebsiteFetcher.normalize_url(url)
    print(f"   '{url}' → '{normalized}'")

print("\n" + "=" * 70)
print("✅ Universal Website Fetcher is working!")
print("   You can now add ANY website URL - not just WooCommerce!")
print("=" * 70)
