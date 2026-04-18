from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models import Bot, BotSettings, Integration, Message, Lead, User
from schemas.bot import (
    BotResponse, BotSettingsUpdate, BotModeUpdate, BotStatusUpdate, SettingsResponse,
    TestChatRequest, TestChatResponse
)
from services import decode_token
from services.encryption import encrypt_value, decrypt_value
from services.bot_engine import handle_message
from services.default_bot import refresh_cache as default_refresh, _get_cache
from services.ai_service import AVAILABLE_MODELS
from config import get_settings as get_app_settings
from pydantic import BaseModel
import logging


def get_plan_limits(plan: str) -> dict:
    """Get limits based on user plan."""
    if plan == "growth":
        return {"custom_responses": -1, "custom_products": -1}  # unlimited
    return {"custom_responses": 10, "custom_products": 10}  # starter


def get_user_plan(user_id: int, db: Session) -> str:
    """Get user plan from database."""
    user = db.query(User).filter(User.id == user_id).first()
    return user.plan if user else "starter"

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bots", tags=["bots"])


def get_current_user_id(request: Request) -> int:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    payload = decode_token(auth[7:])
    if not payload:
        raise HTTPException(401, "Invalid token")
    return int(payload.get("sub", 0))


@router.get("/me", response_model=BotResponse)
def get_my_bot(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    bot = db.query(Bot).filter(Bot.user_id == user_id).first()
    if not bot:
        raise HTTPException(404, "Bot not found")
    return bot


@router.get("/ai/models")
def get_ai_models():
    """Get available AI models per provider."""
    return AVAILABLE_MODELS


@router.patch("/mode")
def update_mode(data: BotModeUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    bot = db.query(Bot).filter(Bot.user_id == user_id).first()
    if not bot:
        raise HTTPException(404, "Bot not found")
    if data.mode not in ("default", "predefined", "ai"):
        raise HTTPException(400, "Invalid mode. Must be: default, predefined, ai")
    bot.mode = data.mode
    db.commit()
    db.refresh(bot)
    return bot


@router.patch("/status")
def update_status(data: BotStatusUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    bot = db.query(Bot).filter(Bot.user_id == user_id).first()
    if not bot:
        raise HTTPException(404, "Bot not found")
    bot.status = data.status
    db.commit()
    return {"status": "ok", "bot_status": bot.status}


@router.get("/settings", response_model=SettingsResponse)
def get_settings(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    bot = db.query(Bot).filter(Bot.user_id == user_id).first()
    if not bot or not bot.settings:
        raise HTTPException(404, "Settings not found")
    s = bot.settings
    return {
        "id": s.id,
        "bot_id": s.bot_id,
        "prompt": s.prompt,
        "model_name": s.model_name,  # Provider: openai, gemini, openrouter, qwen
        "specific_model_name": s.specific_model_name,  # Specific model: gpt-4o, gemini-2.0-flash, etc.
        "temperature": s.temperature,
        "language": s.language,
        "custom_responses": s.custom_responses,
        "custom_products": s.custom_products,
        "has_api_key": bool(s.api_key),
    }


@router.patch("/settings")
def update_settings(data: BotSettingsUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    bot = db.query(Bot).filter(Bot.user_id == user_id).first()
    if not bot or not bot.settings:
        raise HTTPException(404, "Settings not found")

    s = bot.settings
    user_plan = get_user_plan(user_id, db)
    limits = get_plan_limits(user_plan)

    # Enforce plan-based limits for custom_responses
    if data.custom_responses is not None:
        max_rules = limits["custom_responses"]
        if max_rules >= 0 and len(data.custom_responses) > max_rules:
            raise HTTPException(400, f"Starter plan allows maximum {max_rules} predefined rules. Upgrade to Growth for unlimited.")
        s.custom_responses = data.custom_responses

    # Handle custom products with plan-based limit
    if data.custom_products is not None:
        max_products = limits["custom_products"]
        if max_products >= 0 and isinstance(data.custom_products, list) and len(data.custom_products) > max_products:
            raise HTTPException(400, f"Starter plan allows maximum {max_products} custom products. Upgrade to Growth for unlimited.")
        s.custom_products = data.custom_products

    if data.prompt is not None: s.prompt = data.prompt
    if data.model_name is not None: s.model_name = data.model_name
    if data.specific_model_name is not None: s.specific_model_name = data.specific_model_name
    if data.api_key is not None: s.api_key = encrypt_value(data.api_key)
    if data.temperature is not None: s.temperature = data.temperature
    if data.language is not None: s.language = data.language

    db.commit()
    db.refresh(s)
    return {"status": "ok"}


@router.post("/settings/import")
async def import_settings(request: Request, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Import predefined rules from JSON."""
    try:
        data = await request.json()
        if not isinstance(data, dict):
            raise HTTPException(400, "Invalid JSON format. Expected a dictionary of keyword: response")

        user_plan = get_user_plan(user_id, db)
        limits = get_plan_limits(user_plan)
        max_rules = limits["custom_responses"]

        if max_rules >= 0 and len(data) > max_rules:
            raise HTTPException(400, f"Import exceeds maximum of {max_rules} rules for your plan. Upgrade to Growth for unlimited.")

        bot = db.query(Bot).filter(Bot.user_id == user_id).first()
        if not bot or not bot.settings:
            raise HTTPException(404, "Settings not found")

        # Merge or override? QWEN.md says "Automatically applies rules / Overrides manual rules if selected"
        # We'll override for simplicity in this step.
        bot.settings.custom_responses = data
        db.commit()
        return {"status": "ok", "count": len(data)}
    except Exception as e:
        raise HTTPException(400, f"Import failed: {str(e)}")


@router.post("/test-chat")
def test_chat(data: TestChatRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Test chat endpoint - simulates WhatsApp message without webhook."""
    bot = db.query(Bot).filter(Bot.user_id == user_id).first()
    if not bot:
        raise HTTPException(404, "Bot not found")

    # Get integration
    integ = db.query(Integration).filter(Integration.bot_id == bot.id).first()
    if not integ:
        raise HTTPException(404, "Integrations not found")

    # Decrypt credentials and check for cached products
    woo_key = woo_secret = ""
    woo_url = wp_url = ""
    has_cached_products = False
    
    # First, check if we have cached products in the database
    if integ.woo_products_cached and integ.woo_categories_cached:
        has_cached_products = True
        logger.info(f"Using cached WooCommerce data: {integ.woo_products_count} products")
    
    # Get credentials for live fetch if needed
    if integ.woo_consumer_key:
        try:
            woo_key = decrypt_value(integ.woo_consumer_key)
            woo_secret = decrypt_value(integ.woo_consumer_secret)
            # Use woocommerce_url if set, otherwise fall back to wp_base_url
            woo_url = integ.woocommerce_url or integ.wp_base_url or "https://example.com"
            wp_url = integ.wp_base_url or woo_url
        except Exception:
            pass

    # If no cached products, try to fetch them live
    if not has_cached_products and woo_key and woo_url:
        from services.woocommerce_fetcher import WooCommerceFetcher
        logger.info(f"Attempting live WooCommerce fetch for {woo_url}")
        woo_result = WooCommerceFetcher.fetch_products_with_auth(
            woo_url, woo_key, woo_secret
        )
        if woo_result["success"]:
            # Cache the results in the database
            import json
            integ.woo_products_cached = True
            integ.woo_categories_cached = json.dumps(woo_result["categories"])
            integ.woo_products_count = woo_result["total_products"]
            db.commit()
            has_cached_products = True
            logger.info(f"Live WooCommerce fetch successful: {woo_result['total_products']} products")
        else:
            logger.warning(f"Live WooCommerce fetch failed: {woo_result.get('error')}")
            # Fall back to default credentials
            if not woo_key or woo_key == "":
                app_settings = get_app_settings()
                woo_key = app_settings.DEFAULT_WC_KEY
                woo_secret = app_settings.DEFAULT_WC_SECRET
                woo_url = app_settings.DEFAULT_WC_URL
                wp_url = woo_url

    # If still no cached products, use default credentials
    if not has_cached_products and (not woo_key or woo_key == ""):
        app_settings = get_app_settings()
        woo_key = app_settings.DEFAULT_WC_KEY
        woo_secret = app_settings.DEFAULT_WC_SECRET
        woo_url = app_settings.DEFAULT_WC_URL
        wp_url = woo_url

    # Refresh cache
    stores_url = f"{woo_url}/wp-content/plugins/store-locator-plugin/data/stores.json" if woo_url else ""
    default_refresh(bot.id, woo_key, woo_secret, woo_url, stores_url, wp_url)

    # Get bot settings
    bs = db.query(BotSettings).filter(BotSettings.bot_id == bot.id).first()
    bot_settings = {
        "prompt": bs.prompt if bs else "",
        "model_name": bs.model_name if bs else "openrouter",
        "specific_model_name": bs.specific_model_name if bs else None,
        "api_key": decrypt_value(bs.api_key) if bs and bs.api_key else "",
        "temperature": bs.temperature if bs else 70,
        "language": bs.language if bs else "english",
        "custom_responses": bs.custom_responses if bs else {},
    }

    # Get user plan for feature gating
    user_plan = get_user_plan(user_id, db)

    # Get cached data
    c = _get_cache(bot.id)
    products = c.get("products", [])
    categories = c.get("categories", [])
    contact_info = c.get("contact", {})

    # Route through bot engine with plan check
    reply = handle_message(
        bot_mode=bot.mode,
        bot_id=bot.id,
        text=data.message,
        phone="test_phone",
        name="Test User",
        bot_settings=bot_settings,
        integrations={
            "woo_key": woo_key, "woo_secret": woo_secret, "woo_url": woo_url,
            "wp_url": wp_url, "whatsapp_token": None,
            "phone_number_id": integ.phone_number_id,
        },
        contact_info=contact_info,
        products=products,
        categories=categories,
        business_type=integ.business_type or "product",
        user_plan=user_plan
    )

    # Save messages to DB
    db_msg_user = Message(
        bot_id=bot.id,
        sender="user",
        phone_number="test_phone",
        message=data.message,
    )
    db.add(db_msg_user)
    db.flush()

    if reply:
        db_msg_bot = Message(
            bot_id=bot.id,
            sender="bot",
            phone_number="test_phone",
            message=reply[:1000],
        )
        db.add(db_msg_bot)

    db.commit()

    return {"reply": reply or "No response generated", "mode": bot.mode, "bot_id": bot.id}
