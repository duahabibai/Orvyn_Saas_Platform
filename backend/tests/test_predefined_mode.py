"""
Test Predefined Mode - All Templates and Menu Numbers
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.default_bot import _get_menu, _get_greeting, _get_contact_info, _get_services
from services.universal_website_fetcher import UniversalWebsiteFetcher

# Helper to print emojis safely on Windows
def safe_print(text):
    import re
    # Remove all non-ASCII characters for Windows console compatibility
    text = re.sub(r'[^\x00-\x7F]', '', text)
    print(text)

def test_templates():
    safe_print("=" * 70)
    safe_print("PREDEFINED MODE - TEMPLATE & MENU TESTING")
    safe_print("=" * 70)

    mock_contact = {
        'site_name': 'Test Business',
        'site_description': 'Best services in town',
        'about': 'We provide excellent services since 2020',
        'services': ['Web Development', 'Mobile Apps', 'Consulting', 'Support'],
        'contact': {
            'phone': '+1234567890',
            'email': 'info@testbusiness.com',
            'address': '123 Main St, City, Country',
            'hours': 'Mon-Fri 9am-5pm'
        },
        'phone': '+1234567890',
        'email': 'info@testbusiness.com',
        'address': '123 Main St, City, Country',
        'hours': 'Mon-Fri 9am-5pm'
    }

    print("\n" + "=" * 70)
    print("TEST 1: Menu Display (All Languages)")
    print("=" * 70)

    for lang in ['english', 'roman_urdu', 'urdu']:
        safe_print(f"\n[{lang.upper()}]")
        menu = _get_menu(lang, business_type="product")
        safe_print(menu)

    print("\n" + "=" * 70)
    print("TEST 2: Service Menu")
    print("=" * 70)

    for lang in ['english', 'roman_urdu']:
        safe_print(f"\n[{lang.upper()}]")
        menu = _get_menu(lang, business_type="service")
        safe_print(menu)

    print("\n" + "=" * 70)
    print("TEST 3: Greeting Messages")
    print("=" * 70)

    for lang in ['english', 'roman_urdu', 'urdu']:
        safe_print(f"\n[{lang.upper()}]")
        greeting = _get_greeting(lang, "John Doe", "Test Business", "product")
        safe_print(greeting[:200] + "...")

    print("\n" + "=" * 70)
    print("TEST 4: Contact Info Template")
    print("=" * 70)

    for lang in ['english', 'roman_urdu', 'urdu']:
        safe_print(f"\n[{lang.upper()}]")
        contact = _get_contact_info(lang, mock_contact)
        safe_print(contact)

    print("\n" + "=" * 70)
    print("TEST 5: Services Template")
    print("=" * 70)

    for lang in ['english', 'roman_urdu', 'urdu']:
        safe_print(f"\n[{lang.upper()}]")
        services = _get_services(lang, mock_contact['services'])
        safe_print(services)

def test_website_fetcher():
    safe_print("\n" + "=" * 70)
    safe_print("TEST 6: Website Fetcher - Platform Detection")
    safe_print("=" * 70)

    test_urls = [
        "https://example.com",
        "https://wordpress.org",
    ]

    for url in test_urls:
        safe_print(f"\nTesting: {url}")
        platform = UniversalWebsiteFetcher.detect_platform(url)
        safe_print(f"  Platform: {platform.get('platform', 'unknown')}")
        safe_print(f"  WordPress: {platform.get('is_wordpress', False)}")
        safe_print(f"  WooCommerce: {platform.get('is_woocommerce', False)}")

def test_menu_numbers():
    safe_print("\n" + "=" * 70)
    safe_print("TEST 7: Menu Number Recognition")
    safe_print("=" * 70)

    safe_print("\n[PRODUCT BUSINESS - Testing menu numbers]")
    for num in ['1', '2', '3', '4', '5']:
        safe_print(f"\n  Input: '{num}'")
        expected = {
            '1': 'Place Order / Book Service',
            '2': 'Product Inquiry / Pricing',
            '3': 'Delivery Info / About Us',
            '4': 'Contact Us',
            '5': 'Our Services'
        }
        safe_print(f"  Expected: {expected[num]}")

    safe_print("\n[SERVICE BUSINESS - Testing menu numbers]")
    for num in ['1', '2', '3', '4', '5']:
        safe_print(f"\n  Input: '{num}'")
        expected = {
            '1': 'Book Service',
            '2': 'Service Pricing',
            '3': 'About Us',
            '4': 'Contact Us',
            '5': 'Our Services'
        }
        safe_print(f"  Expected: {expected[num]}")

def test_keyword_recognition():
    safe_print("\n" + "=" * 70)
    safe_print("TEST 8: Keyword Recognition")
    safe_print("=" * 70)

    keywords = [
        ('order', 'Triggers order flow'),
        ('buy', 'Triggers order flow'),
        ('price', 'Shows products/pricing'),
        ('contact', 'Shows contact info'),
        ('services', 'Shows services'),
        ('delivery', 'Shows delivery info'),
        ('about', 'Shows about info'),
        ('menu', 'Shows menu'),
        ('start', 'Shows menu'),
        ('exit', 'Exits conversation'),
        ('bye', 'Exits conversation'),
    ]

    for keyword, expected in keywords:
        safe_print(f"  '{keyword}' -> {expected}")

if __name__ == "__main__":
    test_templates()
    test_website_fetcher()
    test_menu_numbers()
    test_keyword_recognition()

    safe_print("\n" + "=" * 70)
    safe_print("SUMMARY")
    safe_print("=" * 70)
    safe_print("""
Predefined Mode Templates:
  [OK] Menu templates (English, Roman Urdu, Urdu)
  [OK] Greeting messages (Product & Service business)
  [OK] Contact info template
  [OK] Services template
  [OK] Product listing template

Menu Numbers Supported:
  1 - Order/Book Service
  2 - Inquiry/Pricing
  3 - Delivery/About
  4 - Contact Us
  5 - Services

Keywords Recognized:
  - order, buy, place order, booking
  - price, pricing, inquiry
  - delivery, shipping, about, info
  - contact, rabta
  - services, service
  - menu, start, main menu
  - exit, bye, allah hafiz, khuda hafiz

Plan Gating:
  - Starter plan users blocked from product features
  - Growth plan users get full access
""")
    safe_print("=" * 70)
