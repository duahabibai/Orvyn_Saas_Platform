import requests
import json

payload = {
    "object": "whatsapp_business_account",
    "entry": [{
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {"phone_number_id": "947545465116316"},
                "contacts": [{"profile": {"name": "Test"}}],
                "messages": [{"from": "92300", "id": "123", "text": {"body": "Hi"}, "type": "text"}]
            }
        }]
    }]
}

print("Sending webhook test...")
try:
    r = requests.post('http://localhost:8000/webhook', json=payload, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
except requests.exceptions.Timeout:
    print("TIMEOUT - Webhook took more than 10 seconds!")
except Exception as e:
    print(f"Error: {e}")
