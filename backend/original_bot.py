"""
AI Sales Assistant - Royal Plastics / Babji Manufacturing
Professional Sales Bot with Language Selection
🌍 Multi-language: English, Roman Urdu, Urdu
📦 Sales-focused: Quantity, Retail/Wholesale, Location
📋 Order Flow: Professional order taking with confirmation
🏪 Service Pages: Product selling focus
"""

import os
import re
import json
import logging
import requests
import time
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(override=True)
logger = logging.getLogger(__name__)

# ===================== CONFIG =====================
OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY", "")
WC_KEY = os.getenv("WC_CONSUMER_KEY", "")
WC_SECRET = os.getenv("WC_CONSUMER_SECRET", "")
WC_URL = "https://hiveworks-me.com/wp-json/wc/v3"
WP_URL = "https://hiveworks-me.com/wp-json/wp/v2"
SITE = "https://hiveworks-me.com"
STORES_URL = f"{SITE}/wp-content/plugins/store-locator-plugin/data/stores.json"
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"

AI_MODELS = ["openai/gpt-oss-20b:free"]

# ===================== CACHE =====================
cache = {
    "products": [], "categories": [], "about": "",
    "contact": {}, "faq": [], "stores_raw": [], "stores_by_city": {},
    "last_updated": None, "ttl": timedelta(minutes=30)
}
model_health = {"working": None, "failed": set()}

# ===================== RATE LIMITING =====================
_rate_lock = threading.Lock()
_last_429 = 0
_last_req = 0

def _is_rate_limited():
    global _last_429
    with _rate_lock:
        if _last_429 > 0 and (time.time() - _last_429) < 5:
            return True
        _last_429 = 0
    return False

def _throttle():
    global _last_req
    with _rate_lock:
        wait = 0.8 - (time.time() - _last_req)
        if wait > 0:
            time.sleep(wait)
        _last_req = time.time()

# ===================== DATA FETCHING =====================
def fetch_all_website_data():
    global cache
    if cache["products"] and cache["last_updated"]:
        if datetime.now() - cache["last_updated"] < cache["ttl"]:
            return cache

    logger.info("Fetching website data from API...")

    try:
        r = requests.get(f"{WC_URL}/products",
            params={"consumer_key": WC_KEY, "consumer_secret": WC_SECRET, "per_page": 100}, timeout=20)
        if r.status_code == 200:
            cache["products"] = r.json()
            cats = set()
            for p in cache["products"]:
                for c in p.get("categories", []):
                    n = c.get("name", "")
                    if n: cats.add(n)
            cache["categories"] = sorted(list(cats))
            logger.info(f"Fetched {len(cache['products'])} products, {len(cache['categories'])} categories")
    except Exception as e:
        logger.error(f"Products error: {e}")

    try:
        r = requests.get(STORES_URL, timeout=15)
        if r.status_code == 200:
            data = r.json()
            cache["stores_raw"] = []
            cache["stores_by_city"] = {}
            if isinstance(data, dict):
                for city, stores in data.items():
                    if isinstance(stores, list):
                        for s in stores:
                            s["_city"] = city
                        cache["stores_raw"].extend(stores)
                        cache["stores_by_city"][city] = stores
            elif isinstance(data, list):
                cache["stores_raw"] = data
                for s in data:
                    city = s.get("city", "Other")
                    if city not in cache["stores_by_city"]:
                        cache["stores_by_city"][city] = []
                    cache["stores_by_city"][city].append(s)
            logger.info(f"Fetched {len(cache['stores_raw'])} stores, {len(cache['stores_by_city'])} cities")
    except Exception as e:
        logger.error(f"Stores error: {e}")

    try:
        r = requests.get(f"{WP_URL}/pages", params={"slug": "contact-us", "per_page": 1}, timeout=15)
        if r.status_code == 200 and r.json():
            html = r.json()[0].get("content", {}).get("rendered", "")
            txt = clean_html(html)
            ph = re.search(r'[\+]?[0-9][0-9\s\-]{9,}', txt)
            em = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', txt)
            cache["contact"] = {
                "phone": ph.group().strip() if ph else "+92 310 542 5253",
                "email": em.group() if em else "info@royalplastics.net",
                "address": txt[:150] if txt else "North Karachi, Pakistan"
            }
    except:
        cache["contact"] = {"phone": "+92 310 542 5253", "email": "info@royalplastics.net", "address": "North Karachi, Pakistan"}

    cache["last_updated"] = datetime.now()
    return cache

def clean_html(h):
    if not h: return ""
    t = re.sub(r'<[^>]+>', ' ', h)
    return re.sub(r'\s+', ' ', t).strip()

# ===================== LANGUAGE =====================
LANGUAGES = {
    'english': {'name': 'English', 'code': 'en'},
    'roman_urdu': {'name': 'Roman Urdu', 'code': 'ur'},
    'urdu': {'name': 'Urdu', 'code': 'ur'}
}

def get_language_name(lang_code):
    return LANGUAGES.get(lang_code, {}).get('name', 'English')

def get_language_selection():
    return """🌍 *Welcome to Royal Plastics!*
*Assalam o Alaikum!* 👋

Please select your language first:

1️⃣ *English*
2️⃣ *Roman Urdu* (اردو in English)
3️⃣ *Urdu* (اردو)

💬 Reply with *1*, *2*, or *3*"""

def get_greeting_by_lang(lang, user_name):
    greetings = {
        'english': f"""👋 Welcome *{user_name}*! I'm *Hivey* from Royal Plastics.

🏭 *Your Professional Sales Partner*
30+ years making quality household & plastic products

💬 How can I help you today? Type a number:

1️⃣ 🛒 *Place an Order*
2️⃣ 💰 *Wholesale / Retail Inquiry*
3️⃣ 🚚 *Delivery Information*
4️⃣ 📞 *Contact Us*
5️⃣ ℹ️ *Our Services*

💡 Type *menu* anytime to see these options!""",

        'roman_urdu': f"""👋 Khush amdeed *{user_name}*! Main *Hivey* hoon Royal Plastics se.

🏭 *Aap ka Professional Sales Partner*
30+ saal ka tajurba quality products mein

💬 Aaj main aap ki kaise madad kar sakta hoon? Number type karein:

1️⃣ 🛒 *Order Karein*
2️⃣ 💰 *Wholesale / Retail Inquiry*
3️⃣ 🚚 *Delivery ki Maloomat*
4️⃣ 📞 *Hum se Rabta*
5️⃣ ℹ️ *Humari Services*

💡 *menu* likhein kabhi bhi options dekhne ke liye!""",

        'urdu': f"""👋 خوش آمدید *{user_name}*! میں *Hivey* ہوں Royal Plastics سے۔

🏭 *آپ کا پروفیشنل سیلز پارٹنر*
30+ سال کا تجربہ کوالٹی پروڈکٹس میں

💬 آج میں آپ کی کیسے مدد کر سکتا ہوں؟ نمبر ٹائپ کریں:

1️⃣ 🛒 *آرڈر کریں*
2️⃣ 💰 *ہول سیل / ریٹیل انکوائری*
3️⃣ 🚚 *ڈیلیوری کی معلومات*
4️⃣ 📞 *ہم سے رابطہ*
5️⃣ ℹ️ *ہماری سروسز*

💡 *menu* لکھیں کبھی بھی آپشنز دیکھنے کے لیے!"""
    }
    return greetings.get(lang, greetings['english'])

# ===================== PRODUCT HELPERS =====================
def find_by_sku(sku, products):
    sku_clean = re.sub(r'[^A-Za-z0-9-]', '', sku).lower()
    for p in products:
        p_sku = re.sub(r'[^A-Za-z0-9-]', '', p.get("sku", "")).lower()
        if sku_clean in p_sku or p_sku in sku_clean:
            return p
    return None

def find_by_name(name, products):
    return [p for p in products if name.lower() in p.get("name", "").lower()]

def find_by_category(cat, products):
    return [p for p in products if any(cat.lower() in c.get("name", "").lower() for c in p.get("categories", []))]

# ===================== SEND FUNCTIONS =====================
def mark_as_read(message_id, token, phone_id):
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        requests.post(url, headers=headers, json={
            "messaging_product": "whatsapp", "status": "read", "message_id": message_id
        }, timeout=5)
    except: pass

def send_image(to, image_url, caption, token, phone_id):
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(url, headers=headers, json={
            "messaging_product": "whatsapp", "to": to, "type": "image",
            "image": {"link": image_url, "caption": caption}
        }, timeout=15)
        return r.status_code == 200
    except: return False

def send_text(to, text, token, phone_id):
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(url, headers=headers, json={
            "messaging_product": "whatsapp", "to": to, "type": "text",
            "text": {"body": text}
        }, timeout=15)
        if r.status_code != 200:
            logger.error(f"SendText failed: {r.status_code} {r.text[:200]}")
        return r.status_code == 200
    except Exception as e:
        logger.error(f"SendText error: {e}")
        return False

# ===================== DATABASE =====================
import sqlite3
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        phone TEXT PRIMARY KEY,
        name TEXT,
        language TEXT DEFAULT 'english',
        step TEXT DEFAULT 'language_select',
        sales_step TEXT,
        product TEXT,
        quantity TEXT,
        order_type TEXT,
        location_type TEXT,
        address TEXT,
        phone_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def save_user(phone, name=None, language=None, step=None, sales_step=None,
              product=None, quantity=None, order_type=None, location_type=None, address=None):
    conn = sqlite3.connect(DB_PATH)
    try:
        updates = []
        values = []

        if name is not None:
            updates.append("name = ?"); values.append(name)
        if language is not None:
            updates.append("language = ?"); values.append(language)
        if step is not None:
            updates.append("step = ?"); values.append(step)
        if sales_step is not None:
            updates.append("sales_step = ?"); values.append(sales_step)
        if product is not None:
            # Serialize dict to JSON for storage
            if isinstance(product, dict):
                updates.append("product = ?"); values.append(json.dumps(product))
            else:
                updates.append("product = ?"); values.append(product)
        if quantity is not None:
            updates.append("quantity = ?"); values.append(quantity)
        if order_type is not None:
            updates.append("order_type = ?"); values.append(order_type)
        if location_type is not None:
            updates.append("location_type = ?"); values.append(location_type)
        if address is not None:
            updates.append("address = ?"); values.append(address)

        if updates:
            values.append(phone)
            conn.execute(f"""UPDATE users SET
                            {', '.join(updates)},
                            last_active = CURRENT_TIMESTAMP
                            WHERE phone = ?""", values)
            if conn.total_changes == 0:
                columns = ['phone'] + [u.split(' = ')[0] for u in updates]
                all_values = [phone] + values[:-1]
                placeholders = ', '.join(['?' for _ in all_values])
                conn.execute(f"""INSERT INTO users ({', '.join(columns)})
                                VALUES ({placeholders})""", all_values)
        conn.commit()
    except Exception as e:
        logger.error(f"save_user error: {e}")
    finally:
        conn.close()

def clear_session_state(phone):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""UPDATE users SET
                        step = 'language_select',
                        sales_step = NULL,
                        product = NULL,
                        quantity = NULL,
                        order_type = NULL,
                        location_type = NULL,
                        address = NULL,
                        last_active = CURRENT_TIMESTAMP
                        WHERE phone = ?""", (phone,))
        conn.commit()
        logger.info(f"Cleared session state for {phone}")
    except Exception as e:
        logger.error(f"clear_session_state error: {e}")
    finally:
        conn.close()

def get_user(phone):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
    conn.close()
    if user:
        d = dict(user)
        # Deserialize product from JSON
        if d.get("product") and d["product"].startswith("{"):
            try:
                d["product"] = json.loads(d["product"])
            except:
                pass
        return d
    return None

init_db()

# ===================== AI ENGINE =====================
def build_concise_catalog():
    products = cache.get("products", [])
    if not products:
        return "No products in catalog."

    catalog = "PRODUCTS:\n"
    for p in products[:20]:
        name = p.get("name", "?")[:35]
        sku = p.get("sku", "")
        price = p.get("price", "0")
        stock = "in stock" if p.get("stock_status") == "instock" else "out of stock"
        cats = ", ".join([c.get("name", "")[:12] for c in p.get("categories", []) if c.get("name")])
        catalog += f"  - {name} ({sku}) | {price}PKR | {stock} | {cats}\n"

    if len(products) > 20:
        catalog += f"  ...and {len(products)-20} more\n"

    catalog += f"\nCategories: {', '.join(cache.get('categories', [])[:6])}"
    return catalog

def ai_response(text, lang='english', context=""):
    logger.info(f"AI call: text='{text[:50]}', lang='{lang}'")

    if not OPEN_ROUTER_KEY:
        return None

    if _is_rate_limited():
        logger.info("Rate limit cooldown")
        return None

    _throttle()

    contact = cache.get("contact", {})
    if not contact.get("phone"):
        contact = {"phone": "+92 310 542 5253", "email": "info@royalplastics.net",
                   "address": "North Karachi, Pakistan"}

    catalog = build_concise_catalog()

    lang_instructions = {
        'english': "Respond in English",
        'roman_urdu': "Respond in Roman Urdu (Urdu written in English script, like 'Aap kaise hain?')",
        'urdu': "Respond in Urdu script (اردو)"
    }

    system = f"""You are Hivey, a professional AI sales assistant for Royal Plastics and Babji Manufacturing.

COMPANY:
- 30+ years making household and plastic products
- Website: {SITE}
- Phone: {contact['phone']}
- Email: {contact['email']}
- Address: {contact['address']}
- Delivery: Nationwide across Pakistan and international

PRODUCTS (reference only - don't list unless asked):
{catalog}

SALES FOCUS:
- Your main job is to take orders professionally
- Ask about: quantity needed, retail or wholesale, location (Pakistan or international)
- Guide users through the sales process step by step
- Be helpful and professional like a real salesperson

RULES:
- Be friendly and professional
- Use 1-2 emojis maximum
- Answer DIRECTLY without greetings unless user greeted first
- Keep replies SHORT (2-3 lines max) - this is WhatsApp
- Answer about: products, prices, quality, delivery, orders, services
- If user wants to order, guide them through: Product → Quantity → Retail/Wholesale → Location → Details
- NEVER invent products, prices, or facts
- If unsure, share contact: {contact['phone']}
- If user asks for menu or services, tell them to type "menu" or "services"

LANGUAGE:
{lang_instructions.get(lang, 'Respond in English')}
- Match user's language naturally
- NEVER switch languages mid-message
- For Roman Urdu: use common words like 'hai', 'hain', 'kya', 'mein', etc.
- For Urdu: use proper Urdu script

{context}"""

    for model in AI_MODELS:
        try:
            r = requests.post(OPENROUTER_API, headers={
                "Authorization": f"Bearer {OPEN_ROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": SITE,
                "X-Title": "Hivey Sales Bot"
            }, json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            }, timeout=15)

            if r.status_code == 429:
                global _last_429
                _last_429 = time.time()
                model_health["failed"].add(model)
                continue

            if r.status_code == 200:
                data = r.json()
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if reply and len(reply.strip()) > 1:
                    model_health["working"] = model
                    model_health["failed"].discard(model)
                    return reply.strip()[:400]

            model_health["failed"].add(model)
        except Exception as e:
            model_health["failed"].add(model)
            if "429" in str(e):
                _last_429 = time.time()
            logger.warning(f"AI {model} failed: {e}")

    return None

# ===================== MENU =====================
def get_menu(lang='english'):
    menus = {
        'english': """📋 *Menu*:

1️⃣ 🛒 *Place Order*
2️⃣ 💰 *Wholesale / Retail Inquiry*
3️⃣ 🚚 *Delivery Information*
4️⃣ 📞 *Contact Us*
5️⃣ ℹ️ *Our Services*

💬 Type a number or keyword anytime!""",

        'roman_urdu': """📋 *Menu*:

1️⃣ 🛒 *Order Karein*
2️⃣ 💰 *Wholesale / Retail Inquiry*
3️⃣ 🚚 *Delivery ki Maloomat*
4️⃣ 📞 *Hum se Rabta*
5️⃣ ℹ️ *Humari Services*

💬 Number ya keyword type karein!""",

        'urdu': """📋 *مینو*:

1️⃣ 🛒 *آرڈر کریں*
2️⃣ 💰 *ہول سیل / ریٹیل انکوائری*
3️⃣ 🚚 *ڈیلیوری کی معلومات*
4️⃣ 📞 *ہم سے رابطہ*
5️⃣ ℹ️ *ہماری سروسز*

💬 نمبر یا کی ورڈ ٹائپ کریں!"""
    }
    return menus.get(lang, menus['english'])

# ===================== SERVICE CONTENT =====================
def get_services(lang='english'):
    services = {
        'english': """🏭 *Our Services*

📦 *Product Manufacturing*
• 30+ years experience in plastic products
• Household items & industrial products
• Custom manufacturing available

💼 *Wholesale & Retail*
• Competitive wholesale pricing
• Retail orders welcome
• Bulk order discounts

🚚 *Delivery Services*
• Nationwide delivery across Pakistan
• Express delivery (1-2 days)
• Standard delivery (3-5 days)
• International shipping on request

🎯 *Custom Orders*
• Product customization
• Private labeling available
• Large order capacity

📞 *Support*
• 24/7 customer support
• Order tracking
• Product consultation

💬 Want to order? Type *1* or *order* to start!""",

        'roman_urdu': """🏭 *Humari Services*

📦 *Product Manufacturing*
• 30+ saal ka tajurba plastic products mein
• Household aur industrial products
• Custom manufacturing available

💼 *Wholesale & Retail*
• Competitive wholesale pricing
• Retail orders bhi welcome hain
• Bulk order discounts

🚚 *Delivery Services*
• Pakistan bhar mein delivery
• Express delivery (1-2 din)
• Standard delivery (3-5 din)
• International shipping request par

🎯 *Custom Orders*
• Product customization
• Private labeling available
• Large order capacity

📞 *Support*
• 24/7 customer support
• Order tracking
• Product consultation

💬 Order karna hai? *1* ya *order* likhein!""",

        'urdu': """🏭 *ہماری سروسز*

📦 *پروڈکٹ مینوفیکچرنگ*
• 30+ سال کا تجربہ پلاسٹک پروڈکٹس میں
• ہاؤس ہولڈ اور انڈسٹریل پروڈکٹس
• کسٹم مینوفیکچرنگ دستیاب

💼 *ہول سیل اور ریٹیل*
• مسابقتی ہول سیل قیمتیں
• ریٹیل آرڈرز بھی خوش آمدید
• بلک آرڈر ڈسکاؤنٹ

🚚 *ڈیلیوری سروسز*
• پاکستان بھر میں ڈیلیوری
• ایکسپریس ڈیلیوری (1-2 دن)
• اسٹینڈرڈ ڈیلیوری (3-5 دن)
• بین الاقوامی شپنگ درخواست پر

🎯 *کسٹم آرڈرز*
• پروڈکٹ کسٹمائزیشن
• پرائیویٹ لیبلنگ دستیاب
• بڑے آرڈر کی گنجائش

📞 *سپورٹ*
• 24/7 کسٹمر سپورٹ
• آرڈر ٹریکنگ
• پروڈکٹ کنسلٹیشن

💬 آرڈر کرنا ہے؟ *1* یا *order* لکھیں!"""
    }
    return services.get(lang, services['english'])

# ===================== TEMPLATE MESSAGES =====================
def t_thanks(name, lang='english'):
    thanks = {
        'english': f"✅ Thank you {name}! We're always here to help. 😊\n\n📞 Call anytime: +92 310 542 5253",
        'roman_urdu': f"✅ Shukriya {name}! Hum hamesha yahan hain madad ke liye. 😊\n\n📞 Kabhi bhi call karein: +92 310 542 5253",
        'urdu': f"✅ شکریہ {name}! ہم ہمیشہ یہاں مدد کے لیے ہیں۔ 😊\n\n📞 کسی بھی وقت کال کریں: +92 310 542 5253"
    }
    return thanks.get(lang, thanks['english'])

def t_contact_info(lang='english'):
    c = cache.get("contact", {})
    if not c.get("phone"):
        c = {"phone": "+92 310 542 5253", "email": "info@royalplastics.net",
             "address": "North Karachi, Pakistan"}

    contacts = {
        'english': f"""📞 *Contact Us*

📱 Phone: {c['phone']}
📧 Email: {c['email']}
📍 Address: {c['address']}
🌐 Website: {SITE}

💬 We're here to help 24/7!""",

        'roman_urdu': f"""📞 *Hum se Rabta*

📱 Phone: {c['phone']}
📧 Email: {c['email']}
📍 Address: {c['address']}
🌐 Website: {SITE}

💼 Hum 24/7 madad ke liye yahan hain!""",

        'urdu': f"""📞 *ہم سے رابطہ*

📱 فون: {c['phone']}
📧 ای میل: {c['email']}
📍 پتہ: {c['address']}
🌐 ویب سائٹ: {SITE}

💼 ہم 24/7 مدد کے لیے یہاں ہیں!"""
    }
    return contacts.get(lang, contacts['english'])

def t_delivery_info(lang='english'):
    delivery = {
        'english': """🚚 *Delivery Information*

⏱️ *Standard Delivery*: 3-5 business days
⚡ *Express Delivery*: 1-2 business days
🌍 *International*: Available on request

📦 *Coverage*: Nationwide across Pakistan
💰 *Charges*: Vary by location and order size
📍 *Tracking*: Provided after dispatch

💬 Want to place an order? Type *1* or *order* to start!""",

        'roman_urdu': """🚚 *Delivery ki Maloomat*

⏱️ *Standard Delivery*: 3-5 business days
⚡ *Express Delivery*: 1-2 business days
🌍 *International*: Request par available

📦 *Coverage*: Pakistan bhar mein
💰 *Charges*: Location aur order size par depend
📍 *Tracking*: Dispatch ke baad milta hai

💬 Order karna hai? *1* ya *order* likhein!""",

        'urdu': """🚚 *ڈیلیوری کی معلومات*

⏱️ *اسٹینڈرڈ ڈیلیوری*: 3-5 بزنس دن
⚡ *ایکسپریس ڈیلیوری*: 1-2 بزنس دن
🌍 *بین الاقوامی*: درخواست پر دستیاب

📦 *کوریج*: پاکستان بھر میں
💰 *چارجز*: مقام اور آرڈر کے سائز پر منحصر
📍 *ٹریکنگ*: ڈسپیچ کے بعد فراہم

💬 آرڈر کرنا ہے؟ *1* یا *order* لکھیں!"""
    }
    return delivery.get(lang, delivery['english'])

def t_order_confirm(product, state, lang='english'):
    n = product.get("name", "Product") if isinstance(product, dict) else str(product)
    pr = product.get("price", "0") if isinstance(product, dict) else "0"
    pt = f"{pr} PKR" if pr and pr != "0" else "Contact for price"
    qty = state.get("quantity", 1)
    order_type = state.get("order_type", "Retail")
    location = state.get("location_type", "Pakistan")

    confirmations = {
        'english': f"""✅ *Order Confirmed!*

📦 Product: {n}
🔢 Quantity: {qty}
💼 Type: {order_type}
🌍 Location: {location}
💰 Price: {pt}

👤 Name: {state.get('name', '?')}
📱 Phone: {state.get('phone', '?')}
📍 Address: {state.get('address', '?')}

🚚 We will contact you soon to confirm delivery!
🎉 Thank you for choosing Royal Plastics!

📞 Need help? Call: +92 310 542 5253

━━━━━━━━━━━━━━━━━━
🔘 *What would you like to do now?*

🆕 *new* - Place another order
📋 *menu* - See main menu
👋 *exit* - End conversation""",

        'roman_urdu': f"""✅ *Order Confirm Ho Gaya!*

📦 Product: {n}
🔢 Quantity: {qty}
💼 Type: {order_type}
🌍 Location: {location}
💰 Price: {pt}

👤 Name: {state.get('name', '?')}
📱 Phone: {state.get('phone', '?')}
📍 Address: {state.get('address', '?')}

🚚 Hum jald aap se rabta kareinge delivery confirm karne ke liye!
🎉 Royal Plastics choose karne ka shukriya!

📞 Madad chahiye? Call: +92 310 542 5253

━━━━━━━━━━━━━━━━━━
🔘 *Ab aap kya karna chahte hain?*

🆕 *new* - Dobara order karein
📋 *menu* - Main menu dekhein
👋 *exit* - Baat khatam karein""",

        'urdu': f"""✅ *آرڈر تصدیق ہو گیا!*

📦 پروڈکٹ: {n}
🔢 مقدار: {qty}
💼 قسم: {order_type}
🌍 مقام: {location}
💰 قیمت: {pt}

👤 نام: {state.get('name', '?')}
📱 فون: {state.get('phone', '?')}
📍 پتہ: {state.get('address', '?')}

🚚 ہم جلد آپ سے رابطہ کریں گے!
🎉 Royal Plastics منتخب کرنے کا شکریہ!

📞 مدد چاہیے؟ کال کریں: +92 310 542 5253

━━━━━━━━━━━━━━━━━━
🔘 *اب آپ کیا کرنا چاہتے ہیں?*

🆕 *new* - دوبارہ آرڈر کریں
📋 *menu* - مین مینو دیکھیں
👋 *exit* - بات ختم کریں"""
    }
    return confirmations.get(lang, confirmations['english'])

def t_order_cancelled(lang='english'):
    msgs = {
        'english': "❌ *Order Cancelled.*\n\nNo problem! What would you like to do?\n\n📋 *menu* - See options\n💬 Ask me anything!",
        'roman_urdu': "❌ *Order Cancel Ho Gaya.*\n\nKoi baat nahi! Ab kya karna chahte hain?\n\n📋 *menu* - Options dekhein\n💬 Kuch bhi poochein!",
        'urdu': "❌ *آرڈر منسوخ ہو گیا۔*\n\nکوئی بات نہیں! اب کیا کرنا چاہتے ہیں؟\n\n📋 *menu* - آپشنز دیکھیں\n💬 کچھ بھی پوچھیں!"
    }
    return msgs.get(lang, msgs['english'])

def t_change_lang(lang='english'):
    msgs = {
        'english': "🌍 *Change Language*\n\nReply with a number:\n\n1️⃣ English\n2️⃣ Roman Urdu\n3️⃣ Urdu",
        'roman_urdu': "🌍 *Zaban Badlein*\n\nNumber se reply karein:\n\n1️⃣ English\n2️⃣ Roman Urdu\n3️⃣ Urdu",
        'urdu': "🌍 *زبان تبدیل کریں*\n\nنمبر سے جواب دیں:\n\n1️⃣ English\n2️⃣ Roman Urdu\n3️⃣ Urdu"
    }
    return msgs.get(lang, msgs['english'])

def _t_product_found(name, sku, price, stock, cats, lang):
    """Single product info — text only"""
    msgs = {
        'english': f"""📦 *{name}*
Code: {sku}
Price: {price}
Stock: {stock}
Category: {cats}

💬 To order this product, type *order* or *1*""",
        'roman_urdu': f"""📦 *{name}*
Code: {sku}
Price: {price}
Stock: {stock}
Category: {cats}

💬 Order karne ke liye *order* ya *1* likhein""",
        'urdu': f"""📦 *{name}*
کوڈ: {sku}
قیمت: {price}
اسٹاک: {stock}
کیٹیگری: {cats}

💬 آرڈر کرنے کے لیے *order* یا *1* لکھیں"""
    }
    return msgs.get(lang, msgs['english'])

def _t_category_products(cat, names, total, lang):
    """Category product list — text only"""
    name_list = "\n".join([f"• {n}" for n in names])
    more = f"\n...+ {total - len(names)} more" if total > 8 else ""
    msgs = {
        'english': f"""📂 *{cat}* ({total} products)

{name_list}{more}

💬 Type *order* to buy, or product code for details""",
        'roman_urdu': f"""📂 *{cat}* ({total} products)

{name_list}{more}

💬 *order* likhein khareedne ke liye, ya code for details""",
        'urdu': f"""📂 *{cat}* ({total} پروڈکٹس)

{name_list}{more}

💬 *order* لکھیں خریدنے کے لیے، یا کوڈ تفصیل کے لیے"""
    }
    return msgs.get(lang, msgs['english'])

def _t_all_products(items, total, lang):
    """All products list — text only"""
    item_list = "\n".join(items)
    more = f"\n\n...and {total - 10} more products" if total > 10 else ""
    msgs = {
        'english': f"""🛍️ *Our Products* ({total} total)

{item_list}{more}

💬 Type *order* to buy any product
💬 Type product code (e.g. S-570) for details""",
        'roman_urdu': f"""🛍️ *Humare Products* ({total} total)

{item_list}{more}

💬 Order ke liye *order* likhein
💬 Code likhein details ke liye (e.g. S-570)""",
        'urdu': f"""🛍️ *ہماری پروڈکٹس* ({total} total)

{item_list}{more}

💬 آرڈر کے لیے *order* لکھیں
💬 کوڈ لکھیں تفصیل کے لیے (جیسے S-570)"""
    }
    return msgs.get(lang, msgs['english'])

# ===================== MAIN MESSAGE PROCESSOR =====================
def process_message(text, phone, name):
    """Main message processor — clean flow with language first"""
    tl = text.lower().strip()

    # Get user state from DB
    existing = get_user(phone)
    is_new = False

    if not existing:
        is_new = True
        save_user(phone, name=name, language='english', step='language_select')
        st = {"step": "language_select", "name": name, "language": 'english'}
    else:
        st = {
            "step": existing.get("step", "language_select"),
            "language": existing.get("language", 'english'),
            "name": existing.get("name"),
            "sales_step": existing.get("sales_step"),
            "product": existing.get("product"),
            "quantity": existing.get("quantity"),
            "order_type": existing.get("order_type"),
            "location_type": existing.get("location_type"),
            "address": existing.get("address")
        }

    if not st.get("name") and name and name != "Friend":
        st["name"] = name
        save_user(phone, name=name)

    lang = st.get("language", 'english') or 'english'
    user_name = st.get("name") or name or "Friend"
    st["phone"] = phone
    products = cache.get("products", [])

    # ========================================
    # 1. LANGUAGE SELECTION (mandatory first step)
    # ========================================
    if st["step"] == "language_select":
        if tl in ["1", "english"]:
            st["language"] = 'english'
            st["step"] = "active"
            save_user(phone, language='english', step="active")
            return get_greeting_by_lang('english', user_name)
        elif tl in ["2", "roman urdu", "roman_urdu"]:
            st["language"] = 'roman_urdu'
            st["step"] = "active"
            save_user(phone, language='roman_urdu', step="active")
            return get_greeting_by_lang('roman_urdu', user_name)
        elif tl in ["3", "urdu"]:
            st["language"] = 'urdu'
            st["step"] = "active"
            save_user(phone, language='urdu', step="active")
            return get_greeting_by_lang('urdu', user_name)
        else:
            return get_language_selection()

    # ========================================
    # 2. POST-ORDER: Handle new/menu/exit
    # ========================================
    if st["step"] == "done":
        if tl in ["new", "order", "1", "again", "phir se", "dobara"]:
            save_user(phone, step="sales", sales_step="product")
            if lang == 'roman_urdu':
                return "🛒 Chalein naya order shuru karte hain!\n\n📦 Konsa product chahiye? (Name ya code batayein)"
            elif lang == 'urdu':
                return "🛒 چلیں نیا آرڈر شروع کرتے ہیں!\n\n📦 کون سا پروڈکٹ چاہیے؟ (نام یا کوڈ بتائیں)"
            return "🛒 Let's start a new order!\n\n📦 Which product would you like? (Name or code)"

        if tl in ["exit", "bye", "exit", "khuda hafiz", "allah hafiz", "quit", "stop"]:
            clear_session_state(phone)
            return t_thanks(user_name, lang)

        if tl in ["menu", "main menu", "0"]:
            save_user(phone, step="active", sales_step=None, product=None,
                     quantity=None, order_type=None, location_type=None)
            return get_menu(lang)

        if tl in ["lang", "language", "zaban"]:
            return t_change_lang(lang)

        # If they just chat, let AI handle but stay in "done"
        ai_reply = ai_response(text, lang, context=f"User already ordered. Keep conversation friendly. Language: {get_language_name(lang)}")
        if ai_reply:
            return ai_reply

        return get_menu(lang)

    # ========================================
    # 3. SALES FLOW (order pipeline)
    # ========================================
    if st["step"] == "sales":
        return _handle_sales_flow(text, tl, st, lang, phone, products)

    # ========================================
    # 4. ACTIVE STATE — keywords & AI
    # ========================================
    # Menu keyword
    if tl in ["menu", "main menu", "start", "options", "0"]:
        return get_menu(lang)

    # Services keyword
    if tl in ["services", "service", "5"]:
        return get_services(lang)

    # Delivery keyword
    if tl in ["delivery", "ship", "shipping", "bhejo", "delivery info", "3"]:
        return t_delivery_info(lang)

    # Contact keyword
    if tl in ["contact", "phone", "call", "email", "rabta", "number", "4"]:
        return t_contact_info(lang)

    # Wholesale/Retail — start order
    if any(w in tl for w in ['wholesale', 'retail', 'thok', 'bara order', '2']):
        save_user(phone, step="sales", sales_step="product")
        if lang == 'roman_urdu':
            return "💼 Wholesale/Retail ke liye!\n\n📦 Pehle batayein, konsa product chahiye?"
        elif lang == 'urdu':
            return "💰 ہول سیل/ریٹیل کے لیے!\n\n📦 پہلے بتائیں، کون سا پروڈکٹ چاہیے؟"
        return "💼 For Wholesale/Retail!\n\n📦 First, which product would you like?"

    # Order keyword — start order
    if any(w in tl for w in ['order', 'buy', 'khareed', 'lena', 'mangwana', 'book', '1']):
        save_user(phone, step="sales", sales_step="product")
        if lang == 'roman_urdu':
            return "🛒 Chalein order shuru karte hain!\n\n📦 Konsa product chahiye? (Name ya code batayein)"
        elif lang == 'urdu':
            return "🛒 چلیں آرڈر شروع کرتے ہیں!\n\n📦 کون سا پروڈکٹ چاہیے؟ (نام یا کوڈ بتائیں)"
        return "🛒 Let's start your order!\n\n📦 Which product would you like? (Name or code)"

    # Language change
    if tl in ["lang", "language", "zaban"]:
        return t_change_lang(lang)

    # Greetings
    if any(w in tl for w in ['hi', 'hello', 'hey', 'salam', 'assalam', 'aoa', 'hiii']):
        if lang == 'roman_urdu':
            return f"Hi {user_name}! Kaise hain? 😊\n\n{get_menu(lang)}"
        elif lang == 'urdu':
            return f"ہیلو {user_name}! کیسے ہیں؟ 😊\n\n{get_menu(lang)}"
        return f"Hi {user_name}! How are you? 😊\n\n{get_menu(lang)}"

    # Thanks/Bye
    if any(w in tl for w in ['thank', 'shukriya', 'bye', 'khuda hafiz', 'jazakallah', 'allah hafiz']):
        return t_thanks(user_name, lang)

    # SKU/Product lookup (direct)
    sku_match = re.search(r'([A-Za-z]-?\d{2,})', text)
    if sku_match and products:
        product = find_by_sku(sku_match.group(1), products)
        if product:
            name = product.get("name", "Unknown")
            price = product.get("price", "0")
            pt = f"{price} PKR" if price and price != "0" else "Contact for price"
            sku = product.get("sku", "")
            stock = "In Stock" if product.get("stock_status") == "instock" else "Out of Stock"
            cats = ", ".join([c.get("name", "") for c in product.get("categories", []) if c.get("name")])
            return _t_product_found(name, sku, pt, stock, cats, lang)

    # Category lookup
    for cat in cache.get("categories", []):
        if cat.lower() in tl:
            matched = find_by_category(cat, products)
            if matched:
                names = [p.get("name", "") for p in matched[:8]]
                return _t_category_products(cat, names, len(matched), lang)

    # "products dikhao" / show all products
    if any(w in tl for w in ['products', 'samaan', 'cheezein', 'catalog', 'list', 'dikhao', 'dekha']):
        if products:
            items = []
            for p in products[:10]:
                items.append(f"• {p.get('name', '')} ({p.get('sku', '')}) - {p.get('price', '0')} PKR")
            return _t_all_products(items, len(products), lang)

    # AI — only for general conversation, NOT for order/services/delivery
    ai_reply = ai_response(text, lang, context=f"User language: {get_language_name(lang)}")
    if ai_reply:
        return ai_reply

    # Fallback — show menu
    return _smart_fallback(text, tl, lang, user_name, products)

# ===================== FALLBACK HANDLER =====================
def _smart_fallback(text, tl, lang, user_name, products):
    menu_msg = get_menu(lang)
    defaults = {
        'english': f"I didn't quite get that, {user_name} 😊\n\n{menu_msg}",
        'roman_urdu': f"Main samjha nahi, {user_name} 😊\n\n{menu_msg}",
        'urdu': f"مجھے سمجھ نہیں آیا، {user_name} 😊\n\n{menu_msg}"
    }
    return defaults.get(lang, defaults['english'])

# ===================== SALES FLOW =====================
def _handle_sales_flow(text, tl, st, lang, phone, products):
    """Step-by-step order flow with Retail/Wholesale question"""
    sales_step = st.get("sales_step", "product")

    # Cancel/Back
    if tl in ["cancel", "ruk", "stop", "back", "wapis"]:
        save_user(phone, step="active", sales_step=None, product=None, quantity=None,
                 order_type=None, location_type=None, address=None)
        return t_order_cancelled(lang)

    if tl in ["menu", "main menu", "0"]:
        save_user(phone, step="active", sales_step=None, product=None, quantity=None,
                 order_type=None, location_type=None, address=None)
        return get_menu(lang)

    # --- STEP 1: PRODUCT ---
    if sales_step == "product":
        product_found = None

        # Try SKU first
        sku_m = re.search(r'([A-Za-z]-?\d{2,})', text)
        if sku_m:
            product_found = find_by_sku(sku_m.group(1), products)

        # Try name match
        if not product_found:
            for p in products:
                pn = p.get("name", "").lower()
                psku = p.get("sku", "").lower()
                if pn in tl or tl in pn or psku in tl or tl in psku:
                    product_found = p
                    break

        if product_found:
            prod_name = product_found.get("name", "")
            st["product"] = product_found
            save_user(phone, step="sales", sales_step="quantity", product=product_found)

            if lang == 'roman_urdu':
                return f"✅ *{prod_name}* mil gaya!\n\n📦 Aap ko kitne pieces chahiye?\n(Number type karein, e.g. 1, 5, 10, 100)"
            elif lang == 'urdu':
                return f"✅ *{prod_name}* مل گیا!\n\n📦 آپ کو کتنے pieces چاہئیں؟\n(نمبر ٹائپ کریں، جیسے 1، 5، 10، 100)"
            return f"✅ Found: *{prod_name}*\n\n📦 How many pieces do you need?\n(Type a number, e.g. 1, 5, 10, 100)"
        else:
            if lang == 'roman_urdu':
                return "⚠️ Product nahi mila 😕\n\nPlease share:\n- Product code (e.g., S-570)\n- Ya product name likhein\n\n🔙 *cancel* likhein wapis jane ke liye"
            elif lang == 'urdu':
                return "⚠️ پروڈکٹ نہیں ملا 😕\n\nبراہ کرم شیئر کریں:\n- پروڈکٹ کوڈ (جیسے S-570)\n- یا پروڈکٹ نام لکھیں\n\n🔙 *cancel* واپس جانے کے لیے"
            return "⚠️ Product not found 😕\n\nPlease share:\n- Product code (e.g., S-570)\n- Or product name\n\n🔙 Type *cancel* to go back"

    # --- STEP 2: QUANTITY ---
    if sales_step == "quantity":
        qty_match = re.search(r'(\d+)', text)
        if qty_match:
            qty = int(qty_match.group(1))
            if qty > 0:
                st["quantity"] = str(qty)
                save_user(phone, step="sales", sales_step="order_type", quantity=str(qty))

                if lang == 'roman_urdu':
                    return f"✅ Quantity: *{qty}*\n\n💼 Aap ko *Retail* chahiye ya *Wholesale*?\n\nReply: *retail* ya *wholesale*"
                elif lang == 'urdu':
                    return f"✅ مقدار: *{qty}*\n\n💰 آپ کو *ریٹیل* چاہیے یا *ہول سیل*؟\n\nجواب دیں: *retail* ya *wholesale*"
                return f"✅ Quantity: *{qty}*\n\n💼 Would you like *Retail* or *Wholesale* pricing?\n\nReply: *retail* or *wholesale*"
            else:
                if lang == 'roman_urdu':
                    return "⚠️ Please 0 se zyada quantity enter karein."
                elif lang == 'urdu':
                    return "⚠️ براہ کرم 0 سے زیادہ مقدار درج کریں۔"
                return "⚠️ Please enter a quantity greater than 0."

        if lang == 'roman_urdu':
            return "⚠️ Please valid number enter karein (e.g., 1, 5, 10, 100)"
        elif lang == 'urdu':
            return "⚠️ براہ کرم درست نمبر درج کریں (جیسے 1، 5، 10، 100)"
        return "⚠️ Please enter a valid number (e.g., 1, 5, 10, 100)"

    # --- STEP 3: RETAIL / WHOLESALE TYPE ---
    if sales_step == "order_type":
        order_type = "Retail"
        if any(w in tl for w in ['wholesale', 'thok', 'wholes', 'bara', 'bulk']):
            order_type = "Wholesale"
        elif any(w in tl for w in ['retail', 'chota', 'kam', 'single']):
            order_type = "Retail"

        st["order_type"] = order_type
        save_user(phone, step="sales", sales_step="location", order_type=order_type)

        if lang == 'roman_urdu':
            return f"✅ Type: *{order_type}*\n\n🌍 Aap *Pakistan* mein hain ya *International*?\n\nReply: *pakistan* ya *international*"
        elif lang == 'urdu':
            return f"✅ قسم: *{order_type}*\n\n🌍 کیا آپ *پاکستان* میں ہیں یا *بین الاقوامی*؟\n\nجواب دیں: *pakistan* ya *international*"
        return f"✅ Type: *{order_type}*\n\n🌍 Are you in *Pakistan* or *International*?\n\nReply: *pakistan* or *international*"

    # --- STEP 4: LOCATION ---
    if sales_step == "location":
        location_type = "Pakistan"
        if any(w in tl for w in ['pakistan', 'pak', 'haan', 'yes', 'andar', 'local']):
            location_type = "Pakistan"
        elif any(w in tl for w in ['out', 'bahar', 'international', 'foreign', 'no', 'nai', 'overseas']):
            location_type = "International"

        st["location_type"] = location_type
        save_user(phone, step="sales", sales_step="details", location_type=location_type)

        if lang == 'roman_urdu':
            return f"✅ Location: *{location_type}*\n\n👤 Ab aap apni details share karein:\n\n- Full Name\n- Phone Number\n- Delivery Address\n\n(Sab ek message mein likhein)"
        elif lang == 'urdu':
            return f"✅ مقام: *{location_type}*\n\n👤 اب آپ اپنی تفصیلات شیئر کریں:\n\n- مکمل نام\n- فون نمبر\n- ڈیلیوری پتہ\n\n(سب ایک میسج میں لکھیں)"
        return f"✅ Location: *{location_type}*\n\n👤 Now please share your details:\n\n- Full Name\n- Phone Number\n- Delivery Address\n\n(Write all in one message)"

    # --- STEP 5: USER DETAILS ---
    if sales_step == "details":
        # Parse name, phone, address
        name_match = re.search(r'(?:my name is|i am|name is|mera naam)\s+([A-Za-z\s]+?)(?:,|$|\n)', text, re.I)
        phone_match = re.search(r'[\+]?[0-9][0-9\s\-]{9,15}', text)

        if name_match:
            st["name"] = name_match.group(1).strip()
            save_user(phone, name=st["name"])

        if phone_match:
            st["phone"] = phone_match.group().strip()

        # Assume remaining text is address
        if len(text.strip()) >= 5:
            st["address"] = text.strip()
            save_user(phone, address=st["address"])

            prod = st.get("product")
            prod_name = prod.get("name", "Product") if isinstance(prod, dict) else str(prod)
            qty = st.get("quantity", 1)

            save_user(phone, step="sales", sales_step="confirm")

            if lang == 'roman_urdu':
                return f"✅ Perfect!\n\n📋 Order confirm karein:\n\n*Product:* {prod_name}\n*Quantity:* {qty}\n\n*yes* likhein confirm karne ke liye.\n*cancel* likhein wapis jane ke liye."
            elif lang == 'urdu':
                return f"✅ بہت اچھا!\n\n📋 آرڈر تصدیق کریں:\n\n*پروڈکٹ:* {prod_name}\n*مقدار:* {qty}\n\n*yes* لکھیں تصدیق کے لیے۔\n*cancel* لکھیں واپس جانے کے لیے۔"
            return f"✅ Perfect!\n\n📋 Confirm your order:\n\n*Product:* {prod_name}\n*Quantity:* {qty}\n\nReply *yes* to confirm.\nType *cancel* to go back."
        else:
            if lang == 'roman_urdu':
                return "⚠️ Please complete details share karein:\n- Name\n- Phone\n- Full Address"
            elif lang == 'urdu':
                return "⚠️ براہ کرم مکمل تفصیلات شیئر کریں:\n- نام\n- فون\n- مکمل پتہ"
            return "⚠️ Please share complete details:\n- Name\n- Phone\n- Full Address"

    # --- STEP 6: CONFIRM ---
    if sales_step == "confirm":
        if tl in ["yes", "haan", "han", "confirm", "ok", "okay", "done", "theek"]:
            prod = st.get("product")
            if not prod or not isinstance(prod, dict):
                prod = {"name": str(prod) if prod else "Product", "price": "0"}

            # Mark order as done
            save_user(phone, step="done", sales_step=None)

            return t_order_confirm(prod, st, lang)

        elif tl in ["cancel", "no", "nahi", "nhi", "reject"]:
            save_user(phone, step="active", sales_step=None, product=None,
                     quantity=None, order_type=None, location_type=None)
            return t_order_cancelled(lang)
        else:
            if lang == 'roman_urdu':
                return "⚠️ *yes* likhein confirm karne ke liye.\n*cancel* likhein wapis jane ke liye."
            elif lang == 'urdu':
                return "⚠️ *yes* لکھیں تصدیق کے لیے۔\n*cancel* لکھیں واپس جانے کے لیے۔"
            return "⚠️ Reply *yes* to confirm, or *cancel* to go back."

    return get_menu(lang)

# ===================== ENTRY POINT =====================
def get_response(text, session, site_data=None):
    return process_message(text, session.get('phone', 'unknown'), session.get('name', 'Friend'))

def clear_state(phone):
    pass

def refresh_all():
    cache['last_updated'] = None
    return fetch_all_website_data()
