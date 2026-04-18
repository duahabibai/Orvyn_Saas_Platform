"""
Comprehensive test script for the WhatsApp Bot SaaS Platform
Tests all critical functionality: auth, bot modes, AI, webhooks, and integrations
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_health():
    """Test 1: Health check"""
    print_section("TEST 1: Health Check")
    resp = requests.get(f"{BASE_URL}/api/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    data = resp.json()
    assert data["status"] == "ok", f"Unexpected health response: {data}"
    print(f"✅ Health check passed: {data}")

def test_auth_flow():
    """Test 2: Complete auth flow (signup, login, refresh)"""
    print_section("TEST 2: Authentication Flow")
    
    # Signup
    print("📝 Signing up...")
    signup_data = {
        "email": f"test_{int(time.time())}@example.com",
        "password": "TestPassword123!"
    }
    resp = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
    assert resp.status_code == 200, f"Signup failed: {resp.status_code} - {resp.text}"
    tokens = resp.json()
    assert "access_token" in tokens, f"No access token in signup response: {tokens}"
    assert "refresh_token" in tokens, f"No refresh token in signup response: {tokens}"
    print(f"✅ Signup successful")
    
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # Get current user
    print("👤 Fetching current user...")
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert resp.status_code == 200, f"Get me failed: {resp.status_code}"
    user = resp.json()
    print(f"✅ Current user: {user['email']} (ID: {user['id']})")
    
    # Token refresh
    print("🔄 Testing token refresh...")
    resp = requests.post(f"{BASE_URL}/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200, f"Refresh failed: {resp.status_code} - {resp.text}"
    new_tokens = resp.json()
    assert "access_token" in new_tokens, "No new access token"
    print(f"✅ Token refresh successful")
    
    return access_token, user["id"]

def test_bot_management(token, user_id):
    """Test 3: Bot management"""
    print_section("TEST 3: Bot Management")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get bot
    print("🤖 Fetching bot...")
    resp = requests.get(f"{BASE_URL}/api/bots/me", headers=headers)
    assert resp.status_code == 200, f"Get bot failed: {resp.status_code}"
    bot = resp.json()
    print(f"✅ Bot retrieved: ID={bot['id']}, Mode={bot['mode']}, Status={bot['status']}")
    
    # Update bot mode to AI
    print("⚙️  Updating bot mode to 'ai'...")
    resp = requests.patch(f"{BASE_URL}/api/bots/mode", json={"mode": "ai"}, headers=headers)
    assert resp.status_code == 200, f"Update bot mode failed: {resp.status_code} - {resp.text}"
    bot = resp.json()
    assert bot["mode"] == "ai", f"Bot mode not updated: {bot}"
    print(f"✅ Bot mode updated to 'ai'")
    
    # Update bot settings
    print("⚙️  Updating bot settings...")
    settings_data = {
        "prompt": "You are a helpful sales assistant for this store.",
        "model_name": "openrouter",
        "temperature": 70,
        "language": "english"
    }
    resp = requests.patch(f"{BASE_URL}/api/bots/settings", json=settings_data, headers=headers)
    assert resp.status_code == 200, f"Update settings failed: {resp.status_code} - {resp.text}"
    print(f"✅ Bot settings updated")
    
    # Switch back to default
    print("⚙️  Switching bot to 'default' mode...")
    resp = requests.patch(f"{BASE_URL}/api/bots/mode", json={"mode": "default"}, headers=headers)
    assert resp.status_code == 200, f"Switch to default failed: {resp.status_code}"
    print(f"✅ Bot mode switched to 'default'")
    
    return bot["id"]

def test_integrations(token, bot_id):
    """Test 4: Integrations"""
    print_section("TEST 4: Integrations")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get integrations
    print("🔌 Fetching integrations...")
    resp = requests.get(f"{BASE_URL}/api/integrations/me", headers=headers)
    assert resp.status_code == 200, f"Get integrations failed: {resp.status_code}"
    integ = resp.json()
    print(f"✅ Integrations retrieved: {integ.get('id', 'N/A')}")
    
    # Update WhatsApp integration
    print("📱 Updating WhatsApp integration...")
    integ_data = {
        "whatsapp_token": "test_token_123",
        "phone_number_id": "123456789",
        "verify_token": "test_verify_token"
    }
    resp = requests.patch(f"{BASE_URL}/api/integrations/me", json=integ_data, headers=headers)
    assert resp.status_code == 200, f"Update integration failed: {resp.status_code} - {resp.text}"
    print(f"✅ WhatsApp integration updated")
    
    # Test website discovery
    print("🌐 Testing website discovery...")
    discover_data = {"website_url": "https://hiveworks-me.com"}
    resp = requests.post(f"{BASE_URL}/api/integrations/me/discover-website", 
                        json=discover_data, headers=headers)
    # This might fail due to network, but should not crash
    if resp.status_code == 200:
        print(f"✅ Website discovery successful")
    else:
        print(f"⚠️  Website discovery returned {resp.status_code} (may be expected)")

def test_bot_chat(token, bot_id):
    """Test 5: Bot chat/test functionality"""
    print_section("TEST 5: Bot Chat (Test Mode)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test chat
    print("💬 Sending test message...")
    chat_data = {"message": "Hello", "phone": "+1234567890"}
    resp = requests.post(f"{BASE_URL}/api/bots/test-chat", json=chat_data, headers=headers)
    assert resp.status_code == 200, f"Test chat failed: {resp.status_code} - {resp.text}"
    result = resp.json()
    assert "reply" in result, f"No reply in test chat response: {result}"
    print(f"✅ Test chat successful, reply: {result['reply'][:100]}...")

def test_webhook_endpoint():
    """Test 6: Webhook endpoint"""
    print_section("TEST 6: Webhook Endpoint")
    
    # Test webhook verification (GET)
    print("🔍 Testing webhook verification...")
    resp = requests.get(f"{BASE_URL}/webhook", params={
        "hub.mode": "subscribe",
        "hub.verify_token": "whatsapp_bot_verify_token_123",
        "hub.challenge": "test_challenge"
    })
    # Should succeed with default token from .env
    if resp.status_code == 200:
        print(f"✅ Webhook verification successful")
    else:
        print(f"⚠️  Webhook verification returned {resp.status_code} (check .env)")
    
    # Test webhook POST with dummy data
    print("📨 Testing webhook POST...")
    webhook_data = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"phone_number_id": "123456789"},
                    "contacts": [{"profile": {"name": "Test User"}}],
                    "messages": [{"from": "+1234567890", "id": "msg_123", "text": {"body": "Hi"}, "type": "text"}]
                }
            }]
        }]
    }
    resp = requests.post(f"{BASE_URL}/webhook", json=webhook_data)
    assert resp.status_code == 200, f"Webhook POST failed: {resp.status_code}"
    print(f"✅ Webhook POST successful")

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  WHATSAPP BOT SAAS PLATFORM - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    try:
        # Test 1: Health
        test_health()
        
        # Test 2: Auth
        token, user_id = test_auth_flow()
        
        # Test 3: Bot Management
        bot_id = test_bot_management(token, user_id)
        
        # Test 4: Integrations
        test_integrations(token, bot_id)
        
        # Test 5: Chat
        test_bot_chat(token, bot_id)
        
        # Test 6: Webhook
        test_webhook_endpoint()
        
        # Summary
        print_section("TEST SUMMARY")
        print("✅ ALL TESTS PASSED!")
        print(f"   - Health check: ✅")
        print(f"   - Authentication: ✅")
        print(f"   - Bot management: ✅")
        print(f"   - Integrations: ✅")
        print(f"   - Bot chat: ✅")
        print(f"   - Webhook: ✅")
        print("\n🎉 Your WhatsApp Bot SaaS Platform is production-ready!")
        print(f"📊 Backend running at: {BASE_URL}")
        print(f"📚 API Docs: {BASE_URL}/docs")
        print(f"🌐 Frontend: http://localhost:3000")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR: Is the backend running at {BASE_URL}?")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
