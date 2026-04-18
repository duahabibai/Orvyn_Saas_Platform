"""
Default Bot Engine — Reusable Multi-tenant Logic
Ported from original_bot.py with dynamic site data support.
Full Sales Flow implementation.
"""
import re
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database import engine

logger = logging.getLogger(__name__)

def get_user_plan(user_id: int) -> str:
    """
    Get user plan from database.
    Returns 'starter' or 'growth'.
    """
    from database import SessionLocal
    from models import User

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return user.plan or "starter"
        return "starter"
    except Exception as e:
        logger.error(f"Error fetching user plan: {e}")
        return "starter"
    finally:
        db.close()

# Set logger levels to DEBUG for detailed output
fetcher_logger = logging.getLogger('services.universal_website_fetcher')
fetcher_logger.setLevel(logging.DEBUG)
current_logger = logging.getLogger(__name__)
current_logger.setLevel(logging.DEBUG)

# Thread lock for cache operations
_cache_lock = threading.Lock()
_instance_caches = {}

def _get_cache(bot_id: int) -> dict:
    global _instance_caches
    with _cache_lock:
        if bot_id not in _instance_caches:
            _instance_caches[bot_id] = {
                "products": [], "categories": [], "contact": {},
                "site_name": "", "services": [], "about": "",
                "last_updated": None, "ttl": timedelta(minutes=30),
            }
        return _instance_caches[bot_id]

def clear_cache_for_bot(bot_id: int):
    """Clear the in-memory cache for a specific bot."""
    global _instance_caches
    with _cache_lock:
        if bot_id in _instance_caches:
            del _instance_caches[bot_id]
            logger.info(f"🗑️ Cleared cache for bot {bot_id}")

def refresh_cache(bot_id: int, woo_key: str, woo_secret: str, woo_url: str,
                  stores_url: str = "", wp_url: str = "", business_type: str = "product"):
    """Refresh the cache for a specific bot using UniversalWebsiteFetcher."""
    global _instance_caches
    from services.universal_website_fetcher import UniversalWebsiteFetcher

    site_url = woo_url or wp_url
    if not site_url:
        logger.warning(f"No site URL provided for bot {bot_id}. Skipping cache refresh.")
        return

    logger.info(f"Starting cache refresh for bot {bot_id} with URL: {site_url}, business_type: {business_type}")

    # Always fetch site info (contact, services, about, etc.)
    site_info = UniversalWebsiteFetcher.fetch_site_info(site_url)
    logger.info(f"refresh_cache: Site info fetched for bot {bot_id}: site_name={site_info.get('site_name', 'N/A')}, services={len(site_info.get('services', []))}")

    with _cache_lock:
        c = _instance_caches.get(bot_id, {
            "products": [], "categories": [], "contact": {},
            "site_name": "", "services": [], "about": "",
            "last_updated": None, "ttl": timedelta(minutes=30),
        })
        c.update(site_info)

        # Fetch products ONLY for product-based businesses
        if business_type == "product":
            prod_res = None
            if woo_key and woo_secret:
                prod_res = UniversalWebsiteFetcher.fetch_products_with_auth(site_url, woo_key, woo_secret)
                logger.info(f"refresh_cache: Fetching products via WooCommerce API for bot {bot_id}")
            else:
                prod_res = UniversalWebsiteFetcher.scrape_products_from_website(site_url)
                logger.info(f"refresh_cache: Scraping products from website for bot {bot_id}")

            if prod_res and prod_res.get("success"):
                c["products"] = prod_res.get("products", [])
                c["categories"] = prod_res.get("categories", [])
                logger.info(f"✅ Product cache updated: {len(c['products'])} products, {len(c['categories'])} categories")
            else:
                logger.warning(f"Product fetch failed for bot {bot_id}. Products will be empty. Error: {prod_res.get('error', 'Unknown') if prod_res else 'No response'}")
        else:
            logger.info(f"Skipping product fetch for service-based bot {bot_id}")
        
        # Fetch additional pages if it's WordPress
        plat = UniversalWebsiteFetcher.detect_platform(site_url)
        logger.debug(f"refresh_cache: Detected platform for {site_url}: {plat}")
        if plat.get("is_wordpress"):
            pages_res = UniversalWebsiteFetcher.fetch_wordpress_pages(site_url)
            logger.debug(f"refresh_cache: Return value from fetch_wordpress_pages for bot {bot_id}: {pages_res}")
            if pages_res and pages_res.get("success"):
                page_content = " ".join([p.get("content", "") for p in pages_res.get("pages", {}).values()])
                if page_content:
                    # Append to existing about if any, limit length
                    c["about"] = (c.get("about", "") + " " + page_content)[:2000]
                    logger.info(f"Appended WordPress page content to 'about' for bot {bot_id}. New about length: {len(c['about'])}")

        c["last_updated"] = datetime.now()
        _instance_caches[bot_id] = c
    logger.info(f"✅ Bot {bot_id} cache refreshed. Products: {len(c.get('products', []))}, Services: {len(c.get('services', []))}, Contact: {'Present' if c.get('contact') else 'Empty'}")

# ===================== TEMPLATES =====================

def get_language_selection():
    return """🌍 *Welcome!*
*Assalam o Alaikum!* 👋

Please select your language first:

1️⃣ *English*
2️⃣ *Roman Urdu* (اردو in English)
3️⃣ *Urdu* (اردو)

💬 Reply with *1*, *2*, or *3*"""

def _get_greeting(lang, user_name, site_name, business_type):
    site_name = site_name or "our business"
    
    if business_type == "service":
        greetings = {
            'english': f"""👋 Welcome *{user_name}*! I'm your assistant for *{site_name}*.

🛠️ *Your Service Partner*
💬 How can I help you today? Type a number:

1️⃣ 📅 *Book a Service*
2️⃣ 💰 *Service Pricing*
3️⃣ 🏢 *About Us*
4️⃣ 📞 *Contact Us*
5️⃣ ℹ️ *Our Services*

💡 Type *menu* anytime to see these options!""",
            'roman_urdu': f"""👋 Khush amdeed *{user_name}*! Main *{site_name}* ka assistant hoon.

🛠️ *Aap ka Service Partner*
💬 Aaj main aap ki kaise madad kar sakta hoon? Number type karein:

1️⃣ 📅 *Service Book Karein*
2️⃣ 💰 *Rates ki Maloomat*
3️⃣ 🏢 *Humare Baare Mein*
4️⃣ 📞 *Hum se Rabta*
5️⃣ ℹ️ *Humari Services*

💡 *menu* likhein kabhi bhi options dekhne ke liye!"""
        }
    else:
        greetings = {
            'english': f"""👋 Welcome *{user_name}*! I'm your assistant for *{site_name}*.

🛒 *Your Sales Partner*
💬 How can I help you today? Type a number:

1️⃣ 🛍️ *Place an Order*
2️⃣ 💰 *Product Inquiry*
3️⃣ 🚚 *Delivery Info*
4️⃣ 📞 *Contact Us*
5️⃣ ℹ️ *Our Services*

💡 Type *menu* anytime to see these options!""",
            'roman_urdu': f"""👋 Khush amdeed *{user_name}*! Main *{site_name}* ka assistant hoon.

🛒 *Aap ka Sales Partner*
💬 Aaj main aap ki kaise madad kar sakta hoon? Number type karein:

1️⃣ 🛍️ *Order Karein*
2️⃣ 💰 *Product ki Inquiry*
3️⃣ 🚚 *Delivery ki Maloomat*
4️⃣ 📞 *Hum se Rabta*
5️⃣ ℹ️ *Humari Services*

💡 *menu* likhein kabhi bhi options dekhne ke liye!"""
        }
    return greetings.get(lang, greetings['english'])

def _get_menu(lang, business_type="product"):
    if business_type == "service":
        menus = {
            'english': "📋 *Menu*:\n1️⃣ 📅 *Book Service*\n2️⃣ 💰 *Pricing*\n3️⃣ 🏢 *About*\n4️⃣ 📞 *Contact*\n5️⃣ ℹ️ *Services*\n💬 Type a number!",
            'roman_urdu': "📋 *Menu*:\n1️⃣ 📅 *Booking*\n2️⃣ 💰 *Rates*\n3️⃣ 🏢 *Maloomat*\n4️⃣ 📞 *Rabta*\n5️⃣ ℹ️ *Services*\n💬 Number type karein!"
        }
    else:
        menus = {
            'english': "📋 *Menu*:\n1️⃣ 🛍️ *Order*\n2️⃣ 💰 *Inquiry*\n3️⃣ 🚚 *Delivery*\n4️⃣ 📞 *Contact*\n5️⃣ ℹ️ *Services*\n💬 Type a number!",
            'roman_urdu': "📋 *Menu*:\n1️⃣ 🛍️ *Order*\n2️⃣ 💰 *Inquiry*\n3️⃣ 🚚 *Delivery*\n4️⃣ 📞 *Rabta*\n5️⃣ ℹ️ *Services*\n💬 Number type karein!"
        }
    return menus.get(lang, menus['english'])

def _get_contact_info(lang, contact):
    c = contact or {}
    # Enrich with website info if available
    site_name = c.get('site_name', 'our business')
    site_desc = c.get('site_description', '')
    about = c.get('about', '')[:200]

    contacts = {
        'english': f"📞 *Contact Us*\n\n🏢 {site_name}\n📱 Phone: {c.get('phone', 'Not set')}\n📧 Email: {c.get('email', 'Not set')}\n📍 Address: {c.get('address', 'Not set')}\n\nℹ️ {site_desc[:100] if site_desc else about[:100]}",
        'roman_urdu': f"📞 *Hum se Rabta*\n\n🏢 {site_name}\n📱 Phone: {c.get('phone', 'Not set')}\n📧 Email: {c.get('email', 'Not set')}\n📍 Address: {c.get('address', 'Not set')}\n\nℹ️ {site_desc[:100] if site_desc else about[:100]}",
        'urdu': f"📞 *ہم سے رابطہ*\n\n🏢 {site_name}\n📱 فون: {c.get('phone', 'Not set')}\n📧 ای میل: {c.get('email', 'Not set')}\n📍 پتہ: {c.get('address', 'Not set')}\n\nℹ️ {site_desc[:100] if site_desc else about[:100]}"
    }
    return contacts.get(lang, contacts['english'])

def _get_services(lang, services):
    s_list = "\n".join([f"• {s}" for s in services[:10]]) if services else "Check our website for more details."
    msgs = {
        'english': f"🏭 *Our Services*\n\n{s_list}\n\n💬 Want to order? Type *1* or *order*!",
        'roman_urdu': f"🏭 *Humari Services*\n\n{s_list}\n\n💬 Order karna hai? *1* ya *order* likhein!",
        'urdu': f"🏭 *ہماری سروسز*\n\n{s_list}\n\n💬 آرڈر کرنا ہے؟ *1* یا *order* لکھیں!"
    }
    return msgs.get(lang, msgs['english'])

def _t_all_products(items, total, lang):
    item_list = "\n".join(items[:10])
    more = f"\n\n...and {total - 10} more" if total > 10 else ""
    msgs = {
        'english': f"🛍️ *Our Products* ({total} total)\n\n{item_list}{more}\n\n💬 Type *order* to buy!",
        'roman_urdu': f"🛍️ *Humare Products* ({total} total)\n\n{item_list}{more}\n\n💬 Order ke liye *order* likhein!",
        'urdu': f"🛍️ *ہماری پروڈکٹس* ({total} total)\n\n{item_list}{more}\n\n💬 آرڈر کے لیے *order* لکھیں!"
    }
    return msgs.get(lang, msgs['english'])

def _t_order_confirm(product_name, qty, user_name, address, phone, lang, contact):
    msgs = {
        'english': f"""✅ *Order Confirmed!*
📦 Product: {product_name}
🔢 Quantity: {qty}
👤 Name: {user_name}
📍 Address: {address}
📱 Phone: {phone}

🚚 We will contact you soon!
📞 Support: {contact.get('phone', 'Not set')}""",
        'roman_urdu': f"""✅ *Order Confirm Ho Gaya!*
📦 Product: {product_name}
🔢 Quantity: {qty}
👤 Naam: {user_name}
📍 Address: {address}
📱 Phone: {phone}

🚚 Hum jald rabta kareinge!
📞 Help: {contact.get('phone', 'Not set')}""",
        'urdu': f"""✅ *آرڈر تصدیق ہو گیا!*
📦 پروڈکٹ: {product_name}
🔢 مقدار: {qty}
👤 نام: {user_name}
📍 پتہ: {address}
📱 فون: {phone}

🚚 ہم جلد آپ سے رابطہ کریں گے!
📞 سپورٹ: {contact.get('phone', 'Not set')}"""
    }
    return msgs.get(lang, msgs['english'])

def _search_products(query, products, lang):
    query = query.lower()
    matches = []
    for p in products:
        name = p.get('name', '').lower()
        sku = p.get('sku', '').lower()
        if query in name or query in sku:
            matches.append(f"• {p.get('name')} - {p.get('price', 'Contact')}")
    
    if not matches:
        return None
        
    total = len(matches)
    item_list = "\n".join(matches[:15])
    more = f"\n\n...and {total - 15} more" if total > 15 else ""
    
    msgs = {
        'english': f"🔍 *Search Results for '{query}'*:\n\n{item_list}{more}\n\n💬 Type *1* to order!",
        'roman_urdu': f"🔍 *'{query}' ke liye Results*:\n\n{item_list}{more}\n\n💬 Order ke liye *1* likhein!"
    }
    return msgs.get(lang, msgs['english'])

# ===================== LOGIC =====================

PLAN_ERROR = "⚠️ This feature is available in Growth plan. Please upgrade."

def process(bot_id: int, text: str, phone: str, name: str, business_type: str = "product", user_plan: str = "starter"):
    from models import Lead
    from database import SessionLocal

    db = SessionLocal()
    try:
        # 1. Get user state (Lead) - with proper context loading
        lead = db.query(Lead).filter(Lead.bot_id == bot_id, Lead.phone == phone).first()
        context_changed = False

        if not lead:
            logger.info(f"🆕 New user detected: {phone}, creating lead with language_select step")
            lead = Lead(bot_id=bot_id, phone=phone, name=name, context={"step": "language_select", "language": "english"})
            db.add(lead)
            db.commit()
            db.refresh(lead)
            context_changed = True
        else:
            # Initialize context if missing (for existing leads without context)
            if lead.context is None or lead.context == {}:
                logger.info(f"📞 Existing user {phone} has no context, initializing")
                lead.context = {"step": "language_select", "language": "english"}
                db.commit()
                db.refresh(lead)
                context_changed = True
            else:
                logger.info(f"📞 Existing user: {phone}, context: {lead.context}")

        # Ensure context exists
        st = lead.context or {"step": "language_select", "language": "english"}
        lang = st.get("language", "english")
        tl = text.lower().strip()

        if not context_changed:
            logger.info(f"🧭 Bot state - Step: {st.get('step')}, Language: {lang}, Input: '{text[:30]}'")

        # 2. Get Site Data
        c = _get_cache(bot_id)
        if not c.get("last_updated"):
            from models import Integration
            integ = db.query(Integration).filter(Integration.bot_id == bot_id).first()
            if integ:
                from services.encryption import decrypt_value
                k = decrypt_value(integ.woo_consumer_key) if integ.woo_consumer_key else ""
                s = decrypt_value(integ.woo_consumer_secret) if integ.woo_consumer_secret else ""
                refresh_cache(bot_id, k, s, integ.woocommerce_url or integ.wp_base_url, business_type=integ.business_type or business_type)
                c = _get_cache(bot_id)

        # 3. Handle Universal Keywords - RESET unrecognized counter on valid commands
        if tl in ["menu", "0", "start", "main menu"]:
            # Reset unrecognized input counter when user explicitly requests menu
            st = {"step": "active", "language": lang, "unrecognized_inputs": 0}
            lead.context = st
            db.commit()
            db.refresh(lead)
            logger.info(f"✅ Context updated to active menu, counter reset")
            return _get_menu(lang, business_type)

        if tl in ["exit", "bye", "allah hafiz", "khuda hafiz"]:
            st = {"step": "language_select", "language": lang}
            lead.context = st
            db.commit()
            db.refresh(lead)
            logger.info(f"✅ Context reset to language_select")
            return "✅ Thank you! Type *hi* to start again." if lang == "english" else "✅ Shukriya! Phir milenge."

        # 4. Handle Steps

        # Step: Language Select
        if st.get("step") == "language_select":
            if tl in ["1", "english"]:
                # Force new dict for state persistence
                new_st = {"language": "english", "step": "active", "unrecognized_inputs": 0}
                lead.context = new_st
                db.commit()
                db.refresh(lead)
                logger.info(f"✅ Language set to English, step: active")
                return _get_greeting("english", name, c.get("site_name"), business_type)
            elif tl in ["2", "roman", "roman urdu"]:
                new_st = {"language": "roman_urdu", "step": "active", "unrecognized_inputs": 0}
                lead.context = new_st
                db.commit()
                db.refresh(lead)
                logger.info(f"✅ Language set to Roman Urdu, step: active")
                return _get_greeting("roman_urdu", name, c.get("site_name"), business_type)
            elif tl in ["3", "urdu"]:
                new_st = {"language": "urdu", "step": "active", "unrecognized_inputs": 0}
                lead.context = new_st
                db.commit()
                db.refresh(lead)
                logger.info(f"✅ Language set to Urdu, step: active")
                return _get_greeting("urdu", name, c.get("site_name"), business_type)
            else:
                logger.info(f"⏳ Waiting for language selection (1/2/3)")
                return get_language_selection()

        # Step: Active (Menu) - with plan-based feature gating
        if st.get("step") == "active":
            # 1. Handle Order / Place Order / Booking
            if tl in ["1", "1️⃣", "order", "buy", "place order", "book", "booking"]:
                if user_plan == "starter" and business_type == "product":
                    return PLAN_ERROR
                
                new_st = dict(st)
                new_st.update({"step": "sales_product", "unrecognized_inputs": 0})
                lead.context = new_st
                db.commit()
                db.refresh(lead)
                
                if business_type == "service":
                    return "🛠️ *Service Booking*\n\nWhich service are you interested in? Please type the service name." if lang == "english" else "🛠️ *Service Booking*\n\nAap konsi service lena chahte hain? Meherbani farmakar naam likhein."
                return "🛒 *Place Your Order*\n\nWhich product would you like to buy? (Enter Name or Code)" if lang == "english" else "🛒 *Order Karein*\n\nAap konsi cheez kharidna chahte hain? (Naam ya Code likhein)"

            # 2. Handle Inquiry / Pricing
            if tl in ["2", "2️⃣", "inquiry", "price", "pricing"]:
                if business_type == "product" and user_plan == "starter":
                    return PLAN_ERROR
                
                new_st = dict(st)
                new_st["unrecognized_inputs"] = 0
                lead.context = new_st
                db.commit()
                db.refresh(lead)

                if business_type == "service":
                    return _get_services(lang, c.get("services"))
                
                products = c.get("products", [])
                if not products:
                    return "⚠️ No products found. Please check back later or contact us directly."
                
                items = [f"• {p.get('name', 'Product')} - {p.get('price', 'Contact')}" for p in products[:15]]
                return _t_all_products(items, len(products), lang)

            # 3. Handle Delivery Information OR About Us
            if tl in ["3", "3️⃣", "delivery", "shipping", "about", "info"]:
                new_st = dict(st)
                new_st["unrecognized_inputs"] = 0
                lead.context = new_st
                db.commit()
                db.refresh(lead)
                
                if business_type == "service":
                    about_text = c.get("about", "We provide professional services to our valued clients.")
                    site_name = c.get("site_name", "Our Business")
                    return f"🏢 *About {site_name}*\n\n{about_text[:600]}\n\nType *menu* to go back."

                msgs = {
                    'english': "🚚 *Delivery Information*\n\n✅ We deliver nationwide across Pakistan.\n⏱️ Estimated time: 3-5 business days.\n💰 Cash on Delivery (COD) available!\n\nType *menu* to go back.",
                    'roman_urdu': "🚚 *Delivery ki Maloomat*\n\n✅ Hum poore Pakistan mein delivery karte hain.\n⏱️ Time: 3-5 working days.\n💰 Cash on Delivery ki sahulat mojud hai!\n\n*menu* likhein wapas jane ke liye.",
                }
                return msgs.get(lang, msgs['english'])

            # 4. Handle Contact Us
            if tl in ["4", "4️⃣", "contact", "rabta"]:
                new_st = dict(st)
                new_st["unrecognized_inputs"] = 0
                lead.context = new_st
                db.commit()
                db.refresh(lead)
                return _get_contact_info(lang, c.get("contact"))

            # 5. Handle Our Services
            if tl in ["5", "5️⃣", "services", "service"]:
                new_st = dict(st)
                new_st["unrecognized_inputs"] = 0
                lead.context = new_st
                db.commit()
                db.refresh(lead)
                return _get_services(lang, c.get("services"))

            # Handle unrecognized input with a counter OR Search
            if business_type == "product" and len(tl) > 2:
                products = c.get("products", [])
                search_res = _search_products(text, products, lang)
                if search_res:
                    new_st = dict(st)
                    new_st["unrecognized_inputs"] = 0
                    lead.context = new_st
                    db.commit()
                    db.refresh(lead)
                    return search_res

            unrecognized_count = st.get("unrecognized_inputs", 0)
            if unrecognized_count >= 3:
                logger.warning(f"User {phone} entered unrecognized input 3 times, resetting conversation.")
                new_st = {"step": "language_select", "language": lang, "unrecognized_inputs": 0}
                lead.context = new_st
                db.commit()
                db.refresh(lead)
                return get_language_selection()
            else:
                new_st = dict(st)
                new_st["unrecognized_inputs"] = unrecognized_count + 1
                lead.context = new_st
                db.commit()
                db.refresh(lead)
                logger.info(f"Unrecognized input from user {phone}. Unrecognized count: {new_st['unrecognized_inputs']}")
                return "❓ I didn't understand that. Please choose an option from the menu (1-5)." if lang == "english" else "❓ Samajh nahi aaya. Menu se option choose karein (1-5)."

        # Sales Flow Steps - reset unrecognized counter when in valid flow
        if st.get("step") == "sales_product":
            st.update({"order_product": text, "step": "sales_quantity", "unrecognized_inputs": 0})
            lead.context = st
            db.commit()
            db.refresh(lead)
            logger.info(f"✅ Step changed to sales_quantity, product: {text}")
            return "🔢 How many pieces do you need?" if lang == "english" else "🔢 Kitne pieces chahiye?"

        if st.get("step") == "sales_quantity":
            try:
                qty_val = int(text)
                if qty_val < 1:
                    raise ValueError()
            except (ValueError, TypeError):
                return "Please enter a valid number (e.g., 1, 2, 3)" if lang == "english" else "Barah-e-karam sahi number likhein (maslan: 1, 2, 3)"

            st.update({"order_qty": text, "step": "sales_details", "unrecognized_inputs": 0})
            lead.context = st
            db.commit()
            db.refresh(lead)
            logger.info(f"✅ Step changed to sales_details, qty: {text}")
            return "👤 Please share your Name and Full Address for delivery." if lang == "english" else "👤 Apna Naam aur Mukammal Address likhein delivery ke liye."

        if st.get("step") == "sales_details":
            # Final Confirmation
            product = st.get("order_product")
            qty = st.get("order_qty")
            st["order_address"] = text
            st["step"] = "sales_confirm"
            st["unrecognized_inputs"] = 0
            lead.context = st
            db.commit()
            db.refresh(lead)
            logger.info(f"✅ Step changed to sales_confirm, address: {text}")
            confirm_msg = f"📋 Confirm Order:\nProduct: {product}\nQty: {qty}\nAddress: {text}\n\nReply *yes* to confirm." if lang == "english" else f"📋 Order Confirm Karein:\nCheez: {product}\nQty: {qty}\nAddress: {text}\n\n*yes* likhein confirm karne ke liye."
            return confirm_msg

        if st.get("step") == "sales_confirm":
            if tl in ["yes", "haan", "han", "confirm", "ok"]:
                product = st.get("order_product")
                qty = st.get("order_qty")
                addr = st.get("order_address")
                st = {"step": "active", "language": lang, "unrecognized_inputs": 0}
                lead.context = st
                db.commit()
                db.refresh(lead)
                logger.info(f"✅ Order confirmed! Reset to active menu")
                return _t_order_confirm(product, qty, name, addr, phone, lang, c.get("contact", {}))
            else:
                st["step"] = "active"
                st["unrecognized_inputs"] = 0
                lead.context = st
                db.commit()
                db.refresh(lead)
                logger.info(f"❌ Order cancelled, reset to active")
                return "❌ Order cancelled. Type *menu* for options." if lang == "english" else "❌ Order cancel ho gaya. *menu* likhein."

        # Unknown step - reset to active
        st = {"step": "active", "language": lang, "unrecognized_inputs": 0}
        lead.context = st
        db.commit()
        db.refresh(lead)
        return _get_menu(lang)

    except Exception as e:
        logger.error(f"Default Bot Error: {e}")
        return "Sorry, I'm having some technical issues. Type *menu* to restart."
    finally:
        db.close()
