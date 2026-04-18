# WhatsApp Bot SaaS Platform - Production Deployment Guide

## Project Structure

```
whatsapp-bot-saas/
├── backend/
│   ├── .env                 # Backend environment (production secrets)
│   ├── .env.example         # Template for backend .env
│   ├── requirements.txt     # Python dependencies
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration loader
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── routers/             # API routes
│   ├── services/            # Business logic
│   └── schemas/             # Pydantic schemas
├── frontend/
│   ├── .env.local           # Frontend environment (production)
│   ├── .env.example         # Template for frontend env
│   ├── package.json         # Node dependencies
│   ├── next.config.js       # Next.js configuration
│   └── app/                 # Next.js pages
├── .gitignore
└── README.md
```

## Environment Setup

### 1. Backend .env

```bash
cd backend
cp .env.example .env
```

**Required changes for production:**
- `DATABASE_URL`: PostgreSQL connection string (Render, Supabase, etc.)
- `SECRET_KEY`: Generate secure key with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `ENCRYPTION_KEY`: Must be exactly 32 bytes (generate with Fernet)

### 2. Frontend .env.local

```bash
cd frontend
cp .env.example .env.local
```

**Required changes:**
- `NEXT_PUBLIC_API_URL`: Your deployed backend URL
- `NEXT_PUBLIC_WEBHOOK_URL`: Your webhook URL for Meta configuration

## Database Setup

### Option 1: Render PostgreSQL (Recommended)

1. Create database at https://render.com/database
2. Copy internal connection string
3. Add to `backend/.env`:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

### Option 2: Supabase (Free Tier)

1. Create project at https://supabase.com
2. Settings → Database → Connection string
3. Use pooler mode for production

### Option 3: Self-hosted PostgreSQL

```bash
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres psql
CREATE DATABASE whatsapp_saas;
CREATE USER whatsapp_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE whatsapp_saas TO whatsapp_user;
\q
```

## Running the Application

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev  # Development
npm run build && npm start  # Production
```

## Meta WhatsApp Webhook Setup

1. Go to [Meta Developers Dashboard](https://developers.facebook.com)
2. Create/Select your WhatsApp Business App
3. Add Webhook URL: `https://your-domain.com/webhook`
4. Verify Token: Use the `DEFAULT_VERIFY_TOKEN` from your backend .env
5. Subscribe to messages event

### Per-User Webhook Configuration

Each user gets unique:
- **WhatsApp Token** (encrypted in database)
- **Phone Number ID** (from Meta)
- **Verify Token** (for webhook verification)

These are configured in the Integrations page and **persist** until user changes them.

## Key Production Features

### 1. Persistent Token Management

- Tokens are NEVER cleared unless user explicitly reconfigures
- Each user has unique encrypted tokens
- Tokens survive bot mode changes, website changes, settings updates

### 2. 24/7 Bot Reliability

- Connection pooling (20 connections, 40 overflow)
- Automatic reconnection on connection loss
- Comprehensive error handling
- Request timing and logging
- Signature validation (enforced in production)

### 3. Multi-Tenant Architecture

- All users share same webhook URL
- Routing by phone_number_id
- Isolated data per user
- Per-user usage tracking

### 4. Optional WooCommerce Integration

- Consumer key/secret are OPTIONAL
- Supports product-based and service-based websites
- Auto-discovery of website platform
- Fallback to web scraping if API keys not provided

### 5. Pricing Plans

- **Starter Plan** ($1/month): Service-only flows, 200 conversations/month
- **Growth Plan** ($3/month): Full features, 1500 conversations/month, WooCommerce enabled

## Security

### Encryption

- WhatsApp tokens: Encrypted with Fernet (32-byte key)
- WooCommerce keys: Encrypted
- Verify tokens: Stored as plain text (not secret)
- JWT tokens: HS256 algorithm

### Production Checklist

- [ ] Change `SECRET_KEY` to secure random value
- [ ] Generate new `ENCRYPTION_KEY` (32 bytes)
- [ ] Set `ENVIRONMENT=production`
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS for webhook endpoint
- [ ] Configure CORS origins for your domain
- [ ] Set up rate limiting
- [ ] Enable webhook signature validation

## Monitoring

### Logs

```bash
# Backend logs (stdout)
journalctl -u your-service -f

# Application logs
tail -f backend/logs/*.log
```

### Health Check

```bash
curl https://your-domain.com/health
# Response: {"status": "ok", "app": "WhatsApp Bot SaaS"}
```

## Troubleshooting

### Webhook Not Receiving Messages

1. Verify webhook URL is publicly accessible
2. Check Meta app subscription status
3. Verify verify_token matches
4. Check server logs for signature validation errors

### Database Connection Errors

1. Verify PostgreSQL is running
2. Check connection string format
3. Ensure firewall allows connections
4. Test with `psql` client

### Token Decryption Failures

1. Verify `ENCRYPTION_KEY` is 32 bytes
2. Check key matches between restarts
3. Re-enter tokens if key was changed

## Environment Variable Generation

### Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Generate ENCRYPTION_KEY

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Support

For issues, check:
- Application logs
- Meta Developer Dashboard
- Database connection status
- Environment variable configuration
