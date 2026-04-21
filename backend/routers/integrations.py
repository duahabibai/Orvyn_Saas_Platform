from fastapi import APIRouter, Depends, HTTPException, Request, Body, BackgroundTasks
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
def get_integrations(request: Request, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    from models import Bot
    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")
    
    verify_token = integ.verify_token
    if not verify_token:
        from config import get_settings
        verify_token = get_settings().DEFAULT_VERIFY_TOKEN

    categories = []
    if integ.woo_products_cached and integ.woo_categories_cached:
        try:
            categories = json.loads(integ.woo_categories_cached) if isinstance(integ.woo_categories_cached, str) else integ.woo_categories_cached
        except:
            categories = []

    products_count = integ.woo_products_count if integ.woo_products_cached else 0
    webhook_url = f"{str(request.base_url).rstrip('/')}/webhook" 

    return {
        "id": integ.id,
        "bot_id": integ.bot_id,
        "phone_number_id": integ.phone_number_id,
        "whatsapp_number": integ.whatsapp_number,
        "verify_token": verify_token,
        "woocommerce_url": integ.woocommerce_url,
        "wp_base_url": integ.wp_base_url,
        "business_type": integ.business_type or "product",
        "has_whatsapp_token": bool(integ.whatsapp_token),
        "whatsapp_token_preview": integ.whatsapp_token[:20] + "..." if integ.whatsapp_token else "Not set",
        "has_woo_keys": bool(integ.woo_consumer_key),
        "woo_products_cached": integ.woo_products_cached,
        "woo_categories_cached": categories,
        "woo_products_count": products_count,
        "webhook_url": webhook_url,
    }


@router.patch("/me")
def update_integrations(
    data: IntegrationUpdate, 
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id), 
    db: Session = Depends(get_db)
):
    """Update user integrations with robust error handling and background refresh."""
    from models import Bot
    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")

    user_plan = get_user_plan(user_id, db)
    logger.info(f"Updating integration for user {user_id} (plan: {user_plan})")

    # Plan-based feature gating
    product_field_submitted = (
        (data.business_type is not None and data.business_type == "product") or
        (data.woocommerce_url is not None and data.woocommerce_url.strip() != "") or
        data.woo_consumer_key is not None or
        data.woo_consumer_secret is not None
    )

    if user_plan == "free" and product_field_submitted:
        raise HTTPException(403, PLAN_ERROR_FREE)

    # Track changes for cache refresh
    url_changed = False
    if data.woocommerce_url is not None:
        new_url = UniversalWebsiteFetcher.normalize_url(data.woocommerce_url)
        if integ.woocommerce_url != new_url:
            url_changed = True
            integ.woocommerce_url = new_url

    if data.business_type is not None:
        if integ.business_type != data.business_type:
            url_changed = True
            integ.business_type = data.business_type

    # Update WhatsApp fields
    if data.whatsapp_token is not None:
        if data.whatsapp_token.strip() != "":
            try:
                integ.whatsapp_token = encrypt_value(data.whatsapp_token)
            except Exception as e:
                logger.error(f"WhatsApp token encryption failed: {e}")
                raise HTTPException(500, "Failed to encrypt WhatsApp token")
        else:
            integ.whatsapp_token = None

    if data.phone_number_id is not None:
        new_phone_id = data.phone_number_id.strip()
        if new_phone_id != "" and new_phone_id != integ.phone_number_id:
            # Check if this ID is already used by another integration
            existing = db.query(Integration).filter(
                Integration.phone_number_id == new_phone_id,
                Integration.id != integ.id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail=f"The WhatsApp Phone Number ID '{new_phone_id}' is already registered with another bot. Please use a unique ID."
                )
        integ.phone_number_id = new_phone_id

    if data.whatsapp_number is not None:
        integ.whatsapp_number = data.whatsapp_number.strip()

    if data.verify_token is not None:
        integ.verify_token = data.verify_token.strip()

    # Update WooCommerce fields
    if data.woo_consumer_key is not None:
        if data.woo_consumer_key.strip() != "":
            try:
                integ.woo_consumer_key = encrypt_value(data.woo_consumer_key)
            except Exception as e:
                logger.error(f"Woo Key encryption failed: {e}")
                raise HTTPException(500, "Failed to encrypt WooCommerce Key")
        else:
            integ.woo_consumer_key = None

    if data.woo_consumer_secret is not None:
        if data.woo_consumer_secret.strip() != "":
            try:
                integ.woo_consumer_secret = encrypt_value(data.woo_consumer_secret)
            except Exception as e:
                logger.error(f"Woo Secret encryption failed: {e}")
                raise HTTPException(500, "Failed to encrypt WooCommerce Secret")
        else:
            integ.woo_consumer_secret = None

    if data.wp_base_url is not None:
        integ.wp_base_url = data.wp_base_url.strip()

    # Commit changes
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database commit failed: {e}")
        raise HTTPException(500, f"Database error: {str(e)}")

    # Trigger background cache refresh if needed
    if url_changed:
        from services.default_bot import clear_cache_for_bot, refresh_cache
        clear_cache_for_bot(integ.bot_id)
        
        refresh_url = integ.woocommerce_url or integ.wp_base_url
        if refresh_url:
            key = decrypt_value(integ.woo_consumer_key) if integ.woo_consumer_key else ""
            secret = decrypt_value(integ.woo_consumer_secret) if integ.woo_consumer_secret else ""
            
            logger.info(f"Queueing background cache refresh for bot {integ.bot_id}")
            background_tasks.add_task(
                refresh_cache, 
                integ.bot_id, key, secret, 
                integ.woocommerce_url or "", "", 
                integ.wp_base_url or "", 
                business_type=integ.business_type
            )

    return {"status": "ok"}


@router.post("/me/fetch-website-content")
def fetch_website_content(site_type: str, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    from models import Bot
    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")

    website_url = integ.woocommerce_url if site_type == "product" else integ.wp_base_url
    if not website_url:
        raise HTTPException(400, f"Please provide your {'store' if site_type == 'product' else 'website'} URL first.")

    result = fetch_website_content(website_url, site_type)
    if "error" in result:
        return {"success": False, "message": f"Failed to fetch content: {result['error']}", "data": {}}

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
    from models import Bot
    user_plan = get_user_plan(user_id, db)
    if user_plan == "free":
        raise HTTPException(403, PLAN_ERROR_FREE)

    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")
    
    woo_url = integ.woocommerce_url or integ.wp_base_url
    if not woo_url:
        raise HTTPException(400, "Please provide your website/store URL first.")
    
    consumer_key = consumer_secret = ""
    if integ.woo_consumer_key and integ.woo_consumer_secret:
        try:
            consumer_key = decrypt_value(integ.woo_consumer_key)
            consumer_secret = decrypt_value(integ.woo_consumer_secret)
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {e}")

    if consumer_key and consumer_secret:
        result = UniversalWebsiteFetcher.fetch_products_with_auth(woo_url, consumer_key, consumer_secret)
    else:
        result = UniversalWebsiteFetcher.scrape_products_from_website(woo_url)
    
    if not result["success"]:
        return {
            "success": False,
            "total_products": integ.woo_products_count,
            "total_categories": 0,
            "message": result.get("error", "Failed to fetch content from website."),
            "error": result.get("error")
        }
    
    integ.woo_products_cached = True
    integ.woo_categories_cached = json.dumps(result.get("categories", []))
    integ.woo_products_count = result.get("total_products", 0)
    db.commit()
    
    return {
        "success": True,
        "total_products": result.get("total_products", 0),
        "total_categories": len(result.get("categories", [])),
        "message": f"Successfully fetched {result.get('total_products', 0)} items from your website!"
    }


@router.post("/me/discover-website")
def discover_website(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    from models import Bot
    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")
    
    website_url = integ.woocommerce_url or integ.wp_base_url
    if not website_url:
        raise HTTPException(400, "Please provide your website URL first.")
    
    result = UniversalWebsiteFetcher.auto_discover_and_fetch(website_url)
    if result["success"] and not integ.wp_base_url:
        integ.wp_base_url = UniversalWebsiteFetcher.normalize_url(website_url)
        db.commit()
    
    return result


@router.post("/me/configure-base")
async def configure_integration_base(
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    config: dict = Body(...)
):
    from models import Bot
    user_plan = get_user_plan(user_id, db)
    integration_type = config.get("integration_type")
    
    if user_plan == "free" and integration_type == "product":
        raise HTTPException(403, PLAN_ERROR_FREE)

    integ = db.query(Integration).join(Integration.bot).filter(Bot.user_id == user_id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")

    website_url = config.get("website_url")
    if not integration_type or not website_url:
        raise HTTPException(400, "Integration type and website URL are required.")

    normalized_url = UniversalWebsiteFetcher.normalize_url(website_url)
    integ.business_type = integration_type
    if integration_type == "product":
        integ.woocommerce_url = normalized_url
    else:
        integ.wp_base_url = normalized_url
    
    db.commit()
    
    # Trigger discovery in background
    background_tasks.add_task(UniversalWebsiteFetcher.auto_discover_and_fetch, normalized_url)

    return {"success": True, "message": "Base configuration saved. Discovery started in background."}
