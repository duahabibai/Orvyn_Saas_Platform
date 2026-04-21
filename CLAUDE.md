# ORVYN SaaS Platform - Development Notes

## Project Overview
Multi-tenant WhatsApp bot SaaS platform with AI assistant and WooCommerce integration.

## URLs
- **Frontend (Production):** https://orvynlabs.brandlessdigital.com
- **Backend (Production):** https://orvyn-saas-platform.onrender.com

## Deployment Status

### Backend (Render)
**Status:** Needs redeployment with latest fixes

**Changes to deploy:**
1. CORS configuration updated to allow `https://orvynlabs.brandlessdigital.com`
2. WhatsApp integration now allowed for ALL plans (Free, Starter, Growth)
3. Only WooCommerce/product integration restricted for free users
4. Plan upgrade/downgrade notifications fixed

**Deploy commands:**
```bash
cd backend
git add .
git commit -m "Fix: Allow WhatsApp integration for all plans, fix notifications"
git push
```

### Frontend (Hostinger)
**Status:** Built and ready for upload

**Upload via FileZilla:**
1. Connect to Hostinger
2. Navigate to `public_html`
3. Upload entire contents of `frontend/out/` folder
4. Overwrite all existing files

**Build command:**
```bash
cd frontend
npm run build
```

## Previous Errors (RESOLVED)

### Error: 403 Forbidden on /api/integrations/me
**Cause:** Free plan users were blocked from saving WhatsApp settings
**Fix:** Updated `backend/routers/integrations.py` to only block product integration, not WhatsApp
**Status:** ✅ Fixed, pending deployment

### Error: CORS policy on /api/auth/upgrade-plan
**Cause:** Old backend code on Render without CORS fix
**Fix:** CORS already configured in `backend/main.py` and `backend/.env`
**Status:** ✅ Fixed, pending deployment

### Error: Notifications not refreshing after plan change
**Cause:** Frontend not awaiting data refresh after upgrade/downgrade
**Fix:** Updated `frontend/app/dashboard/subscription/page.tsx` to await usage data
**Status:** ✅ Fixed, pending deployment

## Plan Features

| Feature | Free | Starter ($1/mo) | Growth ($3/mo) |
|---------|------|-----------------|----------------|
| WhatsApp Integration | ✅ | ✅ | ✅ |
| Phone Number ID | ✅ | ✅ | ✅ |
| Verify Token | ✅ | ✅ | ✅ |
| WhatsApp API Token | ✅ | ✅ | ✅ |
| Service-based Flows | ✅ | ✅ | ✅ |
| Product-based Flows | ❌ | ✅ (10 products) | ✅ (unlimited) |
| WooCommerce Integration | ❌ | ✅ | ✅ |
| Product Listing/Search | ❌ | ✅ | ✅ |
| Multi-language Support | ❌ | ❌ | ✅ |
| Live Chat Takeover | ❌ | ❌ | ✅ |
| Broadcast Campaigns | ❌ | Basic | Advanced |
| Advanced Analytics | ❌ | ❌ | ✅ |
| Conversations Limit | 200/month | 500/month | 1500/month |
| AI Requests Limit | 200/month | 500/month | 1500/month |

## Tech Stack
- **Frontend:** Next.js 15, React 19, TypeScript, TailwindCSS
- **Backend:** FastAPI, Python, SQLAlchemy, PostgreSQL
- **Database:** PostgreSQL (Render)
- **Hosting:** Hostinger (frontend), Render (backend)

## Key Files
- Backend CORS: `backend/main.py`, `backend/.env`
- Integrations: `backend/routers/integrations.py`, `frontend/app/dashboard/integrations/page.tsx`
- Subscription: `backend/routers/auth.py`, `frontend/app/dashboard/subscription/page.tsx`
