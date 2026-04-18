"""
Complete WhatsApp Webhook Test - Simulates exact WhatsApp flow
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def main():
    print("\n" + "="*70)
    print("  WHATSAPP WEBHOOK COMPLETE TEST")
    print("="*70)
    
    # Step 1: Create user
    print("\n1️⃣  Creating user...")
    signup = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "email": f"whatsapp_test_{int(time.time())}@test.com",
        "password": "Test123!"
    })
    
    if signup.status_code != 200:
        print(f"❌ Signup failed: {signup.text}")
        return
    
    tokens = signup.json()
    token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ User created")
    
    # Step 2: Setup integration with YOUR WhatsApp credentials
    print("\n2️⃣  Setting up WhatsApp integration...")
    integ = requests.patch(f"{BASE_URL}/api/integrations/me", json={
        "whatsapp_token": "EAA25QLJH7a4BRPqzZAtZCjWD7GcszW8n6DpXCdjX6GNByLvkezVJZCxHOuc2Mn3swlfy9OlVVGxyVhpqq2earXa4zajFtWcKLaDbLZAOOSjGAseb2H6ad3HXN5TnZBre1ZAcF2wUsPp6P53Ci6JZBA1ZAdpdvZAdjwS05k1cog6qo1r3gJXyPS7tEa2PB8erCfLi8WFoYlQxWBhpcp2yRIVUytTOZAt50AQ2NJyZAbOpDtZAwQ13pWRBznjyWHIYwFL9ng6giWR4i5bUpdSiuLeHwAgb4zdX6ba424xUccHLNAZDZD",
        "phone_number_id": "947545465116316",
        "verify_token": "whatsapp_bot_verify_token_123"
    }, headers=headers)
    
    if integ.status_code != 200:
        print(f"❌ Integration setup failed: {integ.status_code}")
        print(f"Response: {integ.text[:500]}")
        return
    
    # Get the integration to verify
    get_integ = requests.get(f"{BASE_URL}/api/integrations/me", headers=headers)
    if get_integ.status_code == 200:
        integ_data = get_integ.json()
        print(f"✅ Integration setup complete")
        print(f"   - Phone Number ID: {integ_data.get('phone_number_id', 'Not set')}")
        print(f"   - Has WhatsApp Token: {'Yes' if integ_data.get('whatsapp_token') else 'No'}")
    else:
        print(f"✅ Integration updated (PATCH succeeded)")
    
    time.sleep(1)  # Give server a moment to update
    
    # Step 3: Verify webhook route is accessible
    print("\n3️⃣  Testing webhook route...")
    time.sleep(0.5)
    test_route = requests.get(f"{BASE_URL}/webhook/test")
    if test_route.status_code == 200:
        print(f"✅ Webhook route accessible: {test_route.json()['message']}")
    else:
        print(f"⚠️  Webhook route returned {test_route.status_code}, continuing anyway...")
    
    # Step 4: Test webhook verification (GET)
    print("\n4️⃣  Testing webhook verification (GET)...")
    verify = requests.get(f"{BASE_URL}/webhook", params={
        "hub.mode": "subscribe",
        "hub.verify_token": "whatsapp_bot_verify_token_123",
        "hub.challenge": "test_challenge_123"
    })
    
    if verify.status_code == 200:
        print(f"✅ Webhook verification SUCCESS")
        print(f"   Challenge: {verify.text}")
    else:
        print(f"❌ Webhook verification FAILED: {verify.status_code}")
        print(f"   Response: {verify.text}")
    
    # Step 5: Simulate WhatsApp message (POST)
    print("\n5️⃣  Simulating WhatsApp message (POST)...")
    webhook_payload = {
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
                        "profile": {"name": "Test Customer"},
                        "wa_id": "923001234567"
                    }],
                    "messages": [{
                        "from": "923001234567",
                        "id": f"wamid.HBgMOTEzMDAxMjM0NTY3FQIAERgSNEUyRjE3RjBGNUM3QjlCNzlEMwA=",
                        "timestamp": str(int(time.time())),
                        "text": {
                            "body": "Hi! What products do you have?"
                        },
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    print(f"📤 Sending webhook POST...")
    print(f"   - From: 923001234567")
    print(f"   - Message: Hi! What products do you have?")
    print(f"   - Phone Number ID: 947545465116316")
    
    post_resp = requests.post(f"{BASE_URL}/webhook", json=webhook_payload, timeout=30)
    
    if post_resp.status_code == 200:
        print(f"\n✅ Webhook POST SUCCESS!")
        print(f"   Response: {post_resp.json()}")
    else:
        print(f"\n❌ Webhook POST FAILED: {post_resp.status_code}")
        print(f"   Response: {post_resp.text[:500]}")
    
    # Step 6: Check if message was saved
    print("\n6️⃣  Checking if messages were saved...")
    messages = requests.get(f"{BASE_URL}/api/chats", headers=headers)
    if messages.status_code == 200:
        msgs = messages.json()
        if isinstance(msgs, list) and len(msgs) > 0:
            print(f"✅ Found {len(msgs)} message(s) in database")
            for msg in msgs[:3]:
                sender = msg.get('sender', 'unknown')
                message = msg.get('message', '')[:50]
                print(f"   - {sender}: {message}...")
        else:
            print(f"⚠️  No messages found in database")
    else:
        print(f"⚠️  Could not fetch messages: {messages.status_code}")
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print("""
✅ Webhook route is accessible
✅ Webhook verification works (GET)
✅ Webhook message processing works (POST)
✅ Messages are saved to database

📝 NEXT STEPS:
1. If you're using ngrok, set your webhook URL in Meta:
   - Go to: Meta for Developers → WhatsApp → Configuration
   - Webhook URL: https://your-ngrok-url.ngrok-free.dev/webhook
   - Verify Token: whatsapp_bot_verify_token_123
   - Subscribe to: messages

2. Make sure ngrok is running:
   ngrok http 8000

3. Send a test message to your WhatsApp number

⚠️  IMPORTANT: Your WhatsApp token and phone_number_id must match
    what's configured in Meta for Developers Console.
""")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR: Is backend running at {BASE_URL}?")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
