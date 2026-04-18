"""
Diagnostic script to test AI mode and WhatsApp webhook
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_ai_mode_directly():
    """Test AI mode directly through test-chat endpoint"""
    print("\n" + "="*70)
    print("  TESTING AI MODE")
    print("="*70)
    
    # Step 1: Login
    print("\n1️⃣  Logging in...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPassword123!"
    })
    
    if login_resp.status_code != 200:
        print(f"❌ Login failed. Trying signup...")
        # Create a new user
        signup_resp = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": f"ai_test_{int(time.time())}@example.com",
            "password": "TestPassword123!"
        })
        if signup_resp.status_code != 200:
            print(f"❌ Signup failed: {signup_resp.text}")
            return
        tokens = signup_resp.json()
        print(f"✅ Signup successful")
    else:
        tokens = login_resp.json()
        print(f"✅ Login successful")
    
    token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get current bot settings
    print("\n2️⃣  Getting bot settings...")
    bot_resp = requests.get(f"{BASE_URL}/api/bots/me", headers=headers)
    if bot_resp.status_code != 200:
        print(f"❌ Get bot failed: {bot_resp.text}")
        return
    bot = bot_resp.json()
    print(f"✅ Bot: ID={bot['id']}, Mode={bot['mode']}")
    
    # Step 3: Switch to AI mode
    print("\n3️⃣  Switching to AI mode...")
    mode_resp = requests.patch(f"{BASE_URL}/api/bots/mode", json={"mode": "ai"}, headers=headers)
    if mode_resp.status_code != 200:
        print(f"❌ Switch to AI mode failed: {mode_resp.text}")
        return
    print(f"✅ Switched to AI mode")
    
    # Step 4: Update AI settings
    print("\n4️⃣  Updating AI settings...")
    settings_resp = requests.patch(f"{BASE_URL}/api/bots/settings", json={
        "model_name": "openrouter",
        "api_key": "sk-4d61b1552bfb3022a98efe201dc0d37388252421",  # From .env
        "prompt": "You are a helpful sales assistant.",
        "temperature": 70,
        "language": "english"
    }, headers=headers)
    
    if settings_resp.status_code != 200:
        print(f"❌ Update settings failed: {settings_resp.text}")
        return
    print(f"✅ AI settings updated")
    
    # Step 5: Get settings to verify
    print("\n5️⃣  Verifying settings...")
    get_settings_resp = requests.get(f"{BASE_URL}/api/bots/settings", headers=headers)
    if get_settings_resp.status_code == 200:
        settings = get_settings_resp.json()
        print(f"✅ Settings verified:")
        print(f"   - Model: {settings['model_name']}")
        print(f"   - Has API Key: {settings['has_api_key']}")
        print(f"   - Temperature: {settings['temperature']}")
    
    # Step 6: Test AI chat
    print("\n6️⃣  Testing AI chat...")
    chat_resp = requests.post(f"{BASE_URL}/api/bots/test-chat", json={
        "message": "Hello, what products do you have?",
        "phone": "+1234567890"
    }, headers=headers)
    
    if chat_resp.status_code != 200:
        print(f"❌ Test chat failed: {chat_resp.status_code}")
        print(f"Response: {chat_resp.text}")
        return
    
    result = chat_resp.json()
    print(f"✅ AI Response received:")
    print(f"   Mode: {result.get('mode')}")
    print(f"   Reply: {result.get('reply', 'NO REPLY')[:200]}")
    
    # Step 7: Switch back to default
    print("\n7️⃣  Switching back to default mode...")
    requests.patch(f"{BASE_URL}/api/bots/mode", json={"mode": "default"}, headers=headers)
    print(f"✅ Switched to default mode")

def test_webhook_flow():
    """Test WhatsApp webhook flow"""
    print("\n" + "="*70)
    print("  TESTING WHATSAPP WEBHOOK FLOW")
    print("="*70)
    
    # Step 1: Login
    print("\n1️⃣  Logging in...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPassword123!"
    })
    
    if login_resp.status_code != 200:
        print(f"❌ Login failed. Please run the AI test first to create a user.")
        return
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get integration
    print("\n2️⃣  Getting integration...")
    integ_resp = requests.get(f"{BASE_URL}/api/integrations/me", headers=headers)
    if integ_resp.status_code != 200:
        print(f"❌ Get integration failed: {integ_resp.text}")
        return
    integ = integ_resp.json()
    print(f"✅ Integration:")
    print(f"   - ID: {integ.get('id')}")
    print(f"   - Phone Number ID: {integ.get('phone_number_id', 'NOT SET')}")
    print(f"   - Has WhatsApp Token: {bool(integ.get('whatsapp_token'))}")
    print(f"   - WooCommerce URL: {integ.get('woocommerce_url', 'NOT SET')}")
    print(f"   - Products Cached: {integ.get('woo_products_cached', False)}")
    
    # Step 3: Update integration with test data
    print("\n3️⃣  Setting up test integration...")
    update_resp = requests.patch(f"{BASE_URL}/api/integrations/me", json={
        "whatsapp_token": "EAA25QLJH7a4BRPqzZAtZCjWD7GcszW8n6DpXCdjX6GNByLvkezVJZCxHOuc2Mn3swlfy9OlVVGxyVhpqq2earXa4zajFtWcKLaDbLZAOOSjGAseb2H6ad3HXN5TnZBre1ZAcF2wUsPp6P53Ci6JZBA1ZAdpdvZAdjwS05k1cog6qo1r3gJXyPS7tEa2PB8erCfLi8WFoYlQxWBhpcp2yRIVUytTOZAt50AQ2NJyZAbOpDtZAwQ13pWRBznjyWHIYwFL9ng6giWR4i5bUpdSiuLeHwAgb4zdX6ba424xUccHLNAZDZD",
        "phone_number_id": "947545465116316",
        "verify_token": "whatsapp_bot_verify_token_123"
    }, headers=headers)
    
    if update_resp.status_code != 200:
        print(f"❌ Update integration failed: {update_resp.text}")
        return
    print(f"✅ Integration updated with WhatsApp credentials")
    
    # Step 4: Test webhook verification
    print("\n4️⃣  Testing webhook verification...")
    verify_resp = requests.get(f"{BASE_URL}/webhook", params={
        "hub.mode": "subscribe",
        "hub.verify_token": "whatsapp_bot_verify_token_123",
        "hub.challenge": "test_challenge_123"
    })
    
    if verify_resp.status_code == 200:
        print(f"✅ Webhook verification successful")
        print(f"   Response: {verify_resp.text}")
    else:
        print(f"❌ Webhook verification failed: {verify_resp.status_code}")
        print(f"   Response: {verify_resp.text}")
    
    # Step 5: Test webhook POST with realistic data
    print("\n5️⃣  Testing webhook POST with message...")
    webhook_data = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "0",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "947545465116316",
                        "phone_number_id": "947545465116316"
                    },
                    "contacts": [{
                        "profile": {"name": "Test User"},
                        "wa_id": "923001234567"
                    }],
                    "messages": [{
                        "from": "923001234567",
                        "id": "wamid.test123",
                        "timestamp": str(int(time.time())),
                        "text": {"body": "Hi, what products do you have?"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    post_resp = requests.post(f"{BASE_URL}/webhook", json=webhook_data)
    if post_resp.status_code == 200:
        print(f"✅ Webhook POST successful")
        print(f"   Response: {post_resp.json()}")
    else:
        print(f"❌ Webhook POST failed: {post_resp.status_code}")
        print(f"   Response: {post_resp.text}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  WHATSAPP BOT DIAGNOSTIC TOOL")
    print("="*70)
    
    try:
        # Test AI mode
        test_ai_mode_directly()
        
        # Test webhook flow
        test_webhook_flow()
        
        print("\n" + "="*70)
        print("  DIAGNOSTIC COMPLETE")
        print("="*70)
        print("\n✅ All tests completed. Check output above for any errors.")
        print("📝 If you see errors, they indicate the specific issue.")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR: Is the backend running at {BASE_URL}?")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
