from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from database import get_db
from models import Integration, Bot
from schemas.integration import IntegrationUpdate, IntegrationResponse, WooCommerceFetchStatus
from services import decode_token
from services.encryption import encrypt_value, decrypt_value
from services.website_fetcher import fetch_website_content
from services.universal_website_fetcher import UniversalWebsiteFetcher
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


PLAN_ERROR_FREE = "⚠️ Product features are not available in Free plan. Please upgrade to Starter or Growth plan."

def get_current_user_id(request: Request) -> int:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    payload = decode_token(auth[7:])
    if not payload:
        raise HTTPException(401, "Invalid token")
    return int(payload.get("sub", 0))


def get_user_plan(user_id: int, db: Session) -> str:
    """Get user plan from database."""
    from models import User
    user = db.query(User).filter(User.id == user_id).first()
    return user.plan if user else "starter"


@router.get("/me", response_model=IntegrationResponse)
def get_integrations(request: Request, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)): # Added request parameter
    from models import Bot
    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")
    # Return the stored verify_token, or fall back to the default from settings
    verify_token = integ.verify_token
    if not verify_token:
        from config import get_settings
        verify_token = get_settings().DEFAULT_VERIFY_TOKEN

    # Parse categories JSON if it exists
    categories = []
    # Only show categories if products are actually cached
    if integ.woo_products_cached and integ.woo_categories_cached:
        try:
            categories = json.loads(integ.woo_categories_cached) if isinstance(integ.woo_categories_cached, str) else integ.woo_categories_cached
        except:
            categories = []

    # Only return product count if cache is active
    products_count = integ.woo_products_count if integ.woo_products_cached else 0
    
    # Construct webhook URL (assuming http://localhost:8000 is the base)
    # In a real app, you might want to use request.url.scheme and request.url.netloc for dynamic URL
    webhook_url = f"http://localhost:8000/webhook" 

    return {
        "id": integ.id,
        "bot_id": integ.bot_id,
        "phone_number_id": integ.phone_number_id,
        "whatsapp_number": integ.whatsapp_number,
        "verify_token": verify_token,  # Return plain text verify token
        "woocommerce_url": integ.woocommerce_url,
        "wp_base_url": integ.wp_base_url,
        "business_type": integ.business_type or "product",
        "has_whatsapp_token": bool(integ.whatsapp_token),
        "whatsapp_token_preview": integ.whatsapp_token[:20] + "..." if integ.whatsapp_token else "Not set",
        "has_woo_keys": bool(integ.woo_consumer_key),
        "woo_products_cached": integ.woo_products_cached,
        "woo_categories_cached": categories,
        "woo_products_count": products_count,
        "webhook_url": webhook_url, # Added webhook_url
    }


@router.patch("/me")
def update_integrations(data: IntegrationUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Update user integrations with PERSISTENT token management.

    Key principles for production SaaS:
    - WhatsApp tokens and phone_number_id are NEVER cleared unless explicitly changed by user
    - Tokens persist across bot mode changes, website changes, and settings updates
    - Only user-initiated reconfiguration removes/updates tokens
    - Each user has unique tokens that are encrypted in database

    PLAN RESTRICTIONS:
    - WhatsApp integration is available in ALL plans (Free, Starter, Growth)
    - Product/WooCommerce integration is only available in Starter and Growth plans
    """
    from models import Bot
    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")

    # Plan-based feature gating
    user_plan = get_user_plan(user_id, db)

    # CRITICAL: Check for product-related fields EXPLICITLY
    # WhatsApp fields are ALWAYS allowed for all plans
    logger.info(f"User {user_id} (plan: {user_plan}) - Received fields: business_type={data.business_type}, woocommerce_url={data.woocommerce_url}, woo_key={data.woo_consumer_key is not None}, woo_secret={data.woo_consumer_secret is not None}")

    product_field_submitted = (
        (data.business_type is not None and data.business_type == "product") or
        (data.woocommerce_url is not None and data.woocommerce_url.strip() != "") or
        data.woo_consumer_key is not None or
        data.woo_consumer_secret is not None
    )

    logger.info(f"Product field submitted: {product_field_submitted}")

    # Only block product integration for free users, WhatsApp is ALWAYS allowed
    if user_plan == "free" and product_field_submitted:
        logger.warning(f"Free user {user_id} attempted to submit product fields")
        raise HTTPException(403, PLAN_ERROR_FREE)
    # Note: WhatsApp fields (phone_number_id, whatsapp_number, verify_token, whatsapp_token) are NOT restricted

    # Track if website URL or type changed - if so, clear old cached data
    old_url = integ.woocommerce_url
    old_type = integ.business_type
    url_changed = False

    if data.woocommerce_url is not None:
        new_url = UniversalWebsiteFetcher.normalize_url(data.woocommerce_url)
        url_changed = (old_url != new_url)
        integ.woocommerce_url = new_url

    if data.business_type is not None:
        if old_type != data.business_type:
            url_changed = True
        integ.business_type = data.business_type

    # CRITICAL: Only update WhatsApp token if explicitly provided (non-empty string)
    # This ensures tokens persist across other updates and are NOT cleared accidentally
    if data.whatsapp_token is not None and data.whatsapp_token.strip() != "":
        integ.whatsapp_token = encrypt_value(data.whatsapp_token)
        logger.info(f"WhatsApp token updated for user {user_id}")
    elif data.whatsapp_token is not None and data.whatsapp_token.strip() == "":
        # User explicitly cleared the token (empty string)
        integ.whatsapp_token = None
        logger.info(f"WhatsApp token explicitly cleared by user {user_id}")
    # If data.whatsapp_token is None (not provided), DO NOTHING - token persists

    # CRITICAL: Phone Number ID persists unless explicitly changed
    if data.phone_number_id is not None and data.phone_number_id.strip() != "":
        integ.phone_number_id = data.phone_number_id
        logger.info(f"Phone Number ID updated for user {user_id}")
    # If None or empty, keep existing value

    if data.whatsapp_number is not None:
        integ.whatsapp_number = data.whatsapp_number

    # DON'T encrypt verify_token - it's not a secret, just a verification string
    if data.verify_token is not None and data.verify_token.strip() != "":
        integ.verify_token = data.verify_token
        logger.info(f"Verify token updated for user {user_id}")

    # WooCommerce credentials - only update if explicitly provided
    if data.woo_consumer_key is not None:
        if data.woo_consumer_key.strip() != "":
            integ.woo_consumer_key = encrypt_value(data.woo_consumer_key)
        else:
            integ.woo_consumer_key = None  # Explicitly cleared
    if data.woo_consumer_secret is not None:
        if data.woo_consumer_secret.strip() != "":
            integ.woo_consumer_secret = encrypt_value(data.woo_consumer_secret)
        else:
            integ.woo_consumer_secret = None  # Explicitly cleared

    if data.wp_base_url is not None:
        integ.wp_base_url = data.wp_base_url

    # If website URL or business type changed, clear old cached data and trigger immediate refresh
    if url_changed:
        logger.info(f"Integration updated for bot {integ.bot_id}, refreshing cache...")
        integ.woo_products_cached = False
        integ.woo_categories_cached = ""
        integ.woo_products_count = 0
        
        # Clear cache and trigger synchronous refresh for immediate availability
        from services.default_bot import clear_cache_for_bot, refresh_cache
        clear_cache_for_bot(integ.bot_id)
        
        # Determine URL for refresh
        refresh_url = integ.woocommerce_url or integ.wp_base_url
        if refresh_url:
            # We need woo credentials if available
            key = decrypt_value(integ.woo_consumer_key) if integ.woo_consumer_key else ""
            secret = decrypt_value(integ.woo_consumer_secret) if integ.woo_consumer_secret else ""
            
            try:
                refresh_cache(integ.bot_id, key, secret, integ.woocommerce_url or "", "", integ.wp_base_url or "", business_type=integ.business_type)
            except Exception as e:
                logger.error(f"Immediate cache refresh failed: {e}")

    db.commit()
    return {"status": "ok"}


@router.post("/me/fetch-website-content")
def fetch_website_content(site_type: str, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Fetch website content for both service and product-based sites.
    
    Args:
        site_type: "service" for service-based sites, "product" for e-commerce
    """
    from models import Bot

    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")

    # Get website URL based on type
    if site_type == "product":
        website_url = integ.woocommerce_url
    else:
        website_url = integ.wp_base_url

    if not website_url:
        raise HTTPException(400, f"Please provide your {'store' if site_type == 'product' else 'website'} URL first.")

    # Fetch website content
    result = fetch_website_content(website_url, site_type)

    if "error" in result:
        return {
            "success": False,
            "message": f"Failed to fetch website content: {result['error']}",
            "data": {}
        }

    # Store extracted content in integration for bot to use
    # You can add fields to Integration model to store this data
    logger.info(f"Successfully fetched website content: {result.get('site_title', '')}")

    return {
        "success": True,
        "message": f"Successfully extracted content from {result.get('site_name', 'website')}",
        "data": {
            "site_title": result.get("site_title", ""),
            "site_name": result.get("site_name", ""),
            "content_preview": result.get("content", "")[:500],
            "products_count": len(result.get("products", [])),
            "services_count": len(result.get("services", [])),
            "contact": result.get("contact", {}),
        }
    }


@router.get("/me/button-code")
def get_whatsapp_button_code(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Generate dynamic WhatsApp button code for user's website."""
    from models import Bot
    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ or not integ.whatsapp_number:
        raise HTTPException(400, "Please set your WhatsApp number in Integrations first.")
    
    number = integ.whatsapp_number.replace("+", "").replace(" ", "").replace("-", "")
    
    code = f"""<!-- WhatsApp Floating Button by ORVYN -->
<a href="https://wa.me/{number}" target="_blank" style="position: fixed; bottom: 20px; right: 20px; background-color: #25D366; color: white; border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 4px 8px rgba(0,0,0,0.2); z-index: 9999;">
    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="white" viewBox="0 0 24 24">
        <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.438 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>
    </svg>
</a>"""
    
    return {"code": code}


@router.post("/me/fetch-woocommerce", response_model=WooCommerceFetchStatus)
def fetch_woocommerce_data(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Fetch WooCommerce products and categories using stored credentials.
    If credentials are missing, falls back to web scraping.
    """
    from models import Bot

    # Plan-based gating: Free plan cannot fetch WooCommerce products
    user_plan = get_user_plan(user_id, db)
    if user_plan == "free":
        raise HTTPException(403, PLAN_ERROR_FREE)

    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")
    
    # Check if we have the WooCommerce URL
    woo_url = integ.woocommerce_url or integ.wp_base_url
    if not woo_url:
        raise HTTPException(400, "Please provide your website/store URL first.")
    
    # Decrypt credentials if available
    consumer_key = ""
    consumer_secret = ""
    if integ.woo_consumer_key and integ.woo_consumer_secret:
        try:
            consumer_key = decrypt_value(integ.woo_consumer_key)
            consumer_secret = decrypt_value(integ.woo_consumer_secret)
        except Exception as e:
            logger.error(f"Failed to decrypt WooCommerce credentials: {e}")

    # Fetch products (API if keys exist, else scraping)
    if consumer_key and consumer_secret:
        result = UniversalWebsiteFetcher.fetch_products_with_auth(
            woo_url, consumer_key, consumer_secret
        )
    else:
        logger.info(f"Keys missing for {woo_url}, using web scraping.")
        result = UniversalWebsiteFetcher.scrape_products_from_website(woo_url)
    
    if not result["success"]:
        return {
            "success": False,
            "total_products": integ.woo_products_count,
            "total_categories": 0,
            "message": result.get("error", "Failed to fetch content from website."),
            "error": result.get("error")
        }
    
    # Update integration with cached data
    integ.woo_products_cached = True
    integ.woo_categories_cached = json.dumps(result.get("categories", []))
    integ.woo_products_count = result.get("total_products", 0)
    db.commit()
    
    logger.info(f"User {user_id}: Cached {result.get('total_products', 0)} products/items")
    
    return {
        "success": True,
        "total_products": result.get("total_products", 0),
        "total_categories": len(result.get("categories", [])),
        "message": f"Successfully fetched {result.get('total_products', 0)} items from your website!"
    }


@router.post("/me/discover-website", response_model=dict)
def discover_website(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Auto-discover website platform and fetch available data.
    Used when user provides only a website URL.
    """
    from models import Bot
    
    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")
    
    # Use woocommerce_url if set, otherwise fall back to wp_base_url
    website_url = integ.woocommerce_url or integ.wp_base_url
    if not website_url:
        raise HTTPException(400, "Please provide your website URL first.")
    
    # Discover and fetch data (works with ANY website)
    result = UniversalWebsiteFetcher.auto_discover_and_fetch(website_url)
    
    # Update integration with discovered data
    if result["success"]:
        site_info = result.get("site_info", {})
        
        # If we don't have wp_base_url set, set it now
        if not integ.wp_base_url:
            integ.wp_base_url = UniversalWebsiteFetcher.normalize_url(website_url)
        
        db.commit()
    
    return result


@router.post("/me/configure-base")
async def configure_integration_base(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    integration_config: dict = Body(...) # Expecting { "integration_type": "product" | "service", "website_url": "...", "consumer_key": "...", "consumer_secret": "..." }
):
    """
    Configures integration base for product or service, fetching relevant data.
    """
    # Plan-based gating: Free plan cannot configure product integration
    user_plan = get_user_plan(user_id, db)
    if user_plan == "free":
        if integration_config.get("integration_type") == "product":
            raise HTTPException(403, PLAN_ERROR_FREE)

    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")

    integration_type = integration_config.get("integration_type")
    website_url = integration_config.get("website_url")
    consumer_key = integration_config.get("consumer_key")
    consumer_secret = integration_config.get("consumer_secret")

    if not integration_type or not website_url:
        raise HTTPException(400, "Integration type and website URL are required.")

    normalized_url = UniversalWebsiteFetcher.normalize_url(website_url)

    platform_info = UniversalWebsiteFetcher.detect_platform(normalized_url)
    is_wordpress = platform_info.get("is_wordpress", False)
    is_woocommerce = platform_info.get("is_woocommerce", False)

    fetched_data = {}
    message = ""

    if integration_type == "product":
        if is_woocommerce:
            wc_key = consumer_key or (decrypt_value(integ.woo_consumer_key) if integ.woo_consumer_key else None)
            wc_secret = consumer_secret or (decrypt_value(integ.woo_consumer_secret) if integ.woo_consumer_secret else None)

            if not wc_key or not wc_secret:
                logger.warning("WooCommerce keys missing, falling back to scraping for products.")
                result = UniversalWebsiteFetcher.scrape_products_from_website(normalized_url)
                message = "WooCommerce keys not provided. Attempted to scrape products. "
            else:
                result = UniversalWebsiteFetcher.fetch_products_with_auth(normalized_url, wc_key, wc_secret)
                message = "Fetched WooCommerce products via API. "

            if result.get("success"):
                integ.woo_products_cached = True
                integ.woo_categories_cached = json.dumps(result.get("categories", []))
                integ.woo_products_count = result.get("total_products", 0)
                fetched_data["products_count"] = result.get("total_products", 0)
                fetched_data["categories"] = result.get("categories", [])
                message += f"Successfully fetched {result.get('total_products', 0)} products and {len(result.get('categories', []))} categories."
            else:
                message += f"Failed to fetch products: {result.get('error', 'Unknown error')}"
                integ.woo_products_cached = False
                integ.woo_categories_cached = ""
                integ.woo_products_count = 0
                fetched_data["error"] = result.get("error", "Unknown error")

        else:
            result = UniversalWebsiteFetcher.scrape_products_from_website(normalized_url)
            if result.get("success"):
                integ.woo_products_cached = True # Repurposing for general product fetch status
                integ.woo_categories_cached = "" # No categories specific to this method
                integ.woo_products_count = result.get("total_products", 0)
                fetched_data["products_count"] = result.get("total_products", 0)
                fetched_data["products_preview"] = result.get("products", [])[:5] # Store a preview
                message = f"Scraped {result.get('total_products', 0)} potential products from the website. "
            else:
                message = f"Failed to scrape products: {result.get('error', 'Unknown error')}"
                integ.woo_products_cached = False
                integ.woo_products_count = 0
                fetched_data["error"] = result.get("error", "Unknown error")

        if normalized_url:
            integ.woocommerce_url = normalized_url

    elif integration_type == "service":
        if is_wordpress:
            # Keys are optional for WordPress now
            result = UniversalWebsiteFetcher.fetch_wordpress_pages(normalized_url)
            
            if result.get("success"):
                # Store fetched page summaries (or contact info)
                integ.woo_categories_cached = json.dumps(result.get("pages", {})) 
                fetched_data["pages_count"] = len(result.get("pages", {}))
                fetched_data["contact_info"] = result.get("contact_info", {})
                message = "Fetched WordPress pages and contact info. "
            else:
                # Fallback to general site info if WordPress API fails
                logger.warning(f"WordPress API failed for {normalized_url}, falling back to general info.")
                result = UniversalWebsiteFetcher.fetch_site_info(normalized_url)
                fetched_data["site_title"] = result.get("site_name")
                fetched_data["services_count"] = len(result.get("services", []))
                message = f"Fetched general website info for '{result.get('site_name')}'. "
            
            if normalized_url:
                integ.wp_base_url = normalized_url
        else:
            # For non-WordPress service sites, fetch general site info
            result = UniversalWebsiteFetcher.fetch_site_info(normalized_url)
            if result.get("site_name"):
                integ.woo_products_cached = True # General content fetched status
                integ.woo_products_count = len(result.get("services", []))
                fetched_data["site_title"] = result.get("site_name")
                fetched_data["content_preview"] = result.get("about", "")[:500] # Store a preview
                fetched_data["services_count"] = len(result.get("services", []))
                fetched_data["contact"] = result.get("contact", {})
                message = f"Fetched general website info for '{result.get('site_name')}'. "
            else:
                message = f"Failed to fetch website info: {result.get('error', 'Unknown error')}"
                integ.woo_products_cached = False
                integ.woo_products_count = 0
                fetched_data["error"] = result.get("error", "Unknown error")

            if normalized_url:
                integ.wp_base_url = normalized_url 

    integ.business_type = integration_type 
    db.commit()

    return {
        "success": True,
        "message": message,
        "data": fetched_data
    }

