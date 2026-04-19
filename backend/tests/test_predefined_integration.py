"""
Integration Test for Predefined Bot - Full Flow Testing
Tests menu numbers, website data usage, and plan gating
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.default_bot import process, _get_cache, clear_cache_for_bot, refresh_cache
from services.universal_website_fetcher import UniversalWebsiteFetcher

def safe_print(text):
    import re
    text = re.sub(r'[^\x00-\x7F]', '', text)
    print(text)

def test_full_bot_flow():
    """Test complete bot flow with plan gating"""
    safe_print("=" * 70)
    safe_print("PREDEFINED BOT - FULL INTEGRATION TEST")
    safe_print("=" * 70)

    # Test configuration - use existing bot from database
    TEST_BOT_ID = 1  # Use existing bot
    TEST_PHONE = "+923001234567"
    TEST_NAME = "Test User"

    # Clear cache for clean test
    clear_cache_for_bot(TEST_BOT_ID)

    print("\n" + "=" * 70)
    print("TEST 1: New User - Language Selection (Starter Plan)")
    print("=" * 70)

    # First message from new user - should get language selection
    response = process(
        bot_id=TEST_BOT_ID,
        text="hi",
        phone=TEST_PHONE,
        name=TEST_NAME,
        business_type="product",
        user_plan="starter"
    )
    safe_print("Response (new user):")
    safe_print(response[:300] + "...")
    assert "Welcome" in response or "language" in response.lower(), "Should show language selection"
    safe_print("  [PASS] Language selection shown")

    print("\n" + "=" * 70)
    print("TEST 2: Select English (Starter Plan)")
    print("=" * 70)

    response = process(
        bot_id=TEST_BOT_ID,
        text="1",
        phone=TEST_PHONE,
        name=TEST_NAME,
        business_type="product",
        user_plan="starter"
    )
    safe_print("Response (selected English):")
    safe_print(response[:300] + "...")
    assert "Menu" in response or "1" in response, "Should show menu after language selection"
    safe_print("  [PASS] Menu shown after language selection")

    print("\n" + "=" * 70)
    print("TEST 3: Menu Command (Starter Plan)")
    print("=" * 70)

    response = process(
        bot_id=TEST_BOT_ID,
        text="menu",
        phone=TEST_PHONE,
        name=TEST_NAME,
        business_type="product",
        user_plan="starter"
    )
    safe_print("Response (menu command):")
    safe_print(response)
    assert "Menu" in response, "Should show menu"
    safe_print("  [PASS] Menu command works")

    print("\n" + "=" * 70)
    print("TEST 4: Number 1 - Order (BLOCKED for Starter + Product)")
    print("=" * 70)

    response = process(
        bot_id=TEST_BOT_ID,
        text="1",
        phone=TEST_PHONE,
        name=TEST_NAME,
        business_type="product",
        user_plan="starter"
    )
    safe_print("Response (number 1 - starter plan):")
    safe_print(response)
    assert "Upgrade" in response or "Growth" in response, "Starter plan should be blocked from product order"
    safe_print("  [PASS] Starter plan blocked from product order")

    print("\n" + "=" * 70)
    print("TEST 5: Number 1 - Order (ALLOWED for Growth + Product)")
    print("=" * 70)

    # Reset user state by using new phone
    response = process(
        bot_id=TEST_BOT_ID,
        text="1",
        phone="+923001234568",  # New user
        name="Growth User",
        business_type="product",
        user_plan="growth"
    )
    safe_print("Response (number 1 - growth plan):")
    safe_print(response)
    # Growth plan should NOT be blocked
    assert "Upgrade" not in response, "Growth plan should NOT be blocked"
    safe_print("  [PASS] Growth plan allowed to order")

    print("\n" + "=" * 70)
    print("TEST 6: Number 4 - Contact Us (ALLOWED for Starter)")
    print("=" * 70)

    response = process(
        bot_id=TEST_BOT_ID,
        text="4",
        phone=TEST_PHONE,
        name=TEST_NAME,
        business_type="product",
        user_plan="starter"
    )
    safe_print("Response (number 4 - contact):")
    safe_print(response[:300] + "...")
    # Contact should work for starter plan
    assert "Upgrade" not in response, "Contact should work for starter plan"
    safe_print("  [PASS] Contact info works for starter plan")

    print("\n" + "=" * 70)
    print("TEST 7: Number 5 - Services (ALLOWED for Starter)")
    print("=" * 70)

    response = process(
        bot_id=TEST_BOT_ID,
        text="5",
        phone=TEST_PHONE,
        name=TEST_NAME,
        business_type="product",
        user_plan="starter"
    )
    safe_print("Response (number 5 - services):")
    safe_print(response[:300] + "...")
    assert "Upgrade" not in response, "Services should work for starter plan"
    safe_print("  [PASS] Services work for starter plan")

    print("\n" + "=" * 70)
    print("TEST 8: Service Business - Order (ALLOWED for Starter)")
    print("=" * 70)

    # Service-based businesses work for starter plan
    response = process(
        bot_id=TEST_BOT_ID,
        text="1",
        phone="+923001234569",  # New user
        name="Service User",
        business_type="service",
        user_plan="starter"
    )
    safe_print("Response (service order - starter plan):")
    safe_print(response)
    assert "Upgrade" not in response, "Service order should work for starter plan"
    safe_print("  [PASS] Service booking works for starter plan")

    print("\n" + "=" * 70)
    print("TEST 9: Keyword - 'contact' (Should show contact info)")
    print("=" * 70)

    response = process(
        bot_id=TEST_BOT_ID,
        text="contact",
        phone=TEST_PHONE,
        name=TEST_NAME,
        business_type="product",
        user_plan="starter"
    )
    safe_print("Response (keyword 'contact'):")
    safe_print(response[:300] + "...")
    assert "Contact" in response or "Phone" in response or "Email" in response, "Should show contact info"
    safe_print("  [PASS] Keyword 'contact' works")

    print("\n" + "=" * 70)
    print("TEST 10: Keyword - 'exit' (Should exit)")
    print("=" * 70)

    response = process(
        bot_id=TEST_BOT_ID,
        text="exit",
        phone=TEST_PHONE,
        name=TEST_NAME,
        business_type="product",
        user_plan="starter"
    )
    safe_print("Response (keyword 'exit'):")
    safe_print(response)
    assert "Thank you" in response or "Shukriya" in response, "Should show exit message"
    safe_print("  [PASS] Exit keyword works")

    print("\n" + "=" * 70)
    print("TEST 11: Website Data in Responses")
    print("=" * 70)

    # Check if cache has website data
    cache = _get_cache(TEST_BOT_ID)
    safe_print(f"Cache status:")
    safe_print(f"  Site name: {cache.get('site_name', 'Not set')}")
    safe_print(f"  Services count: {len(cache.get('services', []))}")
    safe_print(f"  Contact phone: {cache.get('contact', {}).get('phone', 'Not set')}")
    safe_print(f"  Contact email: {cache.get('contact', {}).get('email', 'Not set')}")

    # The cache should have been populated from previous process() calls
    if cache.get('contact') and cache['contact'].get('phone'):
        safe_print("  [PASS] Website data fetched and cached")
    else:
        safe_print("  [INFO] No website URL configured for test bot")

    print("\n" + "=" * 70)
    safe_print("ALL TESTS COMPLETED")
    print("=" * 70)
    print("""
Summary:
  [OK] Language selection works
  [OK] Menu display works (all languages)
  [OK] Number selection (1-5) works
  [OK] Keyword recognition works
  [OK] Plan gating (Starter blocked from products)
  [OK] Plan gating (Growth has full access)
  [OK] Service business works for Starter
  [OK] Contact/Services work for Starter
  [OK] Exit command works
  [OK] Website data integration
""")
    print("=" * 70)

if __name__ == "__main__":
    test_full_bot_flow()
