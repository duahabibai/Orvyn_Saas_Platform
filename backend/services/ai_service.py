"""Multi-provider AI service.

Supported providers (set via bot_settings.model_name):
  - openai
  - gemini
  - openrouter
  - qwen
"""
import time
import json
import threading
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

_rate_lock = threading.Lock()
_last_429 = 0
_last_req = 0

# Available models per provider (latest paid versions)
AVAILABLE_MODELS: Dict[str, list] = {
    "openai": [
        {"value": "gpt-4o", "label": "GPT-4o (Latest)", "type": "paid"},
        {"value": "gpt-4o-mini", "label": "GPT-4o Mini (Fast)", "type": "paid"},
        {"value": "o1", "label": "O1 (Reasoning)", "type": "paid"},
        {"value": "o1-mini", "label": "O1 Mini", "type": "paid"},
        {"value": "o3-mini", "label": "O3 Mini", "type": "paid"},
    ],
    "openrouter": [
        {"value": "openai/gpt-4o", "label": "GPT-4o", "type": "paid"},
        {"value": "anthropic/claude-3.5-sonnet", "label": "Claude 3.5 Sonnet", "type": "paid"},
        {"value": "google/gemini-pro-1.5", "label": "Gemini Pro 1.5", "type": "paid"},
        {"value": "meta-llama/llama-3.1-70b-instruct", "label": "Llama 3.1 70B", "type": "paid"},
        {"value": "openai/gpt-oss-20b:free", "label": "GPT-OSS 20B (Free)", "type": "free"},
    ],
    "gemini": [
        {"value": "gemini-2.0-flash", "label": "Gemini 2.0 Flash", "type": "paid"},
        {"value": "gemini-2.0-pro", "label": "Gemini 2.0 Pro", "type": "paid"},
        {"value": "gemini-2.0-flash-lite", "label": "Gemini 2.0 Flash Lite", "type": "paid"},
    ],
    "qwen": [
        {"value": "qwen-plus", "label": "Qwen Plus", "type": "paid"},
        {"value": "qwen-max", "label": "Qwen Max", "type": "paid"},
        {"value": "qwen-turbo", "label": "Qwen Turbo (Fast)", "type": "paid"},
        {"value": "qwen-long", "label": "Qwen Long", "type": "paid"},
    ],
}

# Provider configurations
PROVIDERS = {
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "header": "Authorization",
        "header_fmt": "Bearer {key}",
        "extra_headers": {"HTTP-Referer": "https://example.com", "X-Title": "WhatsApp Bot"},
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "header": "Authorization",
        "header_fmt": "Bearer {key}",
        "extra_headers": {},
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "header": "Authorization",
        "header_fmt": "Bearer {key}",
        "extra_headers": {},
    },
    "qwen": {
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "header": "Authorization",
        "header_fmt": "Bearer {key}",
        "extra_headers": {},
    },
}


def ai_reply(text: str, lang: str, api_key: str, provider: str,
             prompt: str, temperature: float, contact: dict,
             products: list, categories: list, model_name: str = None,
             business_type: str = "product", user_plan: str = "starter") -> Optional[str]:
    """Call AI API with the specified provider.

    Args:
        provider: "openai", "gemini", "openrouter", or "qwen"
        temperature: 0.0 to 1.0
        model_name: Specific model to use (optional, uses provider default if not set)
        business_type: "product" or "service"
        user_plan: "starter" or "growth" - affects what info AI can share
    """
    if not api_key or not api_key.strip():
        logger.error("AI mode: API key is empty or None")
        return None

    api_key = api_key.strip()
    logger.info(f"AI mode: Using provider '{provider}' with key '{api_key[:10]}...'")

    global _last_429, _last_req
    with _rate_lock:
        if _last_429 > 0 and (time.time() - _last_429) < 5:
            logger.warning("AI request skipped due to recent rate limit")
            return None
        wait = 0.8 - (time.time() - _last_req)
        if wait > 0:
            time.sleep(wait)
        _last_req = time.time()

    lang_map = {
        'english': "Respond in English",
        'roman_urdu': "Respond in Roman Urdu (Urdu written in English script, like 'Aap kaise hain?')",
        'urdu': "Respond in Urdu script (اردو)"
    }

    # Build website info section
    site_name = contact.get('site_name', 'our business')
    site_desc = contact.get('site_description', '')
    about = contact.get('about', '')
    services = contact.get('services', [])

    # Extract contact details with fallbacks
    contact_phone = contact.get('phone', '')
    contact_email = contact.get('email', '')
    contact_address = contact.get('address', '')
    contact_hours = contact.get('hours', '')

    # Feature gating: Free plan = service only, Starter/Growth = product access
    # Starter plan: limit to 10 products, Growth: unlimited (up to 30 in AI context)
    show_products = (user_plan in ["starter", "growth"] and business_type == "product")
    product_limit = 10 if user_plan == "starter" else 30

    # Build CONTACT section FIRST (most important for service queries)
    contact_section = f"## 📞 CONTACT INFO for {site_name}:\n"
    contact_section += f"- Phone: {contact_phone if contact_phone else 'Available on website'}\n"
    contact_section += f"- Email: {contact_email if contact_email else 'Available on website'}\n"
    contact_section += f"- Address: {contact_address if contact_address else 'Available on website'}\n"
    if contact_hours:
        contact_section += f"- Business Hours: {contact_hours}\n"

    website_section = f"## 🌐 WEBSITE INFO ({site_name}):\n"
    if site_desc: website_section += f"- Description: {site_desc}\n"
    if about: website_section += f"- About: {about[:800]}\n"
    if services: website_section += f"- 🛠️ Services: {', '.join(services[:15])}\n"
    website_section += f"- Business Type: {business_type.upper()} based\n"
    website_section += f"- User Plan: {user_plan.title()}\n"

    # Build product catalog section with plan-based limits
    catalog_section = ""
    if business_type == "product":
        if show_products and products:
            catalog_lines = ["## 🛍️ PRODUCT CATALOG:"]
            for p in products[:product_limit]:
                p_name = p.get('name', '?')[:50]
                sku = p.get('sku', '')
                price = p.get('price', '0')
                stock = "In Stock" if p.get("stock_status") == "instock" else "Out of Stock"
                catalog_lines.append(f"  - {p_name} | SKU: {sku} | {price} PKR | {stock}")
            if len(products) > product_limit:
                catalog_lines.append(f"  ...and {len(products) - product_limit} more products")
            if user_plan == "starter":
                catalog_lines.append("\n📦 *Note*: Starter plan shows first 10 products. Upgrade to Growth for full catalog.")
            catalog_section = "\n".join(catalog_lines)
        elif user_plan == "free":
            catalog_section = "## PRODUCTS: Not available in Free plan. Upgrade to Starter or Growth for product catalog access."
        else:
            catalog_section = "## PRODUCTS: No product data available. Focus on services and contact info."
    else:
        # Service mode: Products are not relevant - emphasize services
        catalog_section = "## 🛠️ SERVICE MODE: Focus on providing information about SERVICES, CONTACT DETAILS, BUSINESS HOURS, and LOCATION. No product catalog available."

    # Build system prompt: user's custom prompt + website data
    user_prompt = prompt.strip() if prompt else ""
    if not user_prompt:
        if business_type == "service":
            services_text = ", ".join(services[:10]) if services else "various professional services"
            user_prompt = (f"You are a professional service assistant for {site_name}. "
                          f"We offer {services_text}. "
                          f"Use the website data below to provide information about our services and contact details. "
                          f"If specific contact details like email/phone are 'Refer to our website', politely ask them to check our site or offer to have a human reach out.")
        else:
            # Product-based business - all paid plans get product access
            user_prompt = (f"You are a professional sales assistant for {site_name}. "
                          f"Use the website data below to answer questions about our products, services, and how to reach us.")

    lang_instruction = ""
    if lang and lang.lower() != 'auto':
        lang_instruction = f"\n\n## LANGUAGE:\n{lang_map.get(lang, 'Respond in English')}\n- Match the user's language naturally"

    system = f"""{user_prompt}

{website_section}

{catalog_section}

{contact_section}

## RULES:
- Source of Truth: ONLY use the info provided above. NEVER make up products, prices, or details.
- CONTACT INFO: When asked about phone, email, address, or hours - use the ## CONTACT INFO section above.
- SERVICES: When asked about services - use the ## SERVICES section above. List them clearly.
- PRODUCT SEARCH: If user asks for a specific product, SEARCH the ## PRODUCT CATALOG section. List matches with prices.
- SERVICE BUSINESS: If business_type is SERVICE, focus ONLY on services, contact, address, hours - NO products.
- Short & Sweet: Keep replies under 3 lines. This is WhatsApp.
- Tone: Professional, helpful, and concise.
- Missing Info: If contact details show "Available on website", politely offer to have a human contact them.
- Order Flow: If they want to order/hire, ask: Item → Quantity → Name → Address.
- Plan Features: Free plan = service info only. Starter/Growth = full product catalog access.
{lang_instruction}"""

    logger.info(f"AI ({provider}) system prompt built - total length: {len(system)} chars")
    logger.info(f"AI ({provider}) user message: '{text[:50]}...'")

    cfg = PROVIDERS.get(provider, PROVIDERS["openrouter"])

    headers = {
        "Content-Type": "application/json",
        cfg["header"]: cfg["header_fmt"].format(key=api_key),
    }
    for k, v in cfg.get("extra_headers", {}).items():
        headers[k] = v

    # Model selection logic
    default_models = {
        "openrouter": "openai/gpt-4o-mini",
        "openai": "gpt-4o-mini",
        "gemini": "gemini-2.0-flash",
        "qwen": "qwen-plus",
    }

    # If model_name was passed (this is specific_model_name from database)
    model = model_name or default_models.get(provider, "openai/gpt-4o-mini")
    
    # Strip "models/" prefix for Gemini OpenAI-compatible endpoint if present
    if provider == "gemini" and model.startswith("models/"):
        model = model.replace("models/", "")
    
    # Safety check: if user switched provider but kept old specific_model_name
    # (e.g. provider=openai but model=gemini-2.0), fallback to default
    is_valid_for_provider = False
    if provider in AVAILABLE_MODELS:
        valid_values = [m["value"] for m in AVAILABLE_MODELS[provider]]
        if model in valid_values:
            is_valid_for_provider = True
    
    # Custom check for OpenRouter paths or direct model values
    if not is_valid_for_provider:
        if provider == "openrouter" and "/" in model:
            # Valid OpenRouter path (e.g. provider/model)
            pass
        else:
            model = default_models.get(provider, "openai/gpt-4o-mini")

    logger.info(f"AI ({provider}) final selection: model={model}")

    try:
        request_payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            "temperature": temperature,
            "max_tokens": 500,
            "stream": False
        }

        # Handle provider-specific payload differences if any
        if provider == "gemini" and "generativelanguage" in cfg["url"]:
            # Google Gemini OpenAI-compatible endpoint is mostly standard
            pass
            
        r = requests.post(cfg["url"], headers=headers, json=request_payload, timeout=30, verify=False)
        logger.info(f"AI ({provider}) API response status: {r.status_code}")

        if r.status_code == 200:
            data = r.json()
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info(f"AI ({provider}) raw response: {reply[:100] if reply else 'EMPTY'}...")
            if reply and len(reply.strip()) > 1:
                return reply.strip()[:600]
            logger.warning(f"AI ({provider}) response was empty or too short")
        else:
            logger.error(f"AI ({provider}) API error: {r.status_code} - {r.text[:200] if r.text else 'No content'}")
    except Exception as e:
        logger.error(f"AI ({provider}) exception: {e}", exc_info=True)

    return None
