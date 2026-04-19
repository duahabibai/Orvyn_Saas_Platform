"""
Test AI Mode with Real Business Websites
Tests websites that typically have contact info (local businesses, services)
"""
import sys
sys.path.insert(0, '.')

from services.universal_website_fetcher import UniversalWebsiteFetcher

print("=" * 70)
print("Testing AI Mode with Business Websites (Contact Info Focus)")
print("=" * 70)

# Test with business websites that should have contact info
test_websites = [
    {
        "name": "WordPress.org (Tech Service)",
        "url": "https://wordpress.org",
        "business_type": "service",
        "expected": "Services and about info"
    },
    {
        "name": "Example.com (Simple)",
        "url": "https://example.com",
        "business_type": "service",
        "expected": "Basic info only"
    },
    {
        "name": "BBC News (Media)",
        "url": "https://www.bbc.com/news",
        "business_type": "service",
        "expected": "About info, some contact links"
    }
]

def test_website(website):
    """Test website info extraction"""
    print(f"\n{'='*70}")
    print(f"Testing: {website['name']}")
    print(f"URL: {website['url']}")
    print(f"Expected: {website['expected']}")
    print(f"{'='*70}")

    # Fetch site info
    site_info = UniversalWebsiteFetcher.fetch_site_info(website['url'])

    # Display results - encode to avoid Windows console Unicode errors
    def safe_str(s, max_len=60):
        return str(s)[:max_len].encode('utf-8').decode('ascii', 'ignore')

    # Display results
    print(f"\n[EXTRACTION RESULTS]")
    print(f"  [+] Site Name: '{safe_str(site_info.get('site_name', 'MISSING'))}...'")
    print(f"  [+] Description: '{safe_str(site_info.get('site_description', 'MISSING'))}...'")
    print(f"  [+] About: '{safe_str(site_info.get('about', 'MISSING'))}...'")
    print(f"  [+] Services: {len(site_info.get('services', []))} found")
    if site_info.get('services'):
        for s in site_info['services'][:5]:
            print(f"      - {safe_str(s)}")

    # Contact info
    contact = site_info.get('contact', {})
    print(f"\n[CONTACT INFO]")
    print(f"  Phone: {contact.get('phone', 'MISSING (common for large sites)')}")
    print(f"  Email: {contact.get('email', 'MISSING (common for large sites)')}")
    print(f"  Address: {safe_str(contact.get('address', 'MISSING'), max_len=40)}")
    print(f"  Hours: {safe_str(contact.get('hours', 'MISSING'), max_len=40)}")

    # Evaluation
    print(f"\n[EVALUATION]")
    has_basic_info = bool(site_info.get('site_name')) and bool(site_info.get('about'))
    has_contact = bool(contact.get('phone') or contact.get('email'))
    has_services = len(site_info.get('services', [])) > 0

    print(f"  Basic Info (name + about): {'YES' if has_basic_info else 'NO'}")
    print(f"  Direct Contact (phone/email): {'YES' if has_contact else 'NO (site links to contact page)'}")
    print(f"  Services/Categories: {'YES' if has_services else 'NO'}")

    # AI readiness
    print(f"\n[AI READINESS]")
    if has_basic_info:
        print(f"  [OK] AI can answer questions about what this site/business is")
    if has_services:
        print(f"  [OK] AI can list services/categories offered")
    if has_contact:
        print(f"  [OK] AI can provide direct contact info")
    else:
        print(f"  [INFO] AI will guide users to check website's contact page")

    return {
        'website': website['name'],
        'has_basic_info': has_basic_info,
        'has_contact': has_contact,
        'has_services': has_services,
        'services_count': len(site_info.get('services', []))
    }

# Run tests
results = []
for site in test_websites:
    result = test_website(site)
    results.append(result)

# Summary
print(f"\n\n{'='*70}")
print("SUMMARY: AI Mode Website Info Extraction")
print("="*70)

for r in results:
    print(f"\n{r['website']}:")
    print(f"  Basic Info: {'OK' if r['has_basic_info'] else 'MISSING'}")
    print(f"  Direct Contact: {'OK' if r['has_contact'] else 'LINKS TO CONTACT PAGE'}")
    print(f"  Services: {r['services_count']} found")

print(f"\n{'='*70}")
print("NOTES:")
print("="*70)
print("""
1. Large websites (WordPress.org, BBC) often don't have direct contact
   info on homepage - they link to dedicated contact pages. This is
   NORMAL behavior and the AI handles it by guiding users appropriately.

2. Small business websites typically DO have contact info directly on
   their homepage - the scraper is designed to extract that.

3. The AI mode works with ANY extracted info:
   - If site name + about exists -> AI can describe the business
   - If services exist -> AI can list them
   - If contact exists -> AI can share phone/email
   - If no contact -> AI politely guides users to check website

4. For WooCommerce sites with API credentials -> Full product catalog
   is available to AI (Growth plan only).
""")

print("="*70)
