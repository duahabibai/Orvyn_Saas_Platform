"""
Universal Website Data Fetcher

Fetches products, categories, and site information from ANY website URL.
Supports multiple platforms: WooCommerce, Shopify, WordPress, or custom websites.
Uses web scraping as fallback when no API is available.
"""
import re
import logging
import requests
from typing import Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import json
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class UniversalWebsiteFetcher:
    """Fetches data from ANY website using APIs or web scraping."""

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL by ensuring it has a scheme and no trailing slash."""
        if not url:
            return ""
        url = url.strip().rstrip("/")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    @staticmethod
    def detect_platform(base_url: str) -> dict:
        """Detect what platform the website is running."""
        result = {
            "platform": "unknown",
            "is_wordpress": False,
            "is_woocommerce": False,
            "is_shopify": False,
            "detected_endpoints": []
        }

        try:
            logger.info(f"Platform detection: Fetching {base_url}")
            resp = requests.get(base_url, timeout=10, verify=False, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            logger.info(f"Platform detection: {base_url} status code: {resp.status_code}")
            if resp.status_code == 200:
                html = resp.text.lower()
                
                if "shopify" in html or ".myshopify.com" in html:
                    result["is_shopify"] = True
                    result["platform"] = "shopify"
                
                if "/wp-content/" in html or "/wp-includes/" in html or "wp-json" in html:
                    result["is_wordpress"] = True
                    result["platform"] = "wordpress"
                
                # Check for WooCommerce specifically
                if "woocommerce" in html or "wc-api" in html:
                    result["is_woocommerce"] = True
                    if result["platform"] == "wordpress":
                        result["platform"] = "woocommerce"

                # Proactive endpoint check
                try:
                    logger.info(f"Platform detection: Checking wp-json for {base_url}")
                    wp_resp = requests.get(f"{base_url.rstrip('/')}/wp-json/", timeout=5, verify=False)
                    logger.info(f"Platform detection: wp-json status code: {wp_resp.status_code}")
                    if wp_resp.status_code == 200:
                        result["detected_endpoints"].append("wp-json")
                        result["is_wordpress"] = True
                except Exception as e:
                    logger.warning(f"Platform detection: wp-json check failed: {e}")
        except Exception as e:
            logger.warning(f"Platform detection for {base_url} failed: {e}")
        return result

    @staticmethod
    def fetch_site_info(base_url: str) -> dict:
        """Fetch basic site information from any website."""
        info = {
            "site_name": "",
            "site_description": "",
            "about": "",
            "services": [],
            "contact": {},
            "pages": []
        }

        try:
            logger.info(f"🌐 Fetching site info for: {base_url}")
            resp = requests.get(base_url, timeout=12, verify=False, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            logger.info(f"Fetching site info for {base_url}: Status code {resp.status_code}")
            if resp.status_code == 200:
                html = resp.text
                soup = BeautifulSoup(html, 'html.parser')
                
                title_tag = soup.find('title')
                if title_tag:
                    info["site_name"] = title_tag.get_text().strip()
                    logger.info(f"Extracted site name: {info['site_name']}")
                
                meta_desc = soup.find('meta', attrs={'name': re.compile(r'description', re.I)})
                if meta_desc:
                    info["site_description"] = meta_desc.get('content', '').strip()
                    logger.info(f"Extracted site description (truncated): {info['site_description'][:50]}...")
                
                info["contact"] = UniversalWebsiteFetcher._extract_contact_info(html, soup)
                logger.info(f"Extracted contact info: {info['contact']}")
                info["about"] = UniversalWebsiteFetcher._extract_about_info(html, soup)
                logger.info(f"Extracted about info (truncated): {info['about'][:50]}...")
                info["services"] = UniversalWebsiteFetcher._extract_services(html, soup)
                logger.info(f"Extracted {len(info['services'])} services.")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch site info for {base_url} due to network error: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch site info for {base_url} due to parsing error: {e}")

        return info

    @staticmethod
    def _extract_contact_info(html: str, soup: BeautifulSoup) -> dict:
        contact = {"phone": "", "email": "", "address": "", "hours": ""}
        text = soup.get_text(separator=' ', strip=True)

        # Look for contact section specifically - expanded selectors
        contact_sections = []
        contact_patterns = r'contact|footer|info|address|store|about|team|company|corporate|headquarters|office'
        for tag in soup.find_all(['div', 'section', 'footer', 'address', 'header'], class_=re.compile(contact_patterns, re.I)):
            contact_sections.append(tag.get_text(separator=' ', strip=True))

        # Also look for contact links
        for link in soup.find_all('a', href=re.compile(r'contact|about|tel:|mailto:', re.I)):
            contact_text = link.get_text(strip=True)
            if contact_text and len(contact_text) > 3:
                contact_sections.append(contact_text)

        contact_text = ' '.join(contact_sections) if contact_sections else text

        # Phone - More robust regex to capture common formats
        phone_patterns = [
            r'[\+]?[0-9]{1,3}[\s\-]?\(?[0-9]{1,4}\)?[\s\- ]?[0-9]{1,4}[\s\- ]?[0-9]{1,9}', # International format, Pakistan format
            r'[0-9]{10,11}', # Simple 10-11 digit number
            r'0[0-9]{10}', # Pakistani mobile format
            r'\+\(?[0-9]{1,3}\)?\s?(\d[\s-]?){6,}', # General international format
            r'tel:[\+\d\s\-]+', # tel: links
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, contact_text)
            if phone_match:
                phone = phone_match.group().strip()
                # Clean up tel: prefix
                phone = re.sub(r'^tel:', '', phone)
                contact["phone"] = phone
                break # Use the first one found

        # Also check for tel: links directly
        if not contact["phone"]:
            tel_link = soup.find('a', href=re.compile(r'^tel:', re.I))
            if tel_link:
                contact["phone"] = tel_link.get('href', '').replace('tel:', '').strip()

        # Email - search in contact sections first, then full text
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', contact_text)
        if not email_match:
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if email_match:
            contact["email"] = email_match.group()

        # Also check for mailto: links
        if not contact["email"]:
            mailto_link = soup.find('a', href=re.compile(r'^mailto:', re.I))
            if mailto_link:
                contact["email"] = mailto_link.get('href', '').replace('mailto:', '').strip()

        # Address - Look for contact sections first with expanded keywords
        address_found = False
        address_keywords = ['street', 'road', 'avenue', 'lane', 'area', 'city', 'pakistan', 'pk', 'address', 'location',
                           'boulevard', 'drive', 'court', 'place', 'suite', 'floor', 'building', 'plaza', 'center',
                           'centre', 'block', 'phase', 'sector', 'town', 'country', 'zip', 'postal']

        for section in contact_sections:
            address_lines = [line.strip() for line in section.split('\n')
                           if len(line.strip().split()) > 3
                           and any(kw in line.lower() for kw in address_keywords)]
            if address_lines:
                contact["address"] = ", ".join(address_lines[:2])
                address_found = True
                break

        if not address_found:
            address_lines = [line.strip() for line in text.split('\n')
                           if len(line.strip().split()) > 3
                           and any(kw in line.lower() for kw in address_keywords)]
            if address_lines:
                contact["address"] = ", ".join(address_lines[:2])

        # Business hours - look for timing patterns with expanded search
        hours_patterns = [
            r'(?i)(?:opening\s*(?:hours|times?)|business\s*hours?|working\s*hours?|hours[:\s]+)\s*[:\-]?\s*([a-z0-9\s,\-\:]+(?:am|pm|mon|tue|wed|thu|fri|sat|sun)+)',
            r'(?i)(?:mon|tue|wed|thu|fri|sat|sun)[a-z\s]*[\d\s\-:am]+',
            r'(?i)(?:9|10|8)\s*am?\s*[-–to]+\s*(?:5|6|pm)',  # e.g., "9am - 5pm"
        ]
        for pattern in hours_patterns:
            hours_match = re.search(pattern, contact_text, re.IGNORECASE)
            if hours_match:
                contact["hours"] = hours_match.group(0).strip()[:100]
                break

        # Also look for hours in dedicated elements
        if not contact["hours"]:
            for tag in soup.find_all(['div', 'span', 'p'], class_=re.compile(r'hours|time|schedule', re.I)):
                hours_text = tag.get_text(strip=True)
                if re.search(r'(am|pm|mon|tue|wed|thu|fri|sat|sun)', hours_text, re.I):
                    contact["hours"] = hours_text[:100]
                    break

        logger.info(f"Extracted contact: {contact}")
        return contact

    @staticmethod
    def _extract_about_info(html: str, soup: BeautifulSoup) -> str:
        # Simple extraction for prompt context
        for s in soup(['script', 'style', 'nav', 'footer']): s.decompose()
        about_text = soup.get_text(separator=' ', strip=True)[:1000]
        logger.info(f"Extracted about text (truncated): {about_text[:50]}...")
        return about_text

    @staticmethod
    def _extract_services(html: str, soup: BeautifulSoup) -> list:
        services = []
        # Expanded keywords for service detection
        keywords = [
            'service', 'solution', 'offer', 'provide', 'expert', 'feature',
            'specialize', 'package', 'plan', 'product', 'category', 'section',
            'department', 'program', 'support', 'help', 'guide', 'tutorial',
            'resource', 'tool', 'platform', 'system', 'software', 'app'
        ]

        # Also look for navigation items and menu links
        nav_items = []
        for nav in soup.find_all(['nav', 'ul'], class_=re.compile(r'menu|nav|menu-item', re.I)):
            for li in nav.find_all('li'):
                nav_items.append(li.get_text(strip=True))

        # Search in headings and links
        for h in soup.find_all(['h2', 'h3', 'h4', 'h5', 'li', 'a']):
            t = h.get_text(strip=True)
            # Clean up whitespace and normalize
            t = ' '.join(t.split())
            if 5 < len(t) < 100:
                # Check for keyword match
                if any(k in t.lower() for k in keywords):
                    # Filter out generic text
                    if not any(generic in t.lower() for generic in ['click here', 'read more', 'learn more', 'view all']):
                        if t not in services:
                            services.append(t)
                            logger.debug(f"Potential service found: {t}")

        # Also extract from nav items (often contain service names)
        for item in nav_items:
            item = ' '.join(item.split())
            if 5 < len(item) < 80 and item not in services:
                if not any(generic in item.lower() for generic in ['home', 'contact', 'about', 'login', 'sign']):
                    services.append(item)
                    logger.debug(f"Potential service from nav: {item}")

        if not services:
            logger.warning("No services found using keywords. Trying generic headings.")
            # Fallback: look for any short, non-generic headings if no keywords matched
            for h in soup.find_all(['h2', 'h3', 'h4', 'h5']):
                 t = h.get_text(strip=True)
                 t = ' '.join(t.split())  # Normalize whitespace
                 if 5 < len(t) < 100 and 2 <= len(t.split()) <= 6:  # Reasonable heading length
                     # Filter generic headings
                     if not any(generic in t.lower() for generic in ['welcome', 'latest', 'featured', 'popular']):
                         if t not in services:
                            services.append(t)
                            logger.debug(f"Potential service found (fallback): {t}")

        final_services = services[:15] # Limit to 15 services
        logger.info(f"Extracted {len(final_services)} services.")
        return final_services

    @staticmethod
    def scrape_products_from_website(base_url: str) -> dict:
        result = {"success": False, "products": [], "categories": [], "total_products": 0}
        try:
            logger.info(f"🔍 Scraping products from: {base_url}")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            resp = requests.get(base_url, timeout=12, verify=False, headers=headers)
            logger.info(f"Scraping {base_url}: Status code {resp.status_code}")

            if resp.status_code == 200:
                html = resp.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # Broadly look for product-like containers using common class name patterns
                # Improved patterns to catch more variations
                patterns = [
                    re.compile(r'product', re.I), re.compile(r'item', re.I), 
                    re.compile(r'card', re.I), re.compile(r'entry', re.I),
                    re.compile(r'shop', re.I), re.compile(r'grid', re.I),
                    re.compile(r'listing', re.I), re.compile(r'detail', re.I)
                ]
                
                found_items = []
                # Try finding elements by common product-related class names
                for pattern in patterns:
                    elements = soup.find_all(class_=pattern)
                    logger.debug(f"Scraping {base_url}: Found {len(elements)} elements matching pattern '{pattern.pattern}'")
                    found_items.extend(elements)
                
                # Deduplicate based on extracted name to avoid listing same product multiple times
                seen_names = set()
                extracted_products = []

                for item in found_items:
                    # Try to find the product name tag (common tags like h2, h3, a, strong)
                    name_tag = item.find(['h2', 'h3', 'h4', 'a', 'strong', 'span'], class_=re.compile(r'(name|title|heading)', re.I))
                    if not name_tag:
                        # Fallback: search for any prominent text within the item if no specific name tag found
                        name_tag = item.find(string=re.compile(r'\w{5,}', re.I)) # Look for text with at least 5 chars

                    if name_tag:
                        name = name_tag.get_text(strip=True)
                        # Basic validation for name (length, not just numbers/symbols)
                        if name and len(name) > 3 and not name.isnumeric() and len(re.findall(r'[a-zA-Z]', name)) > 0:
                            if name not in seen_names:
                                # Try to find price
                                price = "Contact us" # Default price
                                # Search for price patterns within the item's text
                                price_text_elements = item.find_all(string=re.compile(r'(\d+|Rs|PKR|\$|€|£)', re.I))
                                for pt_element in price_text_elements:
                                    price_text = pt_element.parent.get_text(strip=True) if pt_element.parent else pt_element.get_text(strip=True)
                                    price_match = re.search(r'([R|r][s|S]?\.?\s?\d+[\d,.]*|[P|p][K|K][R|R]\s?\d+[\d,.]*|\$\s?\d+[\d,.]*|€\s?\d+[\d,.]*|£\s?\d+[\d,.]*)', price_text)
                                    if price_match:
                                        price = price_match.group()
                                        break # Found a price, stop searching

                                extracted_products.append({"name": name, "price": price})
                                seen_names.add(name)
                                logger.debug(f"Scraped product: Name='{name}', Price='{price}'")
                
                # If no products found with common patterns, try a broader approach
                if not extracted_products:
                    logger.warning(f"No products found using common patterns on {base_url}. Trying broader heading search.")
                    # Fallback: look for headings (h2, h3) that might be product names
                    for h in soup.find_all(['h2', 'h3', 'h4']):
                        name = h.get_text(strip=True)
                        # Basic validation for name
                        if name and len(name) > 5 and not name.isnumeric() and len(re.findall(r'[a-zA-Z]', name)) > 0:
                            if name not in seen_names:
                                extracted_products.append({"name": name, "price": "Contact us"})
                                seen_names.add(name)
                                logger.debug(f"Scraped product (fallback heading): Name='{name}', Price='Contact us'")

                if extracted_products:
                    result["success"] = True
                    result["products"] = extracted_products
                    result["total_products"] = len(extracted_products)
                    logger.info(f"✅ Successfully scraped {result['total_products']} items from {base_url}")
                else:
                    logger.warning(f"Could not scrape any products from {base_url} even with fallback.")
            else:
                logger.warning(f"Scraping {base_url} failed with status code: {resp.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Scraping {base_url} failed due to network error: {e}")
        except Exception as e:
            logger.error(f"Scraping {base_url} failed due to parsing or other error: {e}")
        return result

    @staticmethod
    def fetch_products_with_auth(base_url: str, key: str, secret: str) -> dict:
        res = {"success": False, "products": [], "categories": [], "method": "api"}
        try:
            logger.info(f"Attempting to fetch products via WooCommerce API for: {base_url}")
            url = f"{base_url.rstrip('/')}/wc/v3/products"
            headers = {"User-Agent": "Mozilla/5.0"} # Add user-agent for API calls too
            r = requests.get(url, params={"consumer_key": key, "consumer_secret": secret, "per_page": 50}, timeout=20, verify=False, headers=headers)
            logger.info(f"WooCommerce API request to {url}: Status code {r.status_code}")

            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list): # Ensure response is a list of products
                    res["products"] = [{"name": p.get('name', 'Unnamed Product'), "price": p.get('price', 'Contact us')} for p in data]
                    res["success"] = True
                    res["total_products"] = len(res["products"])
                    logger.info(f"Successfully fetched {res['total_products']} products via WooCommerce API.")
                else:
                    logger.warning(f"WooCommerce API returned unexpected data format: {data}")
            else:
                logger.warning(f"WooCommerce API request failed for {base_url} with status code: {r.status_code}. Response: {r.text}")
                # Fallback to scraping if API fails
                logger.info(f"Falling back to scraping products from {base_url}")
                return UniversalWebsiteFetcher.scrape_products_from_website(base_url)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"WooCommerce API request failed for {base_url}: {e}")
            logger.info(f"Falling back to scraping products from {base_url}")
            return UniversalWebsiteFetcher.scrape_products_from_website(base_url)
        except Exception as e:
            logger.error(f"An unexpected error occurred during WooCommerce API fetch for {base_url}: {e}")
            logger.info(f"Falling back to scraping products from {base_url}")
            return UniversalWebsiteFetcher.scrape_products_from_website(base_url)
        return res

    @staticmethod
    def fetch_wordpress_pages(base_url: str) -> dict:
        res = {"success": False, "pages": {}, "contact_info": {}}
        try:
            logger.info(f"Attempting to fetch WordPress pages from: {base_url}")
            url = f"{base_url.rstrip('/')}/wp-json/wp/v2/pages"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, params={"per_page": 10}, timeout=15, verify=False, headers=headers)
            logger.info(f"WordPress API request to {url}: Status code {r.status_code}")

            if r.status_code == 200:
                pages = r.json()
                if isinstance(pages, list): # Ensure response is a list of pages
                    for p in pages:
                        slug = p.get('slug')
                        content = p.get('content', {}).get('rendered', '')
                        # Basic sanitization to remove HTML tags, limit length
                        sanitized_content = re.sub(r'<[^>]+>', '', content)[:1000] if content else ""
                        if slug and sanitized_content:
                            res["pages"][slug] = {"content": sanitized_content}
                    res["success"] = True
                    logger.info(f"Successfully fetched {len(res['pages'])} WordPress pages.")
                else:
                    logger.warning(f"WordPress API returned unexpected data format: {pages}")
            else:
                logger.warning(f"WordPress API request failed for {base_url} with status code: {r.status_code}. Response: {r.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"WordPress API request failed for {base_url}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during WordPress API fetch for {base_url}: {e}")
        return res
