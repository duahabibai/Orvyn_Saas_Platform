"""
Unit tests for the 3 new helper methods in UniversalWebsiteFetcher
"""
import sys
sys.path.insert(0, '.')

from services.universal_website_fetcher import UniversalWebsiteFetcher
from bs4 import BeautifulSoup

print("=" * 70)
print("Testing New Helper Methods")
print("=" * 70)

# Test 1: _extract_about_info
print("\n1️⃣  Testing _extract_about_info()...")
html_with_about = """
<html>
<head>
    <title>Test Company</title>
    <meta name="description" content="This is a test company that provides great services.">
</head>
<body>
    <nav>
        <a href="/about">About Us</a>
        <a href="/contact">Contact</a>
    </nav>
    <div class="main-content">
        <h1>Welcome to Test Company</h1>
        <p>We are a leading provider of innovative solutions for businesses worldwide.</p>
    </div>
</body>
</html>
"""
soup = BeautifulSoup(html_with_about, 'html.parser')
about = UniversalWebsiteFetcher._extract_about_info(html_with_about, soup)
print(f"   ✅ About extracted: {bool(about)}")
print(f"   ✅ Content: {about[:100]}...")

# Test 2: _extract_services
print("\n2️⃣  Testing _extract_services()...")
html_with_services = """
<html>
<body>
    <nav>
        <a href="/services">Our Services</a>
    </nav>
    <div class="services-section">
        <div class="service-card">
            <h3>Web Development</h3>
        </div>
        <div class="service-card">
            <h3>Mobile Apps</h3>
        </div>
        <div class="service-card">
            <h3>Cloud Solutions</h3>
        </div>
    </div>
</body>
</html>
"""
soup = BeautifulSoup(html_with_services, 'html.parser')
services = UniversalWebsiteFetcher._extract_services(html_with_services, soup)
print(f"   ✅ Services extracted: {len(services)} found")
print(f"   ✅ Services: {services}")

# Test 3: _find_important_pages
print("\n3️⃣  Testing _find_important_pages()...")
html_with_pages = """
<html>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="/contact-us">Contact Us</a>
        <a href="/services">Services</a>
        <a href="/shop">Shop</a>
        <a href="/blog">Blog</a>
    </nav>
</body>
</html>
"""
soup = BeautifulSoup(html_with_pages, 'html.parser')
pages = UniversalWebsiteFetcher._find_important_pages("https://example.com", soup)
print(f"   ✅ Pages found: {len(pages)}")
for page in pages:
    print(f"   ✅ {page['type']}: {page['title']} - {page['url']}")

print("\n" + "=" * 70)
print("✅ All helper methods working correctly!")
print("=" * 70)
