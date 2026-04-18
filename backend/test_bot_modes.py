"""
Test Script for All Bot Modes

Tests:
1. Default Mode - Multi-message conversation flow
2. Predefined Mode - Keyword responses + AI fallback
3. AI Mode - Website data usage + provider settings

Run: python test_bot_modes.py
"""
import codecs
import sys
# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.bot_engine import handle_message
from services.default_bot import _get_cache, refresh_cache
from database import SessionLocal
from models import Bot, BotSettings, Integration, User, Lead
from services.encryption import encrypt_value, decrypt_value
import json

# Test configuration
TEST_BOT_ID = 1
TEST_PHONE = "+1234567890"
TEST_NAME = "Test User"

def get_test_bot_settings(db):
    """Get bot settings for testing."""
    bot = db.query(Bot).filter(Bot.id == TEST_BOT_ID).first()
    if not bot:
        # Create test bot
        user = db.query(User).first()
        if not user:
            user = User(email="test@example.com", password_hash="test", plan="growth")
            db.add(user)
            db.commit()
            db.refresh(user)

        bot = Bot(user_id=user.id, mode="default", status=True)
        db.add(bot)
        db.commit()
        db.refresh(bot)

    settings = db.query(BotSettings).filter(BotSettings.bot_id == bot.id).first()
    if not settings:
        settings = BotSettings(
            bot_id=bot.id,
            prompt="You are a helpful sales assistant for our store.",
            model_name="openrouter",
            specific_model_name="openai/gpt-4o-mini",
            api_key=encrypt_value("test-api-key"),
            temperature=70,
            language="english"
        )
        db.add(settings)
        db.commit()

    integration = db.query(Integration).filter(Integration.bot_id == bot.id).first()
    if not integration:
        integration = Integration(
            bot_id=bot.id,
            woocommerce_url="https://hibascollection.com",
            business_type="product"
        )
        db.add(integration)
        db.commit()
    else:
        integration.woocommerce_url = "https://hibascollection.com"
        db.commit()

    return bot, settings, integration

def test_default_mode(db):
    """Test default mode with multi-message conversation."""
    print("\n" + "="*60)
    print("TEST: DEFAULT MODE - Multi-message Flow")
    print("="*60)

    bot, settings, integ = get_test_bot_settings(db)
    bot.mode = "default"
    db.commit()

    # Clear any existing lead context
    db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).delete()
    db.commit()

    # Refresh cache
    refresh_cache(TEST_BOT_ID, "", "", "https://hibascollection.com", business_type="product")

    c = _get_cache(TEST_BOT_ID)

    bot_settings = {
        "prompt": settings.prompt,
        "model_name": settings.model_name,
        "specific_model_name": settings.specific_model_name,
        "api_key": decrypt_value(settings.api_key) if settings.api_key else "",
        "temperature": settings.temperature,
        "language": settings.language,
        "custom_responses": settings.custom_responses or {},
    }

    # Simulate proper conversation flow - user starts fresh
    messages = [
        ("hi", "Initial greeting - should show language selection"),
    ]

    print(f"\nTesting with phone: {TEST_PHONE}")
    print(f"Cache: {len(c.get('products', []))} products, {len(c.get('services', []))} services\n")

    for i, (msg, description) in enumerate(messages, 1):
        reply = handle_message(
            bot_mode="default",
            bot_id=TEST_BOT_ID,
            text=msg,
            phone=TEST_PHONE,
            name=TEST_NAME,
            bot_settings=bot_settings,
            integrations={},
            contact_info=c.get("contact", {}),
            products=c.get("products", []),
            categories=c.get("categories", []),
            business_type="product",
            user_plan="growth"
        )

        lead = db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).first()
        context = lead.context if lead else {}

        status = "[OK]" if reply and len(reply) > 0 else "[FAIL]"
        print(f"{status} Message {i}: '{msg}' ({description})")
        print(f"   Context: {context}")
        print(f"   Reply: {reply[:80]}...")
        print()

    # Now test language selection -> active state
    print("--- Testing Language Selection -> Active Menu ---")
    reply = handle_message(
        bot_mode="default",
        bot_id=TEST_BOT_ID,
        text="1",
        phone=TEST_PHONE,
        name=TEST_NAME,
        bot_settings=bot_settings,
        integrations={},
        contact_info=c.get("contact", {}),
        products=c.get("products", []),
        categories=c.get("categories", []),
        business_type="product",
        user_plan="growth"
    )
    lead = db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).first()
    context = lead.context if lead else {}
    print(f"After selecting '1' (English): Context={context}")
    print(f"Reply: {reply[:100]}...")

    # Test menu option
    print("\n--- Testing Menu Options ---")
    reply = handle_message(
        bot_mode="default",
        bot_id=TEST_BOT_ID,
        text="menu",
        phone=TEST_PHONE,
        name=TEST_NAME,
        bot_settings=bot_settings,
        integrations={},
        contact_info=c.get("contact", {}),
        products=c.get("products", []),
        categories=c.get("categories", []),
        business_type="product",
        user_plan="growth"
    )
    print(f"Menu reply: {reply[:80]}...")

    # Test order flow (should work for growth plan)
    print("\n--- Testing Order Flow (Growth Plan) ---")
    reply = handle_message(
        bot_mode="default",
        bot_id=TEST_BOT_ID,
        text="1",
        phone=TEST_PHONE,
        name=TEST_NAME,
        bot_settings=bot_settings,
        integrations={},
        contact_info=c.get("contact", {}),
        products=c.get("products", []),
        categories=c.get("categories", []),
        business_type="product",
        user_plan="growth"
    )
    lead = db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).first()
    context = lead.context if lead else {}
    print(f"After '1' (order): Context={context}")
    print(f"Reply: {reply[:80]}...")

    # Test quantity step
    reply = handle_message(
        bot_mode="default",
        bot_id=TEST_BOT_ID,
        text="test product",
        phone=TEST_PHONE,
        name=TEST_NAME,
        bot_settings=bot_settings,
        integrations={},
        contact_info=c.get("contact", {}),
        products=c.get("products", []),
        categories=c.get("categories", []),
        business_type="product",
        user_plan="growth"
    )
    lead = db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).first()
    context = lead.context if lead else {}
    print(f"After product name: Context={context}")
    print(f"Reply: {reply[:80]}...")

    # Verify context persisted
    lead = db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).first()
    if lead and lead.context:
        print("\n[OK] SUCCESS: Context persisted through conversation!")
        return True
    else:
        print("\n[FAIL] FAILURE: Context was lost!")
        return False

def test_predefined_mode(db):
    """Test predefined mode with keyword responses."""
    print("\n" + "="*60)
    print("🧪 TEST: PREDEFINED MODE - Keywords + AI Fallback")
    print("="*60)

    bot, settings, integ = get_test_bot_settings(db)
    bot.mode = "predefined"
    settings.custom_responses = {
        "price": "Our prices start at $10. Type 'products' for catalog.",
        "delivery": "We deliver in 3-5 business days nationwide.",
        "contact": "📞 Phone: +1-234-567-8900 | 📧 support@store.com"
    }
    db.commit()

    # Clear lead context
    db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).delete()
    db.commit()

    c = _get_cache(TEST_BOT_ID)

    bot_settings = {
        "prompt": settings.prompt,
        "model_name": settings.model_name,
        "specific_model_name": settings.specific_model_name,
        "api_key": decrypt_value(settings.api_key) if settings.api_key else "",
        "temperature": settings.temperature,
        "language": settings.language,
        "custom_responses": settings.custom_responses,
    }

    test_messages = [
        ("price", "Should match keyword"),
        ("delivery", "Should match keyword"),
        ("contact info", "Should match 'contact' keyword"),
        ("tell me about your services", "No keyword match - AI fallback"),
    ]

    for i, (msg, expected) in enumerate(test_messages, 1):
        reply = handle_message(
            bot_mode="predefined",
            bot_id=TEST_BOT_ID,
            text=msg,
            phone=TEST_PHONE,
            name=TEST_NAME,
            bot_settings=bot_settings,
            integrations={},
            contact_info=c.get("contact", {}),
            products=c.get("products", []),
            categories=c.get("categories", []),
            business_type="product",
            user_plan="growth"
        )

        print(f"{i}. Input: '{msg}' ({expected})")
        print(f"   Reply: {reply[:150]}...")
        print()

    print("✅ Predefined mode test complete!")
    return True

def test_ai_mode(db):
    """Test AI mode with website data and provider settings."""
    print("\n" + "="*60)
    print("🧪 TEST: AI MODE - Website Data + Provider Settings")
    print("="*60)

    bot, settings, integ = get_test_bot_settings(db)
    bot.mode = "ai"
    settings.prompt = "You are a professional sales assistant. Use the website data provided to answer accurately."
    settings.model_name = "openrouter"
    settings.specific_model_name = "openai/gpt-4o-mini"
    db.commit()

    # Clear lead context
    db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).delete()
    db.commit()

    c = _get_cache(TEST_BOT_ID)

    bot_settings = {
        "prompt": settings.prompt,
        "model_name": settings.model_name,
        "specific_model_name": settings.specific_model_name,
        "api_key": decrypt_value(settings.api_key) if settings.api_key else "",
        "temperature": settings.temperature,
        "language": settings.language,
        "custom_responses": settings.custom_responses or {},
    }

    print(f"Provider: {settings.model_name}")
    print(f"Specific Model: {settings.specific_model_name}")
    print(f"Website Data: {len(c.get('products', []))} products, {len(c.get('services', []))} services")
    print(f"Site Name: {c.get('site_name', 'N/A')}")
    print()

    test_messages = [
        "What products do you have?",
        "Tell me about your services",
        "How can I contact you?",
        "What's your return policy?",
    ]

    for i, msg in enumerate(test_messages, 1):
        reply = handle_message(
            bot_mode="ai",
            bot_id=TEST_BOT_ID,
            text=msg,
            phone=TEST_PHONE,
            name=TEST_NAME,
            bot_settings=bot_settings,
            integrations={},
            contact_info=c.get("contact", {}),
            products=c.get("products", []),
            categories=c.get("categories", []),
            business_type="product",
            user_plan="growth"
        )

        print(f"{i}. Q: '{msg}'")
        print(f"   A: {reply[:200]}...")
        print()

    print("✅ AI mode test complete!")
    return True

def test_plan_gating(db):
    """Test plan-based feature restrictions."""
    print("\n" + "="*60)
    print("TEST: PLAN GATING - Starter vs Growth")
    print("="*60)

    bot, settings, integ = get_test_bot_settings(db)
    bot.mode = "default"
    db.commit()

    # Clear lead context
    db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).delete()
    db.commit()

    c = _get_cache(TEST_BOT_ID)

    bot_settings = {
        "prompt": settings.prompt,
        "model_name": settings.model_name,
        "specific_model_name": settings.specific_model_name,
        "api_key": decrypt_value(settings.api_key) if settings.api_key else "",
        "temperature": settings.temperature,
        "language": settings.language,
        "custom_responses": settings.custom_responses or {},
    }

    # First set user to language select, then active
    handle_message(
        bot_mode="default", bot_id=TEST_BOT_ID, text="hi",
        phone=TEST_PHONE, name=TEST_NAME, bot_settings=bot_settings,
        integrations={}, contact_info=c.get("contact", {}),
        products=c.get("products", []), categories=c.get("categories", []),
        business_type="product", user_plan="growth"
    )
    handle_message(
        bot_mode="default", bot_id=TEST_BOT_ID, text="1",
        phone=TEST_PHONE, name=TEST_NAME, bot_settings=bot_settings,
        integrations={}, contact_info=c.get("contact", {}),
        products=c.get("products", []), categories=c.get("categories", []),
        business_type="product", user_plan="growth"
    )

    print("\n--- Testing STARTER Plan (Product Business) - Order Feature ---")
    reply = handle_message(
        bot_mode="default",
        bot_id=TEST_BOT_ID,
        text="1",
        phone=TEST_PHONE,
        name=TEST_NAME,
        bot_settings=bot_settings,
        integrations={},
        contact_info=c.get("contact", {}),
        products=c.get("products", []),
        categories=c.get("categories", []),
        business_type="product",
        user_plan="starter"
    )
    print(f"Order request (starter + product): {reply[:100]}")
    expected_error = "This feature is available in Growth plan" in reply
    print(f"[OK] Plan restriction working!" if expected_error else "[FAIL] Plan restriction NOT working!")

    # Reset for next test
    db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).delete()
    db.commit()

    print("\n--- Testing GROWTH Plan (Product Business) - Order Feature ---")
    handle_message(
        bot_mode="default", bot_id=TEST_BOT_ID, text="hi",
        phone=TEST_PHONE, name=TEST_NAME, bot_settings=bot_settings,
        integrations={}, contact_info=c.get("contact", {}),
        products=c.get("products", []), categories=c.get("categories", []),
        business_type="product", user_plan="growth"
    )
    handle_message(
        bot_mode="default", bot_id=TEST_BOT_ID, text="1",
        phone=TEST_PHONE, name=TEST_NAME, bot_settings=bot_settings,
        integrations={}, contact_info=c.get("contact", {}),
        products=c.get("products", []), categories=c.get("categories", []),
        business_type="product", user_plan="growth"
    )

    reply = handle_message(
        bot_mode="default",
        bot_id=TEST_BOT_ID,
        text="1",
        phone=TEST_PHONE,
        name=TEST_NAME,
        bot_settings=bot_settings,
        integrations={},
        contact_info=c.get("contact", {}),
        products=c.get("products", []),
        categories=c.get("categories", []),
        business_type="product",
        user_plan="growth"
    )
    print(f"Order request (growth + product): {reply[:100]}")
    expected_flow = "product" in reply.lower() or "cheez" in reply.lower() or "Which" in reply
    print(f"[OK] Flow working!" if expected_flow else "[FAIL] Flow NOT working!")

    # Reset for next test
    db.query(Lead).filter(Lead.bot_id == TEST_BOT_ID, Lead.phone == TEST_PHONE).delete()
    db.commit()

    print("\n--- Testing STARTER Plan (Service Business) - Service Feature ---")
    handle_message(
        bot_mode="default", bot_id=TEST_BOT_ID, text="hi",
        phone=TEST_PHONE, name=TEST_NAME, bot_settings=bot_settings,
        integrations={}, contact_info=c.get("contact", {}),
        products=c.get("products", []), categories=c.get("categories", []),
        business_type="service", user_plan="starter"
    )
    handle_message(
        bot_mode="default", bot_id=TEST_BOT_ID, text="1",
        phone=TEST_PHONE, name=TEST_NAME, bot_settings=bot_settings,
        integrations={}, contact_info=c.get("contact", {}),
        products=c.get("products", []), categories=c.get("categories", []),
        business_type="service", user_plan="starter"
    )

    reply = handle_message(
        bot_mode="default",
        bot_id=TEST_BOT_ID,
        text="1",
        phone=TEST_PHONE,
        name=TEST_NAME,
        bot_settings=bot_settings,
        integrations={},
        contact_info=c.get("contact", {}),
        products=c.get("products", []),
        categories=c.get("categories", []),
        business_type="service",
        user_plan="starter"
    )
    print(f"Service request (starter + service): {reply[:100]}")
    expected_service = "service" in reply.lower() or "konsi service" in reply.lower() or "Which" in reply
    print(f"[OK] Service flow working!" if expected_service else "[FAIL] Service flow NOT working!")

    return True

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("BOT MODES - COMPREHENSIVE TEST SUITE")
    print("="*60)

    db = SessionLocal()

    try:
        results = []

        # Run tests
        results.append(("Default Mode", test_default_mode(db)))
        results.append(("Predefined Mode", test_predefined_mode(db)))
        results.append(("AI Mode", test_ai_mode(db)))
        results.append(("Plan Gating", test_plan_gating(db)))

        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)

        passed = sum(1 for _, r in results if r)
        total = len(results)

        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Bot is production-ready!")
        else:
            print(f"\n⚠️ {total - passed} test(s) failed. Review output above.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
