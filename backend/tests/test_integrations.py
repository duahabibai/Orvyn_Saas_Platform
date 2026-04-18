"""
Test script to verify WooCommerce integration endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Testing WooCommerce Integration Endpoints")
print("=" * 60)

# Step 1: Health check
print("\n1️⃣  Health Check...")
try:
    resp = requests.get(f"{BASE_URL}/api/health")
    print(f"   ✅ Status: {resp.status_code}")
    print(f"   ✅ Response: {resp.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 2: Try to access integrations (should fail without auth)
print("\n2️⃣  Testing authentication requirement...")
try:
    resp = requests.get(f"{BASE_URL}/api/integrations/me")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 401:
        print("   ✅ Correctly requires authentication")
    else:
        print(f"   ⚠️  Unexpected response: {resp.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 3: Test WooCommerce fetcher service directly
print("\n3️⃣  Testing WooCommerceFetcher service...")
try:
    from services.woocommerce_fetcher import WooCommerceFetcher
    
    # Test URL normalization
    test_url = "hiveworks-me.com"
    normalized = WooCommerceFetcher.normalize_url(test_url)
    print(f"   ✅ Normalized URL: {test_url} → {normalized}")
    
    # Test platform detection (this might take a few seconds)
    print("   🔍 Detecting platform...")
    platform = WooCommerceFetcher.detect_platform(normalized)
    print(f"   ✅ Platform detected:")
    print(f"      - WordPress: {platform['is_wordpress']}")
    print(f"      - WooCommerce: {platform['is_woocommerce']}")
    print(f"      - Endpoints: {platform['detected_endpoints']}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Check database schema
print("\n4️⃣  Checking database schema...")
try:
    import sqlite3
    conn = sqlite3.connect('saas_bot.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(integrations)')
    columns = cursor.fetchall()
    print(f"   ✅ Integration table has {len(columns)} columns:")
    for col in columns:
        print(f"      - {col[1]} ({col[2]})")
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Test suite completed!")
print("=" * 60)
