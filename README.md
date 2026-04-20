# WhatsApp Bot SaaS Platform (ORVYN)

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
│   │   ├── (auth)/         # Auth route group (login, signup)
│   │   ├── dashboard/      # User dashboard pages
│   │   └── not-found.tsx   # Custom 404 page
│   ├── components/         # React components
│   ├── lib/                # Utilities (API client)
│   ├── public/             # Static assets
│   ├── out/                # Production build output
│   ├── next.config.js      # Next.js configuration
│   ├── vercel.json         # Vercel deployment config
│   ├── netlify.toml        # Netlify deployment config
│   └── package.json        # Dependencies & scripts
├── frontend/ftp-deploy/    # FileZilla FTP deployment configs
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

### Frontend (Development)

```bash
cd frontend
npm install
npm run dev
```

### Frontend (Production Build)

```bash
cd frontend
npm run build        # Creates static export in out/
npm run preview      # Preview production build locally
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
- **404 on direct page access**: Ensure server has proper rewrite rules (see `frontend/DEPLOYMENT.md`)

---

## 🌐 Deployment

### Supported Platforms

| Platform | Guide |
|----------|-------|
| Vercel | See `frontend/vercel.json` |
| Netlify | See `frontend/netlify.toml` |
| Render | Static site deployment |
| Apache | `.htaccess` included in build |
| Nginx | See `frontend/DEPLOYMENT.md` |
| FTP/SFTP | See `frontend/ftp-deploy/README.md` |

### Production Build

```bash
cd frontend
npm run build        # Outputs to out/
```

Upload contents of `out/` to your hosting provider.

### Environment Variables (Production)

Set these in your hosting platform:

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL |

See `frontend/DEPLOYMENT.md` for detailed deployment instructions.
