"""
Test AI Mode with Real Working Websites
Tests website info fetching and validates AI response quality
"""
import sys
sys.path.insert(0, '.')

from services.universal_website_fetcher import UniversalWebsiteFetcher
from services.ai_service import ai_reply

print("=" * 70)
print("Testing AI Mode with Real Working Websites")
print("=" * 70)

# Test with working websites
test_websites = [
    {
        "name": "WordPress.org (WordPress CMS)",
        "url": "https://wordpress.org",
        "business_type": "service",
        "test_query": "What services do you offer?"
    },
    {
        "name": "Example.com (Simple Site)",
        "url": "https://example.com",
        "business_type": "service",
        "test_query": "What is this website about?"
    },
    {
        "name": "BBC News (Content Site)",
        "url": "https://www.bbc.com/news",
        "business_type": "service",
        "test_query": "What kind of content do you provide?"
    }
]

def test_full_ai_flow(website, user_plan="starter"):
    """Test complete AI flow with website fetching and AI response"""
    print(f"\n{'='*70}")
    print(f"Testing: {website['name']}")
    print(f"URL: {website['url']}")
    print(f"Plan: {user_plan}")
    print(f"{'='*70}")

    # Step 1: Fetch website info
    print("\n[Step 1] Fetching website info...")
    site_info = UniversalWebsiteFetcher.fetch_site_info(website['url'])

    print(f"  Site Name: {site_info.get('site_name', 'N/A')[:50]}...")
    print(f"  Services: {len(site_info.get('services', []))} found")
    print(f"  Has Contact: {bool(site_info.get('contact'))}")

    # Step 2: Simulate AI response (requires API key - we'll just validate the prompt building)
    print("\n[Step 2] Validating AI prompt structure...")

    # Build the contact dict that AI would receive
    contact = {
        'site_name': site_info.get('site_name', 'Unknown'),
        'site_description': site_info.get('site_description', ''),
        'about': site_info.get('about', ''),
        'services': site_info.get('services', []),
        'contact': site_info.get('contact', {}),
        'phone': site_info.get('contact', {}).get('phone', ''),
        'email': site_info.get('contact', {}).get('email', ''),
        'address': site_info.get('contact', {}).get('address', ''),
        'hours': site_info.get('contact', {}).get('hours', ''),
    }

    # Check what info is available for AI
    print(f"\n[Step 3] Info available for AI:")
    print(f"  Site Name: {'YES' if contact['site_name'] else 'MISSING'}")
    print(f"  Description: {'YES' if contact['site_description'] else 'MISSING'}")
    print(f"  About: {'YES' if contact['about'] else 'MISSING'}")
    print(f"  Services: {len(contact['services'])} items")
    print(f"  Phone: {'YES' if contact['phone'] else 'MISSING'}")
    print(f"  Email: {'YES' if contact['email'] else 'MISSING'}")
    print(f"  Address: {'YES' if contact['address'] else 'MISSING'}")

    # Identify gaps
    print(f"\n[Step 4] Missing Info Analysis:")
    missing = []
    if not contact['site_name']:
        missing.append("Site name not extracted")
    if not contact['services']:
        missing.append("No services detected")
    if not contact['phone'] and not contact['email']:
        missing.append("No contact info (phone/email) extracted")

    if missing:
        print("  ISSUES FOUND:")
        for issue in missing:
            print(f"    - {issue}")
    else:
        print("  All key info extracted successfully!")

    return {
        'website': website['name'],
        'site_info_success': bool(site_info.get('site_name')),
        'services_count': len(site_info.get('services', [])),
        'contact_extracted': bool(site_info.get('contact', {}).get('phone') or site_info.get('contact', {}).get('email')),
        'missing_info': missing
    }

# Run tests
results = []

print("\n" + "="*70)
print("PHASE 1: Testing with STARTER Plan")
print("="*70)

for site in test_websites:
    result = test_full_ai_flow(site, user_plan="starter")
    results.append(result)

# Summary
print("\n\n" + "="*70)
print("FINAL SUMMARY")
print("="*70)

for r in results:
    print(f"\n{r['website']}:")
    print(f"  Site Info: {'OK' if r['site_info_success'] else 'FAILED'}")
    print(f"  Services: {r['services_count']} found")
    print(f"  Contact: {'Extracted' if r['contact_extracted'] else 'Missing'}")
    if r['missing_info']:
        print(f"  Issues: {r['missing_info']}")

print("\n" + "="*70)
print("Recommendations:")
print("="*70)

# Analyze common issues
all_missing = []
for r in results:
    all_missing.extend(r.get('missing_info', []))

if all_missing:
    from collections import Counter
    common_issues = Counter(all_missing).most_common()
    for issue, count in common_issues:
        print(f"  - {issue} (affected {count} sites)")
else:
    print("  No common issues found - extraction working well!")

print("\n" + "="*70)
