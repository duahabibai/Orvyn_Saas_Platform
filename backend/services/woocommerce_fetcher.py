"""
WooCommerce Auto-Fetch Service
"""
import re
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class WooCommerceFetcher:
    """Fetches data from WooCommerce/WordPress websites."""

    @staticmethod
    def normalize_url(url: str) -> str:
        if not url: return ""
        url = url.strip().rstrip("/")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    @staticmethod
    def fetch_site_info(base_url: str) -> dict:
        info = {"site_name": "", "site_description": "", "contact": {}, "services": []}
        try:
            resp = requests.get(base_url, timeout=15, verify=False, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                html = resp.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # Site Name & Desc
                title = soup.find('title')
                if title: info["site_name"] = title.get_text().strip()
                meta = soup.find('meta', attrs={'name': re.compile(r'description', re.I)})
                if meta: info["site_description"] = meta.get('content', '').strip()
                
                # Contact
                info["contact"] = WooCommerceFetcher._extract_contact_info(html)
                # Services (Service Based)
                info["services"] = WooCommerceFetcher._extract_services(html, soup)
        except Exception as e:
            logger.warning(f"Failed to fetch site info: {e}")
        return info

    @staticmethod
    def _extract_contact_info(html: str) -> dict:
        contact = {"phone": "", "email": "", "address": ""}
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        phones = re.findall(r'[\+]?[0-9][0-9\s\-]{9,15}', text)
        if phones: contact["phone"] = phones[0].strip()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if emails: contact["email"] = emails[0]
        return contact

    @staticmethod
    def _extract_services(html: str, soup) -> list:
        services = []
        # Look for headings or lists that suggest services
        for tag in soup.find_all(['h2', 'h3', 'h4', 'li']):
            text = tag.get_text(strip=True)
            if any(k in text.lower() for k in ['service', 'solution', 'offer', 'work', 'what we do']):
                if 5 < len(text) < 100:
                    services.append(text)
        return list(set(services))[:15]

    @staticmethod
    def fetch_products_with_auth(base_url: str, key: str, secret: str) -> dict:
        # Fetching products
        result = {"success": False, "products": [], "categories": []}
        try:
            url = f"{base_url.rstrip('/')}/wc/v3/products"
            r = requests.get(url, params={"consumer_key": key, "consumer_secret": secret, "per_page": 50}, timeout=20, verify=False)
            if r.status_code == 200:
                result.update({"success": True, "products": r.json()})
        except: pass
        return result

    @staticmethod
    def fetch_wordpress_pages(base_url: str) -> dict:
        res = {"success": False, "pages": {}}
        try:
            url = f"{base_url.rstrip('/')}/wp-json/wp/v2/pages"
            r = requests.get(url, params={"per_page": 20}, timeout=15, verify=False)
            if r.status_code == 200:
                for p in r.json():
                    slug = p.get('slug')
                    text = re.sub(r'<[^>]+>', '', p.get('content', {}).get('rendered', ''))
                    res["pages"][slug] = text[:1000]
                res["success"] = True
        except: pass
        return res
