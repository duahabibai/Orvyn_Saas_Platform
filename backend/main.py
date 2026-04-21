"""
WhatsApp Bot SaaS Platform - FastAPI Backend
Production-ready multi-tenant WhatsApp bot with pricing plans
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import auth, bots, integrations, webhook, chat, conversations
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version="2.0")

# Configure CORS with high compatibility for production
origins = [
    "https://orvynlabs.brandlessdigital.com",
    "https://orvyn-saas-platform.onrender.com",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3004",
]

if settings.ALLOWED_ORIGINS:
    for o in settings.ALLOWED_ORIGINS.split(","):
        origin = o.strip()
        if origin:
            if origin not in origins:
                origins.append(origin)
            # Add variation with/without trailing slash
            alt = origin[:-1] if origin.endswith("/") else f"{origin}/"
            if alt not in origins:
                origins.append(alt)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://orvynlabs.brandlessdigital.com",
        "https://orvyn-saas-platform.onrender.com",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3004",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)# Include routers
app.include_router(auth.router)
app.include_router(bots.router)
app.include_router(integrations.router)
app.include_router(webhook.router)
app.include_router(chat.router)
app.include_router(conversations.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "2.0 - Multi-tenant SaaS with Pricing Plans"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
