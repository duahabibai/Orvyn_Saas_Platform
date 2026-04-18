"""
Test AI mode and show backend logs
"""
import requests
import time

BASE_URL = "http://localhost:8000"

# Create user and test
print("Creating test user...")
signup = requests.post(f"{BASE_URL}/api/auth/signup", json={
    "email": f"ai_test_{int(time.time())}@test.com",
    "password": "Test123!"
})

if signup.status_code != 200:
    print(f"Signup failed: {signup.text}")
    exit(1)

tokens = signup.json()
token = tokens["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print(f"✅ User created, token: {token[:20]}...")

# Set to AI mode with a VALID OpenRouter key
print("\nSetting up AI mode...")
requests.patch(f"{BASE_URL}/api/bots/mode", json={"mode": "ai"}, headers=headers)

# IMPORTANT: You need a VALID OpenRouter API key
# The key in .env (sk-4d61b1552bfb3022a98efe201dc0d37388252421) is NOT an OpenRouter key
# It looks like a WooCommerce key

# For testing, let's try with the key as-is
requests.patch(f"{BASE_URL}/api/bots/settings", json={
    "model_name": "openrouter",
    "api_key": "sk-4d61b1552bfb3022a98efe201dc0d37388252421",
    "prompt": "You are a helpful assistant. Answer in 2 lines max.",
    "temperature": 70
}, headers=headers)

print("✅ AI mode configured")

# Test chat
print("\nSending test message to AI mode...")
chat = requests.post(f"{BASE_URL}/api/bots/test-chat", json={
    "message": "Hello! What can you help me with?",
    "phone": "+1234567890"
}, headers=headers)

if chat.status_code == 200:
    result = chat.json()
    print(f"\n📝 AI Response:")
    print(f"Mode: {result.get('mode')}")
    print(f"Reply: {result.get('reply')}")
else:
    print(f"❌ Chat failed: {chat.status_code} - {chat.text}")

print("\n✅ Test complete. Check the backend console for AI error logs.")
print("The backend should show detailed error messages about why AI failed.")
