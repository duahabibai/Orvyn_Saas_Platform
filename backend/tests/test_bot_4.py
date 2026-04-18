import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models import Bot, Integration, User, Lead
from services.bot_engine import handle_message
from services.default_bot import _get_cache, refresh_cache

def test_bot_4():
    db = SessionLocal()
    bot_id = 4
    bot = db.query(Bot).get(bot_id)
    integ = db.query(Integration).filter(Integration.bot_id == bot_id).first()
    user = db.query(User).get(bot.user_id)
    
    print(f"Testing Bot {bot_id} for user {user.email}")
    print(f"Mode: {bot.mode}, Type: {integ.business_type}, URL: {integ.wp_base_url}")
    
    # Simulate first message
    text = "hi"
    phone = "923331234567"
    name = "User"
    
    # 1. Setup cache
    refresh_cache(bot_id, "", "", integ.woocommerce_url, business_type=integ.business_type)
    
    c = _get_cache(bot_id)
    print(f"Cache Site Name: {c.get('site_name')}")
    print(f"Cache Products: {len(c.get('products', []))}")
    
    # 2. Handle message
    bs = bot.settings
    bot_settings = {
        "prompt": bs.prompt,
        "model_name": bs.model_name,
        "specific_model_name": bs.specific_model_name,
        "api_key": "dummy", # not needed for default mode
        "temperature": bs.temperature,
        "language": bs.language,
        "custom_responses": bs.custom_responses,
    }
    
    reply = handle_message(
        bot_mode=bot.mode,
        bot_id=bot_id,
        text=text,
        phone=phone,
        name=name,
        bot_settings=bot_settings,
        integrations={
            "woo_url": integ.woocommerce_url,
            "wp_url": integ.wp_base_url,
        },
        contact_info=c.get("contact"),
        products=c.get("products", []),
        categories=c.get("categories", []),
        business_type=integ.business_type,
        user_plan=user.plan
    )
    
    print(f"Reply: {reply}")

if __name__ == "__main__":
    test_bot_4()
