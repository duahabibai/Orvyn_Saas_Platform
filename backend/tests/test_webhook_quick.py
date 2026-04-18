import requests

# Test webhook POST
payload = {
    "object": "whatsapp_business_account",
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "type": "text",
                    "text": {"body": "Hello"},
                    "id": "msg123",
                    "from": "1234567890"
                }],
                "contacts": [{"profile": {"name": "TestUser"}}],
                "metadata": {"phone_number_id": "947545465116316"}
            }
        }]
    }]
}

r = requests.post('http://localhost:8000/webhook', json=payload)
print(f"Webhook Response: {r.json()}")
