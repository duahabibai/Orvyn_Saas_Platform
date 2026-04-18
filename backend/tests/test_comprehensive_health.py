"""
Comprehensive System Health Check
Tests all major functionality
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"
passed = 0
failed = 0
total = 0

def test(name, func):
    global passed, failed, total
    total += 1
    try:
        func()
        print(f"✅ {total}. {name}")
        passed += 1
    except Exception as e:
        print(f"❌ {total}. {name}: {str(e)}")
        failed += 1

# ===== TESTS =====

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"

def test_api_health():
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"

def test_webhook_get():
    r = requests.get(f"{BASE_URL}/webhook/test")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"

def test_webhook_verify():
    r = requests.get(f"{BASE_URL}/webhook", params={
        "hub.mode": "subscribe",
        "hub.verify_token": "whatsapp_bot_verify_token_123",
        "hub.challenge": "test_challenge"
    })
    assert r.status_code == 200
    assert r.text == "test_challenge"

def test_signup():
    r = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "email": "healthcheck@test.com",
        "password": "testpass123",
        "full_name": "Health Check User"
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "healthcheck@test.com",
        "password": "testpass123"
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data

def test_duplicate_signup():
    r = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "email": "healthcheck@test.com",
        "password": "testpass123",
        "full_name": "Duplicate"
    })
    assert r.status_code == 400

def test_invalid_login():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "healthcheck@test.com",
        "password": "wrongpassword"
    })
    assert r.status_code == 401

def test_get_profile():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "healthcheck@test.com",
        "password": "testpass123"
    })
    token = r.json()["access_token"]
    
    r2 = requests.get(f"{BASE_URL}/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert r2.status_code == 200
    data = r2.json()
    assert data["email"] == "healthcheck@test.com"

def test_invalid_token():
    r = requests.get(f"{BASE_URL}/api/auth/me", headers={
        "Authorization": "Bearer invalidtoken123"
    })
    assert r.status_code == 401

def test_token_refresh():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "healthcheck@test.com",
        "password": "testpass123"
    })
    data = r.json()
    refresh_token = data["refresh_token"]
    
    r2 = requests.post(f"{BASE_URL}/api/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert r2.status_code == 200
    assert "access_token" in r2.json()

def test_get_integrations():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "healthcheck@test.com",
        "password": "testpass123"
    })
    token = r.json()["access_token"]
    
    r2 = requests.get(f"{BASE_URL}/api/integrations/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert r2.status_code == 200
    data = r2.json()
    assert "id" in data
    assert "bot_id" in data

def test_update_integrations():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "healthcheck@test.com",
        "password": "testpass123"
    })
    token = r.json()["access_token"]
    
    r2 = requests.patch(f"{BASE_URL}/api/integrations/me", headers={
        "Authorization": f"Bearer {token}"
    }, json={
        "woocommerce_url": "https://test-example.com"
    })
    assert r2.status_code == 200
    assert r2.json()["status"] == "ok"

def test_cors():
    r = requests.options(f"{BASE_URL}/api/auth/signup", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    })
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"

def test_webhook_post():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "type": "text",
                        "text": {"body": "Test message"},
                        "id": "test_msg_123",
                        "from": "9876543210"
                    }],
                    "contacts": [{"profile": {"name": "Test"}}],
                    "metadata": {"phone_number_id": "947545465116316"}
                }
            }]
        }]
    }
    r = requests.post(f"{BASE_URL}/webhook", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_docs_available():
    r = requests.get(f"{BASE_URL}/docs")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")

# ===== RUN TESTS =====

print("\n" + "="*60)
print("🧪 COMPREHENSIVE SYSTEM HEALTH CHECK")
print("="*60 + "\n")

test("Health endpoint", test_health)
test("API Health endpoint", test_api_health)
test("Webhook test endpoint", test_webhook_get)
test("Webhook Meta verification", test_webhook_verify)
test("User signup", test_signup)
test("User login", test_login)
test("Duplicate email rejection", test_duplicate_signup)
test("Invalid password rejection", test_invalid_login)
test("Get user profile (authenticated)", test_get_profile)
test("Invalid token rejection", test_invalid_token)
test("Token refresh", test_token_refresh)
test("Get integrations (authenticated)", test_get_integrations)
test("Update integrations (authenticated)", test_update_integrations)
test("CORS configuration", test_cors)
test("Webhook POST handler", test_webhook_post)
test("API docs available", test_docs_available)

# ===== SUMMARY =====

print("\n" + "="*60)
print(f"📊 TEST SUMMARY: {passed}/{total} passed, {failed}/{total} failed")
print("="*60 + "\n")

if failed == 0:
    print("🎉 ALL TESTS PASSED! System is working perfectly.")
    sys.exit(0)
else:
    print(f"⚠️  {failed} test(s) failed. Please check the errors above.")
    sys.exit(1)
