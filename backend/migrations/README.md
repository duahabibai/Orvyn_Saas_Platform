# Database Migrations for PostgreSQL

This directory contains database migrations for the WhatsApp Bot SaaS platform.

## Production Database Setup

### Option 1: Using Render PostgreSQL (Recommended)

1. Create a PostgreSQL database on [Render](https://render.com/database)
2. Copy the connection string to your `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```
3. Tables are created automatically on application startup

### Option 2: Using Supabase (Free Tier)

1. Create a project on [Supabase](https://supabase.com)
2. Go to Project Settings → Database
3. Copy the connection string (use transaction/pooler mode for production)
4. Add to `.env`

### Option 3: Self-hosted PostgreSQL

```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# Create database and user:
sudo -u postgres psql
CREATE DATABASE whatsapp_saas;
CREATE USER whatsapp_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE whatsapp_saas TO whatsapp_user;
\q

# Add to .env:
DATABASE_URL=postgresql://whatsapp_user:your_secure_password@localhost:5432/whatsapp_saas
```

## Automatic Table Creation

The application automatically creates tables on startup via `database.py`:

```python
Base.metadata.create_all(bind=engine)
```

This is suitable for:
- Development environments
- Small production deployments
- Applications without complex migration needs

## Manual Migration Script

For production environments requiring explicit migration control, use:

```bash
cd backend
python -c "from database import init_db; init_db()"
```

## Schema Overview

### Tables

1. **users** - User accounts
   - id, email, password_hash, role, full_name, created_at

2. **bots** - Bot instances (one per user)
   - id, user_id, mode, status, created_at

3. **bot_settings** - Bot configuration
   - id, bot_id, prompt, model_name, api_key (encrypted), temperature, language, custom_responses, custom_products

4. **integrations** - WhatsApp, WooCommerce, WordPress integrations
   - id, bot_id, whatsapp_token (encrypted), phone_number_id, verify_token, woocommerce_url, woo_consumer_key (encrypted), woo_consumer_secret (encrypted), wp_base_url, business_type

5. **messages** - Message history
   - id, bot_id, sender, phone_number, message, timestamp

6. **leads** - Customer leads
   - id, bot_id, phone, name, last_message, context, created_at, updated_at

7. **usage_stats** - Usage tracking
   - id, user_id, whatsapp_messages_sent, ai_requests_made, updated_at

## Connection Pooling (Production)

PostgreSQL connection pooling is configured in `database.py`:
- Pool size: 20 connections
- Max overflow: 40 connections
- Pool recycle: 30 minutes
- Pre-ping: Enabled (connection health checks)

This supports 24/7 bot operation with high availability.
