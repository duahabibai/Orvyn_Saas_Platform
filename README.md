# WhatsApp Bot SaaS Platform

Multi-tenant WhatsApp bot platform with AI assistant, WooCommerce integration, and dashboard.

## 📁 Project Structure

```
project/
├── backend/                 # FastAPI backend
│   ├── data/               # Database files (SQLite)
│   ├── logs/               # Application logs
│   ├── migrations/         # Database migration scripts
│   ├── models/             # SQLAlchemy models
│   ├── routers/            # API routes
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── tests/              # Test files
│   ├── main.py             # Entry point
│   ├── config.py           # Configuration
│   ├── database.py         # Database setup
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js dashboard
│   ├── app/                # Pages and routes
│   ├── components/         # React components
│   └── lib/                # Utilities
├── .env.example            # Environment variables template
└── docker-compose.yml      # Docker setup
```

## 🚀 Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker (All-in-one)

```bash
docker-compose up -d
```

## 🔧 Configuration

1. Copy `.env.example` to `.env`
2. Update the values:
   - `DATABASE_URL` - SQLite or PostgreSQL
   - `SECRET_KEY` - JWT secret
   - `ENCRYPTION_KEY` - For encrypting API keys
   - Default WooCommerce credentials (optional)

## 📡 API Endpoints

- `GET /health` - Health check
- `GET /docs` - Swagger API documentation
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /webhook` - WhatsApp webhook (Meta)
- `GET /api/integrations/me` - Get user integrations
- `PATCH /api/integrations/me` - Update integrations

## 🤖 Bot Modes

- **default** - Uses WooCommerce/WordPress data
- **predefined** - Keyword-based responses
- **ai** - AI provider (OpenAI, Gemini, OpenRouter, Qwen)

## 📦 Features

- ✅ Multi-tenant architecture
- ✅ JWT authentication
- ✅ WhatsApp Cloud API integration
- ✅ WooCommerce product sync
- ✅ WordPress page integration
- ✅ AI-powered responses
- ✅ Real-time chat dashboard
- ✅ Lead management
- ✅ Multi-language support (English, Urdu, Roman Urdu)

## ⚠️ Important Notes

- The original bot logic is preserved in `backend/original_bot.py`
- If no SaaS config is set, the system falls back to original bot behavior
- All API keys are encrypted in the database
- Webhook signature validation is enforced

## 🧪 Testing

```bash
cd backend/tests
python -m pytest
```

## 🐛 Troubleshooting

- **Database errors**: Check `DATABASE_URL` in `.env`
- **Webhook not receiving**: Ensure ngrok is running and URL is updated in Meta
- **Frontend not connecting**: Verify `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
