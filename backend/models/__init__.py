from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # admin, user
    plan = Column(String(20), default="starter")  # starter, growth
    full_name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bot = relationship("Bot", back_populates="owner", uselist=False, cascade="all, delete-orphan")


class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    mode = Column(String(20), default="default")  # default, predefined, ai
    status = Column(Boolean, default=True)  # True=active, False=stopped
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="bot")
    settings = relationship("BotSettings", back_populates="bot", uselist=False, cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="bot", uselist=False, cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="bot", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="bot", cascade="all, delete-orphan")


class BotSettings(Base):
    __tablename__ = "bot_settings"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), unique=True, nullable=False)
    prompt = Column(Text, nullable=True)
    model_name = Column(String(50), default="openrouter")  # Provider: openai, gemini, openrouter, qwen
    specific_model_name = Column(String(100), nullable=True) # Exact model: gpt-4o, etc.
    api_key = Column(Text, nullable=True)  # Encrypted
    temperature = Column(Integer, default=70)
    language = Column(String(20), default="english")
    custom_responses = Column(JSON, nullable=True)
    custom_products = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    bot = relationship("Bot", back_populates="settings")


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), unique=True, nullable=False)
    whatsapp_token = Column(Text, nullable=True)  # Encrypted
    phone_number_id = Column(String(100), nullable=True)
    whatsapp_number = Column(String(30), nullable=True)  # For wa.me link generation
    verify_token = Column(String(100), nullable=True)  # Encrypted
    woocommerce_url = Column(String(255), nullable=True)  # WooCommerce store URL
    woo_consumer_key = Column(Text, nullable=True)  # Encrypted
    woo_consumer_secret = Column(Text, nullable=True)  # Encrypted
    wp_base_url = Column(String(255), nullable=True)
    woo_products_cached = Column(Boolean, default=False)  # Whether products have been fetched
    woo_categories_cached = Column(JSON, nullable=True)  # Cached category list
    woo_products_count = Column(Integer, default=0)  # Number of cached products
    business_type = Column(String(20), default="product")  # product, service
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    bot = relationship("Bot", back_populates="integrations")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(20), nullable=False)  # "user" or "bot"
    phone_number = Column(String(30), nullable=False, index=True)
    message = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    bot = relationship("Bot", back_populates="messages")


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        UniqueConstraint("bot_id", "phone", name="uq_bot_phone"),
    )

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    phone = Column(String(30), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    last_message = Column(Text, nullable=True)
    context = Column(JSON, nullable=True)  # To store session state (step, language, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    bot = relationship("Bot", back_populates="leads")


class Usage(Base):
    __tablename__ = "usage_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    whatsapp_messages_sent = Column(Integer, default=0)
    whatsapp_limit = Column(Integer, default=1000)
    ai_requests_made = Column(Integer, default=0)
    ai_limit = Column(Integer, default=500)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")
