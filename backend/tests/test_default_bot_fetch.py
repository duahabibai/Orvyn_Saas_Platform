"""Test default bot cache refresh"""
from services.default_bot import refresh_cache, _get_cache

# Test with the actual integration data
bot_id = 3
woo_key = ""
woo_secret = ""
woo_url = "https://hibascollection.com"
wp_url = "https://hibascollection.com/"

print(f"Refreshing cache for bot {bot_id}...")
print(f"URL: {woo_url}")
print(f"WP URL: {wp_url}")
print(f"Has Woo Keys: {bool(woo_key)}")

refresh_cache(bot_id, woo_key, woo_secret, woo_url, wp_url=wp_url)

c = _get_cache(bot_id)
print(f"\nProducts: {len(c.get('products', []))}")
print(f"Categories: {len(c.get('categories', []))}")
print(f"Contact: {c.get('contact', {})}")

if c.get('products'):
    print(f"\nFirst product:")
    p = c['products'][0]
    if isinstance(p, dict):
        print(f"  Name: {p.get('name', 'N/A')}")
        print(f"  Price: {p.get('price', 'N/A')}")
        print(f"  SKU: {p.get('sku', 'N/A')}")
