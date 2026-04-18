"""Website content fetcher service.

Fetches and extracts content from websites for both:
- Service-based sites (WordPress, business sites)
- Product-based sites (WooCommerce, e-commerce)
"""
import re
import logging
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


def is_valid_url(url: str) -> bool:
    """Check if URL is valid and accessible."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ["http", "https"] and parsed.netloc)
    except Exception:
        return False


def fetch_website_content(url: str, site_type: str = "service") -> Dict:
    """Fetch and extract website content.
    
    Args:
        url: Website URL to fetch
        site_type: "service" for service-based sites, "product" for e-commerce
    
    Returns:
        Dictionary with extracted content
    """
    if not is_valid_url(url):
        logger.error(f"Invalid URL: {url}")
        return {"error": "Invalid URL", "content": "", "products": [], "services": []}
    
    # Normalize URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        logger.info(f"Fetching website content: {url} (type: {site_type})")
        
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15,
            allow_redirects=True,
            verify=True
        )
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
            return {
                "error": f"HTTP {response.status_code}",
                "content": "",
                "products": [],
                "services": [],
                "site_title": "",
                "site_name": ""
            }
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract basic site info
        site_title = soup.title.string.strip() if soup.title else ""
        site_name = extract_site_name(soup, url)
        
        result = {
            "site_title": site_title,
            "site_name": site_name,
            "url": url,
            "site_type": site_type,
        }
        
        # Extract content based on site type
        if site_type == "product":
            products = extract_products(soup, url)
            result["products"] = products
            result["content"] = extract_general_content(soup)
        else:  # service
            services = extract_services(soup)
            result["services"] = services
            result["content"] = extract_general_content(soup)
        
        # Always extract contact info
        result["contact"] = extract_contact_info(soup)
        
        logger.info(f"Successfully extracted content from {url}: {len(result.get('products', []))} products, {len(result.get('services', []))} services")
        return result
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching {url}")
        return {"error": "Request timeout", "content": "", "products": [], "services": []}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return {"error": str(e), "content": "", "products": [], "services": []}
    except Exception as e:
        logger.error(f"Unexpected error processing {url}: {e}", exc_info=True)
        return {"error": f"Processing error: {str(e)}", "content": "", "products": [], "services": []}


def extract_site_name(soup: BeautifulSoup, url: str) -> str:
    """Extract site/business name from the page."""
    # Try logo/brand
    logo = soup.find("img", {"class": re.compile(r"logo|brand", re.I)})
    if logo and logo.get("alt"):
        return logo["alt"].strip()
    
    # Try meta tags
    meta = soup.find("meta", property="og:site_name")
    if meta and meta.get("content"):
        return meta["content"].strip()
    
    # Try h1
    h1 = soup.find("h1")
    if h1:
        return h1.get_text().strip()[:100]
    
    # Fallback to domain name
    try:
        domain = urlparse(url).netloc.replace("www.", "")
        return domain.split(".")[0].title()
    except Exception:
        return ""


def extract_products(soup: BeautifulSoup, url: str) -> List[Dict]:
    """Extract product information from e-commerce site."""
    products = []
    
    # Look for WooCommerce product patterns
    product_selectors = [
        "li.product",
        "div.product",
        "article.product",
        "[class*='product-item']",
        "[class*='product-card']",
    ]
    
    product_elements = []
    for selector in product_selectors:
        elements = soup.select(selector)
        if elements:
            product_elements = elements
            break
    
    for elem in product_elements[:20]:  # Limit to 20 products
        try:
            name_elem = elem.find(["h2", "h3", "a", "div"], class_=re.compile(r"product.*name|name", re.I))
            name = name_elem.get_text().strip() if name_elem else ""
            
            price_elem = elem.find(["span", "div", "p"], class_=re.compile(r"price|amount", re.I))
            price = price_elem.get_text().strip() if price_elem else ""
            
            desc_elem = elem.find(["p", "div"], class_=re.compile(r"description|excerpt", re.I))
            description = desc_elem.get_text().strip()[:200] if desc_elem else ""
            
            img_elem = elem.find("img")
            image = ""
            if img_elem:
                image = urljoin(url, img_elem.get("src", "") or img_elem.get("data-src", ""))
            
            if name:
                products.append({
                    "name": name[:100],
                    "price": price[:50],
                    "description": description,
                    "image": image,
                })
        except Exception as e:
            logger.warning(f"Error extracting product: {e}")
            continue
    
    # If no structured products found, try to get product-like items
    if not products:
        # Look for links that might be products
        links = soup.find_all("a", href=True)
        for link in links[:30]:
            href = link["href"]
            text = link.get_text().strip()
            if ("/product/" in href or "/shop/" in href) and text and len(text) > 3:
                products.append({
                    "name": text[:100],
                    "price": "",
                    "description": "",
                    "image": "",
                    "url": urljoin(url, href),
                })
    
    return products


def extract_services(soup: BeautifulSoup) -> List[Dict]:
    """Extract services information from service-based site."""
    services = []
    
    # Look for service sections
    service_selectors = [
        "[class*='service']",
        "[class*='feature']",
        "[class*='offering']",
        "[id*='services']",
        "[id*='features']",
    ]
    
    service_elements = []
    for selector in service_selectors:
        elements = soup.select(selector)
        if elements:
            service_elements = elements
            break
    
    for elem in service_elements[:15]:
        try:
            name_elem = elem.find(["h2", "h3", "h4"])
            name = name_elem.get_text().strip() if name_elem else ""
            
            desc_elem = elem.find("p")
            description = desc_elem.get_text().strip()[:300] if desc_elem else ""
            
            if name and len(name) > 3:
                services.append({
                    "name": name[:100],
                    "description": description,
                })
        except Exception as e:
            logger.warning(f"Error extracting service: {e}")
            continue
    
    return services


def extract_general_content(soup: BeautifulSoup) -> str:
    """Extract general content from the page."""
    content_parts = []
    
    # Extract from main content areas
    main = soup.find("main") or soup.find("div", id="content") or soup.find("div", class_="content")
    
    if main:
        # Get text from headings and paragraphs
        for tag in main.find_all(["h1", "h2", "h3", "p", "li"])[:30]:
            text = tag.get_text().strip()
            if text and len(text) > 10:
                content_parts.append(text)
    else:
        # Fallback to body
        body = soup.find("body")
        if body:
            for tag in body.find_all(["h1", "h2", "h3", "p"])[:30]:
                text = tag.get_text().strip()
                if text and len(text) > 10:
                    content_parts.append(text)
    
    # Join and limit content
    content = "\n".join(content_parts)
    return content[:2000]  # Limit to 2000 chars


def extract_contact_info(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract contact information from the page."""
    contact = {
        "phone": "",
        "email": "",
        "address": "",
    }
    
    # Extract phone numbers
    phone_patterns = [
        r'[\+]?[\d\s\-\(\)]{10,}',
    ]
    
    # Look for phone links
    phone_links = soup.find_all("a", href=re.compile(r"tel:", re.I))
    if phone_links:
        contact["phone"] = phone_links[0]["href"].replace("tel:", "").strip()
    
    # Extract emails
    email_links = soup.find_all("a", href=re.compile(r"mailto:", re.I))
    if email_links:
        contact["email"] = email_links[0]["href"].replace("mailto:", "").strip()
    
    # Look for email patterns in text
    if not contact["email"]:
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        emails = email_pattern.findall(soup.get_text())
        if emails:
            contact["email"] = emails[0]
    
    # Extract address (basic extraction)
    address_keywords = ["address", "location", "office", "visit us at"]
    for keyword in address_keywords:
        elem = soup.find(string=re.compile(keyword, re.I))
        if elem:
            parent = elem.parent if hasattr(elem, 'parent') else None
            if parent:
                contact["address"] = parent.get_text().strip()[:200]
                break
    
    return contact
