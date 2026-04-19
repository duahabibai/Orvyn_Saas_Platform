"""
Debug contact info extraction - see what's actually on the pages
"""
import sys
sys.path.insert(0, '.')

import requests
from bs4 import BeautifulSoup
import re

test_urls = [
    "https://wordpress.org",
    "https://example.com",
    "https://www.bbc.com/news"
]

for url in test_urls:
    print(f"\n{'='*70}")
    print(f"DEBUGGING: {url}")
    print(f"{'='*70}")

    try:
        resp = requests.get(url, timeout=15, verify=False, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Look for contact links
        print("\n1. Mailto links:")
        for link in soup.find_all('a', href=re.compile(r'mailto:', re.I)):
            print(f"   - href: {link.get('href')}")
            print(f"     text: {link.get_text(strip=True)}")

        print("\n2. Tel links:")
        for link in soup.find_all('a', href=re.compile(r'tel:', re.I)):
            print(f"   - href: {link.get('href')}")
            print(f"     text: {link.get_text(strip=True)}")

        print("\n3. Contact page links:")
        for link in soup.find_all('a', href=re.compile(r'contact|about', re.I)):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if text and len(text) < 50:
                print(f"   - {text}: {href}")

        print("\n4. Footer content:")
        footer = soup.find('footer')
        if footer:
            footer_text = footer.get_text(separator='\n', strip=True)
            # Look for email pattern in footer
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', footer_text)
            if emails:
                print(f"   Emails found: {emails}")
            # Look for phone pattern
            phones = re.findall(r'[\+\d][\d\s\-]{8,15}', footer_text)
            if phones:
                print(f"   Phones found: {phones[:3]}")
            print(f"   Footer text (first 500 chars): {footer_text[:500]}...")

        print("\n5. Any email in full HTML:")
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resp.text)
        if emails:
            print(f"   Emails: {emails[:5]}")
        else:
            print("   No emails found in HTML")

    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "="*70)
