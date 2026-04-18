"""
Direct AI API test - shows exact error from AI provider
"""
import requests
import json

# Test the AI API directly with the same key from .env
API_KEY = "sk-4d61b1552bfb3022a98efe201dc0d37388252421"
URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "https://example.com",
    "X-Title": "WhatsApp Bot",
}

payload = {
    "model": "openai/gpt-oss-20b:free",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in 2 lines"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

print("Testing OpenRouter API directly...")
print(f"URL: {URL}")
print(f"API Key: {API_KEY[:20]}...")
print(f"Model: {payload['model']}")
print()

try:
    resp = requests.post(URL, headers=headers, json=payload, timeout=20)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\nParsed response:")
        print(json.dumps(data, indent=2)[:500])
    else:
        print(f"\n❌ API returned error {resp.status_code}")
except Exception as e:
    print(f"❌ Request failed: {e}")
