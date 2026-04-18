import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models import Bot, Integration, User, BotSettings
from services.bot_engine import handle_message
from services.default_bot import refresh_cache, _get_cache

def test_multi_tenancy():
    db = SessionLocal()
    
    # We have Bot ID 1 (Hiba) and Bot ID 4 (Brandless)
    test_bots = [1, 4]
    
    for bot_id in test_bots:
        bot = db.query(Bot).get(bot_id)
        integ = db.query(Integration).filter(Integration.bot_id == bot_id).first()
        user = db.query(User).get(bot.user_id)
        bs = db.query(BotSettings).filter(BotSettings.bot_id == bot_id).first()
        
        print(f"\n--- Testing Isolation for {user.email} (Bot {bot_id}) ---")
        print(f"Business: {integ.business_type}, Mode: {bot.mode}, URL: {integ.woocommerce_url or integ.wp_base_url}")
        
        # 1. Setup cache for this specific bot
        url = integ.woocommerce_url or integ.wp_base_url
        refresh_cache(bot_id, "", "", url, business_type=integ.business_type)
        c = _get_cache(bot_id)
        print(f"Cache Site Name: {c.get('site_name')}")
        
        # 2. Simulate 'hi' message
        bot_settings = {
            "prompt": bs.prompt,
            "model_name": bs.model_name,
            "specific_model_name": bs.specific_model_name,
            "api_key": "dummy",
            "temperature": bs.temperature,
            "language": bs.language,
            "custom_responses": bs.custom_responses,
        }
        
        reply = handle_message(
            bot_mode=bot.mode,
            bot_id=bot_id,
            text="hi",
            phone="923000000000",
            name="Test User",
            bot_settings=bot_settings,
            integrations={"woo_url": url},
            contact_info=c.get("contact"),
            products=c.get("products", []),
            categories=c.get("categories", []),
            business_type=integ.business_type,
            user_plan=user.plan
        )
        print(f"Reply: {reply.replace('👋', '').strip()[:100]}...")

if __name__ == "__main__":
    test_multi_tenancy()
