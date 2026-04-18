# 💰 PRICING SYSTEM (STRICT FEATURE CONTROL)

You must implement pricing with STRICT feature gating.

---

# 🎯 PLANS

## 🟠 STARTER PLAN ($1/month)

Features:

- WhatsApp bot access
- ONLY Service-based flow (NO product support)
- Website content fetch (basic)
- Limited predefined templates
- AI bot integration (user provides API key)
- Up to 200 conversations/month
- Basic lead capture
- Test mode (sandbox)
- Basic dashboard
- Email support

---

❌ NOT ALLOWED IN STARTER:

- Product-based flows
- WooCommerce integration
- Product listing / product search
- Live chat takeover
- Multi-language support
- Advanced automation
- Advanced analytics
- Unlimited templates

---

## 🟢 GROWTH PLAN ($3/month)

Features:

- Everything in Starter
- Product + Service flows BOTH
- WooCommerce integration ENABLED
- Product listing + search
- Advanced website learning
- Unlimited templates
- Smart AI responses
- Up to 1500 conversations/month
- Full automation funnel
- User tagging
- Broadcast campaigns
- Advanced dashboard
- Multi-language support
- Live chat takeover
- Priority support

---

# 🧠 BACKEND IMPLEMENTATION

## Add in users table:

plan = "starter" or "growth"
default = "starter"

---

# 🔐 STRICT FEATURE ENFORCEMENT

## PRODUCT FEATURE LOCK

IF user.plan == "starter":

- BLOCK WooCommerce API usage
- BLOCK product search
- BLOCK product listing

Return:

"Upgrade to Growth plan to use product features"

---

## SERVICE ONLY FLOW

IF starter:

- allow WordPress (services)
- allow basic chatbot

---

## LIMIT SYSTEM

Starter:

- max 200 conversations/month

Growth:

- max 1500 conversations/month

---

## AUTOMATION LIMITS

Starter:

- limited rules
- limited menus

Growth:

- unlimited

---

# 🚫 BLOCK LOGIC (IMPORTANT)

Before executing ANY feature:

Check:

IF feature requires "growth" AND user.plan == "starter":
    return error message

---

# 💬 ERROR MESSAGE

Standard message:

"⚠️ This feature is available in Growth plan. Please upgrade."

---

# 🧩 FRONTEND IMPLEMENTATION

## HIDE FEATURES (STARTER)

Do NOT show:

- Product integrations
- WooCommerce fields
- Advanced settings

---

## SHOW LOCK UI

If user tries restricted feature:

- Show modal:

"Upgrade to Growth to unlock this feature"

---

# 📊 DASHBOARD DISPLAY

Show:

Plan: Starter / Growth  
Usage: X / limit  

---

# 🛠️ ADMIN CONTROL

Admin can:

- Change plan manually
- Monitor usage

---

# 🔁 USAGE RESET

Reset monthly usage automatically

---

# 🎯 FINAL BEHAVIOR

Starter user:

- Only service chatbot works
- No product features visible or usable

Growth user:

- Full SaaS access

---

# ⚠️ DO NOT BREAK

- existing bot logic
- webhook system
- chat flow

Only ADD plan-based restrictions