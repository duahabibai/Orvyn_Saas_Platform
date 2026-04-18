"""
WhatsApp Webhook Debug Tool - Shows EXACTLY what happens step by step
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def debug_whatsapp_flow():
    """Debug the entire WhatsApp message flow"""
    
    print("\n" + "="*70)
    print("  WHATSAPP WEBHOOK DEBUG TOOL")
    print("="*70)
    
    # Step 1: Create/login user
    print("\n📝 Step 1: Creating user...")
    signup = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "email": f"wa_debug_{int(time.time())}@test.com",
        "password": "Test123!"
    })
    
    if signup.status_code == 200:
        tokens = signup.json()
        print(f"✅ User created successfully")
    else:
        # Try login
        signup = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        if signup.status_code != 200:
            print(f"❌ Cannot create or login to user")
            return
        tokens = signup.json()
        print(f"✅ Logged in successfully")
    
    token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get bot info
    print("\n🤖 Step 2: Getting bot info...")
    bot_resp = requests.get(f"{BASE_URL}/api/bots/me", headers=headers)
    if bot_resp.status_code != 200:
        print(f"❌ Failed to get bot: {bot_resp.text}")
        return
    
    bot = bot_resp.json()
    bot_id = bot["id"]
    print(f"✅ Bot ID: {bot_id}")
    print(f"   Mode: {bot['mode']}")
    print(f"   Status: {bot['status']}")
    
    # Step 3: Setup WhatsApp integration
    print("\n📱 Step 3: Setting up WhatsApp integration...")
    
    # YOUR WhatsApp credentials from .env
    wa_token = "EAA25QLJH7a4BRPqzZAtZCjWD7GcszW8n6DpXCdjX6GNByLvkezVJZCxHOuc2Mn3swlfy9OlVVGxyVhpqq2earXa4zajFtWcKLaDbLZAOOSjGAseb2H6ad3HXN5TnZBre1ZAcF2wUsPp6P53Ci6JZBA1ZAdpdvZAdjwS05k1cog6qo1r3gJXyPS7tEa2PB8erCfLi8WFoYlQxWBhpcp2yRIVUytTOZAt50AQ2NJyZAbOpDtZAwQ13pWRBznjyWHIYwFL9ng6giWR4i5bUpdSiuLeHwAgb4zdX6ba424xUccHLNAZDZD"
    phone_number_id = "947545465116316"
    verify_token = "whatsapp_bot_verify_token_123"
    
    integ_resp = requests.patch(f"{BASE_URL}/api/integrations/me", json={
        "whatsapp_token": wa_token,
        "phone_number_id": phone_number_id,
        "verify_token": verify_token
    }, headers=headers)
    
    if integ_resp.status_code != 200:
        print(f"❌ Failed to setup integration: {integ_resp.text}")
        return
    
    print(f"✅ Integration updated")
    print(f"   Phone Number ID: {phone_number_id}")
    print(f"   WhatsApp Token: {wa_token[:30]}...")
    print(f"   Verify Token: {verify_token}")
    
    # Step 4: Verify integration was saved
    print("\n🔍 Step 4: Verifying integration was saved...")
    get_integ = requests.get(f"{BASE_URL}/api/integrations/me", headers=headers)
    if get_integ.status_code == 200:
        integ = get_integ.json()
        print(f"✅ Integration retrieved from DB:")
        print(f"   - phone_number_id: {integ.get('phone_number_id')}")
        print(f"   - has_whatsapp_token: {integ.get('has_whatsapp_token')}")
        print(f"   - whatsapp_token_preview: {integ.get('whatsapp_token_preview', 'N/A')}")
    else:
        print(f"⚠️  Could not verify integration: {get_integ.status_code}")
    
    # Step 5: Test webhook verification
    print("\n✅ Step 5: Testing webhook verification...")
    verify_resp = requests.get(f"{BASE_URL}/webhook", params={
        "hub.mode": "subscribe",
        "hub.verify_token": verify_token,
        "hub.challenge": "test123"
    })
    
    if verify_resp.status_code == 200:
        print(f"✅ Webhook verification works")
    else:
        print(f"❌ Webhook verification failed: {verify_resp.status_code}")
        print(f"   Response: {verify_resp.text}")
    
    # Step 6: Simulate WhatsApp webhook POST
    print("\n📨 Step 6: Simulating WhatsApp webhook POST...")
    
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "0",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": phone_number_id,
                        "phone_number_id": phone_number_id  # THIS IS THE KEY FIELD!
                    },
                    "contacts": [{
                        "profile": {"name": "Test Customer"},
                        "wa_id": "923001234567"
                    }],
                    "messages": [{
                        "from": "923001234567",
                        "id": f"wamid.HBgMOTEzMDAxMjM0NTY3FQIAERgS{int(time.time())}",
                        "timestamp": str(int(time.time())),
                        "text": {
                            "body": "Hello! What products do you have?"
                        },
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    print(f"📤 Sending webhook with:")
    print(f"   - phone_number_id in metadata: {phone_number_id}")
    print(f"   - Message from: 923001234567")
    print(f"   - Message text: Hello! What products do you have?")
    
    post_resp = requests.post(f"{BASE_URL}/webhook", json=webhook_payload, timeout=30)
    
    if post_resp.status_code == 200:
        print(f"\n✅ Webhook POST returned 200 OK")
        print(f"   Response: {post_resp.json()}")
    else:
        print(f"\n❌ Webhook POST failed with {post_resp.status_code}")
        print(f"   Response: {post_resp.text[:500]}")
    
    # Step 7: Check if messages were saved
    print("\n💾 Step 7: Checking database for messages...")
    time.sleep(1)  # Give DB time to save
    
    chats_resp = requests.get(f"{BASE_URL}/api/chats", headers=headers)
    if chats_resp.status_code == 200:
        messages = chats_resp.json()
        if isinstance(messages, list) and len(messages) > 0:
            print(f"✅ Found {len(messages)} message(s) in database:")
            for msg in messages[-3:]:  # Last 3 messages
                sender = msg.get('sender', '?')
                text = msg.get('message', '')[:80]
                print(f"   {sender}: {text}")
        else:
            print(f"⚠️  No messages found in database")
            print(f"   This means the webhook did not process the message!")
    else:
        print(f"⚠️  Could not fetch chats: {chats_resp.status_code}")
    
    # Summary
    print("\n" + "="*70)
    print("  DEBUG SUMMARY")
    print("="*70)
    print("""
📝 What to check:

1. If Step 4 shows phone_number_id matches what you sent in webhook:
   ✅ They match = Good!
   ❌ They don't match = Webhook can't find your bot!

2. If Step 7 shows messages in database:
   ✅ Messages exist = Webhook processing works!
   ❌ No messages = Webhook failed to find bot or crashed

3. Check backend console for these log messages:
   - "📨 Webhook received"
   - "Processing message with Bot ID: X"
   - "Bot X replied: ..."
   - "✅ WhatsApp message sent to ..."

🔧 Common Issues:

Issue: "No bot found for phone_number_id"
Fix: Make sure the phone_number_id in your webhook payload matches
     what's in the Integrations table EXACTLY.

Issue: "No WhatsApp token or phone_number_id"
Fix: Check that you entered both fields in the Integrations page.

Issue: Messages in DB but not sent to WhatsApp
Fix: Check that wa_token decrypts successfully and phone_number_id is set.

📱 For Real WhatsApp Testing:

1. Start ngrok: ngrok http 8000
2. Copy the ngrok URL (e.g., https://abc123.ngrok-free.dev)
3. In Meta for Developers → WhatsApp → Configuration:
   - Webhook URL: https://abc123.ngrok-free.dev/webhook
   - Verify Token: whatsapp_bot_verify_token_123
   - Subscribe to: messages
4. Send a message to your WhatsApp number
5. Check backend console for logs
""")

if __name__ == "__main__":
    try:
        debug_whatsapp_flow()
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR: Is backend running at {BASE_URL}?")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
